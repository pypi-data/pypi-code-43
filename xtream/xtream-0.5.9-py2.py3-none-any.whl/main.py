# coding: utf-8
import click
import math
import time
import random
import platform
from nstream.os import *

version_info="0.0.1"
try:
    range_type = xrange
except NameError:
    range_type = range

c_platform=None
runner=None
pass_runner = click.make_pass_decorator(OSBase)

@click.group()
@click.pass_context
def cli(ctx):
  c_platform=platform.system()
  if c_platform=="Windows":
    c_version=platform.platform().split("-")[1]
    ctx.obj=WindowsDeployer(c_version)
  if c_platform=="Linux":
    linux_distribution=platform.linux_distribution()
    c_dist=linux_distribution[0]
    c_version=linux_distribution[1]
    if c_dist=="Ubuntu":
      ctx.obj=UbuntuDeployer(c_version)
    if c_dist=="CentOS Linux":
      ctx.obj=CentosDeployer(c_version)
  pass

@cli.command()
@click.option('--app', default="db", type=str,
              help='install an nstream module. options are db,lb,store')
def install(app):
  """Install an nstream module.  options are db,lb,store"""
  click.echo(app)



@cli.command()
@click.option('--app', default="db", type=str,
              help='start an nstream module. options are db,lb,store')
def start(app):
  """Start an nstream module.  options are db,lb,store"""
  click.echo(app)

@cli.command()
@click.option('--app', default="db", type=str,
              help='stop an nstream module. options are db,lb,store')
def stop(app):
  """Stop an nstream module.  options are db,lb,store"""
  click.echo(app)


@cli.command()
@pass_runner
def init(runner):
  """Initialize an nstream server."""
  runner.initialize()


@cli.command()
def version():
  """display version information"""
  click.echo("nstream commandline utility "+version_info)

@cli.command()
@click.argument('option')
def license(option):
    """nstream license utility. options are verify,request,validate"""
    click.echo(option)

  
@cli.command()
def clear():
    """Clears the entire screen."""
    click.clear()


@cli.command()
def pause():
    """Waits for the user to press a button."""
    click.pause()


#@cli.command()
#def menu():
#    """nstream menu setup"""
#    menu = 'main'
#    while 1:
#        if menu == 'main':
#            click.echo('Main menu:')
#            click.echo('  d: debug menu')
#            click.echo('  q: quit')
#            char = click.getchar()
#            if char == 'd':
#                menu = 'debug'
#            elif char == 'q':
#                menu = 'quit'
#            else:
#                click.echo('Invalid input')
#        elif menu == 'debug':
#            click.echo('Debug menu')
#            click.echo('  b: back')
#            char = click.getchar()
#            if char == 'b':
#                menu = 'main'
#            else:
#                click.echo('Invalid input')
#        elif menu == 'quit':
#            return



def main():
  cli()


if __name__=="__main__":
  cli()
  