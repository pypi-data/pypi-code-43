from functools import wraps
import argparse
import sys
import logging
import asyncio
from datetime import datetime
from http import HTTPStatus
from typing import Dict
import json
from dataclasses import asdict

from aiohttp import web

from arps import __version__ as arps_version

from arps.core.agent_id_manager import AgentID
from arps.core.clock import simulator_clock_factory
from arps.core import logger_setup
from arps.core.policies.monitor import merge_monitor_logs
from arps.core.payload_factory import parse_payload_type
from arps.core.simulator.fake_communication_layer import FakeCommunicationLayer
from arps.core.remove_logger_files import remove_logger_files

from arps.apps.configuration_file_loader import load_manager_environment
from arps.apps.agent_manager import AgentManagerCreationError
from arps.apps.agent_manager import (AgentManager,
                                     JSONType,
                                     AgentManagerRequestError)
from arps.apps.real_environment_agent_manager import RealEnvironmentAgentManager
from arps.apps.simulator_environment_agent_manager import SimulatorEnvironmentAgentManager
from arps.apps.simulator_handler import SimulatorHandler
from arps.apps.run_server import run_server, RoutesBuilder

# pylint: disable-msg=C0103

logger = logging.getLogger()

simulator_handler = None
agent_managers: Dict[int, AgentManager] = {}


def agent_manager_handler(func):
    @wraps(func)
    def handler(*args, **kwargs):
        info = args[0].match_info
        agent_manager = None
        if 'identifier' not in info:
            agent_manager = next(iter(agent_managers.values()))
            logger.info('Agent Manager not specified, using the first server available')
            return func(agent_manager, *args, **kwargs)

        available_ams = list(agent_managers.keys())
        logger.info(f'Available Agent Managers {available_ams}')
        identifier = int(info['identifier'])
        logger.info(f'Requested Agent Manager {identifier}')
        agent_manager = agent_managers[identifier] if identifier in available_ams else None
        if agent_manager:
            logger.info(f'Request will be executed by Agent Manager {identifier}')
            return func(agent_manager, *args, **kwargs)

        logger.warning(f'Agent Manager {identifier} not found')

        reason = f'Invalid agent manager: {identifier}, available agents: {available_ams}'
        return web.json_response(reason=reason, status=HTTPStatus.BAD_REQUEST)
    return handler


def precond_method_with_body(post_handler):
    @wraps(post_handler)
    async def inner(agent_manager: AgentManager, request):
        logger.info(f'AM {agent_manager.identifier} received headers {request.headers}')
        content_type = request.headers.get('Content-type')

        if content_type != 'application/json':
            reason = f'Invalid Content-type {content_type}; expect application/json'
            return web.json_response(reason=reason, status=HTTPStatus.BAD_REQUEST)

        return await post_handler(agent_manager, request)
    return inner


@agent_manager_handler
async def index(agent_manager: AgentManager, _) -> JSONType:
    return web.json_response(data=agent_manager.index())


@agent_manager_handler
async def about(agent_manager: AgentManager, _) -> JSONType:
    return web.json_response(data=agent_manager.about())


@agent_manager_handler
@precond_method_with_body
async def spawn_agent(agent_manager: AgentManager, request):
    content = await request.content.read()
    logger.info(f'content received {content}')
    content = json.loads(content.decode())

    policies = content.get('policies', {})

    try:
        result = await agent_manager.spawn_agent(policies=policies)
        return web.json_response(data=result)
    except AgentManagerRequestError as error:
        return web.json_response(reason=str(error), status=HTTPStatus.BAD_REQUEST)


@agent_manager_handler
async def terminate_agent(agent_manager: AgentManager, request):
    agent_id = request.match_info.get('agent_id')

    if not agent_id:
        message = 'No agent id provided'
        logger.warning(message)
        return web.json_response(reason=message, status=HTTPStatus.BAD_REQUEST)

    try:
        result = await agent_manager.terminate_agent(agent_id=AgentID.from_str(agent_id))
        return web.json_response(data=result)
    except AgentManagerRequestError as error:
        return web.json_response(reason=str(error), status=HTTPStatus.BAD_REQUEST)


@agent_manager_handler
async def missing_agent_id(agent_manager: AgentManager, _):
    message = "Missing agent id: '/agents/{agent_id}'"
    return web.json_response(reason=message, status=HTTPStatus.BAD_REQUEST)


@agent_manager_handler
async def list_agents(agent_manager: AgentManager, _):
    return web.json_response(data=agent_manager.list_agents())


@agent_manager_handler
async def agents_status(agent_manager: AgentManager, request) -> JSONType:
    agent_id = request.match_info.get('agent_id')

    query = request.rel_url.query
    request_type = query.get('request_type')
    if request_type is None:
        return web.json_response(reason='expecte request_type parameter(info, sensors, or actuators)',
                                 status=HTTPStatus.BAD_REQUEST)

    available_agents = agent_manager.list_agents()

    if agent_id not in available_agents['agents']:
        reason = f'Resource /{agent_id} not found; Agent ID {agent_id} is not running'
        return web.json_response(status=HTTPStatus.NOT_FOUND, reason=reason)

    provider = AgentID.from_str(agent_id)
    status_awaitable = agent_manager.agents_status(request_type=parse_payload_type(request_type),
                                                   provider=provider)

    try:
        result = await asyncio.wait_for(status_awaitable, 10.0)
        return web.json_response(data=asdict(result))
    except AgentManagerRequestError as err:
        return web.json_response(status=HTTPStatus.BAD_REQUEST, reason=str(err))


@agent_manager_handler
@precond_method_with_body
async def update_agents_relationship(agent_manager: AgentManager, request):
    content = await request.content.read()
    logger.info(f'content received {content}')
    content = json.loads(content.decode())

    from_agent = AgentID.from_str(request.match_info.get('agent_id'))
    to_agent = content.get('agent_id')
    operation = content.get('operation')

    if not any([from_agent, to_agent, operation]):
        return web.json_response(reason='Check if parameters are present: from_agent, to_agent, and operation',
                                 status=HTTPStatus.BAD_REQUEST)

    update_agents_relationship_task = agent_manager.update_agents_relationship(from_agent=from_agent,
                                                                               to_agent=to_agent,
                                                                               operation=operation)
    try:
        result = await asyncio.wait_for(update_agents_relationship_task, 10.0)
        return web.json_response(data=asdict(result))
    except AgentManagerRequestError as err:
        return web.json_response(status=HTTPStatus.BAD_REQUEST, reason=str(err))


@agent_manager_handler
@precond_method_with_body
async def update_policy(agent_manager: AgentManager, request):
    content = await request.content.read()
    logger.info(f'content received {content}')
    content = json.loads(content.decode())

    agent_id = AgentID.from_str(request.match_info.get('agent_id'))
    operation = content.get('operation')
    policy = content.get('policy')
    period = content.get('period')

    if not any([policy, operation]):
        return web.json_response(reason='Check if parameters are present: operation and policy',
                                 status=HTTPStatus.BAD_REQUEST)

    update_policy_task = agent_manager.update_policy(agent_id=agent_id,
                                                     operation=operation,
                                                     policy=policy,
                                                     period=period)
    try:
        result = await asyncio.wait_for(update_policy_task, 10.0)
        return web.json_response(data=asdict(result))
    except AgentManagerRequestError as err:
        return web.json_response(status=HTTPStatus.BAD_REQUEST, reason=str(err))


@agent_manager_handler
async def monitor_logs(agent_manager: AgentManager, _):
    '''Return a csv file with the following header:

    "data,time,[Resource1],...[ResourceN]"

    If the same monitor resource is monitored by the two different
    monitor policies, then the header will be:

    "data,time,[Resource]_x,[Resource]_y,...[ResourceN]"

    '''
    try:
        monitor_logs = await asyncio.wait_for(agent_manager.monitor_logs(), 10.0)
    except AgentManagerRequestError as err:
        return web.json_response(status=HTTPStatus.BAD_REQUEST, reason=str(err))

    csv_buffer = merge_monitor_logs(monitor_logs)

    current_time = datetime.now().strftime('%Y%m%d-%H%M%S.%f')
    monitor_attachment = f'Attachment;filename=monitor_{current_time}.csv'

    return web.Response(body=csv_buffer, content_type='text/csv',
                        headers={'Content-Disposition': monitor_attachment})


@agent_manager_handler
async def policy_repository(agent_manager: AgentManager, _) -> JSONType:
    result = await agent_manager.policy_repository()
    return web.json_response(data=result)


@agent_manager_handler
async def loaded_touchpoints(agent_manager: AgentManager, _) -> JSONType:
    result = await agent_manager.loaded_touchpoints()
    return web.json_response(data=result,
                             headers={'Access-Control-Allow-Origin': '*'})


def check_if_is_simulation(func):
    @wraps(func)
    def check_decorator(*args, **kwargs):
        if simulator_handler:
            return func(*args, **kwargs)

        reason = 'not running as simulator, check your config files'
        return web.json_response(status=HTTPStatus.CONFLICT,
                                 reason=reason)

    return check_decorator

@check_if_is_simulation
async def sim_index(_):
    return web.json_response({'available_commands':
                              {
                                  'run': 'run simulation',
                                  'status': 'retrieve status (stopped, running)',
                                  'stop': 'stop simulation',
                                  'result': 'retrieve result (as csv)',
                                  'save': 'save current status'
                              }})


@check_if_is_simulation
async def run_simulator(_):
    simulator_handler.run()
    return web.json_response(simulator_handler.status())


@check_if_is_simulation
async def simulator_status(_):
    return web.json_response(simulator_handler.status())


@check_if_is_simulation
async def stop_simulator(_):
    simulator_handler.stop()
    return web.json_response(simulator_handler.status())


@check_if_is_simulation
async def simulator_last_result(request):
    try:
        sim_result, file_name = simulator_handler.result()
        return web.Response(body=sim_result,
                            content_type='application/zip',
                            headers={'Content-Disposition': file_name})
    except RuntimeError:
        return web.Response(reason='Error while retrieving last result file. Did you run the simulation? Did you stop the running simulation?',
                            status=HTTPStatus.CONFLICT)


@check_if_is_simulation
async def save_simulator(_):
    agents_managers_actions = {am.identifier: am.actions_tracker for am in agent_managers.values()}
    result = simulator_handler.save(agents_managers_actions)
    return web.json_response(result)


def parse_arguments():
    parser = argparse.ArgumentParser(
        'Runs agent manager. Can run as simulator, with fake communication, sensors, and actuators or with real agents')
    parser.add_argument(
        '--config_file',
        required=True,
        help='configuration file containing domain specific parameters')
    parser.add_argument(
        '--port',
        default=5000,
        type=int,
        help='port to listen for clients')
    parser.add_argument('--version', action='version', version=f'ARPS {arps_version}')

    return parser.parse_args(sys.argv[1:])


async def setup_simulator_environment(manager_environment):
    clock = simulator_clock_factory()
    comm_layer = FakeCommunicationLayer()

    for configuration in manager_environment.configuration:
        agent_mgr = SimulatorEnvironmentAgentManager(manager_configuration=configuration,
                                                     communication_layer=comm_layer,
                                                     clock=clock)
        await agent_mgr.start()
        agent_managers[agent_mgr.identifier] = agent_mgr

    global simulator_handler

    simulator_handler = SimulatorHandler(clock, manager_environment)


async def setup_real_environment(loaded_manager_configuration):
    agent_mgr = RealEnvironmentAgentManager(loaded_manager_configuration)
    await agent_mgr.start()
    agent_managers[agent_mgr.identifier] = agent_mgr


def setup_routes():
    get_routes = {
        r'/': index, r'/{identifier:\d+}': index,
        r'/about': about, r'/{identifier:\d+}/about': about,
        r'/monitor_logs': monitor_logs, r'/{identifier:\d+}/monitor_logs': monitor_logs,
        r'/list_agents': list_agents, r'/{identifier:\d+}/list_agents': list_agents,
        r'/policy_repository': policy_repository,
        r'/{identifier:\d+}/policy_repository': policy_repository,
        r'/loaded_touchpoints': loaded_touchpoints,
        r'/{identifier:\d+}/loaded_touchpoints': loaded_touchpoints,
        r'/agents/{agent_id}': agents_status,
        r'/{identifier:\d+}/agents/{agent_id}': agents_status,
        r'/agents': missing_agent_id, r'/{identifier:\d+}/agents': missing_agent_id
    }

    put_routes = {
        r'/agents/{agent_id}/relationship': update_agents_relationship,
        r'/{identifier:\d+}/agents/{agent_id}/relationship': update_agents_relationship,
        r'/agents/{agent_id}/policy': update_policy,
        r'/{identifier:\d+}/agents/{agent_id}/policy': update_policy,
        r'/agents': missing_agent_id, r'/{identifier:\d+}/agents': missing_agent_id
    }

    post_routes = {
        r'/agents': spawn_agent,
        r'/{identifier:\d+}/agents': spawn_agent
    }

    delete_routes = {
        r'/agents/{agent_id}': terminate_agent,
        r'/{identifier:\d+}/agents/{agent_id}': terminate_agent,
        r'/agents': missing_agent_id, r'/{identifier:\d+}/agents': missing_agent_id
    }

    sim_get_routes = {
        r'/sim': sim_index,
        r'/sim/run': run_simulator,
        r'/sim/status': simulator_status,
        r'/sim/stop': stop_simulator,
        r'/sim/result': simulator_last_result,
        r'/sim/save': save_simulator,
    }

    routes_builder = RoutesBuilder()
    routes_builder.add_get(get_routes)
    routes_builder.add_get(sim_get_routes)
    routes_builder.add_post(post_routes)
    routes_builder.add_put(put_routes)
    routes_builder.add_delete(delete_routes)

    return routes_builder.routes

def main():
    # with open('agent_manager_runner.pid', 'a') as f:
    #     f.write(str(os.getpid()) + '\n')
    logger_setup.set_to_rotate(logger, level=logging.DEBUG,
                               file_name_prefix='agent_manager_runner')

    parsed_args = parse_arguments()

    manager_environment = load_manager_environment(parsed_args.config_file)

    try:
        loop = asyncio.get_event_loop()
        if manager_environment.run_as_simulator:
            logger.info('Running as simulator')
            loop.run_until_complete(setup_simulator_environment(manager_environment))
        else:
            loop.run_until_complete(setup_real_environment(manager_environment.configuration))

        async def cleanup(_):
            for agent_manager in agent_managers.values():
                await agent_manager.cleanup()

        routes = setup_routes()

        run_server(parsed_args.port, routes, cleanup=cleanup)
        logger.info('rest service has stopped')

    except AgentManagerCreationError as creation_error:
        remove_logger_files(logger)
        logger.error(str(creation_error))
        sys.exit(str(creation_error))


if __name__ == '__main__':
    main()
