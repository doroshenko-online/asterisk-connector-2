import logging
import sys

from os import environ as env

from multiprocessing import Process

import redis

from ami_parser.ami_parser import start
from call_maker.app import send_stats, start_app

REDIS_URL = env['REDIS_URL']
APP_PORT = int(env.get('APP_PORT') or 5000)
AMI_HOST = env['AMI_HOST']
AMI_PORT = int(env.get('AMI_PORT') or 5038)
AMI_USER = env['AMI_USER']
AMI_SECRET = env['AMI_SECRET']
AGGR_STATS = bool(int(env.get('AGGR_STATS') or 0))


if __name__ == '__main__':
    LOG_FORMAT = '[%(asctime)s][%(levelname)s]: %(message)s'
    logging.basicConfig(format=LOG_FORMAT, datefmt='%d-%m-%y %H:%M:%S', level=logging.DEBUG)

    procs = []

    redis = redis.from_url(REDIS_URL)

    try:
        redis.client()
    except Exception:
        logging.error('Can`t connect to redis')
        sys.exit(-2)
    else:
        logging.info('Successfully connected to redis')

    if AGGR_STATS:
        parser = Process(target=start, args=(AMI_HOST, AMI_PORT, AMI_USER, AMI_SECRET, redis,))
        procs.append(parser)

        stat_sender = Process(target=send_stats, args=(redis,))
        procs.append(stat_sender)

    call_maker = Process(target=start_app, args=(AMI_HOST, AMI_PORT, AMI_USER, AMI_SECRET, redis, APP_PORT, AGGR_STATS))
    procs.append(call_maker)

    for proc in procs:
        proc.start()
