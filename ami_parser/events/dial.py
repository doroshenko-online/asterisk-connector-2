from ami_parser.events.event import Event


class Dial(Event):
    channel_name = None
    callerid_num = None
    callerid_name = None
    dial_string = None
    destination = None
    sub_event = None
    dest_unique_id = None
    dial_status = None

    def __init__(self, event: dict, redis=None) -> None:
        self.channel_name = event.get('Channel')
        self.sub_event = event.get('SubEvent')
        self.dest_unique_id = event.get('DestUniqueID')
        self.dial_status = event.get('DialStatus')
        self.callerid_num = event.get('CallerIDNum')
        self.callerid_name = event.get('CallerIDName')
        self.dial_string = event.get('Dialstring')
        self.destination = event.get('Destination')
        
        super().__init__(event, redis)
        self.unique_id = event.get('UniqueID')
