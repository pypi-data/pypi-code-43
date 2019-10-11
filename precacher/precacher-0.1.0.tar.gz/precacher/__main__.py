#!/usr/bin/python
# coding=utf-8
"""
Replays the top N queries from a Pi-hole or dnscrypt-proxy TSV log
file against a specific nameserver.
"""

__author__ = 'dcoker'

import argparse
import collections
import concurrent.futures
import logging
import multiprocessing
import re

import dns.resolver

LOG_FORMAT_DNSCRYPT_PROXY_TSV = 'dnscrypt-proxy-tsv'
LOG_FORMAT_PIHOLE_DNSMASQ = 'pihole-dnsmasq'
LOG_FORMAT_CHOICES = {LOG_FORMAT_DNSCRYPT_PROXY_TSV,
                      LOG_FORMAT_PIHOLE_DNSMASQ}

LOG_FORMAT = '%(levelname)s:%(asctime)s %(message)s'
ALLOWED_TYPES = {'A', 'AAAA'}
Query = collections.namedtuple('Query', ['type', 'query'])


def parse_args(args):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--verbose",
                        action="store_true",
                        help="Verbose mode.")
    parser.add_argument("--file",
                        type=argparse.FileType('r'),
                        required=True,
                        help="Full path to DNS log.")
    parser.add_argument("--format",
                        default=LOG_FORMAT_PIHOLE_DNSMASQ,
                        choices=LOG_FORMAT_CHOICES,
                        help="Format of log file.")
    parser.add_argument("--servers",
                        default="192.168.1.1",
                        help="Comma-delimited list of DNS server IP "
                             "addresses.")
    parser.add_argument("--top",
                        default=1000,
                        type=int,
                        help="The number of common queries to replay.")
    parser.add_argument("--max_workers",
                        default=multiprocessing.cpu_count() * 2,
                        type=int,
                        help="Max parallelism for sending blocking DNS "
                             "queries.")
    args = parser.parse_args(args)
    return args


def main(args=None):
    args = parse_args(args)
    configure_logging(args)

    resolver = configure_resolver(args)
    queries = summarize_queries(args)
    resolve_top(resolver, args.max_workers, queries.most_common(args.top))


def configure_logging(args):
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def configure_resolver(args):
    nameservers = [server.strip() for server in args.servers.split(",")]
    logging.info("Replaying queries to: %r", nameservers)
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = nameservers
    return resolver


def summarize_queries(args):
    parser = {
        LOG_FORMAT_PIHOLE_DNSMASQ: parse_pihole_dnsmasq,
        LOG_FORMAT_DNSCRYPT_PROXY_TSV: parse_dnscrypt_proxy_tsv
    }[args.format]

    query_count = 0
    queries = collections.Counter()

    for line in args.file.readlines():
        parsed = parser(line)
        if not parsed:
            continue
        query_count += 1
        if parsed.type in ALLOWED_TYPES:
            queries.update({parsed})

    logging.info("Found %d total queries with %d unique lookups.",
                 query_count, len(queries))
    return queries


def parse_dnscrypt_proxy_tsv(line):
    line = line.strip().split("\t")
    return Query(line[3], line[2])


def parse_pihole_dnsmasq(line):
    match = re.match(
        r'^.+dnsmasq\[\d+\]: query\[(?P<type>[A-Z]+)\] (?P<query>[\S]+)',
        line
    )
    if not match:
        return None
    groups = match.groupdict()
    return Query(groups['type'], groups['query'])


def resolve_top(resolver, max_workers, queries):
    logging.debug("Using %d threads.", max_workers)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) \
            as executor:
        for query, _ in queries:
            executor.submit(resolve, query, resolver)


def resolve(query, resolver):
    try:
        answer = resolver.query(query.query, query.type,
                                raise_on_no_answer=False)
        if answer.rrset:
            logging.debug("%s => %s", query, answer.rrset)
        else:
            logging.debug("%s => none", query)
    except dns.rdatatype.UnknownRdatatype:
        logging.debug("%s => bad type", query)
    except dns.resolver.NXDOMAIN:
        logging.debug("%s => NXDOMAIN", query)
