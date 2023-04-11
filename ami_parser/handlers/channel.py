import logging
from multiprocessing import context
from typing import Union

from ami_parser.enums import ChannelStates, ChannelTypes


class Channel:

    unique_id = None
    _callerid_num = None
    _callerid_name = None
    name = None
    state = ChannelStates.DOWN.value
    channel_type = None
    timestamp = None

    def __init__(self, event: 'Newchannel') -> None:
        self.unique_id = event.unique_id
        self._callerid_num = event.callerid_num
        self._callerid_name = event.callerid_name
        self.name = event.channel_name
        self.state = event.channel_state
        self.timestamp = event.timestamp

        if ChannelTypes.LOCAL.value in self.name:
            self.channel_type = ChannelTypes.LOCAL.value
        elif ChannelTypes.SIP.value in self.name:
            self.channel_type = ChannelTypes.SIP.value
        elif ChannelTypes.PJSIP.value in self.name:
            self.channel_type = ChannelTypes.PJSIP.value

    @property
    def callerid_num(self) -> str:
        return self._callerid_num


    @callerid_num.setter
    def callerid_num(self, callerid_num: str) -> None:
        logging.info(f'Set callerid_num {callerid_num} for channel {self.unique_id}')
        self._callerid_num = callerid_num

    @property
    def callerid_name(self) -> Union[str, None]:
        return self._callerid_name

    @callerid_name.setter
    def callerid_name(self, callerid_name: str) -> None:
        logging.info(f'Set callerid_name {callerid_name} for channel {self.unique_id}')
        self._callerid_name = callerid_name

    def __str__(self) -> str:
        return f'Name: {self.callerid_name} | Num: {self.callerid_num} | Name: {self.name}'
