import sys
import os
import subprocess
from typing import List, Dict, Optional
import pathlib

import simplejson as json
import psutil

from arps.core.agent_id_manager import AgentID
from arps.core.payload_factory import (PayloadType,
                                       parse_payload_type)
from arps.core.real.raw_communication_layer import RawCommunicationLayer
from arps.core.real.rest_communication_layer import RESTCommunicationLayer
from arps.core.real.real_communication_layer import RegistrationError
from arps.core.real.agents_directory_helper import AgentsDirectoryHelper
from arps.core.real.rest_api_utils import random_port

from arps.apps.agent_manager import (AgentManager,
                                     JSONType,
                                     AgentManagerCreationError,
                                     AgentManagerRequestError)
from arps.apps.configuration_file_loader import load_touchpoints_classes
from arps.apps.multiplatform_process import create_process, terminate_process
from arps.apps.client import AgentClient
from arps.apps.configuration_file_loader import InvalidConfigurationError


class RealEnvironmentAgentManager(AgentManager):

    def __init__(self, manager_configuration):
        self.comm_layer_type = manager_configuration.comm_layer_type
        if self.comm_layer_type == 'raw':
            comm_layer_cls = RawCommunicationLayer
        elif self.comm_layer_type == 'REST':
            comm_layer_cls = RESTCommunicationLayer
        else:
            raise AgentManagerCreationError('Invalid Communication Layer Class. Check configuration file. "comm_layer" options are "raw" or "REST"')

        self.agent_config = manager_configuration.agent_config
        self.agents_directory = manager_configuration.agents_directory
        self.agents_directory_helper = AgentsDirectoryHelper(**self.agents_directory)

        super().__init__(manager_configuration.identifier)

        base_port = random_port()

        self.comm_layer = comm_layer_cls(base_port,
                                         self.agents_directory_helper)
        self.agent_client = None

        self.loaded_policies = self.load_policies_available()

    async def start(self):
        await self.comm_layer.start()
        try:
            client_id = AgentID(self.identifier, 0)
            self.agent_client = AgentClient(identifier=client_id,
                                            communication_layer=self.comm_layer)
        except RegistrationError as err:
            raise AgentManagerCreationError(f'Error: {err}. \nCheck the identifier field in the configuration file or if there is other agent manager running. If not remove manually from agents directory. Check if agents directory is running')

    async def spawn_agent(self, *, policies: Dict[str, Optional[int]]) -> JSONType:
        if not policies:
            raise AgentManagerRequestError('agent not created, no policy specified')

        agent_id = self.agent_id_manager.next_available_id()
        port = random_port()
        popen = ['agent_runner',
                 '--id', str(agent_id.root_id), str(agent_id.agent_identifier),
                 '--port', str(port),
                 '--agents_dir_addr', self.agents_directory['address'],
                 '--agents_dir_port', str(self.agents_directory['port']),
                 '--config_file', self.agent_config,
                 '--comm_layer', self.comm_layer_type]
        self.logger.debug(f'Spawning agents with policies: {policies}')
        for policy, period in policies.items():
            if period is not None:
                popen.extend(('--periodic_policy', policy, str(period)))
            else:
                popen.extend(('--policy', policy))

        self.logger.debug('Agent paramaters {}'.format(popen))

        (success, message), proc = create_process(popen,
                                                  stderr=subprocess.PIPE,
                                                  stdout=subprocess.PIPE)

        if not success:
            raise AgentManagerRequestError(message)

        self.running_agents[(agent_id, port)] = proc
        self.agent_id_manager.commit()

        return f'Agent {agent_id} created'

    def list_agents(self) -> JSONType:
        running_agents = sorted(str(agent_id) for agent_id, _ in self.running_agents)
        return {'agents': running_agents}

    async def terminate_agent(self, *, agent_id: AgentID) -> JSONType:
        if agent_id not in [agent_id for agent_id, _ in self.running_agents]:
            raise AgentManagerRequestError('Agent id not found. Try list_agents resource to list available agents')

        self.logger.info('Requested termination of agent {}'.format(agent_id))

        agent_proc, port = next((agent_proc, port) for (running_agent_id, port), agent_proc in self.running_agents.items() if running_agent_id == agent_id)

        self.logger.info('Signal sent to agent {} (pid: {}). Waiting until is terminated'.format(agent_id, agent_proc.pid))
        self.remove_process_files(agent_proc.pid)
        returncode, message = terminate_process(agent_proc)

        self.logger.info('Unregistering Agent {}'.format((agent_id, port)))
        del self.running_agents[(agent_id, port)]

        self.logger.info('Agent {} finalized, return code set as {}'.format(agent_id, returncode))
        if returncode != 0:
            self.logger.info(message)
            self.logger.info('Removing agent {} from agents_directory'.format(agent_id))
            # Sometimes the agent fails to terminate correctly but
            # removes itself from the yellow pages
            self.agents_directory_helper.remove(parameters={'id': agent_id})
            return f'Return code is not 0, agent {agent_id} has been forcefully terminated'

        message = f'Agent {agent_id} terminated successfully'

        self.logger.info(message)

        return message

    def remove_process_files(self, pid):
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            self.logger.warning('No such process %s', pid)

        files = [pathlib.Path(pfile.path) for pfile in process.open_files()]
        files = [pfile for pfile in files if pfile.suffix == '.log']
        for f in files:
            try:
                os.remove(f)
            except (PermissionError, FileNotFoundError, OSError) as err:
                self.logger.warning('Error: %s', err)

    async def _agent_status(self, request_type: PayloadType, provider: AgentID):
        try:
            request_type = parse_payload_type(request_type)

            result = await self.agent_client.send_request(provider,
                                                          request_type)

            self.logger.debug(f'agent_status returns: {result}')
            return result
        except ValueError as error:
            message = 'Invalid request type: {}'.format(error)
            self.logger.error(message)
            raise AgentManagerRequestError(message)

    def _providers(self, providers_identifier: List[AgentID]) -> List[str]:
        if not providers_identifier:
            return self.running_agents.keys()

        return [(agent_identifier, port) for (agent_identifier, port) in self.running_agents.keys()
                if agent_identifier in providers_identifier]

    async def update_agents_relationship(self, *,
                                         from_agent: AgentID,
                                         to_agent: str,
                                         operation: str):
        content = {'operation': operation, 'to_agent': to_agent}

        result = await self.agent_client.send_request(from_agent,
                                                      PayloadType.meta_agent,
                                                      content)
        if result.type != PayloadType.error:
            return result

        raise AgentManagerRequestError(result.content)

    async def update_policy(self, *, agent_id: AgentID, operation: str, policy: str, period: int):
        content = {'operation': operation, 'policy': policy, 'period': period}

        result = await self.agent_client.send_request(agent_id,
                                                      PayloadType.policy,
                                                      content)
        if result.type != PayloadType.error:
            return result

        raise AgentManagerRequestError(result.content)

    def load_policies_available(self):
        with open(self.agent_config) as agent_conf:
            agent_config = json.load(agent_conf)

            resources = agent_config['resources']
            resources = [resource['class'] for resource in resources]
            monitor_policies = [f'{resource}MonitorPolicy' for resource in resources]

            policies = agent_config['agent_config']['policies']

            return policies + monitor_policies

    async def policy_repository(self) -> JSONType:
        return self.loaded_policies

    async def loaded_touchpoints(self) -> JSONType:
        with open(self.agent_config) as agent_conf:
            agent = json.load(agent_conf)
            agent_config = agent['agent_config']
            sensors = []
            actuators = []
            for resource in agent['resources']:
                sensors.extend(resource['class'] for sensor in agent_config['sensors'] if resource['id'] == sensor['resource_id'])
                actuators.extend(resource['class'] for actuator in agent_config['actuators'] if resource['id'] == actuator['resource_id'])

            return {'sensors': sensors, 'actuators': actuators}

    def finish_all_agents(self):
        self.logger.info('finalizing agents {}'.format([agent_id for (agent_id, _) in self.running_agents]))

        for (agent_id, _), running_agent in self.running_agents.items():
            self.logger.info('terminating for agent %s', agent_id)
            returncode, message = terminate_process(running_agent, timeout=1)
            self.logger.info(f'Return code {returncode} for agent {running_agent}')
            if returncode != 0:
                self.logger.warning(message)
                self.logger.warning(f'Removing agent {agent_id} from agents_directory')
                self.agents_directory_helper.remove(parameters={'id': agent_id})

            self.logger.info('Agent %s terminated successfully', agent_id)

    async def cleanup(self):
        self.finish_all_agents()

        await self.agent_client.finalize()

        await self.comm_layer.close()

        self.logger.info('cleanup successfully executed')
