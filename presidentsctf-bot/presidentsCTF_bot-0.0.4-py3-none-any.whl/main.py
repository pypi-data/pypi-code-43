#!/usr/bin/env python3

import argparse
import datetime
import glob
import json
import logging
import os

from presidentsCTF import api, config, db, notify, display

def compute_team_change(prev, cur, team_id, time):
    change = {"solves":0, "points":0, "rank":0, "new": False}
    solve = None

    # new team, nothing to compare against
    if prev is None:
        num_chals = cur["solves"]
        points = cur["score"]
        rank = 0
        change = {"solves":num_chals, "points":points, "rank":rank, "new": True}
        solve = (team_id, points, num_chals, time)
        return change, solve

    # check solves
    num_chals = cur["solves"] - prev["solves"]
    change["solves"] = num_chals
    if num_chals > 0:
        # may be more than one challenge
        points = cur["score"] - prev["score"]
        change["points"] = points
        solve = (team_id, points, num_chals, time)
        if num_chals > 1:
            logging.debug("more than one solve in this update: {}".format(solve))


    # check rank
    rank_change = prev["rank"] - cur["rank"]
    change["rank"] = rank_change
    return change, solve


def update_from_json(data):
    # check validity: data has the fields we need
    if not all([f in data for f in ["boardId", "timestamp", "results"]]):
        logging.error("missing fields in data: {}".format(data))
        return None

    # ensure actually got results
    if len(data["results"]) == 0:
        logging.debug("empty results, either the event has not started or the server is down")
        return None

    event_id = data["boardId"]

    # get previous team state to allow computation of changes
    prev_teams = {t["team_id"]:t for t in db.all_teams_by_id(event_id)}

    # extract team info from json and format into db rows
    cur_teams = []
    for team in data["results"]:
        team_id = team["teamId"]
        fields = ["teamName", "rank","score", "problemCount", "start"]
        name, rank, score, solves, start = [team[f] for f in fields]
        t = (team_id, name, rank, score, solves, start, event_id)
        cur_teams.append(t)

    # store current teams
    db.store_all_teams(cur_teams)

    # compute changes in this update
    # use the time from the api as the "updated as of" timestamp
    time  = api.parse_time(data["timestamp"])
    changes = {}
    solves = []
    for current in db.all_teams_by_id(event_id):
        team_id = current["team_id"]
        previous = prev_teams[team_id] if team_id in prev_teams else None
        change, solve = compute_team_change(previous, current, team_id, time)
        if solve is not None:
            changes[team_id] = change
            solves.append(solve)

    # store solves to database
    db.store_all_solves(solves)

    logging.debug("number of changes in update: {}".format(len(changes)))
    return changes


def validate_events(fetch):
    """Ensures that events exist in the database and that we are able to contact
    the API endpoint"""
    for e in config.config['events']:
        event_id = e["event_id"]
        db.store_event(event_id, e["name"], e["url"], e["take"])
        event = db.event_by_id(event_id)
        if fetch:
            data = api.fetch_event(event)
            if "results" in data:
                logging.debug("Validation: API fetch succeeded for {}".format(e["name"]))
            else:
                logging.error("Validation: API fetch failed, check event configuration for {} ".format(e["name"]))
                return False
    return True

def event_slug(event):
    """provide a short form of the event id"""
    return event["event_id"][:6]

def export_results(data, event, time):
    """store the json response data as a local file"""
    fname = "export_{}_{}.json".format(event_slug(event),time.strftime("%Y-%m-%d_%H%M.%S"))
    with open(fname,'w') as outf:
        outf.write(json.dumps(data))
    print("Exported {} to {}".format(event["name"], fname))

def load_results(fname):
    """load json response data from local file (as created with export_results"""
    with open(fname,'rb') as inf:
        return json.loads(inf.read())

def local_update(event, directory):
    """Loading from a local directory of json exports. Relies on sortable
    naming scheme for temporal order.
    """

    export_slug = "export_{}_*.json".format(event_slug(event))
    exports = glob.glob(os.path.join(directory, export_slug))
    exports.sort()
    logging.debug("Updating: {} : from {} with {} files".format(event["name"], directory, len(exports)))
    changes = []
    for export_name in exports:
        data = load_results(export_name)
        change = update_from_json(data)
        if change is not None and len(change) > 0:
            logging.debug("loaded with changes: {}".format(export_name))
            changes.append(change)

    return changes


def remote_update(event, export):
    changes = None
    event_id = event["event_id"]
    logging.debug("Updating: {} : {}".format(event["name"], event_id))

    # fetch json from api
    data = api.fetch_event(event)

    # process json from api
    if "boardId" in data and data["boardId"] == event_id:
        if export:
            # store as local time since data contains the event timestamp
            local_time = datetime.datetime.now()
            export_results(data, event, local_time)

        # store results and compute changes
        res = update_from_json(data)
        return [res] if res is not None else []

    logging.error("Invalid remote update json. Missing or incorrect boardId")
    return None


def process(args):
    # filter events to match request
    events = db.all_events()
    if args.event is not None:
        events = [e for e in events if args.event in e["event_id"]]

    for e in events:
        if args.local is None:
            event_changes = remote_update(e, args.export)
        else:
            event_changes = local_update(e, args.local)

        e_id = e["event_id"]
        if not args.quiet:
            display.scoreboard(e_id, args.active, args.known, args.top)
        if event_changes is not None:
            # may have more than one change set if loading from local json
            for change in event_changes:
                display.summarize_changes(change, args.slack, args.twitter)


def main():

    # setup arguments
    parser = argparse.ArgumentParser(description="President's CTF Score Bot")
    parser.add_argument('--debug', help='verbose logging', action='store_true',
            default=False)
    parser.add_argument('--quiet', help='no scoreboard', action='store_true',
            default=False)
    parser.add_argument('--config', help='config file to load from')
    parser.add_argument('--event', help='single event id to update (prefix allowed)')
    parser.add_argument('--local', help='load json files from dir (test/dev)')
    parser.add_argument('--export', help='export raw json response', action='store_true', default=False)

    view_opts = parser.add_argument_group('View Options', 'Choose which teams are shown on the scoreboard.')
    view_opts.add_argument('--active', help='show active teams (default=True)', action='store_true', default=True)
    view_opts.add_argument('--known', help='show known teams (default=False)',  action='store_true', default=False)
    view_opts.add_argument('--top', help='show top N teams', type=int, default=0)


    notify_opts = parser.add_argument_group('Notification Options', 'Choose destinations to post updates to.')
    notify_opts.add_argument('--slack', help='post updates to slack', action='store_true', default=False)
    notify_opts.add_argument('--twitter', help='post updates to twitter', action='store_true', default=False)
    args = parser.parse_args()

    # setup logging
    logging.basicConfig(level=logging.WARN,format='%(asctime)s %(levelname)-6s %(message)s')
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # load configuration
    if args.config:
        config.load_config(args.config)
    else:
        config.load_config()

    # load db
    db_path = config.config["db"]
    db.load(db_path)

    # validate events in configuration
    if not validate_events(args.local is None):
        logging.error("validating events in configuration")
        exit(1)

    process(args)

if __name__ == '__main__':
    main()
