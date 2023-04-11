from ami_parser.events import bridge, dial, event, hangup, hanguprequest, newchannel, softhanguprequest


class EventFabric:

    @staticmethod
    def get_event(event_dict, redis=None) -> event.Event:
        event_name = event_dict.get('Event')

        if event_name == 'Newchannel':
            return newchannel.Newchannel(event_dict, redis)
        elif event_name == 'Dial':
            return dial.Dial(event_dict, redis)
        elif event_name == 'Bridge':
            return bridge.Bridge(event_dict, redis)
        elif event_name == 'HangupRequest':
            return hanguprequest.HangupRequest(event_dict, redis)
        elif event_name == 'Hangup':
            return hangup.Hangup(event_dict, redis)
