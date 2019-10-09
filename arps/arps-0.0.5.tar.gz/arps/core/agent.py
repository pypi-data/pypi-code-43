import logging
from abc import abstractmethod
from typing import List, Optional, Any

from arps.core.agent_id_manager import AgentID
from arps.core.communication_layer import CommunicableEntity
from arps.core.policies_executor import PoliciesExecutor


class Agent(CommunicableEntity):
    '''
    Base class for agents

    An agent has two list of touchpoints available: sensors and actuators
    '''

    def __init__(self, **kwargs):
        '''
        Keyword parameters:
        - sensors: list of sensors to be read
        - actuators: list of actuators to be controlled
        '''

        self._environment = kwargs.pop('environment')
        # Sometimes the related agent can be terminated or be non
        # existent from the beginning.  The decision about what to do
        # when the agent is not found is responsibility of the user. A
        # policy that does not found the agent can simply remove it
        # from this list or it can wait a bit
        self._related_agents = set()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._process: PoliciesExecutor = None
        super().__init__(**kwargs)

        assert isinstance(self.identifier, AgentID)

    def include_as_related(self, agent_id: AgentID):
        assert isinstance(agent_id, AgentID)

        self._related_agents.add(agent_id)

    def remove_as_related(self, agent_id: AgentID):
        assert isinstance(agent_id, AgentID)

        self._related_agents.remove(agent_id)

    @property
    def related_agents(self):
        return frozenset(self._related_agents)

    def sensors(self) -> List[str]:
        '''
        Returns a list of available sensors
        '''
        return list(self._environment.sensors.keys())

    def actuators(self) -> List[str]:
        '''
        Returns a list of available actuators
        '''
        return list(self._environment.actuators.keys())

    def read_sensor(self, sensor_id: str) -> Any:
        return self._environment.sensors[sensor_id].read()

    def read_actuator(self, actuator_id: str) -> Any:
        return self._environment.actuators[actuator_id].read()

    def modify_actuator(self, actuator_category, **actuator_attributes):
        return self._environment.actuators[actuator_category].set(**actuator_attributes)

    def add_policy(self, policy_identifier: str, period: Optional[int] = None):
        policy = self._environment.load_policy(policy_identifier, period)
        self._process.add_policy(policy)

    def is_policy_registered(self, policy_identifier: str) -> bool:
        return self._environment.is_policy_registered(policy_identifier)

    @abstractmethod
    async def run(self):
        '''Execute control loop
        '''


class _AgentImplementation(Agent):
    '''
    Responsible to run process.

    created by agent_factory.create_agent.

    When created a single process is added. This process will take care of the upper layer logic
    while this class will handle host stuff
    '''

    def __init__(self, **kwargs):
        self._process = None
        self._metrics_logger = kwargs.pop('metrics_logger')
        super().__init__(**kwargs)

    @property
    def process(self):
        return self._process

    async def receive(self, message):
        self.logger.debug('agent %s received message ', self.identifier)
        self._process.receive(message)
        self._metrics_logger.update_number_of_messages()

    @property
    def metrics_logger(self):
        return self._metrics_logger

    async def run(self):
        self.logger.debug(f'running agent {self.identifier}')
        await self._process.run()

    def _add_process(self, process):
        process.host = self
        self._process = process
        self._process.logger = logging.getLogger('Agent_{}_Process'.format(self.identifier))

    def __repr__(self):
        return f'Agent(identifier={self.identifier}, policies={self._process!r})'

    def __str__(self):
        return 'Agent {}'.format(self.identifier)
