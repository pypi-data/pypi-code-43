# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "14/08/2019"


from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from Orange.widgets.widget import OWWidget, Input
from darfix.core.dataset import Dataset
from darfix.gui.utils import ChooseDimensionWidget


class ZSumWidgetOW(OWWidget):

    """
    Widget that sums a stack of images by the z axis.
    """

    name = "z sum"
    icon = "icons/zsum.svg"
    want_main_area = False

    # Inputs
    class Inputs:
        dataset = Input("dataset", Dataset)

    def __init__(self):
        super().__init__()

        self._plot = Plot2D(parent=self)
        self._plot.setDefaultColormap(Colormap(name='viridis', normalization='linear'))
        self.controlArea.layout().addWidget(self._plot)
        self._chooseDimensionWidget = ChooseDimensionWidget(self)
        self._chooseDimensionWidget.hide()
        self.controlArea.layout().addWidget(self._chooseDimensionWidget)
        self._chooseDimensionWidget.filterChanged.connect(self._filterStack)
        self._chooseDimensionWidget.stateDisabled.connect(self._wholeStack)

    @Inputs.dataset
    def setDataset(self, dataset):
        # Make sum of dataset data
        if dataset:
            self.dataset = dataset
            image = dataset.data.sum(axis=0)
            self._plot.addImage(image)
            self.open()
            if dataset.reshaped_data is not None:
                self._chooseDimensionWidget.show()
                self._chooseDimensionWidget.setDimensions(dataset.dims)
        else:
            self._plot.clear()

    def _filterStack(self, dim=0, val=0):
        data = self.dataset.get_reshaped_data(dim, val)
        if data.shape[0]:
            image = data.sum(axis=0)
            self._plot.addImage(image)
        else:
            self._plot.clear()

    def _wholeStack(self):
        image = self.dataset.data.sum(axis=0)
        self._plot.addImage(image)
