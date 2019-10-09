from typing import Tuple

from arps.core.agent_id_manager import AgentID
from arps.core.payload_factory import (PayloadType,
                                       Request,
                                       create_meta_agent_response,
                                       MetaOp)
from arps.core.policy import ActionType, ReflexPolicy


class MetaAgentProviderPolicy(ReflexPolicy):
    '''
    Provides a way to add, remove related agents

    To add or remove an agent, create a request using PayloadFactory.create_meta_agent_request(...)

    If the agent is already related, nothing will happen.

    See tests for more examples.
    '''

    def _condition(self, host, event, epoch) -> bool:
        '''
        Returns True if contains a request of PayloadType.meta_agent
        '''
        if not isinstance(event, Request):
            self.logger.debug('Event is not a request')
            return False

        is_meta_agent = event.type == PayloadType.meta_agent
        self.logger.debug(f'Event is a meta agent request: {is_meta_agent}')
        return is_meta_agent

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        '''
        Modifies an agent's related agents by adding or removing the specified agent identifier
        '''

        sender_id = event.sender_id
        receiver_id = event.receiver_id
        message_id = event.message_id

        agent_identifier = event.content.meta
        action = None
        operation = event.content.op

        async def related_agent_op(operation):
            self.logger.info(f'Executing {operation.__name__} of agent {agent_identifier} as related')
            operation(AgentID.from_str(agent_identifier))
            content = f'Operation {operation.__name__} of {agent_identifier} performed in {host.identifier}'
            self.logger.debug(content)
            await host.send(create_meta_agent_response(receiver_id,
                                                       sender_id,
                                                       content,
                                                       message_id),
                            AgentID.from_str(sender_id))

        if operation == MetaOp.add:
            self.logger.info('add agent {} into {} related agents'.format(agent_identifier,
                                                                          host.identifier))

            action = related_agent_op(host.include_as_related)
        elif operation == MetaOp.remove:
            self.logger.info('remove agent {} from {} related agents'.format(agent_identifier,
                                                                             host.identifier))
            action = related_agent_op(host.remove_as_related)
        else:
            content = 'unknown operation code {}'.format(operation)
            self.logger.warning(content)
            action = host.send(create_meta_agent_response(receiver_id,
                                                          sender_id,
                                                          content,
                                                          message_id),
                               AgentID.from_str(sender_id))

        self.logger.debug('Return as event with action {}'.format(action))
        return (ActionType.event, action)
