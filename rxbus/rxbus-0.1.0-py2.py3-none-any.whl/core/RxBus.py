#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
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
        print(_class)
        subjectList = self.objectMap.get(_class)
        self.targtToClassMap[targt] = _class
        targtMap = self.targtMap
        if not subjectList:
            subjectList = list()

        def _createObserver(observable: rx.Observable, scheduler: rx.typing.Scheduler):
            subjectList.append(observable)
            targtMap[targt] = observable

        self.objectMap[_class] = subjectList

        return rx.create(_createObserver)

    def unRegister(self, targt):
        _Class = self.targtToClassMap[targt]
        observable = self.targtMap[targt]
        del self.targtMap[targt]
        del self.targtToClassMap[targt]
        subjectList = self.objectMap[_Class]
        if subjectList:
            subjectList.remove(observable)
        self.objectMap[_Class] = subjectList
        del self.targtMap[targt]

    def post(self, data):
        for _Class in self.objectMap:
            if type(data) == _Class:
                subjectList = self.objectMap[_Class]
                for subject in subjectList:
                    subject.on_next(data)


instance = RxBus()
