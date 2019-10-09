# coding=utf-8

""" Chart widget for Map tab """

from ipywidgets import *
from traitlets import *
from .. import utils


class ChartTab(HBox):
    def __init__(self, map, name='Chart', **kwargs):
        super(ChartTab, self).__init__(**kwargs)
        self.map = map
        self.name = name
        self.selector = Select()


