from ami_parser.events.event import Event


class Bridge(Event):
    bridge_state = None
    unique_id_1 = None
    unique_id_2 = None
    callerid_1 = None
    callerid_2 = None

    def __init__(self, event: dict, redis=None) -> None:
        self.bridge_state = event.get('Bridgestate')
        self.unique_id_1 = event.get('Uniqueid1')
        self.unique_id_2 = event.get('Uniqueid2')
        self.callerid_1 = event.get('CallerID1')
        self.callerid_2 = event.get('CallerID2')
        super().__init__(event, redis)
