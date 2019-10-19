#! /usr/bin/env python
# coding: utf-8

#  __author__ = 'meisanggou'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

if sys.version_info <= (2, 7):
    sys.stderr.write("ERROR: jingyun-cli requires Python Version 2.7 or above.\n")
    sys.stderr.write("Your Python Version is %s.%s.%s.\n" % sys.version_info[:3])
    sys.exit(1)

name = "jingyun-cli"
version = "0.5.10"
url = "https://github.com/meisanggou/jingyun"
license = "MIT"
author = "meisanggou"
short_description = "jingyun deploy cli tools"
long_description = """"""
keywords = "jingyun-cli"
install_requires = ["requests", "six", "supervisor", "docker-compose", "mysqldb-rich"]

entry_points = {'console_scripts': [
    'json-merge=jingyun_cli.json.cli:json_merge',
    'jy-json-merge=jingyun_cli.json.cli:json_merge',
    'jy-oss-download=jingyun_cli.oss.cli:multi_download',
    'jy-key=jingyun_cli.key.cli:handle_key',
    'jy-conf-format=jingyun_cli.conf.cli:environ_format',
    'jy-conf-read=jingyun_cli.conf.cli:read_conf',
    'jy-ssh-nonkey=jingyun_cli.ssh.cli:non_key',
    'jy-jingd-usermod=jingyun_cli.jingd.user:cli_main',
    'jy-jingd-reanalysis=jingyun_cli.jingd.sample:cli_main',
    'jy-supervisorctl=jingyun_cli.jingd.jy_supervisor:jy_supervisorctl',
    'jy-supervisord=jingyun_cli.jingd.jy_supervisor:jy_supervisord',
    'jy-docker-clear=jingyun_cli.docker.clear:clear',
    'jy-docker-compose=jingyun_cli.docker.jy_compose:main',
    'jy-sql-table=jingyun_cli.sql.cli:op_table',
    'jy-sql-link=jingyun_cli.sql.cli:link',
    'jy-server-port=jingyun_cli.server.find_port:find_one_port',
    'jy-server-ip=jingyun_cli.server.ip:get_ip'
]}

setup(name=name,
      version=version,
      author=author,
      author_email="zhouheng@gene.ac",
      url=url,
      packages=["jingyun_cli", "jingyun_cli/util", "jingyun_cli/json", "jingyun_cli/oss", "jingyun_cli/key",
                "jingyun_cli/conf", "jingyun_cli/ssh", "jingyun_cli/jingd", "jingyun_cli/docker", "jingyun_cli/sql",
                "jingyun_cli/server"],
      license=license,
      description=short_description,
      long_description=long_description,
      keywords=keywords,
      install_requires=install_requires,
      entry_points=entry_points
      )
