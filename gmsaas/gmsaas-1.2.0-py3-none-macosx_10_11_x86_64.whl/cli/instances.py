# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Cli for subcommand instance
"""

import click

from tabulate import tabulate

from gmsaas.model.instanceinfo import InstanceInfo, InstanceState, TunnelState, DEFAULT_ADB_SERIAL
from gmsaas.errors import (
    AdbTunnelBusyPortError,
    AdbTunnelGenericError,
    AdbTunnelRunningOnDifferentPortError,
    AdbTunnelInstanceNotReadyError,
)
from .checks import credentials_required, adb_tools_required
from ..saas import get_client, authcache
from ..adbtunnel import get_adb_tunnel
from ..logger import LOGGER, echo_info

INSTANCES_TABLE_HEADERS = ["UUID", "NAME", "ADB SERIAL", "STATE"]
UUID_HEADER_INDEX = INSTANCES_TABLE_HEADERS.index("UUID")
NAME_HEADER_INDEX = INSTANCES_TABLE_HEADERS.index("NAME")


def _merge_instances(platform_instances, tunnel_instances):
    """
    Merge info coming from both platform and adbtunnel, they both share the same `uuid`.
    """
    merge_instances = platform_instances.copy()

    for _, instance in merge_instances.items():
        if instance.uuid in tunnel_instances:
            instance.adb_serial = tunnel_instances[instance.uuid].adb_serial
            if not instance.adb_serial:
                instance.adb_serial = DEFAULT_ADB_SERIAL
            instance.tunnel_state = tunnel_instances[instance.uuid].tunnel_state
        LOGGER.debug(instance)
    return merge_instances


@click.group()
def instances():
    """
    Manage your Genymotion Cloud SaaS instances
    """


@click.command("start")
@click.argument("RECIPE_UUID", type=click.UUID)
@click.argument("INSTANCE_NAME")
@click.option(
    "--stop-when-inactive",
    type=click.BOOL,
    is_flag=True,
    help="Automatically stop the instance after long inactivity period",
)
@click.option("--no-wait", type=click.BOOL, is_flag=True, help="Do not wait for the instance to be fully started")
@click.pass_context
@credentials_required
def start_disposable_instance(ctx, recipe_uuid, instance_name, stop_when_inactive, no_wait):
    """
    Start a disposable instance from a recipe
    """
    del ctx
    saas = _get_api_client()

    instance_uuid = saas.start_disposable_instance(recipe_uuid, instance_name, bool(stop_when_inactive), no_wait)
    LOGGER.debug("[%s] Instance started", instance_uuid)
    echo_info(instance_uuid)


@click.command("stop")
@click.argument("INSTANCE_UUID", type=click.UUID)
@click.option("--no-wait", type=click.BOOL, is_flag=True, help="Do not wait for the instance to be fully stopped")
@click.pass_context
@credentials_required
@adb_tools_required
def stop_disposable_instance(ctx, instance_uuid, no_wait):
    """
    Stop a running disposable instance
    """
    del ctx
    instance_uuid = str(instance_uuid)
    adb_tunnel = get_adb_tunnel()
    adb_tunnel.disconnect(instance_uuid)
    tunnel_state = adb_tunnel.wait_for_adb_disconnected(instance_uuid)
    if tunnel_state != TunnelState.DISCONNECTED:
        LOGGER.error("[%s] Instance can't be disconnected from ADB tunnel", instance_uuid)
    saas = _get_api_client()
    saas.stop_disposable_instance(instance_uuid, no_wait)
    LOGGER.debug("[%s] Instance is stopping", instance_uuid)


@click.command("list")
@click.option("--quiet", "-q", is_flag=True, help="Only display running instance UUIDs")
@click.pass_context
@credentials_required
@adb_tools_required
def list_instances(ctx, quiet):
    """
    List all currently running instances
    """
    del ctx
    saas = _get_api_client()
    adb_tunnel = get_adb_tunnel()
    platform_instances = saas.get_instances()
    tunnel_instances = adb_tunnel.get_instances()
    instances_dict = _merge_instances(platform_instances, tunnel_instances)
    LOGGER.debug("%d Instances available", len(instances_dict))
    instances_table = _format_instances(instances_dict)
    instances_table = _sort_instances_table(instances_table)
    if quiet:
        if instances_table:
            click.echo("\n".join([x[UUID_HEADER_INDEX] for x in instances_table]))
    else:
        click.echo(tabulate(instances_table, headers=INSTANCES_TABLE_HEADERS, numalign="left"))


def _sort_instances_table(instances_table):
    # Instances are sorted by NAME
    return sorted(instances_table, key=lambda x: x[NAME_HEADER_INDEX])


def _format_instances(instances_dict):
    """
    Format the list of Instances into a readable table
    """
    formated_instances = [[i.uuid, i.name, i.adb_serial, i.state] for _, i in instances_dict.items()]
    return formated_instances


@click.command("adbconnect")
@click.option("--adb-serial-port", type=click.IntRange(1024, 65535))
@click.argument("INSTANCE_UUID", type=click.UUID)
@click.pass_context
@credentials_required
@adb_tools_required
def connect_instance_to_adb(ctx, instance_uuid, adb_serial_port):
    """
    Connect a running instance to adb
    """
    del ctx
    instance_uuid = str(instance_uuid)

    saas = _get_api_client()
    adb_tunnel = get_adb_tunnel()
    platform_instances = saas.get_instances()
    tunnel_instances = adb_tunnel.get_instances()
    instance = _merge_instances(platform_instances, tunnel_instances).get(
        instance_uuid, InstanceInfo(uuid=instance_uuid)
    )

    if instance.state != InstanceState.ONLINE:
        # Instance should be started in order to connect ADB
        raise AdbTunnelInstanceNotReadyError(instance_uuid, instance.state)

    running_port = instance.get_port()
    if running_port:
        # ADB Tunnel is already running for this instance
        # If it's on the same port: early return
        # Else raise an error
        if running_port == str(adb_serial_port) or not adb_serial_port:
            LOGGER.info("[%s] Instance already connected to ADB tunnel", instance_uuid)
            return
        raise AdbTunnelRunningOnDifferentPortError(instance_uuid, running_port, adb_serial_port)

    adb_tunnel.connect(instance_uuid, adb_serial_port)
    tunnel_state = adb_tunnel.wait_for_adb_connected(instance_uuid)

    if tunnel_state == TunnelState.CONNECTED:
        LOGGER.info("[%s] Instance connected to ADB tunnel", instance_uuid)
        return
    elif tunnel_state == TunnelState.PORT_BUSY:
        raise AdbTunnelBusyPortError(instance_uuid, adb_serial_port)
    raise AdbTunnelGenericError(instance_uuid)


@click.command("adbdisconnect")
@click.argument("INSTANCE_UUID", type=click.UUID)
@click.pass_context
@credentials_required
@adb_tools_required
def disconnect_instance_from_adb(ctx, instance_uuid):
    """
    Disconnect a running instance from adb
    """
    del ctx
    instance_uuid = str(instance_uuid)
    adb_tunnel = get_adb_tunnel()
    adb_tunnel.disconnect(instance_uuid)
    tunnel_state = adb_tunnel.wait_for_adb_disconnected(instance_uuid)

    if tunnel_state == TunnelState.DISCONNECTED:
        LOGGER.info("[%s] Instance disconnected from ADB tunnel", instance_uuid)
        return
    raise AdbTunnelGenericError(instance_uuid)


def _get_api_client():
    """
    Get the Genymotion Cloud SaaS API client
    """
    return get_client(authcache.get_email(), authcache.get_password())


instances.add_command(start_disposable_instance)
instances.add_command(stop_disposable_instance)
instances.add_command(list_instances)
instances.add_command(connect_instance_to_adb)
instances.add_command(disconnect_instance_from_adb)
