#! /usr/bin/env python
# coding: utf-8

import sys
from functools import partial
from jingyun_cli.util.help import help_value, error_and_exit

__author__ = '鹛桑够'

action_config_help = {"en": "", "cn": "更新或新建一个compose服务配置"}
name_help = {"en": "", "cn": "服务的名称"}
file_help = {"en": "", "cn": "compose文件路径"}
compose_dir_help = {"en": "", "cn": "docker-compose.yml所在目录，默认读取环境变量JINGD_CONF_DIR"}
image_help = {"en": "", "cn": "镜像名称"}
ports_help = {"en": "", "cn": "要映射的端口号，例如80:80，可设置多次"}
volumes_help = {"en": "", "cn": "要映射的目录，例如/host/data:/vm/data，可以设置多次"}
restart_help = {"en": "", "cn": "容器的重启策略，可以设置为always"}
create_help = {"en": "", "cn": "文件%s不存在，将会创建"}
exist_service_help = {"en": "", "cn": "compose服务已经存在，将会更新"}
command_help = {"en": "", "cn": "启动容器时执行的命令"}
env_help = {"env": "", "cn": "启动容器时设置的环境变量"}
working_dir_help = {"env": "", "cn": "容器启动时的工作目录"}

help_keys = filter(lambda x: x.endswith("_help"), locals().keys())
help_dict = dict()
for key in help_keys:
    help_dict[key[:-5]] = locals()[key]


g_help = partial(help_value, help_dict)

