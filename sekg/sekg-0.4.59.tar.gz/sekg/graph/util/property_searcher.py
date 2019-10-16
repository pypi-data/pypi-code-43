from pathlib import Path

import gensim

from sekg.graph.exporter.graph_data import GraphData


class KGPropertySearcher(gensim.utils.SaveLoad):
    """
    Search some node in KG on some properties by value.
    Call train()/start_training() and specify the name properties need to search on.
    """

    def __init__(self):
        self.full_name_2_id_set_map = {}
        self.id_2_full_name_set_map = {}
        self.keyword_2_id_set_map = {}
        self.id_2_keyword_set_map = {}

    @classmethod
    def train(cls, graph_data: GraphData or str or Path, *properties):
        """
        train the kg name searcher model from a graph data object by specifying name properties.
        :param properties: the properties that need to be searched on, could be more than one. e.g., "name","qualified_name","labels_en"
        :param graph_data:the path of graph data.
        :return:
        """
        # todo: add some config arguments, to control whether lower the case, split the words.
        if graph_data == None:
            raise Exception("Input GraphData object not exist")

        graph_data_source = None
        if type(graph_data) == str:
            graph_data_source: GraphData = GraphData.load(graph_data)
        if type(graph_data) == Path:
            graph_data_source: GraphData = GraphData.load(str(graph_data))
        if type(graph_data) == GraphData:
            graph_data_source = graph_data

        if graph_data_source is None:
            raise Exception("can't find the graph data")

        searcher = cls()
        searcher.start_training(graph_data_source, *properties)
        return searcher

    def start_training(self, graph_data: GraphData, *properties):
        """
        start train the kg name searcher model from a graph data object by specifying name properties.
        :param properties: the properties that need to be searched on. e.g., "name","qualified_name","labels_en"
        :param graph_data: the GraphData instance
        :return:
        """
        # todo: add some config arguments, to control whether lower the case, split the words.
        self.clear()
        for node_id in graph_data.get_node_ids():
            node_properties = graph_data.get_properties_for_node(node_id=node_id)
            for name_property in properties:
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
