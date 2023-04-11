import logging
from typing import Union
from ami_parser.handlers.call import Call
from ami_parser.handlers.channel import Channel

from ami_parser.singleton import Singleton


class Registry(metaclass=Singleton):
    calls_by_linkedid = {}
    channels_by_uniqueid = {}
    channel_names_map = {}
    channels_to_calls = {}
    redis = None

    def __init__(self, redis) -> None:
        self.redis = redis

    def add_call(self, call: Call) -> bool:
        if call.linkedid in self.calls_by_linkedid:
            logging.debug(f'Call with linkedid {call.linkedid} already in registry')
            return False
        
        else:
            logging.info(f'New call {call.linkedid} was registered')
            self.calls_by_linkedid[call.linkedid] = call
            return True

    def get_call(self, linkedid: str) -> Union[Call, None]:
        return self.calls_by_linkedid.get(linkedid)

    def get_call_by_uniqueid(self, unique_id: str) -> Union[Call, None]:
        return self.channels_to_calls.get(unique_id)

    def remove_call(self, linkedid: str) -> bool:
        if call := self.calls_by_linkedid.get(linkedid):
            for unique_id in call.channels.keys():
                self.unlink_channel_to_call(unique_id)

            logging.info(f'Call {call.linkedid} was unregistered')
            return bool(self.calls_by_linkedid.pop(linkedid, False))
        else:
            logging.warning(f'Call with linkedid {linkedid} is absent in registry')
            return False

    def add_channel(self, channel: Channel) -> bool:
        if channel.unique_id in self.channels_by_uniqueid:
            logging.debug(f'Channel with uniquid {channel.unique_id} already in registry')
            return False
        
        else:
            logging.debug(f'New channel {channel.unique_id} was created')
            self.channels_by_uniqueid[channel.unique_id] = channel
            return True

    def get_channel(self, unique_id: str) -> Union[Channel, None]:
        return self.channels_by_uniqueid.get(unique_id)

    def remove_channel(self, unique_id: str) -> bool:
        if result := self.channels_by_uniqueid.pop(unique_id, False):
            logging.debug(f'Channel {unique_id} was removed')
            return bool(result)
        else:
            return False

    def add_channel_by_name(self, channel: Channel) -> bool:
        if channel.name in self.channel_names_map:
            return False
        
        else:
            self.channel_names_map[channel.name] = channel
            return True

    def get_channel_by_name(self, channel_name: str) -> Union[Channel, None]:
        return self.channel_names_map.get(channel_name)

    def remove_channel_by_name(self, channel_name: str) -> bool:
        if result := self.channel_names_map.pop(channel_name, False):
            return bool(result)
        else:
            return False

    def link_channel_to_call(self, channel: Channel, linkedid: str) -> bool:
        if linkedid in self.calls_by_linkedid:
            logging.debug(f'Channel {channel.unique_id} joining to call {linkedid}')
            self.channels_to_calls[channel.unique_id] = self.calls_by_linkedid[linkedid]
            return True
        else:
            logging.warning(f'Unable to link channel with call. Call with linkedid {linkedid} not in registry')
            return False

    def unlink_channel_to_call(self, unique_id: str) -> bool:
        return bool(self.channels_to_calls.pop(unique_id, False))

    def clear_register(self) -> None:
        self.calls_by_linkedid = {}
        self.channels_by_uniqueid = {}
        self.channel_names_map = {}
        self.channels_to_calls = {}
