import logging
from cliff.lister import Lister
from cliff.command import Command
from mpipes.common import *
import argparse
import os
import mimetypes


class FilesList(Lister):
    'List all job runtime files'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FilesList, self).get_parser(prog_name)
        parser.add_argument('--dur', choices=['h','d','w','m','p'],
                            help='Lifetime duration (h - hour,d - day,w -week,m -month,p - permanent)', required=True)
        parser.add_argument("--path", type=str,
                            help='Server path of runtime files (must start with / and end with /)', default='/')
        parser.add_argument("--start", type=int, help='Start from, 0 - beginning, minus allowed - python slice notation', default=0)
        parser.add_argument("--end", type=int, help='End, -1 last one, minus allowed - python slice notation', default=-1)
        parser.add_argument('job_id', type=str, help='Id of job to get', nargs=1)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        fileds = {
            'start': parsed_args.start,
            'end': parsed_args.end
        }
        resp = con.get_request('/api/micropipes/jobs/{}/runtime/files/{}{}'.format(parsed_args.job_id[0],
                                                                                  parsed_args.dur,parsed_args.path),
                                fields=fileds)
        if resp.status != 200:
            format_err_response(resp)
            return None
        return format_response_list(resp)


class FileAdd(Lister):
    'Add job runtime file - file must not exist on server'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileAdd, self).get_parser(prog_name)
        parser.add_argument('--dur', choices=['h','d','w','m','p'],
                            help='Lifetime duration (h - hour,d - day,w -week,m -month,p - permanent)', required=True)
        parser.add_argument("--path", type=str,
                            help='Server path of runtime files (must start with / and end with /)', default='/')
        parser.add_argument('--job_id', type=str, help='Id of job to add file(s)', required=True)
        parser.add_argument('infile', nargs='+', type=argparse.FileType('rb'))
        return parser

    def take_action(self, parsed_args):
        mime = mimetypes.MimeTypes()
        columns = (
            '_status', '_error'
        )
        con = AuthenticatedConn()
        rt_data = []
        for f in parsed_args.infile:
            basename = os.path.basename(f.name)
            binary_data = f.read()
            mime_type = mime.guess_type(basename)[0]
            if not mime_type:
                mime_type = 'application/octet-stream'
            headers = {'content-type': mime_type}
            resp = con.post_request(
                '/api/micropipes/jobs/{}/runtime/files/{}{}{}'.format(parsed_args.job_id,
                                                parsed_args.dur,parsed_args.path, basename),
                                            headerz=headers,
                                            payload=binary_data
                                    )
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 201:
                rdata = (
                    dt['_status'],
                    dt['_error']
                )
            else:
                rdata = (
                    dt['_status'],
                    None
                )
            rt_data.append(rdata)
        return (columns, rt_data)

class FileDelete(Lister):
    'Delete job runtime file'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileDelete, self).get_parser(prog_name)
        parser.add_argument('--dur', choices=['h','d','w','m','p'],
                            help='Lifetime duration (h - hour,d - day,w -week,m -month,p - permanent)', required=True)
        parser.add_argument("--path", type=str,
                            help='Server path of runtime files (must start with / and end with /)', default='/')
        parser.add_argument('--job_id', type=str, help='Id of job to add file(s)', required=True)
        parser.add_argument('file', nargs='+', type=str)
        return parser

    def take_action(self, parsed_args):
        mime = mimetypes.MimeTypes()
        columns = (
            '_status', '_error'
        )
        con = AuthenticatedConn()
        rt_data = []
        for f in parsed_args.file:
            resp = con.delete_request(
                '/api/micropipes/jobs/{}/runtime/files/{}{}{}'.format(parsed_args.job_id,
                                                parsed_args.dur,parsed_args.path, f)
                                    )
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 200:
                rdata = (
                    dt['_status'],
                    dt['_error']
                )
            else:
                rdata = (
                    dt['_status'],
                    None
                )
            rt_data.append(rdata)
        return (columns, rt_data)


class FileChange(Lister):
    'Change job runtime file - file must exists on server with same name'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileChange, self).get_parser(prog_name)
        parser.add_argument('--dur', choices=['h','d','w','m','p'],
                            help='Lifetime duration (h - hour,d - day,w -week,m -month,p - permanent)', required=True)
        parser.add_argument("--path", type=str,
                            help='Server path of runtime files (must start with / and end with /)', default='/')
        parser.add_argument('--job_id', type=str, help='Id of job to add file(s)', required=True)
        parser.add_argument('infile', nargs='+', type=argparse.FileType('rb'))
        return parser

    def take_action(self, parsed_args):
        mime = mimetypes.MimeTypes()
        columns = (
            '_status', '_error'
        )
        con = AuthenticatedConn()
        rt_data = []
        for f in parsed_args.infile:
            basename = os.path.basename(f.name)
            binary_data = f.read()
            mime_type = mime.guess_type(basename)[0]
            if not mime_type:
                mime_type = 'application/octet-stream'
            headers = {'content-type': mime_type}
            resp = con.put_request(
                '/api/micropipes/jobs/{}/runtime/files/{}{}{}'.format(parsed_args.job_id,
                                                parsed_args.dur,parsed_args.path, basename),
                                            headerz=headers,
                                            payload=binary_data
                                    )
            dt = json.loads(resp.data.decode())
            rdata = ()
            if resp.status != 200:
                rdata = (
                    dt['_status'],
                    dt['_error']
                )
            else:
                rdata = (
                    dt['_status'],
                    None
                )
            rt_data.append(rdata)
        return (columns, rt_data)

class FileGet(Lister):
    'Get/download job runtime file'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileGet, self).get_parser(prog_name)
        parser.add_argument('--dur', choices=['h','d','w','m','p'],
                            help='Lifetime duration (h - hour,d - day,w -week,m -month,p - permanent)', required=True)
        parser.add_argument("--path", type=str,
                            help='Server path of runtime files (must start with / and end with /)', default='/')
        parser.add_argument('--job_id', type=str, help='Id of job to add file(s)', required=True)
        parser.add_argument("--replace", type=str2bool, nargs='?',
                            const=True, default=False,
                            help="Replace local file, if exists")
        parser.add_argument('file', nargs='+', type=str)
        return parser

    def take_action(self, parsed_args):
        mime = mimetypes.MimeTypes()
        columns = (
            '_status', '_error'
        )
        con = AuthenticatedConn()
        rt_data = []
        for f in parsed_args.file:
            resp = con.get_request(
                '/api/micropipes/jobs/{}/runtime/files/{}{}{}'.format(parsed_args.job_id,
                                                parsed_args.dur,parsed_args.path, f)
                                    )
            rdata = ()
            if resp.status != 200:
                dt = json.loads(resp.data.decode())
                rdata = (
                    dt['_status'],
                    dt['_error']
                )
            else:
                try:
                    if os.path.exists(f) and not parsed_args.replace:
                        raise Exception('file exists {} (use --replace)'.format(f))
                    with open(f,'wb') as f:
                        f.write(resp.data)
                    rdata = (
                        'OK',
                        None
                    )
                except Exception as e:
                    rdata = (
                        'local.exception',
                        str(e)
                    )


            rt_data.append(rdata)
        return (columns, rt_data)