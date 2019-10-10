import logging
import json
from cliff.lister import Lister
from mpipes.common import *


class WorkerList(Lister):
    'List workers'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(WorkerList, self).get_parser(prog_name)
        # parser.add_argument("--attr", type=str, help='Attributes to show', default='*')
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        resp = con.get_request('/api/micropipes/workers/')
        if resp.status != 200:
            format_err_response(resp)
            return None
        # return format_response_list(resp, parsed_args.attr)
        return format_response_list(resp)