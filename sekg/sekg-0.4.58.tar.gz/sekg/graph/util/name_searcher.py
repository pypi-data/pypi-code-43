import gensim

from sekg.graph.exporter.graph_data import GraphData, GraphDataReader, NodeInfoFactory


class KGNameSearcher(gensim.utils.SaveLoad):
    """
    search some node in KG by some keyword.

    two way to train a KGNameSearcher.
    1. implement a sekg.graph.exporter.graph_data.NodeInfoFactory based on your purpose. need to create implement some
    new NodeInfo classes based on Node Data in Graph. And call train_from_graph_data_file.
    2. Call train_from_graph_data_file_by_names_properties and specify the name properties need to search on.

    """

    def __init__(self):
        self.full_name_2_id_set_map = {}
        self.id_2_full_name_set_map = {}
        self.keyword_2_id_set_map = {}
        self.id_2_keyword_set_map = {}

    @staticmethod
    def train_from_graph_data_file(graph_data_path, node_info_factory: NodeInfoFactory):
        """
        train the kg name searcher model from a graph data object
        :param node_info_factory: the nodeInfoFactory to create node from node json
        :param graph_data_path:
        :return:
        """
        graph_data: GraphData = GraphData.load(graph_data_path)

        searcher = KGNameSearcher()
        searcher.train(graph_data, node_info_factory)
        return searcher

    @staticmethod
    def train_from_graph_data_file_by_names_properties(graph_data_path, *name_properties):
        """
        train the kg name searcher model from a graph data object by specifying name properties.
        :param name_properties: the name properties that need to be searched on, could be more than one. e.g., "name","qualified_name","labels_en"
        :param graph_data_path:the path of graph data.
        :return:
        """
        graph_data: GraphData = GraphData.load(graph_data_path)

        searcher = KGNameSearcher()
        searcher.train_by_names_properties(graph_data, *name_properties)
        return searcher

    def train(self, graph_data: GraphData, node_info_factory: NodeInfoFactory):
        """
        train the kg name searcher model from a graph data object
        :param node_info_factory: the nodeInfoFactory to create node from node json
        :param graph_data: GraphData instance
        :return:
        """
        graph_data_reader = GraphDataReader(graph_data=graph_data, node_info_factory=node_info_factory)
        # todo: change the read all node from KG by iterate

        for id in graph_data.get_node_ids():
            node_info = graph_data_reader.get_node_info(id)
            name_list = node_info.get_all_names()
            for name in name_list:
                self.add_from_one_name_for_id(name, id)

    def train_by_names_properties(self, graph_data: GraphData, *name_properties):
        """
        train the kg name searcher model from a graph data object by specifying name properties.
        :param name_properties: the name properties that need to be searched on. e.g., "name","qualified_name","labels_en"
        :param graph_data: the GraphData instance
        :return:
        """
        for node_id in graph_data.get_node_ids():
            node_properties = graph_data.get_properties_for_node(node_id=node_id)
            for name_property in name_properties:
                name_value = node_properties.get(name_property, None)
                if not name_value:
                    continue
                if type(name_value) == list or type(name_value) == set:
                    name_list = name_value
                    for name in name_list:
                        self.add_from_one_name_for_id(name, node_id)

                else:
                    name = name_value
                    self.add_from_one_name_for_id(name, node_id)

    def add_full_name_for_id(self, name, id):
        if not name:
            return
        if name not in self.full_name_2_id_set_map.keys():
            self.full_name_2_id_set_map[name] = set([])
        if id not in self.id_2_full_name_set_map.keys():
            self.id_2_full_name_set_map[id] = set([])

        self.full_name_2_id_set_map[name].add(id)
        self.id_2_full_name_set_map[id].add(name)

    def add_keyword_for_id(self, keyword, id):
        if not keyword:
            return
        if keyword not in self.keyword_2_id_set_map.keys():
            self.keyword_2_id_set_map[keyword] = set([])
        if id not in self.id_2_keyword_set_map.keys():
            self.id_2_keyword_set_map[id] = set([])

        self.keyword_2_id_set_map[keyword].add(id)

        self.id_2_keyword_set_map[id].add(keyword)

    def add_keyword_map_from_full_name(self, full_name, id):
        ## todo: change this to fix all

        full_name = full_name.split("(")[0]
        full_name = full_name.replace("-", " ").replace("(", " ").replace(")", " ").strip()

        self.add_keyword_for_id(full_name, id)

        name_words = full_name.split(" ")
        for word in name_words:
            self.add_keyword_for_id(word, id)
            self.add_keyword_for_id(word.lower(), id)

    def add_from_one_name_for_id(self, name, node_id):
        """
        add all the cache for search on the name. e.g., the lower name, the separate keywords for keywords search.
        :param name: the name value.
        :param node_id: the node with the name
        :return:
        """
        self.add_full_name_for_id(name, node_id)
        self.add_full_name_for_id(name.lower(), node_id)
        self.add_keyword_map_from_full_name(name, node_id)
        self.add_keyword_map_from_full_name(name.lower(), node_id)

    def search_by_full_name(self, full_name):
        if full_name in self.full_name_2_id_set_map.keys():
            return self.full_name_2_id_set_map[full_name]
        full_name = full_name.lower()
        if full_name in self.full_name_2_id_set_map.keys():
            return self.full_name_2_id_set_map[full_name]
        return set([])

    def search_by_keyword(self, word):
        if word in self.keyword_2_id_set_map.keys():
            return self.keyword_2_id_set_map[word]
        word = word.lower()

        if word in self.keyword_2_id_set_map.keys():
            return self.keyword_2_id_set_map[word]

        return set([])

    def get_full_names(self, id):
        if id not in self.id_2_full_name_set_map:
            return set([])
        else:
            return self.id_2_full_name_set_map[id]

    def clear(self):
        self.full_name_2_id_set_map = {}
        self.id_2_full_name_set_map = {}
        self.keyword_2_id_set_map = {}
        self.id_2_keyword_set_map = {}
