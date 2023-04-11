import json

from call_maker.constants import REDIS_ACTIVE_CALLS_KEY


def clear_active_calls(redis):
    old_active_calls = redis.get(REDIS_ACTIVE_CALLS_KEY)
    old_active_calls = json.loads(old_active_calls) if old_active_calls else {}
    if old_active_calls:
        for num_src in old_active_calls.keys():
            redis.delete(num_src)

    redis.set(REDIS_ACTIVE_CALLS_KEY, json.dumps({}))
