import time
import logging

from ami_parser.handlers.call import Call
from ami_parser.registry import Registry


class Event:
    event_name = None
    timestamp = None
    unique_id = None
    register = None

    def __init__(self, event: dict, redis=None) -> None:
        self.event_name = event.get('Event')
        self.timestamp = float(event.get('Timestamp', time.time()))
        self.unique_id = event.get('Uniqueid')
        self.register = Registry(redis)

        logging.debug(self.__repr__())

    def do_action(self) -> None:
        Call.handle_event(self)

    def __repr__(self) -> str:
        cls_attrs = ['event_name', 'timestamp', 'unique_id']
        for attribute in self.__dict__:
            if attribute not in cls_attrs:
                cls_attrs.append(attribute)

        repr_str = ""
        for attribute in cls_attrs:
            if attribute != 'register':
                repr_str += f"{attribute}: {self.__getattribute__(attribute)} | "
        
        return repr_str

    def __str__(self) -> str:
        return f"{self.event_name} - {self.unique_id}"
