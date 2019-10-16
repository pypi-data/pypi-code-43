import networkx as nx
from gensim.models.keyedvectors import Word2VecKeyedVectors
from nltk import WordNetLemmatizer

import numpy as np
from gensim import corpora, models
from fuzzywuzzy import fuzz

from sekg.graph.exporter.graph_data import GraphData
from sekg.graph.util.name_searcher import KGNameSearcher
from sekg.ir.models.base import DocumentSimModel
from sekg.ir.preprocessor.ngram import NGramPreprocessor
from sekg.util.annotation import exeTime

from sekg.graph.el.base import EntryPointLinker, EntityLinkResult
from sekg.constant.constant import OperationConstance, DomainConstant, WikiDataConstance, CodeConstant

import json
json.encoder.FLOAT_REPR = lambda x: format(x, '.3f')


class BestSeqSelector:

    def __init__(self, top_num=1):
        self.keyword2candidate_map = {}
        self.G = nx.Graph()
        self.best_selection = []
        self.best_score = []
        self.now_num = 0
        self.top_num = top_num

    def get_candidate_ids(self):
        result = set([])
        for keyword, ids in self.keyword2candidate_map.items():
            result = result | ids
        return list(result)

    def get_keyword_list(self):
        return list(self.keyword2candidate_map.keys())

    def add_candidate_for_keyword(self, keyword, candidate_node_id, score):
        if keyword not in self.keyword2candidate_map:
            self.keyword2candidate_map[keyword] = set([])

        self.keyword2candidate_map[keyword].add(candidate_node_id)
        self.add_candidate_entity_score(node_id=candidate_node_id, score=score)

    def add_candidate_entity_score(self, node_id, score):
        self.G.add_node(node_id, score=score)

    def add_pair_score(self, start_id, end_id, score):
        self.G.add_edge(start_id, end_id, score=score)

    def search_best_k_combination(self):
        self.chosen([], score=0.0, current_chosen_keyword_index=0)
        return self.get_best_k_selection()

    def search_best_combination(self):
        self.chosen([], score=0.0, current_chosen_keyword_index=0)
        return self.get_best_selection()

    def get_best_score(self):
        return self.best_score

    def get_best_selection(self):
        keyword_list = self.get_keyword_list()
        result = {}
        for keyword, node_id in zip(keyword_list, self.best_selection):
            result[keyword] = node_id[0]
        return result

    def get_best_k_selection(self):
        keyword_list = self.get_keyword_list()
        result = []
        for node_list in self.best_selection:
            temp = {}
            for keyword, node_id in zip(keyword_list, node_list):
                temp[keyword] = node_id
            result.append(temp)
        return result

    def insert(self, score, history_chosen, current_chosen_keyword_index):
        if self.now_num == 0:
            self.best_score.append(score)
            self.best_selection.append(history_chosen)
            self.now_num += 1
            return True
        else:
            tag = False
            score_index = 0
            while score_index < self.now_num:
                if self.best_score[score_index] < score:
                        self.best_score.insert(score_index, score)
                        self.best_selection.insert(score_index, history_chosen)
                        self.now_num += 1
                        tag = True
                        break
                score_index += 1
            if self.now_num >= self.top_num:
                self.now_num = self.top_num
                self.best_score = self.best_score[:self.top_num]
                self.best_selection = self.best_selection[:self.top_num]
            return tag

    def chosen(self, history_chosen, score, current_chosen_keyword_index):
        if current_chosen_keyword_index >= len(self.get_keyword_list()):
            tag = self.insert(score, history_chosen, current_chosen_keyword_index)
            if not tag:
                return
        else:
            current_keyword = self.get_keyword_list()[current_chosen_keyword_index]

            candidate_ids = self.keyword2candidate_map[current_keyword]

            for candidate_entity_id in candidate_ids:
                extra_score = self.G.nodes[candidate_entity_id]["score"]

                for history_chosen_entity_id in history_chosen:
                    extra_score += self.G[candidate_entity_id][history_chosen_entity_id]["score"]

                self.chosen(history_chosen + [candidate_entity_id], score=score + extra_score,
                            current_chosen_keyword_index=current_chosen_keyword_index + 1)


class PatternEntityPointLinker(EntryPointLinker):
    DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT = 3

    def __init__(self, preprocessor: NGramPreprocessor,
                 doc_sim_model: DocumentSimModel,
                 kg_name_searcher: KGNameSearcher,
                 graph2vecModel: Word2VecKeyedVectors,
                 graph_data: GraphData,
                 top_num=1
                 ):
        self.preprocessor = preprocessor
        self.doc_sim_model = doc_sim_model
        self.graph2vecModel = graph2vecModel
        self.kg_name_searcher = kg_name_searcher
        self.graph_data = graph_data
        self.lemmatizer = WordNetLemmatizer()
        # to start the util
        self.candidate_list = {}
        self.lemmatizer.lemmatize(word="test")
        self.selector = BestSeqSelector(top_num=top_num)

    def score_full_name(self, candidate_node_ids, keyword, keywords, name_score_map, original_query):
        new_keywords = set([])
        for keyword in keywords:
            new_keywords.add(keyword.lower())
        keywords = new_keywords
        clean_query_string = " ".join(list(keywords))
        # Step 1：计算备选集合之中出现的alias的TF-IDF值，将alias转化为n_array，用于便于后续相似度加成
        alias_list = []
        for node_id in candidate_node_ids:
            alias_list.append(list(self.kg_name_searcher.get_full_names(node_id)))
        dictionary = corpora.Dictionary(alias_list)
        new_corpus = [dictionary.doc2bow(text) for text in alias_list]
        tfidf = models.TfidfModel(new_corpus)

        # 计算 weight array
        weight_array = np.zeros(shape=(len(alias_list), len(dictionary)), dtype=float)
        for index, alias in enumerate(alias_list):
            string_bow = dictionary.doc2bow(alias)
            string_tfidf = tfidf[string_bow]
            for item in string_tfidf:
                weight_array[index, item[0]] = item[1]
        # Step 2：计算得到每个alias的分数向量, 取其加权平均数
        score_array = np.zeros(shape=(len(candidate_node_ids), len(dictionary)), dtype=float)
        for index, node_id in enumerate(candidate_node_ids):
            score = self.compute_position_name_score_for_one_node(
                keywords,
                dictionary,
                clean_query_string,
                node_id,
                original_query,
                len(dictionary)
            )
            if node_id not in name_score_map:
                if score > 0.5:
                    name_score_map[node_id] = score
            elif name_score_map[node_id] < score and score > 0.5:
                name_score_map[node_id] = score
        return name_score_map

    def compute_position_name_score_for_one_node(self, keywords, dictionary, query_string, node_id, original_query,
                                                 dim):
        full_names = self.kg_name_searcher.get_full_names(node_id)
        alia_vec = dictionary.doc2bow(full_names)
        score_vec = np.zeros(shape=(1, dim), dtype=float)
        for index, full_name in enumerate(full_names):
            full_name = self.lemmatizer.lemmatize(full_name.lower())
            query_string = self.lemmatizer.lemmatize(query_string.lower())
            original_query = self.lemmatizer.lemmatize(original_query.lower())
            name_set = set(full_name.split(" "))
            word_count = len(name_set)
            tokens = name_set & keywords
            token_score = 1.0 * len(tokens) / word_count

            appearing = 0.0
            for word in name_set:
                if word in query_string.split():
                    appearing += 1
                elif word in original_query.split():
                    appearing += 1

            appearing_score = appearing / word_count
            index_id = alia_vec[index][0]
            score_vec[0, index_id] = max([token_score, appearing_score])

        return max(list(score_vec[0, :]))

    def extract_keywords(self, query):
        keywords = self.preprocessor.get_n_gram_list(query)
        return keywords

    @exeTime
    def link(self, query, candidate_num=DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT):
        return self.link_n(query, top_num=1, candidate_num=candidate_num)[0]

    @exeTime
    def link_n(self, query, top_num=1, candidate_num=DEFAULT_CANDIDATE_NUM_FOR_EVERY_POINT):
        keywords = self.extract_keywords(query)
        selector = BestSeqSelector(top_num=top_num)
        doc_id_2_doc_retrieval_result_map = {}
        keyword_to_candidate_list_map = dict()

        for keyword in keywords:
            doc_retrieval_result_list = self.get_candidate_for_keyword(
                candidate_num=candidate_num,
                keyword=keyword,
                query=query,
                keywords=keywords,
                name_score_map={},
                node_type="n")
            for key, value in doc_retrieval_result_list.items():
                if len(value) > 0:
                    keyword_to_candidate_list_map[key] = value

        for keyword, doc_retrieval_result_list in keyword_to_candidate_list_map.items():

            for doc_retrieval_result in doc_retrieval_result_list:
                selector.add_candidate_for_keyword(keyword=keyword,
                                                   candidate_node_id=doc_retrieval_result.doc_id,
                                                   score=doc_retrieval_result.score)

                doc_id_2_doc_retrieval_result_map[doc_retrieval_result.doc_id] = doc_retrieval_result
        candidate_ids = selector.get_candidate_ids()

        vector_map = {}

        all_vectors = []

        new_ids = []

        for candidate_id in candidate_ids:
            try:
                vector_map[candidate_id] = self.graph2vecModel.wv[str(candidate_id)]
                all_vectors.append(vector_map[candidate_id])
                new_ids.append(candidate_id)
            except Exception:
                print("No node:", str(candidate_id))
                continue
        candidate_ids = new_ids

        if len(keywords) == 1:
            rate = 0.0
        else:
            rate = 2.0 / (len(list(set(keywords))) - 1.0)

        for start_id in candidate_ids:
            start_vector = vector_map[start_id]
            sim_vector = self.graph2vecModel.wv.cosine_similarities(start_vector, all_vectors)

            for end_id, score in zip(candidate_ids, sim_vector):
                selector.add_pair_score(start_id=start_id, end_id=end_id, score=score * rate)

        best_linking_result = selector.search_best_k_combination()
        result = []
        for index in range(top_num):
            result.append({})
        index = 0
        for node_list in best_linking_result:
            for keyword, node_id in node_list.items():
                doc_retrieval_result = doc_id_2_doc_retrieval_result_map[node_id]
                result[index][keyword] = EntityLinkResult(mention=keyword, node_id=node_id,
                                                          node_name=doc_retrieval_result.doc_name,
                                                          score=doc_retrieval_result.score)
            index += 1

        return result

    def get_candidate_for_keyword(self, candidate_num,
                                  keyword,
                                  query,
                                  name_score_map,
                                  keywords,
                                  node_type):

        new_keyword = self.lemmatizer.lemmatize(keyword.lower(), pos=node_type)
        word_list = new_keyword.split()
        full_name_match_id_set = self.kg_name_searcher.search_by_full_name(new_keyword)
        keyword_match_id_set = self.kg_name_searcher.search_by_keyword(new_keyword)
        if len(full_name_match_id_set | keyword_match_id_set) == 0 and len(word_list) > 1:
            link_result = {}
            for word in word_list:
                for key, value in self.get_candidate_for_keyword(candidate_num,
                                                                 word,
                                                                 query,
                                                                 name_score_map,
                                                                 keywords,
                                                                 node_type).items():
                    if key not in link_result:
                        link_result[key] = value
            return link_result
        else:
            candidate_doc_result_list = []
            # 全名搜索
            # get the operation id
            operation_ids = self.graph_data.get_node_ids_by_label(OperationConstance.LABEL_OPERATION)
            # get the domain id
            domain_term_ids = self.graph_data.get_node_ids_by_label(DomainConstant.LABEL_DOMAIN_TERM)
            wiki_terms_ids = self.graph_data.get_node_ids_by_label(WikiDataConstance.LABEL_WIKIDATA)
            code_terms_ids = self.graph_data.get_node_ids_by_label(CodeConstant.LABEL_CODE_ELEMENT)

            concept_term_ids = domain_term_ids | wiki_terms_ids

            if len(operation_ids & full_name_match_id_set) > 0:
                full_name_match_id_set = operation_ids & full_name_match_id_set
                keyword_match_id_set = operation_ids & keyword_match_id_set
            elif len(concept_term_ids & full_name_match_id_set) > 0:
                # search in domain:
                full_name_match_id_set = concept_term_ids & full_name_match_id_set
                keyword_match_id_set = concept_term_ids & keyword_match_id_set
            full_name_match_id_set = full_name_match_id_set - code_terms_ids
            keyword_match_id_set = keyword_match_id_set - full_name_match_id_set - code_terms_ids

            del operation_ids, domain_term_ids, wiki_terms_ids, concept_term_ids, code_terms_ids

            chosen_ids = set([])

            large_candidate_num = candidate_num + 20

            doc_retrieval_result_list = []

            if len(full_name_match_id_set) > 0:
                doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=large_candidate_num,
                                                                      valid_doc_id_set=full_name_match_id_set)

                for doc in doc_retrieval_result_list:
                    if doc.doc_id not in chosen_ids:
                        chosen_ids.add(doc.doc_id)
                        candidate_doc_result_list.append(doc)

            if len(keyword_match_id_set) > 0:
                doc_retrieval_result_list = self.doc_sim_model.search(query=query, top_num=large_candidate_num,
                                                                      valid_doc_id_set=keyword_match_id_set)

                for doc in doc_retrieval_result_list:
                    if doc.doc_id not in chosen_ids:
                        chosen_ids.add(doc.doc_id)
                        candidate_doc_result_list.append(doc)

            self.score_full_name(candidate_node_ids=list(chosen_ids), keyword=keyword,  keywords=keywords, name_score_map=name_score_map,
                                 original_query=query)

            # compute the total score of a node
            new_candicate_list = []
            for candidate_doc in candidate_doc_result_list:
                if candidate_doc.doc_id in name_score_map:
                    candidate_doc.extra_info["name_score"] = name_score_map[candidate_doc.doc_id]
                    candidate_doc.extra_info["doc_score"] = candidate_doc.score
                    candidate_doc.score = candidate_doc.extra_info["name_score"]
                    name = ""
                    if "term_name" in self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]:
                        name = self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]["term_name"]
                    elif "wikidata_name" in self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]:
                        name = self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]["wikidata_name"]
                    elif "name" in self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]:
                        name = self.graph_data.get_node_info_dict(candidate_doc.doc_id)["properties"]["name"]
                    candidate_doc.extra_info["token_score"] = fuzz.ratio(keyword, name) / 100
                    candidate_doc.score = candidate_doc.extra_info["name_score"] * 0.4 + \
                                          candidate_doc.extra_info["token_score"] * 0.6
                    new_candicate_list.append(candidate_doc)
                    new_candicate_list = sorted(new_candicate_list, key=lambda candidate_doc: candidate_doc.score,
                                                reverse=True)

            return {keyword: new_candicate_list[:candidate_num]}
