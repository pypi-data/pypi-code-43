import importlib
import logging
import pathlib
from typing import Dict
from collections import namedtuple

import simplejson as json

from arps.core.environment import Environment
from arps.core.simulator.event_queue_loader import (EventQueueLoader,
                                                    FileEventQueueLoader,
                                                    RandomEventQueueLoader)
from arps.core.policies.monitor import build_monitor_policy_class, MonitorType
from arps.core.resources_table import ResourcesTable, ResourcesCategories
from arps.core.simulator.estimators_table import EstimatorsTable


class InvalidConfigurationError(Exception):
    '''
    General exception to be used when something unexpected is encountered by the parser
    '''

logger = logging.getLogger('ConfigurationFileLoader')


def load_manager_environment(conf_file_path):
    with open(conf_file_path) as conf_path:
        parsed_configuration = json.loads(conf_path.read())

        run_as_simulator = parsed_configuration['run_as_simulator']
        if not run_as_simulator:
            RealManagerEnvironment = namedtuple('RealManagerEnvironment',
                                                ['run_as_simulator', 'configuration'])
            return RealManagerEnvironment(run_as_simulator,
                                          _load_real_environment(parsed_configuration))


        resources_file = pathlib.Path(*parsed_configuration['resources_available'])
        resources_classes = load_resources_classes(resources_file)

        touchpoints_file = pathlib.Path(*parsed_configuration['touchpoints_available'])
        touchpoints_classes = load_touchpoints_classes(touchpoints_file)

        policies_file = pathlib.Path(*parsed_configuration['policies_available'])
        policies_classes = load_policies_classes(policies_file)

        resources_table = ResourcesTable()
        for manager in parsed_configuration['environments']:
            load_resources_table(manager['identifier'], resources_table,
                                 resources_classes, manager['resources'])

        loaded_managers = [_load_sim_environment(resources_table,
                                                 touchpoints_classes,
                                                 policies_classes,
                                                 manager)
                           for manager in parsed_configuration['environments']]

        for manager in parsed_configuration['environments']:
            _create_relationship_between_manager_resources(manager, resources_table)

        simulator_configuration = parsed_configuration['simulator']
        event_queue_loader = load_event_queue_loader(simulator_configuration['event_queue'],
                                                     resources_table)

        simulation_results_path = pathlib.Path(*simulator_configuration['results_path'])
        simulation_log_formatter = simulator_configuration['log_formatter']

        SimulatorManagerEnvironment = namedtuple('SimulatorManagerEnvironment',
                                                 ['run_as_simulator',
                                                  'resources_table',
                                                  'configuration',
                                                  'event_queue_loader',
                                                  'results_path',
                                                  'log_formatter',
                                                  'pmt'])

        return SimulatorManagerEnvironment(run_as_simulator,
                                           resources_table,
                                           loaded_managers,
                                           event_queue_loader,
                                           simulation_results_path,
                                           simulation_log_formatter,
                                           parsed_configuration.get('pmt'))

def _create_relationship_between_manager_resources(manager, resources_table: ResourcesTable):
    '''
    Used for simulation only.

    Create a relationship between affected resource and resource that indirect affects.

    A resource can affect and be affected by many other resources.

    Args:
    - manager: Manager with information needed to create the relationship between resources
    - resources_table: Resources table containing resources from each environment and organized by their categories
    '''
    for affecting_resource in manager['resources']:
        affected_identifier = affecting_resource.get('affects', None)
        if not affected_identifier:
            continue

        for affected_manager_id, affected_resources_id in affected_identifier.items():
            for affected_resource_id in affected_resources_id:
                resources_categories = resources_table.categories(environment=manager['identifier'])
                resource_instance_affecting = resources_categories.resource_by_identifier(affecting_resource['id'])

                resources_categories = resources_table.categories(environment=int(affected_manager_id))
                resource_instance_affected = resources_categories.resource_by_identifier(affected_resource_id)

                resource_instance_affecting.affects(resource_instance_affected)

def _load_real_environment(configuration):
    ManagerConfiguration = namedtuple('ManagerConfiguration',
                                      ['identifier', 'agent_config',
                                       'agents_directory', 'pmt', 'comm_layer_type'])

    return ManagerConfiguration(configuration['identifier'],
                                pathlib.Path(*configuration['agent_config']),
                                configuration['agents_directory'],
                                configuration.get('pmt'),
                                configuration['comm_layer'])

def _load_sim_environment(resources_table: ResourcesTable,
                          touchpoints_classes,
                          policies_classes,
                          environment: Dict):
    ManagerConfiguration = namedtuple('ManagerConfiguration',
                                      ['identifier', 'agent_environment'])

    identifier = environment['identifier']

    agent_environment = _load_agent_environment(identifier,
                                                touchpoints_classes,
                                                policies_classes,
                                                environment,
                                                resources_table.categories(environment=identifier))


    return ManagerConfiguration(identifier, agent_environment)

def load_resources_classes(resources_file) -> Dict:
    return load_classes_from_file(class_type='resources', file=resources_file)

def load_touchpoints_classes(touchpoints_file) -> Dict:
    return load_classes_from_file(class_type='touchpoints', file=touchpoints_file)

def load_policies_classes(policies_file) -> Dict:
    return load_classes_from_file(class_type='policies', file=policies_file)

def load_classes_from_file(*, class_type : str, file : str) -> Dict:
    '''
    Param:
    - class_type: entry that classifies the class. It can be resources, touchpoints, and policies.
    See conf/dummy_agent.conf and look for key [class_type]_available.
    - file: relative path from the source where the class source code is located

    Returns a dictionary containing class name as key and class type as value
    '''
    with open(file, 'r') as configuration:
        properties = json.loads(configuration.read())
        assert class_type in properties
        base_path = properties['base_path']
        classes_properties = properties[class_type]
        return load_classes(base_path, classes_properties)

def load_classes(base_path, properties) -> Dict:
    '''
    Load classes. Returns a dict containg class name and class

    Args:
    - base_path : path in python format (a.b.c)
    - properties : dict containing a list modules and classes
    '''

    classes = {}
    for prop in properties:
        cls = load_attribute(module_base_path=base_path,
                             module_path=prop['module'],
                             attribute_name=prop['class'])
        classes[cls.__name__] = cls

    return classes

def load_agent_environment(identifier, agent_conf_file : str):
    '''
    Args:
    - identifier: identifier of the environment which the agent is part
    - agent_conf_file: path to the agent configuration file
    '''
    with open(agent_conf_file, 'r') as agent_conf:
        agent_properties = json.loads(agent_conf.read())

        resources_file = pathlib.Path(*agent_properties['resources_available'])
        resources_classes = load_resources_classes(resources_file)

        touchpoints_file = pathlib.Path(*agent_properties['touchpoints_available'])
        touchpoints_classes = load_touchpoints_classes(touchpoints_file)

        policies_file = pathlib.Path(*agent_properties['policies_available'])
        policies_classes = load_policies_classes(policies_file)

        resources_table = ResourcesTable()
        load_resources_table(identifier, resources_table,
                             resources_classes, agent_properties['resources'])

        return _load_agent_environment(identifier,
                                       touchpoints_classes,
                                       policies_classes,
                                       agent_properties,
                                       resources_table.categories(environment=identifier))

def _load_agent_environment(identifier,
                            touchpoints_classes,
                            policies_classes,
                            agent_properties,
                            resources_categories: ResourcesCategories):
    '''
    Load agent environment.
    Create instances of resource classes and link to its sensors and actuators.
    Register policies to be associated with agents

    Args:
    - identifier : agent manager identifier
    - touchpoints_classes : dict containing touchpoint identifier and class
    - policies_classes : dict policies touchpoint identifier and class
    - agent_properties : dict containing sensors, actuators, and policies
    - resources_categories : resources organized by their categories
    '''

    agent_configuration = agent_properties['agent_config']
    sensors = _load_touchpoint_instances(resources_categories,
                                         touchpoints_classes,
                                         agent_configuration['sensors'])
    actuators = _load_touchpoint_instances(resources_categories,
                                           touchpoints_classes,
                                           agent_configuration['actuators'])

    environment = Environment(sensors=sensors, actuators=actuators)

    policies = agent_configuration['policies']
    for policy in policies:
        policy_cls = policies_classes[policy]
        environment.register_policy(policy_cls.__name__, policy_cls)

    for sensor in sensors:
        monitor_sensor_policy_cls = build_monitor_policy_class(f'{sensor.resource_name}MonitorPolicy',
                                                               touchpoint_category=sensor.resource_name,
                                                               monitor_type=MonitorType.Sensor)
        environment.register_policy(monitor_sensor_policy_cls.__name__, monitor_sensor_policy_cls)

    for actuator in actuators:
        monitor_actuator_policy_cls = build_monitor_policy_class(f'{actuator.resource_name}MonitorPolicy',
                                                                 touchpoint_category=actuator.resource_name,
                                                                 monitor_type=MonitorType.Actuator)
        environment.register_policy(monitor_actuator_policy_cls.__name__, monitor_actuator_policy_cls)

    logger.info('loaded resources %s for environment %s', resources_categories, identifier)
    logger.info('loaded sensors %s for environment %s', sensors, identifier)
    logger.info('loaded actuators %s for environment %s', actuators, identifier)
    logger.info('loaded policies %s for environment %s', policies, identifier)

    return environment

def load_resources_table(environment_identifier : int, resources_table : ResourcesTable, resources_classes, resources):
    '''
    Load resources in their categories.

    Args:
    - environment_identifier: environment identifier
    - resources_table : resources classified by their categories in each environment
    - resources_classes : classes available to create new instances based on resources parameter
    - resources : dict file containing resources descriptions. Each resource is composed of:
        - id: unique global identifier of the instance that will be created
        - initial_parameter: initial value of the resource
        - affects: unique global identifier of resource that will be affected by this resource
            * This parameter is used during simulations only
    '''

    for resource in resources:
        resource_identifier = resource['id']

        initial_parameter = resource.get('initial_parameter', None)
        resource_cls = resources_classes[resource['class']]
        if initial_parameter:
            resource_instance = resource_cls(environment_identifier=environment_identifier,
                                             identifier=resource_identifier, **initial_parameter)
        else:
            resource_instance = resource_cls(environment_identifier=environment_identifier,
                                             identifier=resource_identifier)
        resources_table.add_resource(resource_instance)

def load_event_queue_loader(event_queue_properties: Dict,
                            resources_table: ResourcesTable) -> EventQueueLoader:
    '''
    Create loader that will return next simulation event

    Args:

    - event_queue_properties: dict containing module, classes and so on to import correct loader
    and to open the tracefile or the random event generator
    - resources_table: Resources table containing resources from each environment and organized by their categories
    '''
    generator = event_queue_properties['generator']
    event_factory = generator['factory']
    event_factory_cls = load_attribute(module_path=event_factory['module'],
                                       attribute_name=event_factory['class'])

    estimators_table = build_estimators_table(event_queue_properties)

    event_factory_instance = event_factory_cls(resources_table,
                                               estimators_table)

    if not event_queue_properties['deterministic']:
        random_generator = generator['random']
        random_generator_cls = load_attribute(module_path=random_generator['module'],
                                              attribute_name=random_generator['class'])
        number_of_random_events = generator['number_of_random_events']
        return RandomEventQueueLoader(event_factory_instance,
                                      random_generator_cls(),
                                      number_of_random_events)

    event_queue_file = pathlib.Path(*generator['file'])
    return FileEventQueueLoader(event_queue_file,
                                event_factory_instance)


def build_estimators_table(event_queue_properties):
    estimators_table = EstimatorsTable()
    if 'resources_estimator' not in event_queue_properties:
        return estimators_table

    for estimators in event_queue_properties['resources_estimator']:
        environment = estimators['environment']
        for estimator in estimators['estimators']:
            estimator_name = estimator['name']
            module = estimator['module']
            estimator_func_name = estimator['estimator']
            estimator_func = load_attribute(module_path=module,
                                            attribute_name=estimator_func_name)
            estimators_table.add_estimator(environment, estimator_name, estimator_func)
    return estimators_table


def _load_touchpoint_instances(resources_categories: ResourcesCategories,
                               touchpoints_classes, touchpoints_properties):
    touchpoints = list()

    for touchpoint_properties in touchpoints_properties:
        touchpoint_class_name = touchpoint_properties['class']
        resource_id = touchpoint_properties['resource_id']
        touchpoint_class = touchpoints_classes[touchpoint_class_name]
        touchpoint_instance = touchpoint_class(resources_categories.resource_by_identifier(resource_id))
        touchpoints.append(touchpoint_instance)

    return touchpoints

def load_attribute(*, module_base_path: str = '', module_path: str, attribute_name: str):
    '''
    Load attribute from configuration file

    Args:
    - module_path: python syntax module, i.e., "package1.package2.module"
    - attribute_name: attribute to be loaded (class or function)
    '''
    relative_module_base_path = module_base_path.startswith('.') and len(module_base_path) >= 2
    relative_module_path = module_path.startswith('.') and len(module_path) >= 2
    if relative_module_base_path or relative_module_path:
        raise InvalidConfigurationError('Relative import is not allowed')

    if module_base_path == '.':
        module_base_path = ''

    if module_base_path:
        module_path = module_base_path + '.' + module_path

    try:
        logger.info('Loading attribute {} from module {}'.format(attribute_name, module_path))
        module = importlib.import_module(module_path)
        attribute = getattr(module, attribute_name)
    except ImportError as import_error:
        raise InvalidConfigurationError(str(import_error) + ', check if module or attribute name exists')
    except ValueError as value_error:
        raise InvalidConfigurationError(str(value_error) + ', check module')
    except AttributeError as attribute_error:
        raise InvalidConfigurationError(str(attribute_error) + ', check attribute name')

    return attribute
