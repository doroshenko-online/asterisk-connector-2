from enum import Enum


class Dialstatuses(Enum):
    UNKNOWN = 'UNKNOWN'
    CANCEL = 'CANCEL'
    ANSWER = 'ANSWER'
    NOANSWER = 'NOANSWER'
    BUSY = 'BUSY'
    CONGESTION = 'CONGESTION'
    CHANUNAVAIL = 'CHANUNAVAIL'


class DialSubEvents(Enum):
    BEGIN = 'Begin'
    END = 'End'


class BridgeStates(Enum):
    LINK = 'Link'
    UNLINK = 'Unlink'


class ChannelStates(Enum):
    DOWN = 'Down'
    RESERVED = 'Rsrvd'
    OFFHOOK = 'OffHook'
    DIALING = 'Dialing'
    RING = 'Ring'
    RINGING = 'Ringing'
    UP = 'Up'
    BUSY = 'BUSY'
    DIALING_OFFHOOK = 'Dialing Offhook'
    PRE_RING = 'Pre-ring'
    UNKNOWN = 'Unknown'


class ChannelTypes(Enum):
    LOCAL = 'Local'
    SIP = 'SIP'
    PJSIP = 'PJSIP'


class CallTypes(Enum):
    UNKNOWN = 'Unknown'
    INNER = 'Inner'
    INBOUND = 'Inbound'
    OUTBOUND = 'Outbound'
    ORIGINATE = 'Originate'
    CONFERENCE = 'Conference'
    CALLBACK = 'Callback'  # Inbound + Originate
