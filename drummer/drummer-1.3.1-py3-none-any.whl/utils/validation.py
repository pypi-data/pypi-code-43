# -*- coding: utf-8 -*-
from croniter import croniter

def check_cron(_, candidate):
    """Validates cron expression."""

    return croniter.is_valid(candidate)

def check_int(_, candidate):
    """Checks whether candidate is <int>."""
    try:
        int(candidate)
        return True

    except:
        return False

def get_dict_from_args(args):
    """Extracts a dict from task argument string."""

    d = {}
    if args:
        for k,v in [p.strip().split('=') for p in args.split(',')]:
            d[k] = v

    return d
