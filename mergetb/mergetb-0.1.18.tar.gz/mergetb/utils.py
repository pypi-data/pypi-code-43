import logging
import inspect
import mergetb.lib as mergelib
import mergetb.xdc as mergexdc
from mergetb.term import green, gray


def handle_logging_args(parsedargs):
    log_levels = {
        u'none': 100,
        u'all': 0,
        u'debug': logging.DEBUG,
        u'info': logging.INFO,
        u'warning': logging.WARNING,
        u'error': logging.ERROR,
        u'critical': logging.CRITICAL
    }
    log_format = u'%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    log_datefmt = u'%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format, datefmt=log_datefmt,
                        level=log_levels[parsedargs.loglevel])

def add_logging_args(parser):
    parser.add_argument("-L", "--loglevel", dest="loglevel",
                        help="The level at which to log. Must be one of "
                        "none, debug, info, warning, error, or critical. Default is none. ("
                        "This is mostly used for debugging.)",
                        default='none', choices=['none', u'all', u'debug', u'info', u'warning',
                                                 u'error', u'critical'])

# Add functions that should be available on the command line here.
# map via functional subject -> verb -> function.
CMDS = {
    'projects': {
        'list': mergelib.list_projects,
        'info': mergelib.project_info,
        'new': mergelib.new_project,
        'delete': mergelib.delete_project,
        'update': mergelib.update_project,
        'experiments': mergelib.project_experiments,
        'members': mergelib.project_members,
        'member': mergelib.project_member,
        'add-member': mergelib.project_add_member,
        'update-member': mergelib.project_update_member,
        'delete-member': mergelib.project_delete_member,
    },
    'experiments': {
        'list': mergelib.list_experiments,
        'info': mergelib.experiment_info,
        'pull': mergelib.pull_experiment,
        'new': mergelib.new_experiment,
        'delete': mergelib.delete_experiment,
        'push': mergelib.push_experiment_file,
        'history': mergelib.experiment_history,
        'realize': mergelib.realize,
    },
    'realization': {
        'list': mergelib.list_realizations,
        'info': mergelib.get_realization,
        'realize': mergelib.realize,
        'accept': mergelib.accept_realization,
        'reject': mergelib.reject_realization,
        'delete': mergelib.delete_realization,
        'materialize': mergelib.materialize,
    },
    'materialization': {
        'list': mergelib.list_materializations,
        'info': mergelib.get_materialization,
        'status': mergelib.materialization_status,
        'delete': mergelib.dematerialize,
        'attach': mergelib.materialize_attach,
        'detach': mergelib.materialize_detach,
    },
    'users': {
        'list': mergelib.list_users,
        'info': mergelib.user_info,
        'update': mergelib.update_user,
        'delete': mergelib.user_delete,
        'vtoken': mergelib.user_vtoken,
        'validate': mergelib.user_validate,
    },
    'sites': {
        'list': mergelib.list_sites,
        'new': mergelib.new_site,
        'get': mergelib.get_site,
        'delete': mergelib.delete_site,
        'set-cert': mergelib.set_site_cert,
        'activate': mergelib.activate_resources,
        'deactivate': mergelib.deactivate_resources,
        'set-wgd-config': mergelib.set_site_wgd_config,
    },
    'system': {
        'status': mergelib.health,
    },
    'api': {
        'get': mergelib.do_get,
        'delete': mergelib.do_delete,
        'put': mergelib.do_put_file,
        'post': mergelib.do_post_file,
    },
    'xdc': {
        'list': mergelib.list_xdcs,
        'spawn': mergelib.spawn_xdc,
        'destroy': mergelib.destroy_xdc,
        'token': mergelib.xdc_token,
        'web': mergexdc.web,
        'attach': mergelib.xdc_materialize_attach,
        'detach': mergelib.xdc_materialize_detach,
    },
    'account': {
        'init': mergelib.account_init,
        'delete': mergelib.account_delete,
    },
    'pubkey': {
        'list': mergelib.list_pubkeys,
        'add': mergelib.add_pubkey,
        'delete': mergelib.delete_pubkey,
    },
    'pool': {
        'list': mergelib.list_pools,
        'info': mergelib.pool_info,
        'new': mergelib.new_pool,
        'delete': mergelib.delete_pool,
        'sites': mergelib.pool_sites,
        'add-site': mergelib.add_pool_site,
        'del-site': mergelib.del_pool_site,
        'activate-site': mergelib.activate_pool_site,
        'projects': mergelib.pool_projects,
        'add-project': mergelib.add_pool_project,
        'del-project': mergelib.del_pool_project,
        'activate-project': mergelib.activate_pool_project,
    },
    'resources': {
        'list': mergelib.list_resources,
    },
}

def cmd_dict():
    retval = {}
    for subject in sorted(CMDS.keys()):
        retval[subject] = sorted(CMDS[subject].keys())

    return retval

def valid_cmds():
    '''Parse CMDS and build up a list of valid commands. Return as array of strings.'''
    usages = []
    for subject in sorted(CMDS.keys()):
        for verb in sorted(CMDS[subject].keys()):
            sig = inspect.signature(CMDS[subject][verb])
            usages.append('{} {} {}'.format(subject, verb, ' '.join(list(sig.parameters))))

    return usages

def _has_help_str(args):
    for a in args:
        if a in ['-h', '-?', '--help', 'help']:
            return True
    return False

def get_function(subject, verb, args):
    '''Take an array of strings and return:

    usage: the usage string for the function,
    func: the function,
    args: the args to the function

    If func is None, the usage should be given and func not executed.

    CMDS (above) will be used to map subject/verb to a function.
    The function will be inspected to ensure the given arguments
    are expected. If not expected, a usage string will be built from the
    function's docstr. If not, or if "help" is included in the arguments,
    a usage string will be created with a correct command line and the
    doc string from the function.
    '''
    if not subject in CMDS or _has_help_str([subject]):
        usage = gray("|").join(map(green, CMDS.keys()))
        return usage, None, args

    if verb not in CMDS[subject] or _has_help_str([verb]):
        usage = '{} {}'.format(subject, gray('|').join(map(green, CMDS[subject].keys())))
        return usage, None, args

    if callable(CMDS[subject][verb]):
        func = CMDS[subject][verb]
        sig = inspect.signature(func)
        if len(sig.parameters) != len(args) or _has_help_str(args):
            # we are missing expected args on the command line, give
            # generic usage + docstr of function.
            usage = '{} {} {}\n{}\n{}'.format(
                subject, verb, " ".join(list(sig.parameters)), '-'*80, inspect.getdoc(func))
            func = None
        else:
            usage = inspect.getdoc(func)
        return usage, func, args

    return None, None, None
