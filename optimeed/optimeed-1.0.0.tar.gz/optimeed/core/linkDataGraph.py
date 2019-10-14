from optimeed.core import delete_indices_from_list, Graphs, Data


class HowToPlotGraph:
    def __init__(self, attribute_x, attribute_y, kwargs_graph=None, excluded=None):
        self.attribute_x = attribute_x
        self.attribute_y = attribute_y
        if excluded is None:
            self.excluded = list()
        else:
            self.excluded = excluded

        if kwargs_graph is None:
            self.kwargs_graph = dict()
        else:
            self.kwargs_graph = kwargs_graph

    def exclude_col(self, id_col):
        """Add id_col to exclude from the graph"""
        self.excluded.append(id_col)

    def __str__(self):
        theStr = ''
        theStr += "x: {} \t y: {}".format(self.attribute_x, self.attribute_y)
        return theStr


class CollectionInfo:
    def __init__(self, theCollection, kwargs, theID):
        self.collection = theCollection
        self.kwargs = kwargs
        self.id = theID

    def get_collection(self):
        return self.collection

    def get_kwargs(self):
        return self.kwargs

    def get_id(self):
        return self.id


class LinkDataGraph:
    class _collection_linker:
        def __init__(self):
            self.collectionsLinked = list()

        def add_link(self, idSlave, idMaster):
            self.collectionsLinked.append((idSlave, idMaster))

        def get_collection_master(self, idToGet):
            for slave, master in self.collectionsLinked:
                if slave == idToGet:
                    return master
            return idToGet

        def set_same_master(self, idExistingSlave, idOtherSlave):
            """

            :param idExistingSlave: id collection of the existing slave
            :param idOtherSlave: id collection of the new slave that has to be linked to an existing master
            """
            for slave, master in self.collectionsLinked:
                if idExistingSlave == slave:
                    self.add_link(idOtherSlave, master)
                    break

    def __init__(self):
        self.theGraphs = Graphs()
        self.collectionInfos = dict()  # keys are unique ids of collection
        self.HowToPlotGraphs = dict()  # keys are ids of graph
        self.mappingData = dict()  # keys are ids of graph. mappingData[idGraph][idTrace] = idCollection used for trace
        self.collectionLinks = self._collection_linker()
        self.curr_id = 0

    def add_collection(self, theCollection, kwargs=None):
        theId = self.curr_id
        if kwargs is None:
            kwargs = dict()
        theCollectionInfo = CollectionInfo(theCollection, kwargs, theId)
        self.collectionInfos[theId] = theCollectionInfo
        self.curr_id += 1
        return theId

    def add_graph(self, howToPlotGraph):
        idGraph = self.theGraphs.add_graph()
        self.HowToPlotGraphs[idGraph] = howToPlotGraph
        self.mappingData[idGraph] = dict()
        return idGraph

    def createGraphs(self):
        for idGraph in self.theGraphs.get_all_graphs_ids():
            howToPlotGraph = self.get_howToPlotGraph(idGraph)

            for collectionInfo in self.collectionInfos.values():
                self.create_trace(collectionInfo, howToPlotGraph, idGraph)
        return self.theGraphs

    @staticmethod
    def get_x_y_to_plot(theCollection, howToPlotGraph):
        if howToPlotGraph.attribute_x is None:
            x_data = []
        else:
            x_data = theCollection.get_list_attributes(howToPlotGraph.attribute_x)
        y_data = theCollection.get_list_attributes(howToPlotGraph.attribute_y)
        min_length = min(len(x_data), len(y_data))
        return x_data[:min_length], y_data[:min_length]  # Truncate if lengths are not the same

    def get_howToPlotGraph(self, idGraph):
        return self.HowToPlotGraphs[idGraph]

    def get_collectionInfo(self, idCollectionInfo):
        return self.collectionInfos[idCollectionInfo]

    def create_trace(self, collectionInfo, howToPlotGraph, idGraph):
        theCollection = collectionInfo.get_collection()
        kwargs_collection = collectionInfo.get_kwargs()
        kwargs_graph = howToPlotGraph.kwargs_graph
        idCollection = collectionInfo.get_id()

        if idCollection not in howToPlotGraph.excluded:
            x_data, y_data = self.get_x_y_to_plot(theCollection, howToPlotGraph)
            kwargs = dict()
            kwargs.update(kwargs_graph)
            kwargs.update(kwargs_collection)

            theData = Data(x_data, y_data, **kwargs)
            idTrace = self.theGraphs.add_trace(idGraph, theData)
            self.mappingData[idGraph][idTrace] = idCollection

    def get_all_id_graphs(self):
        return list(self.mappingData.keys())

    def get_all_traces_id_graph(self, idGraph):
        return list(self.get_mappingData_graph(idGraph).keys())

    def update_graphs(self):
        for idGraph in self.get_all_id_graphs():
            howToPlotGraph = self.HowToPlotGraphs[idGraph]
            for idTrace in self.get_all_traces_id_graph(idGraph):
                idCollection = self.get_mappingData_trace(idGraph, idTrace)
                theCollection = self.collectionInfos[idCollection].get_collection()
                theData = self.theGraphs.get_graph(idGraph).get_trace(idTrace)
                x, y = self.get_x_y_to_plot(theCollection, howToPlotGraph)
                theData.set_data(x, y)

    def get_idCollection_from_graph(self, idGraph, idTrace, getMaster=True):
        """From indices in the graph, get index of corresponding collection"""
        idColInGraph = self.get_mappingData_trace(idGraph, idTrace)
        if getMaster:
            idColMaster = self.collectionLinks.get_collection_master(idColInGraph)
        else:
            idColMaster = idColInGraph
        return idColMaster

    def get_collection_from_graph(self, idGraph, idTrace, getMaster=True):
        """From indices in the graph, get corresponding collection"""
        return self.collectionInfos[self.get_idCollection_from_graph(idGraph, idTrace, getMaster)].get_collection()

    def get_dataObject_from_graph(self, idGraph, idTrace, idPoint):
        theCol = self.get_collection_from_graph(idGraph, idTrace)
        theData = self.theGraphs.get_graph(idGraph).get_trace(idTrace)
        index_in_data = theData.get_dataIndex_from_graphIndex(idPoint)
        return theCol.get_data()[index_in_data]

    def get_dataObjects_from_graph(self, idGraph, idTrace, idPoint_list):
        theCol = self.get_collection_from_graph(idGraph, idTrace)
        theData = self.theGraphs.get_graph(idGraph).get_trace(idTrace)
        indices_in_data = theData.get_dataIndices_from_graphIndices(idPoint_list)
        return [theCol.get_data()[index_in_data] for index_in_data in indices_in_data]

    def remove_element_from_graph(self, idGraph, idTrace, idPoint, deleteFromMaster=False):
        """Remove element from the graph, or the master collection"""
        theCol = self.get_collection_from_graph(idGraph, idTrace, getMaster=deleteFromMaster)
        theData = self.theGraphs.get_graph(idGraph).get_trace(idTrace)
        index_in_data = theData.get_dataIndex_from_graphIndex(idPoint)
        del theCol.get_data()[index_in_data]

    def remove_elements_from_trace(self, idGraph, idTrace, idPoints, deleteFromMaster=False):
        """Performances optimisation when compared to :meth:`LinkDataGraph.remove_element_from_graph`"""
        theCol = self.get_collection_from_graph(idGraph, idTrace, getMaster=deleteFromMaster)
        theData = self.theGraphs.get_graph(idGraph).get_trace(idTrace)
        indices_in_data = theData.get_dataIndices_from_graphIndices(idPoints)
        delete_indices_from_list(indices_in_data, theCol.get_data())

    def link_collection_to_graph_collection(self, id_collection_graph, id_collection_master):
        """
        Link data
        :param id_collection_graph:
        :param id_collection_master:
        :return:
        """
        self.collectionLinks.add_link(id_collection_graph, id_collection_master)

    def remove_trace(self, idGraph, idTrace):
        self.theGraphs.remove_trace(idGraph, idTrace)
        del self.mappingData[idGraph][idTrace]

    def get_graph_and_trace_from_collection(self, idCollection):
        """Reverse search: from a collection, get the associated graph"""
        res = list()
        for idGraph in self.mappingData:
            for idTrace in self.get_mappingData_graph(idGraph):
                if self.get_mappingData_graph(idGraph)[idTrace] == idCollection:
                    res.append((idGraph, idTrace))
        return res, self.get_collectionInfo(idCollection).get_collection()

    def get_mappingData_graph(self, idGraph):
        return self.mappingData[idGraph]

    def get_mappingData_trace(self, idGraph, idTrace):
        return self.get_mappingData_graph(idGraph)[idTrace]
