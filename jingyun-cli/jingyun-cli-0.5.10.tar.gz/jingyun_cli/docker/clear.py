#! /usr/bin/env python
# coding: utf-8

import os

__author__ = '鹛桑够'


def clear():
    c_ps = "docker rm `docker ps -a -q`"
    os.system(c_ps)

    c_volume = "docker volume rm $(docker volume ls -qf dangling=true)"
    os.system(c_volume)

    c_image = "docker image rmi $(docker images -qf dangling=true)"
    os.system(c_image)

if __name__ == "__main__":
    clear()
