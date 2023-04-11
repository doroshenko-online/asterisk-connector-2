import logging
import socket
import time

from ami_parser.events.event_fabric import EventFabric
from ami_parser.registry import Registry

from call_maker.constants import CLIENT_CONTEXT, MANAGER_CONTEXT
from call_maker.utils import clear_active_calls

logon_str = """Action: login\r\nUsername: {user}\r\nSecret: {secret}\r\n\r\n"""
originate_str = """Action: originate\r\nChannel: Local/{num_src}@{man_context}\r\nContext: {client_context}\r\nExten: {num_dst}\r\nAsync: True\r\n\r\n"""
logoff_str = """Action: logoff\r\n\r\n"""


def start(ami_host, ami_port, ami_user, ami_secret, redis):
    s, ami_version = connect(ami_host, ami_port)

    logging.info(f'Ami version: {ami_version}')

    if not s or not ami_version:
        logging.error('Failed AMI connect')
        raise Exception('Failed AMI connect')

    r = Registry(redis)
    r.clear_register()
    clear_active_calls(redis)

    logon(s, ami_user, ami_secret)
    parse(s, ami_host, ami_port, ami_user, ami_secret, redis)


def connect(ami_host, ami_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((ami_host, ami_port))
    except Exception as e:
        logging.error(e)
        return None, None
    else:
        time.sleep(0.1)
        response = s.recv(1024).decode('utf-8')
        ami_version = float(response.split('/')[1])

    return s, ami_version


def logon(sock, user, secret):
    sock.send(logon_str.format(
        user=user,
        secret=secret
    ).encode())
    time.sleep(0.1)
    sock.recv(1024)

def originate(sock, num_src, num_dst):
    sock.send(
        originate_str.format(
            num_src=num_src,
            num_dst=num_dst,
            man_context=MANAGER_CONTEXT,
            client_context=CLIENT_CONTEXT
        ).encode()
    )


def logoff(sock):
    sock.send(logoff_str.encode())

def parse(sock, ami_host, ami_port, ami_user, ami_secret, redis):
    event_dict = {}
    previous_events = ''

    while True:

        try:
            res = sock.recv(1024).decode('utf-8')
        except Exception:
            logging.warning('Error while reading socket. Reconnect...')
            time.sleep(3)
            break

        events_data = res.split('\r\n\r\n')
        if previous_events:
            events_data[0] = previous_events + events_data[0]
            previous_events = ''

        try:
            divided_events = events_data.pop(-1)
        except IndexError:
            logging.warning(f'Something wrong with events from AMI - {events_data}')

        for event in events_data:
            event_data = event.split('\r\n')
            event_data = [value for value in event_data if value]
            if event_data:
                for row in event_data:
                    row_arr = row.split(':')
                    field = row_arr[0]
                    value = ''.join(row_arr[1:])
                    event_dict[field] = value.strip()

                if event_dict.get('Event'):
                    event_obj = EventFabric.get_event(event_dict, redis)
                    if event_obj:
                        event_obj.do_action()
                event_dict = {}
        previous_events = divided_events

    start(ami_host, ami_port, ami_user, ami_secret, redis)
