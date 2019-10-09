import logging
import os
import platform
import uuid

import opentracing

import scopeagent
from scopeagent.agent.config import load_config_file
from .ci import get_ci_tags
from .git import detect_git_info
from ..instrumentation import patch_all
from ..recorders.http import HTTPRecorder
from ..tracer import BasicTracer, tags

logger = logging.getLogger(__name__)
DEFAULT_API_ENDPOINT = "https://app.scope.dev"


class AgentError(Exception):
    pass


class Agent:
    def __init__(self, api_key=None, api_endpoint=None, repository=None, commit=None, service=None,
                 branch=None, source_root=None, debug=False, dry_run=False, command=None):
        """
        Creates a new Scope agent instance (without installing it). All parameters are optional and will be autodetected
        from the environment where possible.

        :param api_key: the API key to use when sending data to the Scope backend
        :param api_endpoint: the API endpoint of the Scope instance where the data is going to be sent
        :param repository: the git repository URL of the service being instrumented
        :param commit: the commit hash being instrumented
        :param service: the name of the service being instrumented (defaults to `default`)
        :param branch: the branch being instrumented
        :param source_root: the absolute path to the root of the git repository in the local filesystem
        :param debug: if `true`, enables verbose debug logging
        :param dry_run: if `true`, avoids actually sending data to the backend
        :param command: command string used to launch the service being instrumented
        """
        git_info = detect_git_info()
        config_file = load_config_file()

        self.api_key = api_key or \
            os.getenv('SCOPE_APIKEY') or \
            config_file.get('apiKey')
        self.api_endpoint = api_endpoint or \
            os.getenv('SCOPE_API_ENDPOINT') or \
            config_file.get('apiEndpoint') or \
            DEFAULT_API_ENDPOINT
        self.repository = \
            repository or \
            os.getenv('SCOPE_REPOSITORY') or \
            os.getenv('GIT_URL') or \
            os.getenv('CIRCLE_REPOSITORY_URL') or \
            ("https://github.com/%s.git" % os.getenv('TRAVIS_REPO_SLUG') if os.getenv('TRAVIS_REPO_SLUG') else None) or\
            os.getenv('CI_REPOSITORY_URL') or \
            git_info.get('repository')
        self.commit = \
            commit or \
            os.getenv('SCOPE_COMMIT_SHA') or \
            os.getenv('GIT_COMMIT') or \
            os.getenv('CIRCLE_SHA1') or \
            os.getenv('TRAVIS_COMMIT') or \
            os.getenv('CI_COMMIT_SHA') or \
            git_info.get('commit')
        self.service = service or 'default'
        self.branch = \
            branch or \
            os.getenv('SCOPE_BRANCH') or \
            os.getenv('GIT_BRANCH') or \
            os.getenv('CIRCLE_BRANCH') or \
            os.getenv('TRAVIS_BRANCH') or \
            os.getenv('CI_COMMIT_REF_NAME') or \
            git_info.get('branch')
        self.source_root = \
            source_root or \
            os.getenv('SCOPE_SOURCE_ROOT') or \
            os.getenv('WORKSPACE') or \
            os.getenv('CIRCLE_WORKING_DIRECTORY') or \
            os.getenv('TRAVIS_BUILD_DIR') or \
            os.getenv('CI_PROJECT_DIR') or \
            git_info.get('root') or \
            os.getcwd()

        if debug:
            logging.basicConfig()
            logging.getLogger('scopeagent').setLevel(logging.DEBUG)
        self.dry_run = dry_run
        self.command = command

        self.tracer = None
        self.agent_id = str(uuid.uuid4())

    def install(self, testing_mode=False, set_global_tracer=False, autoinstrument=True):
        """
        Installs the tracer and instruments all libraries.

        :param testing_mode: whether the command launched is for running tests
        :param set_global_tracer: if `true`, sets the Scope tracer as the OpenTracing global tracer
        :param autoinstrument: if `true`, patches all supported libraries to enable instrumentation
        :return: None
        """
        if not self.api_key:
            raise AgentError("API key is required")
        if not self.api_endpoint:
            raise AgentError("API endpoint is required")

        # Install tracer
        metadata = {
            tags.AGENT_ID: self.agent_id,
            tags.AGENT_VERSION: scopeagent.version,
            tags.AGENT_TYPE: 'python',
            tags.SOURCE_ROOT: self.source_root,
            tags.HOSTNAME: platform.node(),
            tags.PLATFORM_NAME: platform.system(),
            tags.PLATFORM_VERSION: platform.release(),
            tags.ARCHITECTURE: platform.machine(),
            tags.PYTHON_IMPLEMENTATION: platform.python_implementation(),
            tags.PYTHON_VERSION: platform.python_version(),
        }
        if self.repository:
            metadata[tags.REPOSITORY] = self.repository
        if self.commit:
            metadata[tags.COMMIT] = self.commit
        if self.branch:
            metadata[tags.BRANCH] = self.branch
        if self.service:
            metadata[tags.SERVICE] = self.service
        if self.command:
            metadata[tags.COMMAND] = self.command
        metadata.update(get_ci_tags())
        logger.debug("metadata=%s", metadata)

        # If in CI, always set to testing mode.
        if metadata[tags.CI]:
            testing_mode = True

        # If in testing mode, send health checks every second to track agent running status
        if testing_mode:
            logger.debug("Using a health check period of 1 second (testing mode)")
            period = 1
        else:
            logger.debug("Using a health check period of 1 minute (non testing mode)")
            period = 60

        recorder = HTTPRecorder(
            test_only=True, api_key=self.api_key, api_endpoint=self.api_endpoint, metadata=metadata, period=period,
            dry_run=self.dry_run
        )
        self.tracer = BasicTracer(recorder)
        scopeagent.global_agent = self

        # Register as opentracing global tracer if configured to do so
        if set_global_tracer:
            logger.debug("Using Scope Agent tracer as global tracer (opentracing.tracer)")
            opentracing.tracer = self.tracer

        # Patch all supported libraries
        if autoinstrument:
            logger.debug("Auto instrumentation is enabled")
            patch_all(tracer=self.tracer)
        else:
            logger.debug("Auto instrumentation is disabled")
