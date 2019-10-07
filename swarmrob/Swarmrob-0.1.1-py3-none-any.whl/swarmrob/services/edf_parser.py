#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018,2019 Aljoscha Pörtner
# Copyright 2019 André Kirsch
# This file is part of SwarmRob.
#
# SwarmRob is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SwarmRob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SwarmRob.  If not, see <https://www.gnu.org/licenses/>.

import sys
from parse import *

import jsonpickle
import yaml
import yaml.scanner

from ..logger import local_logger
from ..utils.errors import CompositionException
from . import service_composition
from . import service


def load_edf(path_to_edf):
    """
        Loads an Experiment Definition File (EDF) and returns it as an object
    :param path_to_edf: The URL of the EDF
    :return: Parsed EDF as Object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.debug("Load EDF: %s", path_to_edf)
    file_stream = open(str(path_to_edf), 'r')
    edf_object = yaml.safe_load_all(file_stream)
    return edf_object, file_stream


def create_service_composition_from_edf(path_to_edf):
    """
        Creates a service composition based on a EDF
    :param path_to_edf: The URL of the EDF
    :return: Parsed EDF as service composition object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    service_composition_obj = service_composition.ServiceComposition()
    try:
        edf_object, file_stream = load_edf(path_to_edf)
    except IOError:
        llogger.error("Unable to load compose file: %s", path_to_edf)
        return service_composition_obj
    try:
        for edf_dict in edf_object:
            for key, value in list(edf_dict.items()):
                service_composition_obj = composition_options[key](value, service_composition_obj)
        llogger.debug("Parsed Service Composition %s", jsonpickle.encode(service_composition_obj))
        file_stream.close()
    except yaml.scanner.ScannerError:
        llogger.error("Unable to load compose file: %s", path_to_edf)
        file_stream.close()
        raise CompositionException("Malformed EDF file")
    return service_composition_obj


def parse_compose_services(services, service_composition_obj):
    """
        Parse services of EDF
    :param services: Services of the EDF
    :param service_composition_obj: Current service composition object
    :return: Updated service composition object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    # Level1 - Servicenames
    llogger.debug("Composition Services: %s", list(services.keys()))
    for key_service_name, value_service_name in list(dict(services).items()):
        service_composition_obj = parse_single_service(service_composition_obj, key_service_name, value_service_name)
    return service_composition_obj


def parse_single_service(service_composition_obj, key_service_name, value_service_name):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.debug("Key of service name: %s --> Value of service name: %s", key_service_name, value_service_name)
    docker_service = service.Service()
    docker_service._id = key_service_name
    # Level2 - Image, Environment, ...
    for property_key, property_value in list(dict(value_service_name).items()):
        docker_service = parse_service_property(docker_service, property_key, property_value)
    service_composition_obj.add_service(key_service_name, docker_service)
    llogger.debug("%i Services added to composition", len(service_composition_obj._services))
    llogger.debug("\n" + service_composition_obj.format_service_composition_as_table())
    return service_composition_obj


def parse_service_property(srv, property_key, property_value):
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.debug("Key of property name: %s --> Value of property name: %s", property_key, property_value)
    try:
        docker_service_singleton = property_options[property_key](property_value, srv)
        llogger.debug("Parsed Service: %s", jsonpickle.encode(docker_service_singleton))
    except KeyError:
        llogger.debug("Key is not supported: %s", property_key)
    return srv


def parse_edf_version(version_value, srv_composition):
    """
        Parse version of EDF
    :param version_value: Value of the Version Field
    :param srv_composition: Current service composition object
    :return: Updated service composition object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    srv_composition._version = version_value
    return srv_composition


def parse_service_env(env_set, srv):
    """
        Parse environment variables of the service
    :param env_set: Set of environment variables
    :param srv: Current single service of the EDF
    :return: Updated service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    for env in env_set:
        parsed_env = parse("{env.name}={env.value}", env)
        srv.add_env(parsed_env['env.name'], parsed_env['env.value'])
        llogger.debug("Parsed Environment Variable: %s=%s", parsed_env['env.name'], parsed_env['env.value'])
    return srv


def parse_service_cdf(cdf_tag, srv):
    """
        Parse CDF tag of the service
    :param cdf_tag: Tag of the CDF
    :param srv: Current single service of the EDF
    :return: Updated service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    llogger.debug("Parsed Image Tag: %s", cdf_tag)
    srv._tag = cdf_tag
    return srv


def parse_service_deploy(deployment_conf, srv):
    """
        Parse deployment configuration of the service (Not used)
    :param deployment_conf:  Deployment configuration of the service
    :param srv: Current single service of the EDF
    :return: Update service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    return srv


def parse_service_depends_on(dependency_conf_set, srv):
    """
        Parse dependencies of the service
    :param dependency_conf_set: Dependency configuration of the service
    :param srv: Current service object
    :return: Updated service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    for dependency_conf in dependency_conf_set:
        srv.add_dependency(dependency_conf)
    return srv


def parse_service_devices(device_conf_set, srv):
    """
        Parse devices of service
    :param device_conf_set: Device configuration of service
    :param srv: Current service object
    :return: Updated service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    for device_conf in device_conf_set:
        parsed_device_conf = parse("{device.source}:{device.dest}", device_conf)
        srv.add_device(parsed_device_conf['device.source'], parsed_device_conf['device.dest'])
        llogger.debug("Parsed Devices: %s:%s", parsed_device_conf['device.source'],
                      parsed_device_conf['device.dest'])
    return srv


def parse_service_volumes(volume_conf_set, srv):
    """
        Parse volumes of the service
    :param volume_conf_set:  Volume configuration of service
    :param srv: Current service object
    :return: Updated service object
    """
    llogger = local_logger.LocalLogger()
    llogger.log_call(sys._getframe().f_code.co_name)
    for volume_conf in volume_conf_set:
        parsed_volume_conf = parse("{volume.source}:{volume.dest}", volume_conf)
        srv.add_volume(parsed_volume_conf['volume.source'], parsed_volume_conf['volume.dest'])
        llogger.debug("Parsed Volumes: %s:%s", parsed_volume_conf['volume.source'],
                      parsed_volume_conf['volume.dest'])
    return srv


property_options = {"environment": parse_service_env,
                    "image": parse_service_cdf,
                    "deploy": parse_service_deploy,
                    "depends_on": parse_service_depends_on,
                    "devices": parse_service_devices,
                    "volumes": parse_service_volumes
                    }

composition_options = {"services": parse_compose_services,
                       "version": parse_edf_version,
                       }
