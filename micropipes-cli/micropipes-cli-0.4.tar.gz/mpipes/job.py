import logging
import json
import sys
import argparse
from cliff.lister import Lister
from cliff.show import ShowOne
from mpipes.common import *


class JobList(Lister):
    'List jobs'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobList, self).get_parser(prog_name)
        # parser.add_argument("--attr", type=str, help='Attributes to show', default='*')
        parser.add_argument("--offset", type=int, help='List from', default=0)
        parser.add_argument("--count", type=int, help='Limit results', default=-1)
        return parser

    def list_paged(self, con, offset = 0, count = -1,  page_size = 10):
        rt_items = []
        if count != -1 and page_size > count:
            page_size = count

        while True:
            fileds = {
                'count': page_size,
                'offset': offset
            }
            resp = con.get_request('/api/micropipes/jobs/', fields=fileds)
            if resp.status != 200:
                format_err_response(resp)
                return None
            data = json.loads(resp.data.decode())
            items = data['_items']
            if len(items) == 0:
                return rt_items
            rt_items.extend(items)
            offset += len(items)
            if count != -1 and len(rt_items) + page_size > count:
                page_size = count - len(rt_items)
                if page_size == 0:
                    return rt_items


    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        rt_items = self.list_paged(con, parsed_args.offset, parsed_args.count)
        if not rt_items:
            return None
        return format_response_items(rt_items)

class JobListShort(JobList):
    'List jobs - just this atributes (id, status, created, autostart, priority)'
    def get_parser(self, prog_name):
        return super(JobListShort, self).get_parser(prog_name)

    def take_action(self, parsed_args):
        parsed_args.columns = ['id', 'status', 'created', 'autostart', 'priority']
        return super(JobListShort,self).take_action(parsed_args)

class JobGet(ShowOne):
    'Get one job - to save it for later use  -f json > out.json'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(JobGet, self).get_parser(prog_name)
        parser.add_argument('job_id', type=str, help='Id of job to get', nargs=1)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        resp = con.get_request('/api/micropipes/jobs/{}'.format(parsed_args.job_id[0]))
        if resp.status != 200:
            format_err_response(resp)
            return None
        # return format_response_list(resp, parsed_args.attr)
        return format_response_one(resp)


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