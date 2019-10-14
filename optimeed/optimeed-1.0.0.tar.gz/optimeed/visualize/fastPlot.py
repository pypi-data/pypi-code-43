from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow, start_qt_mainloop
from optimeed.core.graphs import Data, Graphs
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
import signal
import sys


class PlotHolders:
    def __init__(self):
        self.curr_g = None
        self.graphs = Graphs()
        self.theGraphVisual = widget_graphs_visual(self.graphs, refresh_time=-1, is_light=True)
        self.new_plot()

    def add_plot(self, x, y, **kwargs):
        theData = Data(x, y, **kwargs)
        self.graphs.add_trace(self.curr_g, theData)

    def get_wgGraphs(self):
        return self.theGraphVisual

    def new_plot(self):
        self.curr_g = self.graphs.add_graph()

    def set_title(self, theTitle, **kwargs):
        self.theGraphVisual.set_title(self.curr_g, theTitle, **kwargs)

    def reset(self):
        self.__init__()


myPlots = PlotHolders()


def plot(x, y, hold=True, **kwargs):
    """Plot new trace"""
    myPlots.add_plot(x, y, **kwargs)

    if hold is True:
        show()


def show():
    """Show current plots"""
    guiPyqtgraph(myPlots.get_wgGraphs())
    the_mainWindow = gui_mainWindow([myPlots.get_wgGraphs()], size=[1000, 700], neverCloseWindow=False, keep_alive=True)
    the_mainWindow.run()
    myPlots.reset()


def new_plot():
    """Add new plot"""
    myPlots.new_plot()


def set_title(theTitle, **kwargs):
    """Set title of the plot"""
    myPlots.set_title(theTitle, **kwargs)


def multiplot(xx, yy, hold=True, kwargsdict=None):
    theGraphs = Graphs()
    g1 = theGraphs.add_graph()

    for i in range(len(xx)):
        try:
            theData = Data(xx[i], yy[i], **kwargsdict[i])
        except (IndexError, TypeError):
            theData = Data(xx[i], yy[i])
            print(kwargsdict)
        t = theGraphs.add_trace(g1, theData)

    theGraphVisual = widget_graphs_visual(theGraphs, refresh_time=-1, is_light=True)
    guiPyqtgraph(theGraphVisual)
    the_mainWindow = gui_mainWindow([theGraphVisual], size=[1000, 1000], neverCloseWindow=False, keep_alive=hold)
    the_mainWindow.run()

    def handler_quit(sign_number, _):
        app.quit()
        sys.exit(sign_number)

    signal.signal(signal.SIGINT, handler_quit)
    signal.signal(signal.SIGTSTP, handler_quit)
    return the_mainWindow


def plot_graphs(theGraphs):

    theGraphVisual = widget_graphs_visual(theGraphs, refresh_time=1)
    the_mainWindow = gui_mainWindow([theGraphVisual], size=[1000, 700], neverCloseWindow=False)
    the_mainWindow.run()

    start_qt_mainloop()
