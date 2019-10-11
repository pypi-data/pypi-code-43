from __future__ import print_function

import argparse
import logging
import time
import sys

import json
import cas_simulation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--credentials",
                        help="Location of credentials.json", default="credentials.json")
    parser.add_argument("-s", "--url", required=True,
                        help="The entry point URL, like https://csusb.blackboard.com/")
    parser.add_argument("-e", "--expression", required=True,
                        help="A pattern that should the body of the page upon successful authentication")
    parser.add_argument("-w", "--warn-after", type=float,
                        help="Warn if logon exceeds this time (seconds)", default=5.0)
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("--post-auth-check", nargs=2, metavar=('URL', 'EXPRESSION'),
                        help="Additional post-authentication check")
    parser.add_argument("-f", "--form-id",
                        help="Stop the simulation when a form with this id or action is encountered")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(process)d:%(lineno)d]%(levelname)s: %(message)s', filename='/var/log/nagios/cassp-debug.log')
    else:
        logging.basicConfig(level=logging.WARNING)

    try:
        with open(args.credentials) as f:
            credentials = json.load(f)
    except IOError as e:
        logging.error("Unable to read '%s'. Create credentials.json or specify --credentials path/to/credentials.json", args.credentials)
        raise e

    try:
        duration = time.time()
        post_auth_checks = []
        if args.post_auth_check:
            post_auth_checks.append({'url': args.post_auth_check[0],
                                    'pattern': args.post_auth_check[1]})
        simulation = cas_simulation.cas_simulation(args.url,credentials['username'],credentials['password'],args.expression,post_auth_checks=post_auth_checks,skip_form_id=args.form_id)
        success = simulation.run()
        duration = time.time() - duration # wallclock diff as floating point
    except Exception as e:
        print("CRITICAL %s" % e)
        try:
            print("Last URL: %s" % e.geturl())
        except AttributeError:
            pass
        try:
            print("Reason: %s" % e.reason)
        except AttributeError:
            pass
        try:
            e.seek(0)
            print("Page Excerpt: %s" % e.read(1024*4))
        except:
            print("Page Excerpt: (n/a)")
            sys.exit(2)

    if not success:
        print("CRITICAL %s failed" % args.url)
        try:
            print("Last URL: %s" % e.geturl())
        except AttributeError:
            pass
        sys.exit(2)

    if duration > args.warn_after:
        print("WARN CAS login for %s took %0.2fs" % (args.url,duration))
        sys.exit(1)

    print("OK CAS login %s authenticated as %s - took %0.2fs" % (args.url, secrets_cas.username, duration))
    sys.exit(0)
