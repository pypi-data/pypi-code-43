from optimeed.core.tools import printIfShown, SHOW_WARNING
from .graphsVisualWidget.pyqtgraphRedefine import myGraphicsLayoutWidget
from .graphsVisualWidget.pyqtgraph.exporters.SVGExporter import SVGExporter
from .graphsVisualWidget.graphVisual import GraphVisual
from .graphsVisualWidget import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from abc import ABCMeta, abstractmethod
import subprocess
import os


class on_graph_click_interface(metaclass=ABCMeta):
    """Interface class for the action to perform when a point is clicked"""

    @abstractmethod
    def graph_clicked(self, theGraphsVisual, index_graph, index_trace, indices_points):
        """
        Action to perform when a graph is clicked

        :param theGraphsVisual: class widget_graphs_visual that has called the method
        :param index_graph: Index of the graph that has been clicked
        :param index_trace: Index of the trace that has been clicked
        :param indices_points: graph Indices of the points that have been clicked
        :return:
        """
        pass

    @abstractmethod
    def get_name(self):
        pass


class widget_graphs_visual(QtWidgets.QWidget):
    """Widget element to draw a graph. The traces and graphs to draw are defined in :class:`~optimeed.visualize.graphs.Graphs.Graphs` taken as argument.
     This widget is linked to the excellent third-party library pyqtgraph, under MIT license"""
    signal_must_update = QtCore.pyqtSignal()  # Use this signal to refresh the graphs (signal_must_update.emit())
    signal_graph_changed = QtCore.pyqtSignal()  # This signal is send when the graph layout is changed (trace/graphs)

    def __init__(self, theGraphs, **kwargs):
        """

        :param theGraphs: :class:`~optimeed.visualize.graphs.Graphs.Graphs`.
        :param is_light: Light theme option (bool)
        :param refresh_time: Refresh time (in seconds). If < 0: never automatically refreshed.
        :param highlight_last: Option to automatically highlight last point added in data.
        :param linkX: Link the x-axis of the graphs together (bool)
        :param actionOnClick: Action to perform when a point is clicked. Calls the method :meth:`~on_graph_click_interface.graph_clicked`.
        """
        self.is_light = kwargs.get('is_light', False)
        self.refresh_time = kwargs.get('refresh_time', 0.1) * 1000
        self.highlight_last = kwargs.get('highlight_last', False)
        self.linkX = kwargs.get('linkX', False)
        self.theActionOnClick = kwargs.get('actionOnClick', None)

        super().__init__()

        # Configure pyqtgraphs
        if self.is_light:  # Template "Light"
            background_color = 'w'
            foreground_color = (50, 50, 50)
            self.label_color = '#000'
        else:
            background_color = (30, 30, 30)
            foreground_color = (200, 200, 200)
            self.label_color = '#FFF'

        pg.setConfigOption("antialias", True)
        pg.setConfigOption('background', background_color)  # Color of background
        pg.setConfigOption('foreground', foreground_color)  # Color of ticks
        pg.setConfigOptions(useOpenGL=True)  # Otherwise performance issue on line thickness

        # Initializes upper widget and core variables

        main_vertical_layout = QtWidgets.QVBoxLayout(self)
        self.canvasWidget = myGraphicsLayoutWidget()
        main_vertical_layout.addWidget(self.canvasWidget)

        # self.theTraces = dict()
        # self.theWGPlots = dict()
        self.theGraphs = dict()
        self.theGraphsVisual = dict()

        # # Add last buttons
        # Export button
        self.horizontalLayoutGUI = QtWidgets.QHBoxLayout()

        # self.centralLayout
        main_vertical_layout.addLayout(self.horizontalLayoutGUI)

        # Create graphs
        self.theGraphs = theGraphs
        theGraphs.add_update_method(lambda: self.signal_must_update.emit())

        if self.linkX:
            self.link_axes()

        self.update_graphs(singleUpdate=False)
        self.canvasWidget.showMaximized()

        # connect signals
        self.signal_must_update.connect(self.update_graphs)

    def set_graph_disposition(self, indexGraph, row=1, col=1, rowspan=1, colspan=1):
        """
        Change the graphs disposition.

        :param indexGraph: index of the graph to change
        :param row: row where to place the graph
        :param col: column where to place the graph
        :param rowspan: number of rows across which the graph spans
        :param colspan: number of columns across which the graph spans
        :return:
        """
        item = self.get_graph(indexGraph).theWGPlot
        self.canvasWidget.ci.set_graph_disposition(item, row, col, rowspan, colspan)

    def __create_graph(self, idGraph):
        self.theGraphsVisual[idGraph] = GraphVisual(self)

    def __check_graphs(self):
        graph_changed = False
        """If the graphs have been modified, update them."""
        graphs2D = self.theGraphs.get_all_graphs_ids()
        # # Check the graphs

        # Create non existing graphs
        for idGraph in graphs2D:
            if idGraph not in self.theGraphsVisual:
                graph_changed = True
                self.__create_graph(idGraph)  # Create a graph
        # Remove graphs that disappeared
        indexToRemove = []
        for idGraph in self.theGraphsVisual:
            if idGraph not in graphs2D:
                graph_changed = True
                indexToRemove.append(idGraph)
        for idGraph in indexToRemove:
            self.delete_graph(idGraph)

        # # Check the traces
        for idGraph in self.theGraphsVisual:
            graphVisual = self.theGraphsVisual[idGraph]
            traces = self.theGraphs.get_graph(idGraph).get_all_traces()
            tracesVisual = graphVisual.get_all_traces()
            # Create non existing traces
            for idTrace, trace in traces.items():
                if idTrace not in tracesVisual:
                    graph_changed = True
                    graphVisual.add_data(idTrace, None, trace)  # Create the traces

            # Remove traces that  disappeared
            indexToRemove = []
            for idTrace in tracesVisual:
                if idTrace not in traces:
                    graph_changed = True
                    indexToRemove.append(idTrace)

            for idTrace in indexToRemove:
                graphVisual.delete_trace(idTrace)

            # Set color
            graphVisual.apply_palette()

            graphVisual.set_legend()

            if graph_changed:
                self.signal_graph_changed.emit()

    def on_click(self, plotDataItem, clicked_points):  # Clicked_points = list of spotItem
        indices_points = [0]*len(clicked_points)
        index_graph = 0
        index_trace = 0

        # Get index of point
        all_points = plotDataItem.scatter.points().tolist()
        for i, point in enumerate(clicked_points):
            indices_points[i] = all_points.index(point)

        # get index of graph
        for idGraph, graphVisual in self.theGraphsVisual.items():
            for idTrace, traceVisual in graphVisual.get_all_traces().items():
                if traceVisual.thePlotItem == plotDataItem:
                    index_graph = idGraph
                    index_trace = idTrace

        if self.theActionOnClick is not None:
            self.theActionOnClick.graph_clicked(self, index_graph, index_trace, indices_points)

    def update_graphs(self, singleUpdate=True):
        """
        This method is used to update the graph. This is fast but NOT safe (especially when working with threads).
        To limit the risks, please use self.signal_must_update.emit() instead.

        :param singleUpdate: if set to False, the graph will periodically refres each self.refreshtime
        """
        self.__check_graphs()
        # self.fast_update()
        for graph in self.theGraphsVisual.values():
            graph.update()
        if self.refresh_time > 0 and not singleUpdate:
            QtCore.QTimer().singleShot(self.refresh_time, lambda: self.update_graphs(False))

    def fast_update(self):
        """Use this method to update the graph in a fast way. NOT THREAD SAFE."""
        for graph in self.theGraphsVisual.values():
            graph.fast_update()

    def exportGraphs(self):
        """Export the graphs"""
        dlg = QtWidgets.QFileDialog.getSaveFileName()[0]
        if dlg:
            root, ext = os.path.splitext(dlg)
            filename_svg = root + '.svg'
            filename_png = root + '.png'
            filename_pdf = root + '.pdf'
            filename_txt = root + '.txt'

            # Export txt
            theStr = self.theGraphs.export_str()
            with open(filename_txt, 'w') as f:
                f.write(theStr)

            # Export svg
            my_exporter = SVGExporter(self.canvasWidget.sceneObj)
            my_exporter.params.param('scaling stroke').setValue(True)
            my_exporter.export(filename_svg)

            # Export png
            converter_cmd_line = 'inkscape -z ' + filename_svg + ' -D -e ' + filename_png + ' -d 400'
            subprocess.Popen(converter_cmd_line, shell=True)

            # Export pdf
            converter_cmd_line = 'inkscape -z ' + filename_svg + ' -A ' + filename_pdf + ' --export-area-drawing'
            subprocess.Popen(converter_cmd_line, shell=True)

    def link_axes(self):
        keys = list(self.theGraphsVisual.keys())
        for key in keys:
            self.theGraphsVisual[key].linkXToGraph(self.theGraphsVisual[keys[0]])

    def get_graph(self, idGraph) -> GraphVisual:
        """Get corresponding :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.GraphVisual.GraphVisual` of the graph idGraph"""
        return self.theGraphsVisual[idGraph]

    def keyPressEvent(self, event):
        """
        What happens if a key is pressed.
        R: reset the axes to their default value
        """
        if event.key() == QtCore.Qt.Key_R:
            for idGraphVisual in self.get_all_graphsVisual():
                self.get_graph(idGraphVisual).theWGPlot.autoRange()
                # graphVisual.set_lims(self.theTraces[idGraph][0])

    def delete_graph(self, idGraph):
        """Delete the graph idGraph"""
        try:
            self.theGraphsVisual[idGraph].delete()
            self.theGraphsVisual.pop(idGraph)
        except KeyError:
            printIfShown("Graph already deleted", SHOW_WARNING)

    def get_all_graphsVisual(self):
        """Return a dictionary {idGraph: :class:`~optimeed.visualize.gui.widgets.graphsVisualWidget.GraphVisual.GraphVisual`}."""
        return self.theGraphsVisual

    def get_layout_buttons(self):
        """Get the QGraphicsLayout where it's possible to add buttons, etc."""
        return self.horizontalLayoutGUI

    def set_actionOnClick(self, theActionOnClick):
        """Action to perform when the graph is clicked

        :param theActionOnClick: :class:`on_graph_click_interface`
        :return:
        """
        self.theActionOnClick = theActionOnClick

    def set_title(self, idGraph, titleName, **kwargs):
        """Set title of the graph

        :param idGraph: id of the graph
        :param titleName: title to set
        """
        self.get_graph(idGraph).set_title(titleName, **kwargs)

    def set_article_template(self, graph_size_x=8.8, graph_size_y=4.4, legendPosition="NW"):
        """Method to set the graphs to article quality graph.

        :param graph_size_x: width of the graph in cm
        :param graph_size_y: height of the graph in cm
        :param legendPosition: position of the legend (NE, SE, SW, NW)
        :return:
        """
        font = "Times New Roman"

        for idGraph in self.get_all_graphsVisual():
            theGraph = self.get_graph(idGraph)
            theGraph.set_fontTicks(7.75, fontname=font)
            theGraph.set_fontLabel(7.75, fontname=font)
            theGraph.set_fontLegend(7.75, '#111', fontname=font)
            theGraph.set_label_pos("left", x_offset=15)
            theGraph.set_label_pos("bottom", y_offset=5)
            theGraph.get_legend().set_offset_sample(10)
            theGraph.get_legend().set_position(legendPosition, (5, 5))
            theGraph.get_legend().set_width_cell_sample(18)
            # theGraph.set_color_palette(blackOnly)
            theGraph.set_numberTicks(10, "left")
            theGraph.update()

        width = self.logicalDpiX() * graph_size_x / 2.54 * 1.1
        height = self.logicalDpiY() * graph_size_y / 2.54 * 1.1
        self.canvasWidget.ci.setFixedWidth(width)
        self.canvasWidget.ci.setFixedHeight(height)
