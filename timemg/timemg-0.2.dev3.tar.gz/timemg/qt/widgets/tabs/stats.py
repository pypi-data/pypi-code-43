#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout

#from timemg.qt.widgets.plot import PlotCanvas
from qtplotlib.barplot import QBarPlot

import numpy as np
import math

from timemg.stats import make_dataframe

class StatsTab(QWidget):

    def __init__(self, data, parent):
        super().__init__(parent=parent)

        self.tabs = parent

        ###################################################

        self.data = data
        self.date_column_index = data.headers.index("Date")

        ###################################################

        df = make_dataframe(self.data)

        df['date'] = df.index

        df['date_fmt'] = df['date'].dt.strftime('%a %d/%m')
        df.loc[::2, 'date_fmt'] = ''

        ###################################################

        vbox = QVBoxLayout(self)

        # See https://matplotlib.org/examples/user_interfaces/embedding_in_qt5.html
        #self.plot_canvas = PlotCanvas(data, parent=self, width=5, height=4, dpi=100)
        #vbox.addWidget(self.plot_canvas)

        self.plot_widget1 = QBarPlot()
        self.plot_widget1.data_color = None #("green", "yellow", "red", "red", "yellow")
        self.plot_widget1.title = "Sleep duration"
        self.plot_widget1.ymin = 0

        NORMAL_SLEEP_HOURS = 8

        tk = list(np.arange(0,      # math.floor(df.sleep_duration_hrs.min()),
                            math.ceil(df.sleep_duration_hrs.max()) + 1,
                            1))

        NUM_DAYS = 90
        self.plot_widget1.data = df.sleep_duration_hrs[-NUM_DAYS:]
        self.plot_widget1.data_color = df.sleep_duration_class[-NUM_DAYS:].values #("green", "yellow", "red", "red", "yellow")

        self.plot_widget1.data_color = ["green" if class_str == "good" else class_str for class_str in self.plot_widget1.data_color] #("green", "yellow", "red", "red", "yellow")
        self.plot_widget1.data_color = ["yellow" if class_str == "medium" else class_str for class_str in self.plot_widget1.data_color] #("green", "yellow", "red", "red", "yellow")
        self.plot_widget1.data_color = ["red" if class_str == "bad" else class_str for class_str in self.plot_widget1.data_color] #("green", "yellow", "red", "red", "yellow")
        #print(self.plot_widget1.data_color)

        self.plot_widget1.hlines = (7, 8, 9)
        self.plot_widget1.hlines_style = (':', '-', ':')

        #df.plot(x='date_fmt', y='sleep_duration_hrs', kind='bar', color=BLUE, yticks=tk, ax=ax)
        #sns.barplot(x="date", y="sleep_duration_hrs", data=df, hue="sleep_duration_class", ax=ax)

        #ax.grid(True, axis="y", linestyle=':', alpha=0.75)

        #ax.axhline(NORMAL_SLEEP_HOURS + 1, color='red', linestyle=':', alpha=0.25)
        #ax.axhline(NORMAL_SLEEP_HOURS, color='red', linestyle=':')
        #ax.axhline(NORMAL_SLEEP_HOURS - 1, color='red', linestyle=':', alpha=0.25)

        #ax.set_title("Sleep duration")
        #ax.set_xlabel("")
        #ax.set_ylabel("Hours")

        #if ax.get_legend() is not None:
        #    ax.get_legend().remove()


        vbox.addWidget(self.plot_widget1)

        ###################################################

        #proxy_model.dataChanged.connect(plot_canvas.update_figure)
        #proxy_model.rowsInserted.connect(plot_canvas.update_figure)  # TODO
        #proxy_model.rowsRemoved.connect(plot_canvas.update_figure)   # TODO

        # Update the stats plot when the tabs switch to the stats tab
#        self.tabs.currentChanged.connect(self.updatePlot)
#
#
#    def updatePlot(self, index):
#        """
#
#        Parameters
#        ----------
#        index
#
#        Returns
#        -------
#
#        """
#
#        # Update the plot whenever the parent tab (i.e. the "stats" tab) is selected as the current tab
#        if index == self.tabs.indexOf(self):
#            #self.plot_canvas.update_figure()
#            self.plot_widget.update_figure()

