import argparse
from logging import basicConfig
import asyncio

from ..client import BeeminderClient


def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--username', metavar='USERNAME', required=True)
    parser.add_argument('--token', metavar='TOKEN', required=True)
    parser.add_argument('--goal', metavar='GOAL')
    parser.add_argument('--datapoint', metavar='DATAPOINT')
    parser.add_argument('--comment', metavar='COMMENT')
    args = parser.parse_args()
    return args


async def run(args):
    beeminder = BeeminderClient(args.username, args.token)
    req_id = str(hash(args.comment))
    if args.datapoint:
        await beeminder.create_datapoint(args.goal, args.datapoint, comment=args.comment, requestid=req_id)
    await beeminder.close()


def main():
    basicConfig()
    args = get_args()
    asyncio.get_event_loop().run_until_complete(run(args))
