import spacy

from nltk.corpus import stopwords
import nltk
import re
from nltk.stem import WordNetLemmatizer

from sekg.ir.preprocessor.base import Preprocessor
from sekg.graph.util.name_searcher import KGNameSearcher

simplenlp = spacy.load('en', disable=["ner", "parser"])
nlp = spacy.load('en')


# todo: the preprocess could change to almost same as extract domain Entity_NP, by fixing the tokenize problem

class SpacyTextPreprocessor(Preprocessor):
    def __init__(self, kg_name_searcher=None):
        self.name_searcher = kg_name_searcher
        self.lemmatizer = WordNetLemmatizer()

    def extract_concept_and_operation(self, query):
        np_list = []
        v_list = []
        # remove stop_word
        new_query = query
        # 处理引号问题
        words = re.split(r"\"|'", new_query)
        if len(words) % 2 == 0:
            words.pop(len(words) - 1)
        for index, np in enumerate(words):
            if index % 2 == 1 and len(str(np)) > 0:
                lemma_token = self.lemmatizer.lemmatize(np)
                # 将得到的特殊词汇进行替换 替换为NP
                new_query = new_query.replace(str("\"" + np + "\""), "Entity_NP")
                np_list.append(lemma_token)
        del words
        doc = nlp(new_query)
        for np in doc.noun_chunks:
            lemma_token = np.lemma_
            # 将得到的名词进行替换 替换为NP
            if lemma_token != "Entity_NP":
                new_query = new_query.replace(str(np), "Entity_NP")
                lemma_token = " ".join(
                    [w for w in nltk.word_tokenize(lemma_token) if w not in stopwords.words('english')])
                lemma_token = lemma_token.replace("Entity_NP", "")
                lemma_token = lemma_token.strip()
                if len(lemma_token) > 0:
                    np_list.append(lemma_token)
        # 相邻的np进行合并，合并新的np
        if len(np_list) > 0:
            np_position = [[index, item] for index, item in enumerate(new_query.split()) if item == "Entity_NP"]
            index = np_position[0][0] + 1
            for i in range(1, len(np_position)):
                if index == np_position[i][0]:
                    np_list[i - 1] += (" " + np_list[i])
                    np_list.pop(i)
                    index += 1
                else:
                    index = np_position[i][0] + 1
        doc = nlp(query)
        for token in doc:
            if token.pos_ == "VERB" and token.is_stop is False:
                # 提取动词
                verb_lemma = token.lemma_
                v_list.append(verb_lemma)
            elif token.pos_ != "NOUN" and token.is_stop is False:
                # 提取其他词汇之中含有同名概念或者操作节点的短语， 若是概念短语，则定义为concept，否则是operation
                token_lemma = token.lemma_
                if len(self.name_searcher.search_by_full_name(token_lemma)) > 0 \
                        and token_lemma not in stopwords.words('english'):
                    tag = False
                    for item in np_list:
                        if token_lemma in item:
                            tag = True
                            break
                    if not tag:
                        np_list.append(token_lemma)
        new_np_list = []
        for item in np_list:
            pattern = re.findall("(\s+[^a-zA-Z1-90]+\s+)", item)
            for p in pattern:
                item = item.replace(p, " ")
            pattern = re.findall("([^a-zA-Z1-90]+\s+)", item)
            for p in pattern:
                item = item.replace(p, " ")
            pattern = re.findall("(\s+[^a-zA-Z1-90]+)", item)
            for p in pattern:
                item = item.replace(p, " ")
            new_np_list.append(item)
        np_list = new_np_list
        del new_np_list
        # 删除特殊字符
        np_list = [re.sub("([^a-zA-Z1-90-]+)", " ", item, count=0, flags=0).strip() for item in np_list]
        np_list = [item for item in np_list if len(re.findall("([a-z|A-Z|1-9|0]+)", item)) > 0]
        return np_list, v_list

    def extract_words_for_query(self, query):
        np_v_list = []

        doc = nlp(query)
        for np in doc.noun_chunks:
            np_words = []
            for np_token in np:
                lemma_token = np_token.lemma_
                if np_token.is_stop:
                    continue

                if np_token.is_digit == True:
                    continue

                if np_token.is_punct == True:
                    continue

                np_words.append(lemma_token)

            clean_np_str = " ".join(np_words)
            if clean_np_str:
                np_v_list.append(clean_np_str)

        for token in doc:
            if token.is_stop == True:
                continue
            if token.is_digit == True:
                continue

            if token.is_punct == True:
                continue

            if token.pos_ == "VERB" and token.is_stop == False:
                verb_lemma = token.lemma_
                np_v_list.append(verb_lemma)

        # todo: extract CamelName split as keyword from this

        return set(" ".join(np_v_list).split())

    def clean(self, text):
        """
        return a list of token from the text, only remove stopword and lemma the word
        :param text: the text need to preprocess
        :return: list of str
        """

        result = []
        doc = simplenlp(text)

        for token in doc:
            if token.is_stop is True:
                continue
            if token.is_digit is True:
                continue

            if token.is_punct is True:
                continue

            result.append(token.lemma_.lower())

        return result
