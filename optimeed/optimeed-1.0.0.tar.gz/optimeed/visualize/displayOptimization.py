from optimeed.core.linkDataGraph import LinkDataGraph, HowToPlotGraph
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow
from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize import start_qt_mainloop, stop_qt_mainloop
from optimeed.visualize.gui.widgets.graphsVisualWidget.examplesActionOnClick.on_click_showinfo import on_graph_click_showInfo
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
from threading import Thread
from threading import Timer
from PyQt5 import QtCore
import queue


class OptimizationDisplayer:
    """Class used to display optimization process in real time"""
    signal_optimization_over = QtCore.pyqtSignal()

    def __init__(self, thePipeOpti, listOfObjectives, theOptimizer, additionalWidgets=None):
        """

        :param thePipeOpti: :class:`~optimeed.optimize.optimizer.PipeOptimization`
        :param listOfObjectives: list of :class:`~optimeed.optimize.objAndCons.interfaceObjCons.InterfaceObjCons`
        :param theOptimizer: :class:`~optimeed.optimize.optimizer.Optimizer`
        :param additionalWidgets: list of QtWidgets (instantiated)
        """
        self.thePipeOpti = thePipeOpti
        self.listOfObjectives = listOfObjectives
        self.theOptimizer = theOptimizer
        if additionalWidgets is None:
            self.additionalWidgets = list()
        else:
            self.additionalWidgets = additionalWidgets

        self.theActionsOnClick = None
        self.theDataLink = None
        self.myWidgetGraphsVisuals = None
        self.id_logOpti = None
        self.windowOpti = None
        self.windowConvergence = None

    def set_actionsOnClick(self, theList):
        """Set actions to perform on click, list of :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.on_graph_click_interface`"""
        self.theActionsOnClick = theList

    def generate_optimizationGraphs(self, refresh_time=0.1):
        """Generates the optimization graphs.

        :return: :class:`~optimeed.core.graphs.Graphs`, :class:`~optimeed.core.linkDataGraph.LinkDataGraph`"""
        collection_devices = self.thePipeOpti.get_historic().get_devices()
        collection_logOpti = self.thePipeOpti.get_historic().get_logopti()

        theDataLink = LinkDataGraph()
        id_logOpti = theDataLink.add_collection(collection_logOpti)
        id_devices = theDataLink.add_collection(collection_devices)
        theDataLink.link_collection_to_graph_collection(id_logOpti, id_devices)  # Link the devices to the logopti

        if len(self.listOfObjectives) == 2:
            x_label = self.listOfObjectives[0].get_name()
            y_label = self.listOfObjectives[1].get_name()
            howToPlot = HowToPlotGraph('objectives[0]', 'objectives[1]', {'x_label': x_label, 'y_label': y_label, 'is_scattered': True})
            theDataLink.add_graph(howToPlot)
            howToPlot.exclude_col(id_devices)
        else:
            for i, objective in enumerate(self.listOfObjectives):
                x_label = 'Time [s]'
                y_label = self.listOfObjectives[i].get_name()
                howToPlot = HowToPlotGraph('time', 'objectives[{}]'.format(i), {'x_label': x_label, 'y_label': y_label})
                theDataLink.add_graph(howToPlot)
                howToPlot.exclude_col(id_devices)

        theGraphs = theDataLink.createGraphs()
        self.theDataLink = theDataLink
        self.id_logOpti = id_logOpti

        """Generate live graph for the optimization"""
        # Set actions on graph click
        if self.theActionsOnClick is None:
            self.theActionsOnClick = list()
            self.theActionsOnClick.append(on_graph_click_showInfo(theDataLink))

        myWidgetGraphsVisuals = widget_graphs_visual(theGraphs, highlight_last=True, refresh_time=-1)
        guiPyqtgraph(myWidgetGraphsVisuals, actionsOnClick=self.theActionsOnClick)  # Add GUI to change action easily and export graphs
        self.myWidgetGraphsVisuals = myWidgetGraphsVisuals
        self.__set_graphs_disposition()
        self.__auto_refresh(refresh_time)

        # Add additional widgets to the visualisation
        listOfWidgets = self.additionalWidgets
        listOfWidgets.append(myWidgetGraphsVisuals)
        myWindow = gui_mainWindow(listOfWidgets, actionOnWindowClosed=lambda _: stop_qt_mainloop())
        myWindow.run()

        self.windowOpti = myWindow

        return theGraphs, theDataLink

    def __change_appearance_violate_constraints(self):
        graphs, theCol = self.theDataLink.get_graph_and_trace_from_collection(self.id_logOpti)
        all_constraints = theCol.get_list_attributes("constraints")
        violate_constraint_indices = list()
        for index, constraints in enumerate(all_constraints):
            for constraint in constraints:
                if constraint > 0:
                    violate_constraint_indices.append(index)  # Index in data
        for graph, trace in graphs:
            theTrace = self.myWidgetGraphsVisuals.get_graph(graph).get_trace(trace)
            theTrace.set_brushes(violate_constraint_indices, (250, 0, 0))

    def __auto_refresh(self, refresh_time):
        if refresh_time > 0:
            self.theDataLink.update_graphs()
            self.__change_appearance_violate_constraints()
            timer = Timer(refresh_time, lambda: self.__auto_refresh(refresh_time))
            timer.daemon = True
            timer.start()

    def __set_graphs_disposition(self):
        """Set nicely the graphs disposition"""
        allGraphs = self.myWidgetGraphsVisuals.get_all_graphsVisual()
        row = 1
        col = 1
        maxNbrRow = 5
        currRow = 1
        for idGraph in allGraphs:
            self.myWidgetGraphsVisuals.set_graph_disposition(idGraph, row, col)
            if currRow >= maxNbrRow:
                row = 1
                col += 1
            else:
                row += 1
            currRow = row

    def launch_optimization(self):
        """Generate graph to analyse optimisation once it is done"""
        self.windowConvergence = Worker()

        """Launch optimisation"""
        que = queue.Queue()
        threadOpti = Thread(target=lambda: que.put(self.__callback_optimization(self.windowConvergence)))
        threadOpti.start()

        start_qt_mainloop()  # Automatically stops at the end of the optimization

        threadOpti.join()
        return que.get()

    def __callback_optimization(self, myWindow):
        resultsOpti, convergence = self.theOptimizer.run_optimization()
        theGraphs = convergence.get_graphs()
        myWindow.signal_show_UI.emit(theGraphs)
        stop_qt_mainloop()

        return resultsOpti, convergence

    @staticmethod
    def on_quit():
        stop_qt_mainloop()


class Worker(QtCore.QObject):
    signal_show_UI = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.graphConvergence = None
        self.window = None
        self.signal_show_UI.connect(self.display_graphs)

    def display_graphs(self, theGraphs):
        myWidgetGraphsVisuals = widget_graphs_visual(theGraphs, highlight_last=False, refresh_time=-1)
        guiPyqtgraph(myWidgetGraphsVisuals)  # Add GUI to change action easily and export graphs
        myWindowConvergence = gui_mainWindow([myWidgetGraphsVisuals], actionOnWindowClosed=lambda _: stop_qt_mainloop())

        myWindowConvergence.run()
        self.window = myWindowConvergence
