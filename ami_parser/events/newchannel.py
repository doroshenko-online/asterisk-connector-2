from ami_parser.events.event import Event
from ami_parser.handlers.call import Call
from ami_parser.handlers.channel import Channel


class Newchannel(Event):
    channel_name = None
    callerid_num = None
    callerid_name = None
    channel_state = None
    exten = None
    context = None

    def __init__(self, event: dict, redis=None) -> None:
        self.channel_name = event.get('Channel')
        self.callerid_num = event['CallerIDNum'] if event.get('CallerIDNum') else None
        self.callerid_name = event['CallerIDName'] if event.get('CallerIDName') else None
        self.channel_state = event.get('ChannelStateDesc')
        self.exten = event.get('Exten')
        self.context = event.get('Context')
        super().__init__(event, redis)

    def do_action(self, config) -> None:
        channel = Channel(self)
        self.register.add_channel(channel)
        self.register.add_channel_by_name(channel)

        return super().do_action(config)
