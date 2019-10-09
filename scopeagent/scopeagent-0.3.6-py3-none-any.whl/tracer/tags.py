from opentracing.ext.tags import *

# General tags
HOSTNAME = 'hostname'
SERVICE = 'service'
COMMAND = 'command'
PLATFORM_NAME = 'platform.name'
PLATFORM_VERSION = 'platform.version'
ARCHITECTURE = 'architecture'
REPOSITORY = 'repository'
COMMIT = 'commit'
BRANCH = 'branch'
SPAN_KIND_PUBLISH = 'publish'
SPAN_KIND_RECEIVE = 'receive'
SOURCE_ROOT = 'source.root'
AGENT_ID = 'agent.id'
AGENT_VERSION = 'agent.version'
AGENT_TYPE = 'agent.type'

# Python specific tags
PYTHON_IMPLEMENTATION = 'python.implementation'
PYTHON_VERSION = 'python.version'

# CI specific tags
CI = 'ci.in_ci'
CI_PROVIDER = 'ci.provider'
CI_BUILD_ID = 'ci.build_id'
CI_BUILD_NUMBER = 'ci.build_number'
CI_BUILD_URL = 'ci.build_url'

# Test related tags
TEST = 'test'
TEST_SUITE = 'test.suite'
TEST_NAME = 'test.name'
TEST_CODE = 'test.code'
TEST_FRAMEWORK = 'test.framework'

TEST_STATUS = 'test.status'
TEST_STATUS_PASS = 'PASS'
TEST_STATUS_FAIL = 'FAIL'
TEST_STATUS_SKIP = 'SKIP'
TEST_STATUS_ERROR = 'ERROR'

# RPC related tags
RPC_OPERATION_ID = 'rpc.id'

# Log fields
ERROR_KIND = 'error.kind'
ERROR_OBJECT = 'error.object'
EVENT = 'event'
MESSAGE = 'message'
STACK = 'stack'
EXCEPTION = 'exception'
EVENT_LOG = 'log'
LOG_LOGGER = 'log.logger'
LOG_LEVEL = 'log.level'
SOURCE = 'source'

# Baggage tags
TRACE_KIND = 'trace.kind'
