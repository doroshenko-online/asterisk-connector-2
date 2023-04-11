from ami_parser.events.event import Event


class Hangup(Event):
    channel_name = None
    callerid_num = None
    callerid_name = None
    connected_line_num = None
    connected_line_name = None
    cause = None

    def __init__(self, event: dict, redis=None) -> None:
        self.channel_name = event.get('Channel')
        self.callerid_num = event.get('CallerIDNum')
        self.callerid_name = event.get('CallerIDName')
        self.connected_line_num = event.get('ConnectedLineNum')
        self.callerid_name = event.get('ConnectedLineName')
        self.cause = event.get('Cause')

        super().__init__(event, redis)

    def do_action(self, config) -> None:
        self.register.remove_channel(self.unique_id)
        self.register.remove_channel_by_name(self.channel_name)
        return super().do_action(config)
