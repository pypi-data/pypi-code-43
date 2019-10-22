""" syncurity_utils.models

This module contains objects representing API constructs or other common objects/singletons

:copyright: (c) 2019 Syncurity
:license: Apache 2.0, see LICENSE.txt for more details
"""

__all__ = ['FactGroup', 'Alert', 'Step', 'Task', 'Incident']


class FactGroup(object):
    """ Everything has a Fact Group"""
    def __init__(self):
        pass


class Alert(FactGroup):
    """ Alerts are a 'specialized' fact group """
    def __init__(self):
        super(Alert, self).__init__()
        pass


class Step(FactGroup):
    """ Steps are a 'specialized' fact group """
    def __init__(self):
        super(Step, self).__init__()
        pass


class Task(FactGroup):
    """ Tasks are a 'specialized' fact group """
    def __init__(self):
        super(Task, self).__init__()
        pass


class Incident(FactGroup):
    """ Incidents are a 'specialized' fact group """
    def __init__(self):
        super(Incident, self).__init__()
        pass
