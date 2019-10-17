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
Cli for subcommand auth
"""

import click

from gmsaas.logger import echo_info
from gmsaas.saas import get_client, authcache
from gmsaas.adbtunnel import get_adb_tunnel


def _logout():
    adbtunnel = get_adb_tunnel()
    if adbtunnel.is_ready():
        adbtunnel.stop()
    authcache.clear()


@click.group()
def auth():
    """
    Manage your Genymotion Cloud SaaS credentials
    """
    pass


@click.command(
    "login",
    short_help="Allows you to input your Genymotion Cloud SaaS credentials, ensure their validity, and store them",
)
@click.argument("email")
@click.argument("password", required=False)
def auth_login(email, password):
    """
    Allows you to input your Genymotion Cloud SaaS credentials, ensure their validity, and store them
    """
    # Note: `short_help` makes help text not being truncated to 45 char, don't remove it.
    if not password:
        password = click.prompt("Password", type=click.STRING, hide_input=True)

    if authcache.get_jwt():
        echo_info("Logged out.")
    _logout()

    client = get_client(email, password)
    jwt = client.login()

    authcache.set_email(email)
    authcache.set_password(password)
    authcache.set_jwt(jwt)

    echo_info("User {} is logged in.\n" "Credentials saved to file: [{}]".format(email, authcache.get_path()))


@click.command("whoami")
def auth_whoami():
    """
    Display credentials currently in use
    """
    email = authcache.get_email()
    if email:
        echo_info(email)
    else:
        echo_info("No credentials found. To set them up, use `gmsaas auth login` command.")


@click.command("logout")
def auth_logout():
    """
    Remove stored credentials and clean up
    """
    _logout()
    echo_info("Logged out.")


auth.add_command(auth_login)
auth.add_command(auth_whoami)
auth.add_command(auth_logout)
