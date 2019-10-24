from sekg.graph.util.name_searcher import KGNameSearcher
from sekg.ir.preprocessor.base import Preprocessor

import re
from itertools import combinations
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class NGramPreprocessor(Preprocessor):
    LENGTH_PRIORITY = 0
    ORDER_PRIORITY = 1

    def __init__(self, n, kg_name_searcher):
        self.n = n
        self.lemmatizer = WordNetLemmatizer()
        self.name_searcher = kg_name_searcher

    def get_n_gram_list(self, query, split_type=LENGTH_PRIORITY):
        entities = []
        words = re.split(r"\"|'", query)
        if len(words) % 2 == 0:
            words.pop(len(words) - 1)
        for index, np in enumerate(words):
            if index % 2 == 1 and len(str(np)) > 0:
                lemma_token = self.lemmatizer.lemmatize(np)
                # 将得到的特殊词汇进行替换 替换为NP
                query = query.replace(str("\"" + np + "\""), "Entity_NP")
                entities.append(lemma_token)
        del words
        paragraph = re.split("[,|.|?|!|:|;]", query)
        # 处理引号问题
        for p in paragraph:
            words = [self.lemmatizer.lemmatize(w) for w in re.split("[\s|/|+|\\|(|)]", p.lower()) if len(w) > 0]
            print(words)
            # words = [w for w in words if w not in stopwords.words('english')]
            no_word = []
            delete_index = []
            w_size = self.n
            if split_type == self.ORDER_PRIORITY:
                index = 0
                while index < len(words):
                    t_tag = min(index + w_size, len(words) - index)
                    while t_tag >= 1:
                        if len(self.name_searcher.search_by_full_name(" ".join(words[index:index + t_tag]))) > 0:
                            entities.append(" ".join(words[index:index + t_tag]))
                            index += t_tag
                            break
                        else:
                            t_tag -= 1
                    if t_tag == 0:
                        no_word.append(words[index])
                        index += 1
            elif split_type == self.LENGTH_PRIORITY:
                index = 0
                while index < len(words):
                    t_tag = min(index + w_size, len(words) - index)
                    while t_tag >= 1:
                        for item in list(combinations(words[index:index + w_size], t_tag)):
                            if len(self.name_searcher.search_by_full_name(" ".join(item))) > 0:
                                if " ".join(list(item)) not in entities:
                                    entities.append(" ".join(list(item)))
                        t_tag -= 1
                    index += 1
        new_entities = []
        for key in entities:
            tag = False
            for item in entities:
                if key != item and key in item:
                    tag = True
            if not tag and key not in stopwords.words('english'):
                new_entities.append(key)
                new_entities = [w for w in new_entities if w.isalnum() and not w.isnumeric()]
        return new_entities


if __name__ == "__main__":
    name_searcher = KGNameSearcher.load(
        "E:\PycharmProjects\KGFeatureLocation\output\graph\jedite-4.3\\NameSearcher\jedite-4.3.v4.2.namesearcher"
    )
    preprocessor = NGramPreprocessor(4, kg_name_searcher=name_searcher)
    query_str = [
        "folding bug, text is in a black hole",
        "Size of file open/save dialogs incorrect on dual displays",
        "Incorrect Python code indentation",
        "Search expression",
        "Autosave turned off for Untitled Documents",
        "Keyboard navigation through menubar inserts char into buffer",
        "Add filter to recent files menu",
        "File Open Dialog: can't handle full pathnames",
        "Provide a way of reloading changed buffers without prompting",
        "Rectangular Selection and Dragging",
        "Filter Bug in File System Browser",
        "Auto-indent breaks if previous line is a single line indent",
        "set \"Search for:\" to \"||\" check \"Regular expressions\" click \"Replace All\" version : jEdit 4.3pre8",
        "Wrong conversion to UTF-16 (with BOM)",
        "caret/display position w/ multiple views open",
    ]
    for query in query_str:
        print(preprocessor.get_n_gram_list(query, preprocessor.LENGTH_PRIORITY))


