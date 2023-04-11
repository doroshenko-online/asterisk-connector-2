from ami_parser.events.event import Event


class HangupRequest(Event):
    channel_name = None

    def __init__(self, event: dict, redis=None) -> None:
        self.channel_name = event.get('Channel')
        super().__init__(event, redis)