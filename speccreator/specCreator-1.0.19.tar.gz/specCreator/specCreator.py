#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import os
realpath=os.path.realpath(__file__)
dirPath = os.path.dirname(realpath)
sys.path.append(dirPath)
from Tools.tips import Tips
from Tools.result import Result
from Tools.formatter import Formatter
from Tools.arguments import Arguments
from Features.env import Env
from Features.init import Init
from Features.initSpec import InitSpec
from Features.package import Package
from Features.autoPackage import AutoPackage
from Features.check import Check

__author__ = "handa"
__version__ = "1.0.19"


def checkopts():
    """检测输入参数

    Arguments:
        user {str} -- 用户名
        projectPath {str} -- 项目目录
    """
    if len(sys.argv) == 1:
        Tips.instance().showTips()
        Result.instance().returnError()
    # 先检查环境 TODO open
    Env.instance().runtimeEnv()
    # 接着看参数
    arg = sys.argv[1]
    if arg == "version":
        Formatter.instance().format_info(__version__)
    elif arg == "initSpec":
        InitSpec.instance().supportBinary()
    elif arg == "init":
        Init.instance().create()
    elif arg == "check":
        Check.instance().check()
    elif arg == "package":
        Package.instance().package()
    elif arg == "autoPackage":
        AutoPackage.instance().autoPackage()
    else:
        Tips.instance().showTips()

def main():
    # 调用接口
    Formatter.instance().format_info("当前版本:"+ __version__)
    checkopts()

if __name__ == "__main__":
    sys.exit(checkopts())


