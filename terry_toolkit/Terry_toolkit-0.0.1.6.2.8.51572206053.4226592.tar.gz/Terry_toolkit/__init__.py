# -*- coding: utf-8 -*-
# __init__.py
#from .a import A
#from .b import B
"""
# Terry_toolkit
===

各种工具合集
文档地址
http://terry-toolkit.terrychan.org/zh/master/

# 安装
> pip3 install Terry_toolkit

"""
#多文件导入以后只用导入 import Terry-toolkit 就可以使用所有类
#>>> import mymodule
#>>> a = mymodule.A()
#>>> a.spam()


from .file import *
from .text import *
from .dict_get import *
from .crawler_baidu import *
from .CxExtractor import *
from .turl import *
from .SearchBaidu import *
# from .TextRank4ZH import TextRank4ZH
from .list import *
from .tjson import *

