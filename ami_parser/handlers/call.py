import logging
import json

from typing import Any, Union

from ami_parser.enums import CallTypes, Dialstatuses, ChannelTypes, DialSubEvents, BridgeStates

from call_maker.constants import MANAGER_CONTEXT, REDIS_ACTIVE_CALLS_KEY, REDIS_END_CALLS_KEY


class Call:

    def __init__(self, linkedid) -> None:
        self.channels_by_timestamp: dict = {}
        self.channels: dict = {}
        self.dialog_durations: dict = {}
        self.dialings: dict = {}
        self.call_duration: int = None  # seconds
        self.hangup_requests: dict = {}
        self.num_src: str = None
        self.num_dst: str = None
        self.transfers: dict = {}
        self.start_timestamp: float = None
        self.end_timestamp: float = None
        self.active_channels: dict = {}
        self.bridges_by_unique_id: dict = {}
        self.linkedid = linkedid

        self.call_type: CallTypes = CallTypes.UNKNOWN
        self.status: Dialstatuses = Dialstatuses.UNKNOWN

    def set_call_type(self) -> None:
        # TODO: Сделать человеческое определение типа для всех звонков
        self.call_type = CallTypes.ORIGINATE.value

    def build_call_characters(self, last_timestamp) -> dict:
        dials = []
        for unique_id, raw_dials in self.dialings.items():
            full_dial = {'Begin': None, 'End': None}
            for dial in raw_dials:
                # dials search
                if dial.sub_event == DialSubEvents.BEGIN.value:
                    full_dial['Begin'] = dial
                elif dial.sub_event == DialSubEvents.END.value:
                    full_dial['End'] = dial
                    if full_dial['Begin']:
                        timestamp_start = full_dial['Begin'].timestamp
                        timestamp_end = full_dial['End'].timestamp
                        s = {
                            'src': self.channels[unique_id].callerid_num,
                            'dst': self.channels[full_dial['Begin'].dest_unique_id].callerid_num,
                            'duration': int(timestamp_end - timestamp_start),
                            'status': full_dial['End'].dial_status,
                            'start_timestamp': timestamp_start,
                            'end_timestamp': timestamp_end,
                            'bridge_duration': 0,
                            'bridge_start_timestamp': None,
                            'bridge_end_timestamp': None,
                            'hangup_callerid': None
                        }
                    else:
                        timestamp_end = full_dial['End'].timestamp
                        s = {
                            'src': None,
                            'dst': self.channels[unique_id].callerid_num,
                            'duration': 0,
                            'status': full_dial['End'].dial_status,
                            'start_timestamp': timestamp_end,
                            'end_timestamp': timestamp_end,
                            'bridge_duration': 0,
                            'bridge_start_timestamp': None,
                            'bridge_end_timestamp': None,
                            'hangup_callerid': None
                        }

                    # bridges search
                    if full_dial['End'].dial_status == Dialstatuses.ANSWER.value:
                        bridge = self.bridges_by_unique_id.get(unique_id)
                        if bridge:
                            bridge_start_timestamp = bridge['link'].timestamp
                            bridge_end_timestamp = bridge['unlink'].timestamp
                            bridge_duration = 0
                            if bridge_start_timestamp and bridge_end_timestamp:
                                bridge_duration = int(bridge_end_timestamp - bridge_start_timestamp)

                            s.update({
                                'bridge_duration': bridge_duration,
                                'bridge_start_timestamp': bridge_start_timestamp,
                                'bridge_end_timestamp': bridge_end_timestamp,
                            })

                    # search who hangup
                    hangup_request = self.hangup_requests.get(unique_id)
                    if not hangup_request and full_dial.get('Begin'):
                        hangup_request = self.hangup_requests.get(full_dial['Begin'].dest_unique_id)
                    who_hangup = None
                    if hangup_request:
                        for channel in self.channels.values():
                            if all([
                                hangup_request.channel_name == channel.name,
                                channel.channel_type != ChannelTypes.LOCAL.value
                            ]):
                                who_hangup = channel.callerid_num
                                break
                    s.update({'hangup_callerid': who_hangup})
                    full_dial = {'Begin': None, 'End': None}
                    dials.append(s)

        self.start_timestamp = min(self.channels_by_timestamp.keys())
        self.end_timestamp = last_timestamp
        self.call_duration = int(self.end_timestamp - self.start_timestamp)
        if dials:
            self.status = dials[-1]['status']

        return {
            'linkedid': self.linkedid,
            'call_duration': self.call_duration,
            'start_timestamp': self.start_timestamp,
            'end_timestamp': self.end_timestamp,
            'status': self.status,
            'dials': dials
        }

    def handle_channel(self, register: 'Registry', unique_id: str) -> None:
        channel = register.get_channel(unique_id)
        if channel:
            self.channels_by_timestamp[channel.timestamp] = channel
            self.channels[channel.unique_id] = channel
            self.active_channels[channel.unique_id] = channel
            register.remove_channel(channel.unique_id)
            register.remove_channel_by_name(channel.name)
            register.link_channel_to_call(channel, self.linkedid)

    def handle_newchannel(self, event: 'Event') -> None:
        if event.unique_id != self.linkedid:
            for unique_id in [event.unique_id, self.linkedid]:
                self.handle_channel(event.register, unique_id)

    def handle_dial(self, event: 'Event') -> None:
        if event.sub_event == DialSubEvents.BEGIN.value:
            if event.unique_id:
                if self.dialings.get(event.unique_id):
                    self.dialings[event.unique_id].append(event)
                else:
                    self.dialings[event.unique_id] = [event]
            self.handle_channel(event.register, event.unique_id)
            self.handle_channel(event.register, event.dest_unique_id)

        elif event.sub_event == DialSubEvents.END.value:
            if event.unique_id:
                if self.dialings.get(event.unique_id):
                    self.dialings[event.unique_id].append(event)
                else:
                    self.dialings[event.unique_id] = [event]

            self.handle_channel(event.register, event.unique_id)

    def handle_bridge(self, event: 'Event') -> None:
        if event.bridge_state == BridgeStates.LINK.value:
            self.handle_channel(event.register, event.unique_id_1)
            self.handle_channel(event.register, event.unique_id_2)
            channel_1 = self.channels.get(event.unique_id_1)
            channel_2 = self.channels.get(event.unique_id_2)

            if channel_1 and event.callerid_1:
                channel_1.callerid_num = event.callerid_1

            if channel_2 and event.callerid_2:
                channel_2.callerid_num = event.callerid_2
            self.bridges_by_unique_id[event.unique_id_1] = {'link': event}

        elif event.bridge_state == BridgeStates.UNLINK.value:
            self.bridges_by_unique_id[event.unique_id_1].update({'unlink': event})

    def handle_hanguprequest(self, event: 'Event') -> None:
        self.hangup_requests[event.unique_id] = event

    def handle_hangup(self, event: 'Event') -> None:
        self.active_channels.pop(event.unique_id, None)

        if not self.active_channels:
            if event.register.get_call(self.linkedid):
                call_data = self.build_call_characters(event.timestamp)
                logging.info(call_data)

                num_src = self.channels[self.linkedid].callerid_num

                self.add_to_stats_queue(event.register.redis, num_src, call_data)                

                event.register.redis.delete(num_src)

                active_calls = event.register.redis.get(REDIS_ACTIVE_CALLS_KEY)
                active_calls = json.loads(active_calls) if active_calls else {}

                active_calls.pop(num_src, None)
                event.register.redis.set(REDIS_ACTIVE_CALLS_KEY, json.dumps(active_calls))

                event.register.remove_call(self.linkedid)

    def get_event_handler(self, event: 'Event') -> Any:
        if event.event_name == 'Newchannel':
            return self.handle_newchannel
        elif event.event_name == 'Dial':
            return self.handle_dial
        elif event.event_name == 'Bridge':
            return self.handle_bridge
        elif event.event_name == 'HangupRequest':
            return self.handle_hanguprequest
        elif event.event_name == 'Hangup':
            return self.handle_hangup
        
    def add_to_stats_queue(self, redis, num_src, call_data) -> None:
        target_data = redis.get(num_src)
        target_data = json.loads(target_data) if target_data else {}

        ended_calls = redis.get(REDIS_END_CALLS_KEY)
        ended_calls = json.loads(ended_calls) if ended_calls else {}
        ended_calls[num_src] = {
            'prj': target_data['prj'],
            'cnet_url': target_data['url'],
            'data': call_data
        }
        redis.set(REDIS_END_CALLS_KEY, json.dumps(ended_calls))

    @classmethod
    def handle_event(cls, event: 'Event') -> None:
        if event.event_name == 'Bridge':
            unique_ids = [event.unique_id_1, event.unique_id_2]
        else:
            unique_ids = [event.unique_id]

        call = None

        for unique_id in unique_ids:
            if event.register.get_call_by_uniqueid(unique_id):
                call = event.register.get_call_by_uniqueid(unique_id)
                break
        else:
            if Call.accept_call(event):
                linkedid = Call.get_linkedid(event)
                if linkedid:
                    call = cls(linkedid)
                    event.register.add_call(call)
                else:
                    logging.warning(f'Can`t find all channels for building a call - {event.unique_id}')

        if call:
            handler = call.get_event_handler(event)
            if handler:
                handler(event)
            else:
                logging.warning(f'Unknown event {event}')

    @staticmethod
    def accept_call(event: 'Event') -> bool:
        if event.event_name == 'Newchannel':
            channel = event.register.get_channel(event.unique_id)
            first_channel = event.register.get_channel_by_name(event.channel_name[:-2] + ';1')
            if channel and first_channel:
                if channel.channel_type == ChannelTypes.LOCAL.value:
                    channel_name_arr = event.channel_name.split('@')
                    context = channel_name_arr[1].replace('-' + channel_name_arr[1].split('-')[-1], '')
                    num_src = channel_name_arr[0][6:]
                    channel.callerid_num = num_src
                    first_channel.callerid_num = num_src

                    call_is_inited = False

                    try:
                        call_is_inited = bool(event.register.redis.get(str(num_src)))
                    except Exception:
                        logging.warning('Something wrong with redis')

                    # Search second local channel of call
                    if all([
                        event.channel_name[-2:] == ';2',
                        channel.channel_type == ChannelTypes.LOCAL.value,
                        MANAGER_CONTEXT in context,
                        call_is_inited
                    ]):
                        return True
        return False

    @staticmethod
    def get_linkedid(event: 'Event') -> Union[str, None]:
        if event.event_name == 'Newchannel':
            """
            For originates only
            """
            channel = event.register.get_channel(event.unique_id)
            if channel and channel.channel_type == ChannelTypes.LOCAL.value:
                first_channel = event.register.get_channel_by_name(event.channel_name[:-2] + ';1')
                return first_channel.unique_id
        # TODO: Получение линкед ид из Dial ивентов для других типов звонков
