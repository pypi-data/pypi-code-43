"""
this class is for analysis the sentence based on dependency tree.

"""
import spacy
from spacy.tokens.doc import Doc

from sekg.util.spacy_fixer import SoftwareTextPOSFixer
from sekg.util.vocabulary_conversion.vocabulary_conversion import VocabularyConversion

from sekg.util.sentenceHandler import SentenceHandler


class DependencyTreeUtil:
    nlp = spacy.load('en', disable=["ner"])
    nlp.add_pipe(SentenceHandler.hyphen_handler, name='sh', before='tagger')
    # 将核心动词与紧挨着的head是这个动词的介词合并
    # nlp.add_pipe(SentenceHandler.merge_verb_prep, name='merge_verb_prep', after='parser')
    nlp.add_pipe(SoftwareTextPOSFixer.fixer_for_pos, name="pos_fixer", after="tagger")

    @staticmethod
    def get_attr_for_be_predicate(doc, predicate_token=None):
        """
        主要是获取主系表中的表语，形容词或者名词，可以用来抽
        the input is the sentence Spacy Doc
        :param doc:
        :return: Span noun chunk for the subject, None for not found.
        """
        if predicate_token == None:
            predicate_token = DependencyTreeUtil.get_main_predicate(doc)
        if predicate_token == None:
            return None
        for possible_attr in doc:
            if possible_attr.dep_ == "attr" and possible_attr.head == predicate_token:
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_attr)
            if possible_attr.dep_ == "acomp" and possible_attr.head == predicate_token:
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_attr)

    @staticmethod
    def split_span_into_parallel(doc, span):
        span_list = []
        if span is None or span.text == "":
            return span_list
        try:
            span_root = span.root
            other_parallel_root_tokens = []
            for token in doc:
                if token.dep_ == "appos" and token.head == span_root:
                    other_parallel_root_tokens.append(token)
                if token.dep_ == "cc" and token.head == span_root:
                    other_parallel_root_tokens.append(token)
            # if len(other_parallel_root_tokens) == 0:
            #     span_list.append(span)
            #     return span_list
            for t in [span_root] + other_parallel_root_tokens:
                left_sub_tree_span = DependencyTreeUtil.get_left_subtree_and_itself_span(doc=doc, token=t)
                span_list.append(left_sub_tree_span)
        except Exception as e:
            print(e)
        return span_list

    @staticmethod
    def get_left_subtree_and_itself_span(doc, token):
        lefts = [t for t in token.lefts]
        index = 0
        pre_index = 0
        for i, or_token in enumerate(doc):
            if or_token.text == token.text:
                index = i
            if len(lefts) > 0:
                if or_token.text == lefts[0].text:
                    pre_index = i
        if len(lefts) == 0:
            return doc[index:index + 1]
        return doc[pre_index:(index + 1)]

    @staticmethod
    def get_main_predicate(doc):
        root = [token for token in doc if token.dep_ == "ROOT"][0]
        if root.pos_ == "VERB" or root.pos_ == 'ADJ':
            return root
        else:
            return None

    @staticmethod
    def get_conj_predicate(doc):
        token_list = []
        for token in doc:
            if token.pos_ == "VERB" and token.head.tag_ == "cc" and token.head.head.dep_ == "ROOT":
                token_list.append(token)
        # token = [token for token in doc if token.pos_ == "VERB" and token.head == "cc" and token.head.head.dep_ == "ROOT"]
        return token_list

    @staticmethod
    def get_main_predicate_with_candidate_verbs(doc, verb_set):
        root = [token for token in doc if token.dep_ == "ROOT"][0]
        for i, token in enumerate(doc):
            if i == 0 and (token.lemma_ in verb_set or VocabularyConversion.couldBeVerb_probability(token.text)):
                return token
            if token.dep_ == "ROOT":
                root = token
                break

        if root.pos_ == "VERB" or (root.lemma_ is not None and root.lemma_ in verb_set):
            return root
        else:
            return None

    @staticmethod
    def is_vbn(doc):
        root = [token for token in doc if token.dep_ == "ROOT"][0]
        if root.pos_ == "VERB":
            if root.tag_ == 'VBN':
                return True
            return False
        else:
            return False

    @staticmethod
    def get_subject(doc):
        """
        the input is the sentence Spacy Doc
        :param doc:
        :return: Span noun chunk for the subject, None for not found.
        """
        for possible_subject in doc:
            if possible_subject.dep_ == "nsubj" and possible_subject.head.dep_ == "ROOT":
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_subject)

            if possible_subject.dep_ == "nsubjpass" and possible_subject.head.dep_ == "ROOT":
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_subject)

        # todo: need to improve for finding more situation. including some error about software text.

        predicate = DependencyTreeUtil.get_main_predicate(doc)
        ## the sentence is lack of the subject and start with verb. eg. "go to school".
        ## the problem of "sort a given number list" must be fixed.
        if predicate is not None and predicate.n_lefts == 0:
            return None

        root = [token for token in doc if token.dep_ == "ROOT"][0]

        if root.n_lefts == 0:
            return None
        else:
            return

    @staticmethod
    def get_subject_exclude_verb(doc, candidate_verb_set):
        """
        the input is the sentence Spacy Doc
        :return: Span noun chunk for the subject, None for not found.
        """
        for possible_subject in doc:
            if possible_subject.dep_ == "nsubj" and possible_subject.head.dep_ == "ROOT" and possible_subject.lemma_ not in candidate_verb_set:
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_subject)

            if possible_subject.dep_ == "nsubjpass" and possible_subject.head.dep_ == "ROOT" and possible_subject.lemma_ not in candidate_verb_set:
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=possible_subject)

        # todo: need to improve for finding more situation. including some error about software text.

        predicate = DependencyTreeUtil.get_main_predicate(doc)
        ## the sentence is lack of the subject and start with verb. eg. "go to school".
        ## the problem of "sort a given number list" must be fixed.
        if predicate is not None and predicate.n_lefts == 0:
            return None

        root = [token for token in doc if token.dep_ == "ROOT"][0]

        if root.n_lefts == 0:
            return None
        else:
            return None

    @staticmethod
    def get_subject_text(doc):

        subject = DependencyTreeUtil.get_subject(doc)
        if subject == None:
            return None
        return subject.text

    @staticmethod
    def get_subtree_span_from_one_token_obj(doc, token):
        if token == None:
            return None
        # for token_ in doc:
        #     if token_.lemma_ == token.lemma_:
        #         token = token_
        token_list = []
        DependencyTreeUtil.get_all_childern_token_under_one_token(doc, token, token_list)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[token.left_edge.i: token.right_edge.i + 1]
        return span[0: len(span) + 1]

    @staticmethod
    def get_subtree_span_from_one_token_obj_by_index(doc, token, i):
        if token == None:
            return None
        if token.text != doc[i].text:
            return None
        token_list = []
        DependencyTreeUtil.get_all_childern_token_under_one_token(doc, token, token_list)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[token.left_edge.i: token.right_edge.i + 1]
        return span[0: len(span) + 1]

    @staticmethod
    def get_subtree_span_from_token_by_index(doc, token):
        if token == None:
            return None
        span = doc[token.left_edge.i: token.right_edge.i + 1]
        return span

    @staticmethod
    def get_all_childern_token_under_one_token(doc, token, token_list):
        if token.lefts:
            for left in token.lefts:
                DependencyTreeUtil.get_all_childern_token_under_one_token(doc, left, token_list)
        token_list.append(token)
        if token.rights:
            for right in token.rights:
                DependencyTreeUtil.get_all_childern_token_under_one_token(doc, right, token_list)

    @staticmethod
    def get_all_childern_token_under_one_token_filter_one(doc, token, token_list, filter):
        if token.text == filter.text and token.tag_[:2] == filter.tag_[
                                                           :2] and token.left_edge.text == filter.left_edge.text and token.right_edge.text == filter.right_edge.text:
            # print('subject.root')
            # print(token.text)
            pass
        else:
            if token.lefts:
                for left in token.lefts:
                    DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one(doc, left, token_list, filter)
            token_list.append(token)
            if token.rights:
                for right in token.rights:
                    DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one(doc, right, token_list, filter)

    @staticmethod
    def get_all_childern_token_under_one_token_filter_one_for_split_sentence(doc, token, token_list, filter):
        if token.text == filter.text and token.tag_ == filter.tag_ and token.dep_ == filter.dep_ and token.head.text == filter.head.text:
            # print('subject.root')
            # print(token.text)
            pass
        else:
            if token.lefts:
                for left in token.lefts:
                    DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one_for_split_sentence(doc, left,
                                                                                                            token_list,
                                                                                                            filter)
            token_list.append(token)
            if token.rights:
                for right in token.rights:
                    DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one_for_split_sentence(doc, right,
                                                                                                            token_list,
                                                                                                            filter)

    @staticmethod
    def get_subtree_span_from_one_token_obj_for_vbn_and_root(doc, subject, token):
        if token is None:
            return None
        token_list = list()
        # for token_ in doc:
        #     if token_.lemma_ == token.lemma_:
        #         token = token_
        # print('subject.root.text')
        # print(subject.root)
        DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one(doc, token, token_list, subject.root)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[subject.root.right_edge.i+1: token.right_edge.i + 1]
        return span[0: len(span) + 1]

    @staticmethod
    def get_subtree_span_token_under_one_token_filter_one_for_split_sentence(doc, filter, token):
        if token == None:
            return None
        token_list = list()
        # for token_ in doc:
        #     if token_.lemma_ == token.lemma_:
        #         token = token_
        # print('subject.root.text')
        # print(subject.root)
        DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one_for_split_sentence(doc, token, token_list,
                                                                                                filter)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[subject.root.right_edge.i+1: token.right_edge.i + 1]
        return span[0: len(span) + 1]

    @staticmethod
    def get_token_children(doc, token):
        token_list = list()
        for token_ in doc:
            if token_.head == token:
                token_list.append(token_)
        if not token_list:
            return token
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        return span[0: len(span) + 1]

    @staticmethod
    def filter_front_prep_subtree(doc, predicate):
        return doc[predicate.i:]

    @staticmethod
    def swap_condition_to_end(doc, predicate):
        for token in doc:
            if token.dep_.startswith('aux') and token.head.text == predicate.text and token.head.dep_ == 'ROOT':
                swap_span = doc[0: token.i].text
                preidcate_span = doc[token.i:].text
                return preidcate_span.strip('.') + ' $$ ' + swap_span
            if token.head.text == predicate.head.text and token.text == predicate.text and predicate.dep_ == token.dep_:
                swap_span = doc[0: token.i].text
                # if token.i > 0:
                #     if doc[token.i - 1].dep_ == 'aux' and doc[token.i - 1].tag_ == 'MD':
                #         if token.i > 1:
                #             swap_span = doc[0: token.i - 1].text
                #             preidcate_span = doc[token.i - 1:].text
                #             return preidcate_span + ' ' + swap_span
                #     else:
                #         swap_span = doc[0: token.i].text

                preidcate_span = doc[token.i:].text
                return preidcate_span.strip('.') + ' $$ ' + swap_span
        return ""

    @staticmethod
    def get_subtree_span_from_one_token_filter_another_token_sub_tree(doc, filter, token):
        if token == None:
            return None
        token_list = list()

        # print('subject.root.text')
        # print(subject.root)
        # for token_ in doc:
        #     if token_.lemma_ == token.lemma_:
        #         token = token_
        DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one(doc, token, token_list, filter)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[subject.root.right_edge.i+1: token.right_edge.i + 1]
        return span[0: len(span) + 1]

    @staticmethod
    def get_subtree_span_from_one_token_filter_another_token_sub_tree_for_split_sentence(doc, filter, token):
        if token == None:
            return None
        token_list = list()

        # print('subject.root.text')
        # print(subject.root)
        # for token_ in doc:
        #     if token_.lemma_ == token.lemma_:
        #         token = token_
        DependencyTreeUtil.get_all_childern_token_under_one_token_filter_one_for_split_sentence(doc, token, token_list,
                                                                                                filter)
        span_text = ' '.join([token.text for token in token_list])
        span = DependencyTreeUtil.nlp(span_text)
        span = DependencyTreeUtil.merge_np_chunks(span)
        span = DependencyTreeUtil.merge_np_of_np(span)
        # span = doc[subject.root.right_edge.i+1: token.right_edge.i + 1]
        if span:
            return span[0: len(span) + 1]
        else:
            return None

    @staticmethod
    def get_subtree_span_from_functional_verb(doc, token):
        if token is None:
            return None

        span = doc[token.i + 1: token.right_edge.i + 1]
        return span

    @staticmethod
    def get_subtree_span_from_one_token_index(doc, token_index):
        token = DependencyTreeUtil.get_token_by_index(doc, token_index=token_index)
        return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token)

    @staticmethod
    def get_token_by_index(doc, token_index):
        if token_index < 0 or token_index > len(doc):
            return None
        token = doc[token_index]
        return token

    @staticmethod
    def get_action_text_for_token(doc, token):
        """
        抽取抽出来的动词作用对象，比如parse A to B， 抽出to B
        :param doc:
        :param token:
        :return:
        """
        result = []
        for candiate_candition_root_token in doc:
            try:
                if candiate_candition_root_token.dep_ == "prep" and candiate_candition_root_token.head == token:
                    span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                                  token=candiate_candition_root_token)
                    result.append(span.text)
            except Exception as e:
                print(e)
        return result

    @staticmethod
    def get_conditions_text_for_token(doc, token):
        """
        get the conditions, eg. StringBuffer could be modified during single thread at one time.
        when given the "modified" as root, the "during single thread at one time." should be return as condition.

        :param doc:
        :param token:
        :return:
        """
        result = []
        for candiate_candition_root_token in doc:
            ## 使用 介词(prep)+短语作为条件
            if candiate_candition_root_token.tag_ == "RBR":
                continue
            if candiate_candition_root_token.dep_ == "prep" and candiate_candition_root_token.head.text == token.text:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=candiate_candition_root_token)
                result.append(span.text)

            ## 使用when+从句作为条件
            if candiate_candition_root_token.dep_ == "advcl" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=candiate_candition_root_token)
                result.append(span.text)

            ## 使用when+从句作为条件
            if candiate_candition_root_token.dep_ == "advmod" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                if len(span) > 1:
                    result.append(span.text)

            ## 使用that+从句作为条件
            if candiate_candition_root_token.dep_ == "ccomp" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)

        if len(result) == 0:
            return ""

        return " ".join(result)

    @staticmethod
    def get_conditions_for_based_on_some_center_node_index_as_text(doc, token_index):
        """
        get the conditions, eg. StringBuffer could be modified during single thread at one time.
        when given the "modified" as root, the "during single thread at one time." should be return as condition.

        :param doc:
        :param token:
        :return:
        """
        token = DependencyTreeUtil.get_token_by_index(doc, token_index)

        return DependencyTreeUtil.get_conditions_text_for_token(doc, token)

    @staticmethod
    def split_large_noun_phase_span_to_adj_and_np(span):
        """
        将一个名词的span切割成多个修饰它的定语与名词，主要服务于特征和category抽取。
        :param span:
        :return:
        """
        root_token = [t for t in span if t.dep_ == "ROOT"][0]
        adj_list = DependencyTreeUtil.get_adj_modifier_for_noun(span, root_token)
        text = span.text
        for adj in adj_list:
            text = text.replace(adj, " ")
        text = text.replace(",", " ")
        # print("replace=", text)

        # todo: fix this,这个是为了取出句子中的主要名词，应该有其他方法。
        new_words = []
        words = text.split(" ")
        for word in words:
            if word.lower() in ["a", "an", "the", ","]:
                continue
            if word == " " or word == "":
                continue
            new_words.append(word)
        text = " ".join(new_words)
        return text, set(adj_list)

    @staticmethod
    def get_adj_modifier_for_noun(doc, token):
        """
        获取修饰名词的形容词部分
        :param doc:
        :param token:
        :return:
        """

        result = []
        for candiate_candition_root_token in doc:
            if candiate_candition_root_token.dep_ == "acl" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token=candiate_candition_root_token)
                result.append(span.text)

            if candiate_candition_root_token.dep_ == "amod" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)

            ## 使用that+从句作为条件
            if candiate_candition_root_token.dep_ == "ccomp" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)
                ## 使用that+从句作为条件
            if candiate_candition_root_token.dep_ == "relcl" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)

            if candiate_candition_root_token.dep_ == "advmod" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)

            if candiate_candition_root_token.dep_ == "advcl" and candiate_candition_root_token.head == token:
                span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc,
                                                                              token=candiate_candition_root_token)
                result.append(span.text)

        if len(result) == 0:
            return []

        return result

    @staticmethod
    def merge_np_chunks(doc: Doc):
        """
        merge the np chunks in to one token for the the better sentence analysis and extractor.
        :param doc:
        :return:
        """
        with doc.retokenize() as retokenizer:
            for chunk in doc.noun_chunks:
                try:
                    attrs = {"LEMMA": chunk[:-1].text + " " + chunk[-1].lemma_,
                             "POS": chunk[-1].pos_,
                             "TAG": chunk[-1].tag_,
                             }
                    retokenizer.merge(chunk, attrs=attrs)
                except Exception as e:
                    print(e)
        return doc

    @staticmethod
    def merge_np_of_np(doc):
        of_merge_index = []
        for of_token in doc:
            if of_token.text == "of" and of_token.head.pos_ == "NOUN":
                flag = False
                third_token_list = [child for child in of_token.children]
                if len(third_token_list) != 0:
                    third_token = third_token_list[0]
                else:
                    third_token = of_token
                if len(of_merge_index) > 0:
                    for index_pair in of_merge_index:
                        if of_token.head.left_edge.i > index_pair[0] and of_token.head.left_edge.i < index_pair[
                            1] and third_token.right_edge.i + 1 > index_pair[1]:
                            of_merge_index.append(
                                (index_pair[0], third_token.right_edge.i + 1, of_token.head.tag_, of_token.head.pos_))
                            of_merge_index.remove(index_pair)
                        if of_token.head.left_edge.i < index_pair[0] and third_token.right_edge.i + 1 > index_pair[1]:
                            of_merge_index.append((of_token.head.left_edge.i, third_token.right_edge.i + 1,
                                                   of_token.head.tag_, of_token.head.pos_))
                            of_merge_index.remove(index_pair)
                else:
                    of_merge_index.append((of_token.head.left_edge.i, third_token.right_edge.i + 1, of_token.head.tag_,
                                           of_token.head.pos_))
        try:
            with doc.retokenize() as retokenizer:
                for start, end, tag, pos in of_merge_index:
                    span = doc[start: end]
                    attrs = {"LEMMA": span.lemma_.replace("  ", " "),
                             "POS": pos,
                             "TAG": tag,
                             }
                    retokenizer.merge(span, attrs=attrs)
        except Exception as e:
            print(e)
        return doc

    @staticmethod
    def merge_clausadvmode_as_condition(doc):
        """
        merge the if condition or Attributive clause into one element to simplify
        :param doc:
        :return:
        """
        # todo: need complete
        # for chunk in doc.noun_chunks:
        #     with doc.retokenize() as retokenizer:
        #         attrs = {"LEMMA": chunk[:-1].text + " " + chunk[-1].lemma_,
        #                  "POS": chunk[-1].pos_,
        #                  "TAG": chunk[-1].tag_,
        #                  }
        #         retokenizer.merge(chunk, attrs=attrs)
        return doc

    @staticmethod
    def get_parallel_predicates(doc, main_predicate_token):
        """
        the input is the sentence Spacy Doc
        :param doc:
        :return: Span noun chunk for the subject, None for not found.
        """
        # todo:这个函数还不能覆盖所有的情况
        parallel_predicate_tokens = []
        for token in doc:
            if token.dep_ == "conj" and token.head == main_predicate_token:
                parallel_predicate_tokens.append(token)

        return parallel_predicate_tokens

    @staticmethod
    def get_object_for_preposition(doc, preposition):

        """
        为一个介词获取他的对象
        :param doc:
        :return: Span noun chunk for the subject, None for not found.
        """
        # todo:这个函数还不能覆盖所有的情况,需要进一步修改,目前只是简单返回介词后面链接的名词
        for token in doc:
            if (token.pos_ == "NOUN" or token.pos_ == "PROPN") and token.head == preposition:
                return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token)
        return None

    @staticmethod
    def get_prep_object_for_preposition(doc, predicate):
        for token in doc:
            if (
                    token.pos_ == "NOUN" or token.pos_ == "PROPN") and token.head.dep_ == "prep" and token.head.i > predicate.i:
                if token.head.head == predicate:
                    return DependencyTreeUtil.get_object_for_preposition(doc, token.head)

    @staticmethod
    def get_object_for_verb(doc, predicate):
        for token in doc:
            if (token.pos_ == "NOUN" or token.pos_ == "PROPN") and token.head == predicate and (
                    token.dep_ == 'dobj' or token.dep_ == 'acomp'):
                return token

    @staticmethod
    def get_object_of_preposition_by(doc):
        """
        为被动语态找间接宾语，如名词的头结点是by
        :param doc:
        :return:
        """
        if 'by' in doc.text:
            for token in doc:
                if token.pos_ == "NOUN" and token.head.text == 'by':
                    return DependencyTreeUtil.get_subtree_span_from_one_token_obj(doc, token)
        return None

    @staticmethod
    def clause_extraction(sent_doc, predicate):
        doc_list = []
        for token in sent_doc:
            if token.dep_ == 'relcl' and token.head.tag_.startswith('NN'):
                clause_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, token)
                subject_sent = DependencyTreeUtil.get_subtree_span_from_one_token_obj_for_vbn_and_root(sent_doc, token,
                                                                                                       predicate)
                # if 'that' in clause_span.text:
                #
                # doc_list.append(clause_span)
                # doc_list.append(subject_sent)

    @classmethod
    def get_can_be_string(cls, doc, predicate):
        aux = None
        auxpass_text = "be"
        neg_text = ""
        # if
        for token in doc:
            if token.tag_ == "MD" and token.head == predicate:
                aux = token.lemma_
            if token.tag_ == "RB" and token.dep_ == "neg" and token.head == predicate:
                neg_text = token.lemma_
            # if token.pos_ == "VERB" and token.lemma == "be" and token.head == predicate:
            #     auxpass = token
        if aux == None and doc[len(doc) - 1].text != predicate.text and doc[len(doc) - 2].text != predicate.text:
            return None
        if neg_text == "":
            return aux + " " + auxpass_text + " " + predicate.text if aux else predicate.text
        else:
            return aux + " " + neg_text + " " + auxpass_text + " " + predicate.text if aux else predicate.text
