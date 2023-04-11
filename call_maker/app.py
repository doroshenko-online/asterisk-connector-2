import logging
import json
import time

from call_maker.constants import CNET_URLS, REDIS_ACTIVE_CALLS_KEY, REDIS_END_CALLS_KEY
from call_maker.utils import clear_active_calls
from ami_parser.ami_parser import connect, logon, logoff, originate

from flask import Flask, request


app = Flask(__name__)
ami_host = None
ami_port = None
ami_user = None
ami_secret = None
redis = None
aggregate_stats = False


@app.route('/make_call')
def make_call():
    num_src = request.args.get('num_src')
    num_dst = request.args.get('num_dst')
    from_project = None

    if aggregate_stats:
        from_project = request.args.get('project')

    if aggregate_stats and from_project not in CNET_URLS:
        logging.info(f'unknown cnet project {from_project}. Num src: {num_src}. Num dst: {num_dst}')
        return json.dumps({'success': False, 'error': f'unknown cnet project {from_project}'})

    redis_data = {'url': CNET_URLS[from_project], 'prj': from_project, 'num_dst': num_dst}


    logging.info(f'New call request - src: {num_src} | dst: {num_dst}')
    if all([redis, num_src, num_dst]):
        s, _ = connect(ami_host, ami_port)
        if s:
            call = redis.get(num_src)
            if call:
                return json.dumps({'success': False, 'error': 'Call already in progress'})
            else:
                if aggregate_stats:
                    redis.set(num_src, json.dumps(redis_data))
                else:
                    redis.setex(num_src, 300, num_dst)

                logon(s, ami_user, ami_secret)
                originate(s, num_src, num_dst)
                time.sleep(0.1)
                logoff(s)

                if aggregate_stats:
                    active_calls = redis.get(REDIS_ACTIVE_CALLS_KEY)
                    active_calls = json.loads(active_calls) if active_calls else {}
                    active_calls[num_src] = 1
                    redis.set(REDIS_ACTIVE_CALLS_KEY, json.dumps(active_calls))

                return json.dumps({'success': True, 'error': None})

    return json.dumps({'success': False, 'error': 'No data for call'})


def start_app(ahost, aport, auser, asecret, red, port, aggr_stats=False):
    global redis
    global ami_host
    global ami_port
    global ami_user
    global ami_secret
    global aggregate_stats

    redis = red
    ami_host = ahost
    ami_port = aport
    ami_user = auser
    ami_secret = asecret
    aggregate_stats = aggr_stats

    # clear old active calls in redis
    clear_active_calls(redis)

    app.run(port=port)


def send_stats(redis):
    while True:
        ended_calls = redis.get(REDIS_END_CALLS_KEY)
        ended_calls = json.loads(ended_calls) if ended_calls else {}
        for num_src in ended_calls.keys():
            send_data = ended_calls[num_src]['data']
            target_url = ended_calls[num_src]['cnet_url']

            # TODO: Отправка на проект

        redis.set(REDIS_END_CALLS_KEY, json.dumps({}))
        time.sleep(1)
