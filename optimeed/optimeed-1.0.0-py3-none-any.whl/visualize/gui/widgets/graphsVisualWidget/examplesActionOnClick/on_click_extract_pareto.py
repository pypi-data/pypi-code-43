from optimeed.visualize.gui.widgets.widget_graphs_visual import on_graph_click_interface
from optimeed.core.tools import get_2D_pareto
from optimeed.core.collection import Collection
from optimeed.visualize.gui.gui_collection_exporter import gui_collection_exporter


class on_click_extract_pareto(on_graph_click_interface):
    """On click: extract the pareto from the cloud of points"""
    def __init__(self, theDataLink, max_x=False, max_y=False):
        """

        :param theDataLink: :class:`~optimeed.visualize.high_level.LinkDataGraph.LinkDataGraph`
        :param max_x: x axis is to maximize or not (bool)
        :param max_y: y axis is to maximize or not (bool)
        """
        self.theDataLink = theDataLink
        self.theCollectionExporter = None
        self.max_x = max_x
        self.max_y = max_y

    def graph_clicked(self, the_graph_visual, index_graph, index_trace, _):
        self.theCollectionExporter = gui_collection_exporter()

        theCollection = self.theDataLink.get_collection_from_graph(index_graph, index_trace, getMaster=False)
        idCollection = self.theDataLink.get_idCollection_from_graph(index_graph, index_trace, getMaster=False)

        x_list, y_list = self.theDataLink.get_x_y_to_plot(theCollection, self.theDataLink.get_howToPlotGraph(index_graph))
        xx, yy, indices = get_2D_pareto(x_list, y_list, max_X=self.max_x, max_Y=self.max_y)

        newCollection = Collection()
        newCollection.set_info("Extracted Pareto" + theCollection.get_info())
        newCollection.set_data([theCollection.get_data()[index] for index in indices])
        self.theCollectionExporter.set_collection(newCollection)

        idCollectionPareto = self.theDataLink.add_collection(newCollection, {"is_scattered": False, "sort_output": True, "legend": 'Pareto extracted'})
        self.theDataLink.create_trace(self.theDataLink.get_collectionInfo(idCollectionPareto), self.theDataLink.get_howToPlotGraph(index_graph), index_graph)
        self.theDataLink.collectionLinks.set_same_master(idCollection, idCollectionPareto)

        self.theDataLink.update_graphs()
        self.theCollectionExporter.show()

    def get_name(self):
        return "Extract pareto"
