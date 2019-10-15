# Unofficial NonameDomain API CLI tool
# Copyright (C) 2019 Slacker

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pynonamedomain
import requests
import tldextract
import click
import json
import ast
import os
import time

VERSION = "1.0.2"

@click.group()
def cli():
    """ Unofficial CLI tool for NonameDomain.hu """

def __create_nnd_object(domain, api_user = None, api_pw = None, token = None):
    domain_extractor = tldextract.TLDExtract(cache_file = False)
    registered_domain = domain_extractor(domain).registered_domain
    try:
        if token:
            nnd = pynonamedomain.NonameDomain(domain = registered_domain, token = token)
        elif api_user and api_pw:
            nnd = pynonamedomain.NonameDomain(domain = registered_domain, api_user = api_user, api_pw = api_pw)
    except ValueError:
        raise click.ClickException("Please provide a username and password")
    except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as e:
        raise click.ClickException(str(e))
    return nnd

def __syntax_check(**kwargs):
    if kwargs["record"]:
        try:
            record = ast.literal_eval(kwargs["record"])
        except SyntaxError:
            raise click.ClickException(f"{kwargs['record']} is not a valid JSON.")
        return record

@cli.command()
@click.option("-d", "--domain", envvar = ["NND_DOMAIN", "CERTBOT_DOMAIN"], required = True, prompt = True, help = "Domain to use. [env: NND_DOMAIN]")
@click.option("-u", "--username", envvar = "NND_USERNAME", required = True, prompt = True, help = "API user's username. [env: NND_USERNAME]")
@click.password_option("-p", "--password", envvar = "NND_PASSWORD", required = True, confirmation_prompt= False, help = "API user's password. [env: NND_PASSWORD]")
@click.option("-q", "--quiet", is_flag = True, help = "Only print out the authentication token.")
def login(domain, username, password, quiet):
    """ Aquire API token. """
    nnd = __create_nnd_object(domain, api_user = username, api_pw = password)
    click.echo(f"{'Your authentication token is: ' if not quiet else ''}{nnd.token}")

@cli.command()
@click.option("-d", "--domain", envvar = ["NND_DOMAIN", "CERTBOT_DOMAIN"], required = True, prompt = True, help = "Domain to use. Not needed for --certbot. [env: NND_DOMAIN]")
@click.option("-t", "--token", envvar = "NND_TOKEN", required = True, prompt = True, help = "Authentication token to be used. [env: NND_TOKEN]")
@click.option("-q", "--quiet", is_flag = True, help = "Only print the hash of the new record.")
@click.option("-c", "--certbot", is_flag = True, help = "For using with certbot. Implies -q. Has 30sec sleep for DNS propagation.")
@click.option("-r", "--record", help = "Data of new record in JSON format. Not needed for --certbot.")
def create(certbot, quiet, **kwargs):
    """ Create new entry in the zone. """
    domain = kwargs.pop("domain", None)
    token = kwargs.pop("token", None)
    if certbot:
        record = dict()
        record["type"] = "TXT"
        record["host"] = "_acme-challenge"
        try:
            record["text"] = os.environ["CERTBOT_VALIDATION"]
        except KeyError:
            raise click.ClickException("'CERTBOT_VALIDATION' environmental variable is needed for certbot mode.")
        record["ttl"] = "60"
    else:
        record = __syntax_check(**kwargs)
    nnd = __create_nnd_object(domain, token = token)
    try:
        record_hash = nnd.create(**record)
        if certbot:
            time.sleep(30)
        click.echo(f"{'The new record is successfully created. Its unique hash is: ' if not certbot and not quiet else ''}{record_hash}")
    except pynonamedomain.SubdomainAlreadyExists:
        raise click.ClickException("An identical subdomain already exists.")

@cli.command()
@click.option("-d", "--domain", envvar = "NND_DOMAIN", required = True, prompt = True, help = "Domain to use. [env: NND_DOMAIN]")
@click.option("-t", "--token", envvar = "NND_TOKEN", required = True, prompt = True, help = "Authentication token to be used. [env: NND_TOKEN]")
@click.option("-q", "--quiet", is_flag = True, help = "Print only hashes.")
@click.option("-o", "--output", type=click.Choice(["json", "csv"]), default = "json", show_default = True, help = "Output format.")
@click.option("-r", "--record", help = "Data of record in JSON format. Omit to return all records. Not needed for --certbot.")
def read(quiet, output, **kwargs):
    """ Read/find DNS entries in the zone. """
    domain = kwargs.pop("domain", None)
    token = kwargs.pop("token", None)
    record = __syntax_check(**kwargs)
    nnd = __create_nnd_object(domain, token = token)
    try:
        if not record:
            found = nnd.read(cached = False)
        else:
            found = nnd.read(cached = False, **record)
        if not quiet:
            if output == "json":
                click.echo(json.dumps(found))
            elif output == "csv":
                for record in found:
                    for value in record.values():
                        click.echo(f"{value};", nl = False)
                    click.echo()
        else:
            for record in found:
                click.echo(record["hash"])
    except pynonamedomain.SubdomainNotFound:
        raise click.ClickException("Subdomain not found.")

@cli.command()
@click.option("-d", "--domain", envvar = "NND_DOMAIN", required = True, prompt = True, help = "Domain to use. [env: NND_DOMAIN]")
@click.option("-t", "--token", envvar = "NND_TOKEN", required = True, prompt = True, help = "Authentication token to be used. [env: NND_TOKEN]")
@click.option("-q", "--quiet", is_flag = True, help = "Suppress output.")
@click.option("-h", "--hash", "record_hash", envvar = "CERTBOT_AUTH_OUTPUT", required = True, help = "Hash of record to be removed.")
def remove(quiet, domain, token, record_hash):
    """ Remove DNS entry from the zone. """
    nnd = __create_nnd_object(domain, token = token)
    try:
        nnd.remove(record_hash)
    except pynonamedomain.SubdomainNotFound:
        raise click.ClickException("Subdomain not found.")
    except (requests.HTTPError, requests.SSLError) as e:
        raise click.ClickException(str(e))
    if not quiet:
        click.echo(f"The record with hash '{record_hash}' has been successfully removed.")

@cli.command()
@click.option("-d", "--domain", envvar = "NND_DOMAIN", required = True, prompt = True, help = "Domain to use. [env: NND_DOMAIN]")
@click.option("-t", "--token", envvar = "NND_TOKEN", required = True, prompt = True, help = "Authentication token to be used. [env: NND_TOKEN]")
@click.option("-q", "--quiet", is_flag = True, help = "Print only the new hash.")
@click.option("-o", "--output", type=click.Choice(["json", "csv"]), default = "json", show_default = True, help = "Output format.")
@click.option("-h", "--hash", "record_hash", required = True, help = "Hash of record to be updated.")
@click.option("-r", "--record", required = True, help = "The delta of the current state and desired state in JSON format.")
def update(quiet, output, domain, token, record_hash, record):
    """ Update DNS entry in the zone. """
    new_values = ast.literal_eval(record)
    nnd = __create_nnd_object(domain, token = token)
    new_record = nnd.update(record_hash, new_values)
    if not quiet:
        if output == "json":
            click.echo(json.dumps(new_record))
        elif output == "csv":
            for value in new_record.values():
                click.echo(f"{value};", nl = False)
            click.echo()
    else:
        click.echo(new_record["hash"])

@cli.command()
def version():
    """ Version info. """
    LICENSE = "Copyright (C) 2019 Slacker\nThis program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute it under certain conditions."
    click.echo(f"nnd-cli {VERSION}\n{LICENSE}")
