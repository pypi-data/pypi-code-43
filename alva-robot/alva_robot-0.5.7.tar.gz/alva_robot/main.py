# coding=utf8

__author__ = 'Alexander.Li'

import sys
import os
import click
from .functions import generator_impl, keypair
from .server import start


def command(f):
    cli.add_command(f)
    return f


@click.group()
def cli():
    pass

@command
@click.command()
@click.argument('name')
def init(name):
    url = generator_impl(name)
    click.echo("config url:\n%s" % url)

@command
@click.command()
def gen():
    pair = keypair()
    click.echo('public key:\n%s\n' % pair.publicKey)
    click.echo('private key:\n%s\n' % pair.privateKey)

@command
@click.command()
@click.argument('mod_path')
@click.option('-w', '--workers')
def serv(mod_path, workers):
    full_path = os.path.abspath(mod_path)
    seqs = full_path.split(os.sep)
    dir_path = os.sep.join(seqs[:-1])
    mod_name = seqs[-1].split('.')[0]
    sys.path.append(dir_path)
    __import__(mod_name)
    #print("dir:%s mod:%s" % (dir_path, mod_name))
    if workers:
        start(workers=int(workers))
    else:
        start()


def main():
    cli()

