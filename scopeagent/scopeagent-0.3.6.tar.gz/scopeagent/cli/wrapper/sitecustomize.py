import os
import shlex
import sys
from distutils.util import strtobool

import scopeagent

argv = shlex.split(os.getenv('SCOPE_COMMAND'))
if len(argv) >= 3 and argv[0] == 'python':
    if argv[1] == '-m':
        argv = ["python -m %s" % argv[2]] + argv[3:]
    else:
        argv = argv[1:]
sys.argv = argv


def bool_getenv(key, default):
    return bool(strtobool(os.environ[key])) if key in os.environ else default


agent = scopeagent.Agent(
    api_key=os.getenv('SCOPE_APIKEY'),
    api_endpoint=os.getenv('SCOPE_API_ENDPOINT'),
    repository=os.getenv('SCOPE_REPOSITORY'),
    commit=os.getenv('SCOPE_COMMIT'),
    service=os.getenv('SCOPE_SERVICE'),
    branch=os.getenv('SCOPE_BRANCH'),
    source_root=os.getenv('SCOPE_SOURCE_ROOT'),
    debug=bool_getenv('SCOPE_DEBUG', False),
    dry_run=bool_getenv('SCOPE_DRYRUN', False),
    command=os.getenv('SCOPE_COMMAND'),
)

agent.install(
    testing_mode=bool_getenv('SCOPE_TESTING_MODE', False),
    set_global_tracer=bool_getenv('SCOPE_SET_GLOBAL_TRACER', False),
    autoinstrument=bool_getenv('SCOPE_AUTO_INSTRUMENT', True),
)
