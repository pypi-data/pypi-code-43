#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AIPipeline.
# @File         : main
# @Time         : 2019-10-12 15:57
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from iapp import App
from apis import lgb_api

# App
app = App()

app.add_route('/ai-pipeline/lgb', lgb_api.api, methods="POST")

import time
import jieba

f = lambda **kwargs: kwargs
f1 = lambda **kwargs: kwargs['x'] + kwargs['y']
f2 = lambda x=1, y=1: x - y
f3 = lambda text='小米是家不错的公司': jieba.lcut(text)

app.add_route("/ai-pipeline/", f, time=time.ctime())
app.add_route("/ai-pipeline/f1", f1, version="1", time=time.time(), a=1, b=111)
app.add_route("/ai-pipeline/f2", f2, version="2")
app.add_route("/ai-pipeline/f3", f3, version="3")

if __name__ == '__main__':
    app.run()
