#!/usr/bin/env python
# -*- coding: utf-8 -*-

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import rx


class RxBus:
    __instance = None

    def __init__(self):
        self.targtMap = dict()
        self.targtToClassMap = dict()
        self.objectMap = dict()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(RxBus, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def register(self, targt, _class) -> rx.Observable:
        subjectList = self.objectMap.get(_class)
        _targtToClasList = self.targtToClassMap.get(targt)
        if not _targtToClasList:
            _targtToClasList = list()
        _targtToClasList.append(_class)
        targtMap = self.targtMap
        if not subjectList:
            subjectList = list()

        def _createObserver(observable: rx.Observable, scheduler: rx.typing.Scheduler):
            subjectList.append(observable)
            targtMap[targt] = observable

        self.objectMap[_class] = subjectList

        return rx.create(_createObserver)

    def unRegister(self, targt):
        _targtToClasList = self.targtToClassMap[targt]
        observable = self.targtMap[targt]
        del self.targtMap[targt]
        del self.targtToClassMap[targt]
        for _targtToClas in _targtToClasList:
            subjectList = self.objectMap[_targtToClas]
            if subjectList:
                subjectList.remove(observable)
            self.objectMap[_targtToClas] = subjectList
            del self.targtMap[targt]

    def post(self, data):
        for _Class in self.objectMap:
            if type(data) == _Class:
                subjectList = self.objectMap[_Class]
                for subject in subjectList:
                    subject.on_next(data)


instance = RxBus()
