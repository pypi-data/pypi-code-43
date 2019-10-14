#! /usr/bin/python
# -*- coding:utf8 -*-

"""监控脚本"""

import asyncio
import argparse

from tail_uwsgi_log.reader import Filereader, Logreader, Mailsender
from tail_uwsgi_log.config import files


async def monitor():
    """监控日志文件"""
    # 每个文件都创建对应任务
    tasks = []
    for file in files:
        logreader = Logreader(re_pattern=file.pattern)
        mailsender = Mailsender(emailconfig=file.emailconfig)
        filereader = Filereader(filename=file.filepath, logreader=logreader, mailsender=mailsender,
                                wait_time=file.wait_time)
        tasks.append(filereader.tail())
    # 执行任务
    await asyncio.gather(*tasks)


def tail_uwsgi_log():
    """Script to parse configs and execute log tail"""
    print('test ok')
    parser = argparse.ArgumentParser(prog='tail_uwsgi_log', description='Tail uwsgi logs')
    parser.add_argument('-c', '--config', type=str, help='Config file path')
    print(parser.parse_args().config)


if __name__ == '__main__':
    asyncio.run(monitor())
