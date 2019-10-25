# -*- coding: utf-8 -*-

from __future__ import print_function

from PyInquirer import style_from_dict, Token, prompt, Separator

from examples import custom_style_1,custom_style_2

from pyfiglet import figlet_format
from colorama import Fore, Back, Style,init
import click, codecs, os.path, re, time
from .utils import printProgressBar, find_version
from .login import login
# from art import *
import os
from colorama import init


#colorama init
init()

# welcomeInfo=text2art("Breeze CLI") 
# print(Fore.BLUE + welcomeInfo)

print(Fore.BLUE + figlet_format("Breeze CLI"))
print(Style.RESET_ALL)


version = find_version("../breezecli", "__init__.py")
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--host',help='Login host... E.g crm.xiaoshouyi.com')
@click.option('--email',help='Login email... E.g test@126.com')
@click.password_option('--password',prompt=False,help='Login password... E.g 123456')
# @click.option('--tenants',prompt=False,help='Which tenants to login E.g tenant1,tenant2')
@click.version_option(message="breeze-cli/%s"%version)
@click.pass_context
def cli(ctx, host, email, password):
    """
    Breeze CLI to help you eailsy operate breeze data...
    """
    ctx.obj = {}
    ctx.obj["host"] = host
    ctx.obj["email"] = email
    ctx.obj["password"] = password

@cli.command()
@click.option('--meta_path',required=True, type=str, help='Provide local meta folder to upload')
@click.pass_context
def upload_meta(ctx,meta_path):
    """
    Upload meta to CFS
    """
    if all([ctx.obj["host"],ctx.obj["email"],ctx.obj["password"]]):
        selectedTenants = tenants_choose_prompt_handle(ctx.obj["host"],ctx.obj["email"],ctx.obj["password"])
    else:
        click.echo(click.style('Need complete auth information:', fg='yellow'))
        selectedTenants = login_prompt_handle()
    # isUpload = YesNo("Confirm upload meta files to %s?"%selectedTenant).launch()
    confrmUpload = [
        {
            'type': 'confirm',
            'message': 'Please confirm to upload?',
            'name': 'confirm',
            'default': True,
        }
    ]

    isUpload = prompt(confrmUpload, style=custom_style_2)
    if isUpload['confirm']:
        for tenant in selectedTenants:
            click.echo(click.style('Uploading meta files to tenant---%s'%tenant, fg='yellow'))

            # A List of Items
            fileList = ["test1.json","form.json","bar.json"]
            for file in fileList:
                items = list(range(0, 10))
                l = len(items)

                # Initial call to print 0% progress
                printProgressBar(0, l, prefix = 'Upload %s:'%file, suffix = 'Complete', length = 50)
                for i, item in enumerate(items):
                    # Do stuff...
                    time.sleep(0.1)
                    # Update Progress Bar
                    printProgressBar(i + 1, l, prefix = 'Upload %s:'%file, suffix = 'Complete', length = 50)

            click.echo(click.style('Totally uploaded %s meta files to tenant---%s'%(len(fileList),tenant), fg='green'))

@cli.command()
@click.option('--store_path', type=str, help='Provide local path for storing the downloaded meta files')
@click.pass_context
def download_meta(ctx,store_path):
    """
    Download meta from CFS
    """
    print("xxx")
    print(store_path)
 

def login_prompt_handle():
    host = click.prompt('Enter env host name', default="crm.xiaoshouyi.com",type=str)
    email = click.prompt('Enter email/username', type=str)
    password = click.prompt('Enter password', confirmation_prompt=True, hide_input=True,type=str),
    return tenants_choose_prompt_handle(host,email,password)

def tenants_choose_prompt_handle(host,email,password):
    tenantsList = login(host,email,password)
    if tenantsList:
        while 1:
            tenantListChoicesList = [
                {
                    'type': 'checkbox',
                    'qmark': '?',
                    'message': 'Choose tenant to upload?',
                    'name': 'name',
                    'choices': tenantsList,
                    'validate': lambda selectedTenants: 'You must choose at least one tenant.' \
                        if len(selectedTenants) == 0 else True
                }
            ]
            selectedTenants = prompt(tenantListChoicesList, style=custom_style_2)
            if selectedTenants["name"]:
                break
        return selectedTenants["name"]
    else:
        click.echo(click.style('Wrong auth information, please use correct auth information to upload', fg='red'))
        os._exit(0)

if __name__ == "__main__":
    cli()
  