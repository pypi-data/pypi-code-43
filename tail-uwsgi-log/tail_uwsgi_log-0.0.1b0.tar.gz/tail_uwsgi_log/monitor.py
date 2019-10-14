#! /usr/bin/python
# -*- coding:utf8 -*-

"""监控脚本"""

import asyncio
import argparse
import configparser

from tail_uwsgi_log.reader import Filereader, Logreader, Mailsender
from tail_uwsgi_log.config import Emailconfig, Logconfig


async def monitor(configs):
    """监控日志文件"""
    # 每个文件都创建对应任务
    tasks = []
    for config in configs:
        emailconfig = Emailconfig(recipients=config.get('mail_recipients', []),
                                  sender=config.get('mail_sender', ''),
                                  password=config.get('mail_password', ''),
                                  host=config.get('mail_host', ''),
                                  port=config.get('mail_port', ''),)
        mailsender = Mailsender(emailconfig=emailconfig)
        logconfig = Logconfig(filepath=config.get('filepath', ''), pattern=config.get('pattern', ''),
                              wait_time=config.get('wait_time', 1.0))

        logreader = Logreader(re_pattern=logconfig.pattern)
        filereader = Filereader(filename=logconfig.filepath, logreader=logreader, mailsender=mailsender,
                                wait_time=logconfig.wait_time)
        tasks.append(filereader.tail())

    # 执行任务
    await asyncio.gather(*tasks)


def tail_uwsgi_log():
    """Script to parse configs and execute log tail"""
    parser = argparse.ArgumentParser(prog='tail_uwsgi_log', description='Tail uwsgi logs')
    parser.add_argument('-c', '--config', type=str, help='Config file path')

    # parse configs
    configs = parse_config(parser.parse_args().config)

    # start tailing tasks
    asyncio.run(monitor(configs))


def parse_config(filepath):
    """从配置文件中读取信息"""
    conf = configparser.ConfigParser()
    conf.read(filepath)

    configs = []
    for section in conf.sections():
        if section.startswith('log'):
            config = {
                'filepath': conf.get(section, 'filepath') if conf.has_option(section, 'filepath') else '',
                'wait_time': conf.getfloat(section, 'wait_time') if conf.has_option(section, 'wait_time') else 1,
                'pattern': conf.get(section, 'pattern') if conf.has_option(section, 'pattern') else '',
            }
            config.update(parse_mail_config(conf, section))
            configs.append(config)

    return configs


def parse_mail_config(conf, section):
    """读取邮件配置信息"""
    mail_info = {
        'mail_host': '',
        'mail_port': '',
        'mail_sender': '',
        'mail_password': '',
        'mail_recipients': '',
    }
    if conf.has_section('mail'):
        for k in mail_info.keys():
            if conf.has_option('mail', k):
                mail_info[k] = conf.get('mail', k)

    for k in mail_info.keys():
        if conf.has_option(section, k):
            mail_info[k] = conf.get(section, k)

    # 整理数据格式
    try:
        mail_info['mail_port'] = int(mail_info['mail_port'])
    except ValueError:
        mail_info['mail_port'] = 465
    mail_info['mail_recipients'] = [i.strip() for i in mail_info.get('mail_recipients', '').split(',')]

    return mail_info
