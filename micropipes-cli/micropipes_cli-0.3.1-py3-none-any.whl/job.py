import logging
import json
import sys
import argparse
from cliff.lister import Lister
from cliff.show import ShowOne
from mpipes.common import str2bool, AuthenticatedConn, format_response_list


class JobList(Lister):
    'List jobs'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobList, self).get_parser(prog_name)
        # parser.add_argument("--attr", type=str, help='Attributes to show', default='*')
        parser.add_argument("--offset", type=int, help='List from', default=0)
        parser.add_argument("--count", type=int, help='Limit results', default=-1)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        fileds = {
            'count': parsed_args.count,
            'offset': parsed_args.offset
        }
        resp = con.get_request('/api/micropipes/jobs/', fields=fileds)
        if resp.status != 200:
            print("{} - {}".format(resp.status, resp.reason))
            return None
        # return format_response_list(resp, parsed_args.attr)
        return format_response_list(resp)


class JobAdd(Lister):
    'Add job'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobAdd, self).get_parser(prog_name)
        parser.add_argument('infile', nargs='+', type=argparse.FileType('r'))
        return parser

    def take_action(self, parsed_args):
        columns = (
            '_status', '_error', '_id'
        )
        con = AuthenticatedConn()
        rt_data = []
        for f in parsed_args.infile:
            job_json = json.load(f)
            resp = con.post_request('/api/micropipes/jobs/', json.dumps(job_json))
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 201:
                rdata = (
                    dt['_status'],
                    dt['_error'],
                    None
                )
            else:
                rdata = (
                    dt['_status'],
                    None,
                    dt['_id']
                )
            rt_data.append(rdata)
        return (columns, rt_data)

class JobEdit(Lister):
    'Change existing job (keeps id, stats, logs ...)'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobEdit, self).get_parser(prog_name)
        parser.add_argument("--job_id", type=str, help='Id of job to change', required=True)
        parser.add_argument('infile', type=argparse.FileType('r'))
        return parser

    def take_action(self, parsed_args):
        columns = (
            '_status', '_error', '_id'
        )
        con = AuthenticatedConn()
        rt_data = []
        job_json = json.load(parsed_args.infile)
        resp = con.put_request('/api/micropipes/jobs/{}'.format(parsed_args.job_id), json.dumps(job_json))
        dt = json.loads(resp.data.decode())
        rdata = ()
        if resp.status != 200:
            rdata = (
                dt['_status'],
                dt['_error'],
                None
            )
        else:
            rdata = (
                dt['_status'],
                None,
                dt['_id']
            )
        rt_data.append(rdata)
        return (columns, rt_data)

class JobStop(Lister):
    'Stop job'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobStop, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--job_ids', type=str, help='comma separated job id(s)')
        group.add_argument('--job_ids_file',  type=argparse.FileType('r'), help='file containing id(s) on new lines, as product of "job list -c=id -f values"')
        return parser

    def take_action(self, parsed_args):
        columns = (
            '_status', '_error', '_id'
        )
        con = AuthenticatedConn()
        if parsed_args.job_ids:
            ids = parsed_args.job_ids.split(",")
        if parsed_args.job_ids_file:
            ids = parsed_args.job_ids_file.readlines()
            ids = [line.strip() for line in ids]

        rt_data = []
        for job_id in ids:
            resp = con.post_request('/api/micropipes/jobs/{}/stop'.format(job_id), None)
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 200:
                rdata = (
                    dt['_status'],
                    dt['_error'],
                    None
                )
            else:
                rdata = (
                    dt['_status'],
                    None,
                    dt['_id']
                )
            rt_data.append(rdata)
        return (columns, rt_data)

class JobStart(Lister):
    'Start job'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobStart, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--job_ids', type=str, help='comma separated job id(s)')
        group.add_argument('--job_ids_file',  type=argparse.FileType('r'), help='file containing id(s) on new lines, as product of "job list -c=id -f values"')
        return parser

    def take_action(self, parsed_args):
        columns = (
            '_status', '_error', '_id'
        )
        con = AuthenticatedConn()
        if parsed_args.job_ids:
            ids = parsed_args.job_ids.split(",")
        if parsed_args.job_ids_file:
            ids = parsed_args.job_ids_file.readlines()
            ids = [line.strip() for line in ids]
        rt_data = []
        for job_id in ids:
            resp = con.post_request('/api/micropipes/jobs/{}/start'.format(job_id), None)
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 200:
                rdata = (
                    dt['_status'],
                    dt['_error'],
                    None
                )
            else:
                rdata = (
                    dt['_status'],
                    None,
                    dt['_id']
                )
            rt_data.append(rdata)
        return (columns, rt_data)

class JobDelete(Lister):
    'Delete job'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobDelete, self).get_parser(prog_name)
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--job_ids', type=str, help='comma separated job id(s)')
        group.add_argument('--job_ids_file',  type=argparse.FileType('r'), help='file containing id(s) on new lines, as product of "job list -c=id -f values"')
        return parser

    def take_action(self, parsed_args):
        columns = (
            '_status', '_error', '_id'
        )
        con = AuthenticatedConn()
        if parsed_args.job_ids:
            ids = parsed_args.job_ids.split(",")
        if parsed_args.job_ids_file:
            ids = parsed_args.job_ids_file.readlines()
            ids = [line.strip() for line in ids]
        rt_data = []
        for job_id in ids:
            resp = con.delete_request('/api/micropipes/jobs/{}'.format(job_id))
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 200:
                rdata = (
                    dt['_status'],
                    dt['_error'],
                    None
                )
            else:
                rdata = (
                    dt['_status'],
                    None,
                    dt['_id']
                )
            rt_data.append(rdata)
        return (columns, rt_data)