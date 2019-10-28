#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rxbus.core import RxBus
from rx import operators as ops, scheduler


class Data:
    def __init__(self):
        self.name = "xxxx"


class Test:
    def __init__(self):
        pass

    def register(self):
        RxBus.instance.register(self, Data).pipe(
            ops.subscribe_on(scheduler.ThreadPoolScheduler())
        ).subscribe(
            on_next=lambda value: print(value.name)
        )

    def unRegister(self):
        RxBus.instance.unRegister(self)

    def send(self):
        RxBus.instance.post(Data())


if "__main__" == __name__:
    test = Test()
    test.register()
    test.send()
    test.send()
