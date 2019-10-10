import logging
from cliff.lister import Lister
from mpipes.common import *


class StatsJobNames(Lister):
    'List job stats names'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsJobNames, self).get_parser(prog_name)
        parser.add_argument('job_id', type=str, help='Id of job to get', nargs=1)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        resp = con.get_request('/api/micropipes/jobs/{}/runtime/stats/names/'.format(parsed_args.job_id[0]))
        if resp.status != 200:
            format_err_response(resp)
            return None
        data = json.loads(resp.data.decode())
        items = data['_items']
        rt_data = []
        for item in items:
            rt_data.append([item])
        return (['Names'],rt_data)

class StatsNames(Lister):
    'List stats names'

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        resp = con.get_request('/api/micropipes/runtime/stats/names/')
        if resp.status != 200:
            format_err_response(resp)
            return None
        data = json.loads(resp.data.decode())
        items = data['_items']
        rt_data = []
        for item in items:
            rt_data.append([item])
        return (['Names'],rt_data)

class StatsPrecisions(Lister):
    'List stats precisions'

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        resp = con.get_request('/api/micropipes/runtime/stats/precisions/')
        if resp.status != 200:
            format_err_response(resp)
            return None
        data = json.loads(resp.data.decode())
        items = data['_items']
        rt_data = []
        for item in items:
            rt_data.append([item])
        return (['Precisions'],rt_data)

class StatsJob(Lister):
    'List job stats'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsJob, self).get_parser(prog_name)
        parser.add_argument("--start", type=int, help='Start from, 0 - beginning, minus allowed - python slice notation', default=-8)
        parser.add_argument("--end", type=int, help='End, -1 last one, minus allowed - python slice notation', default=None)
        parser.add_argument('--prec',choices=['20s','10m','1h','1d'], help='Precision (20s, 10m, 1h, 1d)', default='1h')
        parser.add_argument('--names', type=str, help='Comma separated stat names, if ommited - all stats are returned', required=False)
        parser.add_argument('job_id', type=str, help='Id of job to get', nargs=1)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        fileds = {
            'from': parsed_args.start,
        }
        if parsed_args.end:
            fileds['to'] = parsed_args.end
        if parsed_args.names:
            fileds['stats_names'] = parsed_args.names
        resp = con.get_request('/api/micropipes/jobs/{}/runtime/stats/{}'.format(parsed_args.job_id[0], parsed_args.prec),
                                fields=fileds)
        if resp.status != 200:
            format_err_response(resp)
            return None
        return format_response_stats(resp, parsed_args.prec)

class Stats(Lister):
    'List customer stats (for all jobs)'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Stats, self).get_parser(prog_name)
        parser.add_argument("--start", type=int, help='Start from, 0 - beginning, minus allowed - python slice notation', default=-8)
        parser.add_argument("--end", type=int, help='End, -1 last one, minus allowed - python slice notation', default=None)
        parser.add_argument('--prec', choices=['20s', '10m', '1h', '1d'], help='Precision (20s, 10m, 1h, 1d)', default='1h')
        parser.add_argument('--names', type=str, help='Comma separated stat names, if ommited - all stats are returned', required=False)
        return parser

    def take_action(self, parsed_args):
        con = AuthenticatedConn()
        fileds = {
            'from': parsed_args.start,
        }
        if parsed_args.end:
            fileds['to'] = parsed_args.end
        if parsed_args.names:
            fileds['stats_names'] = parsed_args.names
        resp = con.get_request('/api/micropipes/runtime/stats/{}'.format(parsed_args.prec),
                                fields=fileds)
        if resp.status != 200:
            format_err_response(resp)
            return None
        # print(resp.data.decode())
        return format_response_stats(resp, parsed_args.prec)