import logging
from cliff.lister import Lister
from mpipes.common import *


class LogList(Lister):
    'List existing job runtime logs, levels are (DEBUG,INFO,WARNING, ERROR, CRITICAL)'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(LogList, self).get_parser(prog_name)
        parser.add_argument('--level', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'])
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
        resp = con.get_request('/api/micropipes/jobs/{}/runtime/logs/{}'.format(parsed_args.job_id[0], parsed_args.level),
                                fields=fileds)
        if resp.status != 200:
            format_err_response(resp)
            return None
        return format_response_list(resp)