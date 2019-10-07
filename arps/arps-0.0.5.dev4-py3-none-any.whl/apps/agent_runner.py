import argparse
import sys
import logging
import signal
import platform
import asyncio
from typing import Dict, Optional

from arps import __version__ as arps_version
from arps.core.clock import Clock
from arps.core.agent_factory import (AgentFactory,
                                     AgentCreationError,
                                     build_agent)
from arps.core.agent_id_manager import AgentID
from arps.core.real.real_communication_layer import RealCommunicationLayer
from arps.core.real.raw_communication_layer import RawCommunicationLayer
from arps.core.real.rest_communication_layer import RESTCommunicationLayer
from arps.core.real.agents_directory_helper import AgentsDirectoryHelper
from arps.core.clock import real_time_clock_factory
from arps.core.metrics_logger import MetricsLoggers
from arps.core import logger_setup
from arps.core.remove_logger_files import remove_logger_files
from arps.apps.configuration_file_loader import load_agent_environment
from arps.apps.pid import create_pid_file

# pylint: disable-msg=C0103


class AgentHandler:
    '''
    This class control the life cycle of an agent.

    By default the agent will be listening the port 8888

    Raises AgentCreationError from build_agent when agent creation fails.
    '''

    def __init__(self,
                 environment,
                 clock,
                 agent_id,
                 agent_port=8888,
                 policies=None,
                 agents_directory_helper=None,
                 comm_layer_cls=None):
        '''Initialize agent handler instance

        Params:
        - environment: agent environment
        - agent_id: instance of AgentID created by AgentIDManager
        - agent_port: listening port (default: 8888)
        - policies: policies that will control the agent behaviour
        - agents_directory_helper: agents discovery service where the
          agent will be registered
        - comm_layer_cls: implementation of RealCommunicationLayer
        '''
        assert issubclass(comm_layer_cls, RealCommunicationLayer)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.agent_id = agent_id
        self.communication_layer = comm_layer_cls(agent_port,
                                                  agents_directory_helper)

        self.clock = clock
        try:
            agent_factory = AgentFactory(environment=environment,
                                         communication_layer=self.communication_layer,
                                         metrics_loggers=MetricsLoggers())
            self.agent = self.create_agent(agent_factory,
                                           agent_id=self.agent_id,
                                           policies=policies or [], clock=clock)
        except AgentCreationError as err:
            self.logger.error(err)
            raise RuntimeError(err)
        self.port = agent_port
        self.logger.info(f'created agent server {self.agent_id} to listen on {agent_port}')

    async def start(self):
        self.logger.info('agent has started')
        await self.communication_layer.start()
        self.clock.add_listener(self.agent.run)

    async def finalize(self):
        self.communication_layer.unregister(self.agent.identifier)
        await self.communication_layer.close()
        self.logger.info('agent has stopped')

    def create_agent(self, agent_factory,
                     agent_id: AgentID,
                     policies: Dict[str, Optional[int]],
                     clock: Clock):
        self.logger.info('Policies: {}'.format(policies))
        agent = build_agent(agent_factory, agent_id, policies, clock)

        return agent


def main():
    # with open('agent_runner.log', 'a') as f:
    #     f.write(str(os.getpid()) + '\n')

    parser = build_argument_parser()

    try:
        parsed_args = parser.parse_args()
        print(parsed_args)
    except argparse.ArgumentTypeError as err:
        sys.exit(err)

    if platform.system() == 'Windows':
        def interrupt_application(*_):
            print('Received signal to stop')
            raise KeyboardInterrupt
        signal.signal(signal.SIGBREAK, interrupt_application)

    try:
        asyncio.run(run_agent(parsed_args))
    except KeyboardInterrupt:
        print('agent finished')


async def run_agent(parsed_args):
    agent_id = AgentID(parsed_args.id[0], parsed_args.id[1])
    logger = logging.getLogger()
    logger_setup.set_to_rotate(logger,
                               level=logging.INFO,
                               file_name_prefix=f'agent_{agent_id}')
    environment = load_agent_environment(parsed_args.id[0], parsed_args.config_file)
    agents_directory_helper = AgentsDirectoryHelper(address=parsed_args.agents_dir_addr,
                                                    port=parsed_args.agents_dir_port)

    if not environment:
        remove_logger_files(logger)
        raise ValueError('Required configuration files not present. Check again')

    clock = real_time_clock_factory()

    if parsed_args.comm_layer == 'raw':
        comm_layer_cls = RawCommunicationLayer
    elif parsed_args.comm_layer == 'REST':
        comm_layer_cls = RESTCommunicationLayer
    else:
        remove_logger_files(logger)
        raise ValueError('Invalid Communication Layer selected. Expect raw or REST')

    try:
        policies = {**parsed_args.policy, **parsed_args.periodic_policy}
        agent_handler = AgentHandler(environment=environment,
                                     clock=clock,
                                     agent_id=agent_id,
                                     agent_port=parsed_args.port,
                                     policies=policies,
                                     agents_directory_helper=agents_directory_helper,
                                     comm_layer_cls=comm_layer_cls)
    except RuntimeError as e:
        remove_logger_files(logger)
        sys.exit(e)

    await agent_handler.start()

    with create_pid_file():
        await clock.run()

    await agent_handler.finalize()


def build_argument_parser():
    parser = argparse.ArgumentParser(description='Instantiates an agent with default policies Info and TouchPointStatus')
    parser.add_argument('--id', nargs=2, type=int, required=True, metavar=('Manager id', 'agent id'),
                        help='identifier of the agent creator')
    parser.add_argument('--port', type=int, default=8888,
                        help='agent listen port (default: %(default)s)')
    parser.add_argument('--policy', action=policy_parser(), nargs=1, metavar=('policy'), default={},
                        help='regular policy that handle events. Can be invoked multiple times for each policy')
    parser.add_argument('--periodic_policy', action=policy_parser(), nargs=2, metavar=('policy', 'period'), default={},
                        help='periodic policy that handle events. Can be invoked multiple times for each policy')
    parser.add_argument('--agents_dir_addr', default='localhost',
                        help='agent directory server address')
    parser.add_argument('--agents_dir_port', default=1500, help='agent directory server port')
    parser.add_argument('--config_file', required=True,
                        help='configuration containing domain specific classes (sensors, actuators, and policies)')
    parser.add_argument('--comm_layer', required=True,
                        choices=['REST', 'raw'],
                        help='Type of communication layer used. Options: REST or raw')
    parser.add_argument('--version', action='version', version=f'ARPS {arps_version}')
    return parser


def format(values):
    if len(values) == 2:
        try:
            return values[0], int(values[1])
        except ValueError:
            return values[0], values[1]
    elif len(values) == 1:
        return values[0], None
    else:
        raise argparse.ArgumentTypeError('Unexpected number of arguments.')


def policy_parser():
    class PolicyAction(argparse.Action):
        """Action to assign a string and optional integer"""
        def __call__(self, parser, namespace, values, option_string=None):
            values = format(values)
            if getattr(namespace, self.dest) is None:
                setattr(namespace, self.dest, dict(values))
                return

            if values[0] in getattr(namespace, self.dest):
                raise argparse.ArgumentTypeError('Only one instance of a policy is allowed. Check if a policy is being added more than once')
            getattr(namespace, self.dest)[values[0]] = values[1]

    return PolicyAction


if __name__ == '__main__':
    main()
    sys.exit(0)
