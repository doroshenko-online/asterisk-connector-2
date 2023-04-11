CNET_URLS = {
    'csx': 'https://cnet.apicsx.com/cnet/gate/',
    'joy': 'https://cnet.joy-api.com/cnet/gate/',
    'goldenreels': 'https://cnet.v918cdn.com/cnet/gate',
    'cnqmga': 'https://cnet-mga.appricotta.com/cnet/gate/'
}

REDIS_ACTIVE_CALLS_KEY = 'active_calls'  # dict of active calls
REDIS_END_CALLS_KEY = 'end_calls'  # need only for send stats

MANAGER_CONTEXT = 'from-internal'
CLIENT_CONTEXT = 'from-internal'
