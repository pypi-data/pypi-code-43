from nltk.corpus import wordnet as wn
from sekg.text.extractor.domain_entity.word_util import WordUtil


# from word_forms.word_forms import get_word_forms


class VocabularyConversion:
    def __init__(self):
        self.WN_NOUN = 'n'
        self.WN_VERB = 'v'
        self.WN_ADJECTIVE = 'a'
        self.WN_ADJECTIVE_SATELLITE = 's'
        self.WN_ADVERB = 'r'

    # def word_forms_find(self, word):
    #     forms = get_word_forms(word)
    #     print(forms)
    #     return forms
    @staticmethod
    def couldBeVerb_probability(word):
        """
        check if a word could be a verb
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "v" in tag_count:
            return True
        return False

    @staticmethod
    def couldBeADJECTIVE_High_probability(word):
        return VocabularyConversion.couldBeHigh_probability(word, "a")

    @staticmethod
    def couldBeADJECTIVE_SATELLITE_High_probability(word):
        return VocabularyConversion.couldBeHigh_probability(word, "s")

    @staticmethod
    def couldBeNOUN_High_probability(word):
        return VocabularyConversion.couldBeHigh_probability(word, "n")

    @staticmethod
    def couldBeADVERB_High_probability(word):
        return VocabularyConversion.couldBeHigh_probability(word, "r")

    @staticmethod
    def couldbe_adj(word):
        verb_type = "a"
        if word is None:
            return False
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if verb_type == "a" and "s" in tag_count:
            if "a" in tag_count:
                tag_count["a"] += tag_count["s"]
            else:
                tag_count["a"] = tag_count["s"]
        if verb_type in tag_count and tag_count[verb_type] > 0:
            return True
        return False

    @staticmethod
    def couldBeHigh_probability(word, verb_type, confidence=0.5):
        """
        :param verb_type:
        :param word:
        :return:
        """
        if word is None:
            return False
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if verb_type == "a" and "s" in tag_count:
            if "a" in tag_count:
                tag_count["a"] += tag_count["s"]
            else:
                tag_count["a"] = tag_count["s"]
        if verb_type in tag_count and tag_count[verb_type] >= (len(pairs) * confidence):
            return True
        return False

    @staticmethod
    def non_more_than_adj(word):
        if word.endswith("ed") or (word.endswith("able") and (not word.endswith("table"))):
            return False
        if word is None:
            return False
        sp_list = word.split()
        if len(sp_list) > 1:
            word = sp_list[-1]
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "s" in tag_count:
            if "a" in tag_count:
                tag_count["a"] += tag_count["s"]
            else:
                tag_count["a"] = tag_count["s"]
        if "n" not in tag_count:
            return False
        if "a" not in tag_count:
            return True
        if tag_count["n"] > tag_count["a"]:
            return True
        return False

    def noun_2_verb(self, word):
        """
        名词转动词
        :param word:
        :return:
        """
        t = self.convert(word, from_pos=self.WN_VERB, to_pos=self.WN_NOUN)
        if len(t) != 0 and t[0][1] > 0.5 and t[0][0] != "string":
            return word, True
        if self.couldBeVerb_probability(word) and not word.endswith("ed"):
            return word, True
        result_list = self.convert(word, from_pos=self.WN_NOUN, to_pos=self.WN_VERB)
        if len(result_list) == 0:
            # parser这种单词形式
            if word.endswith("er"):
                t1 = word[0:-1]
                t2 = word[0:-2]
                if WordUtil.couldBeVerb(t1):
                    return t1, False
                if WordUtil.couldBeVerb(t2):
                    return t2, False
        else:
            if result_list[0][1] > 0.4:
                return result_list[0][0], False
        return None, False

    def noun_2_adj(self, word):
        """
        名词转adj
        :param word:
        :return:
        """
        result_list = self.convert(word, from_pos=self.WN_NOUN, to_pos=self.WN_ADJECTIVE)
        if len(result_list) != 0:
            if result_list[0][1] > 0.5:
                return result_list[0][0], False
        return None, False

    def verb_2_noun(self, word):
        """
        verb转noun
        :param word:
        :return:
        """
        result_list = self.convert(word, from_pos=self.WN_VERB, to_pos=self.WN_NOUN)
        if len(result_list) != 0:
            if result_list[0][1] > 0.5:
                return result_list[0][0], False
        return None, False

    def convert(self, word, from_pos, to_pos):
        """ Transform words given from/to POS tags """
        synsets = wn.synsets(word, pos=from_pos)
        if len(word) > 2:
            start_word = word[0:2]
        else:
            start_word = ""
        # Word not found
        if not synsets:
            return []
        # Get all lemmas of the word (consider 'a'and 's' equivalent)
        lemmas = []
        for s in synsets:
            for l in s.lemmas():
                if s.name().split('.')[1] == from_pos or from_pos in (
                        self.WN_ADJECTIVE, self.WN_ADJECTIVE_SATELLITE) and \
                        s.name().split('.')[1] in (self.WN_ADJECTIVE, self.WN_ADJECTIVE_SATELLITE):
                    lemmas += [l]

        # Get related forms
        derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]
        # TODO 过滤
        # filter only the desired pos (consider 'a' and 's' equivalent)
        related_noun_lemmas = []

        for drf in derivationally_related_forms:
            for l in drf[1]:
                if l.synset().name().split('.')[1] == to_pos or to_pos in (
                        self.WN_ADJECTIVE, self.WN_ADJECTIVE_SATELLITE) and \
                        l.synset().name().split('.')[1] in (self.WN_ADJECTIVE, self.WN_ADJECTIVE_SATELLITE):
                    if start_word != "" and len(l._name) > 2 and not str(l._name).startswith(start_word):
                        continue

                    related_noun_lemmas += [l]
        # Extract the words from the lemmas
        words = [l.name() for l in related_noun_lemmas]
        len_words = len(words)

        # Build the result in the form of a list containing tuples (word, probability)
        result = [(w, float(words.count(w)) / len_words) for w in set(words)]
        result.sort(key=lambda w: -w[1])

        # return all the possibilities sorted by probability
        return result


if __name__ == '__main__':
    vocabulary_conversion = VocabularyConversion()
    while True:
        t = input("input")
        a1 = vocabulary_conversion.convert(t, "n", "a")
        print(a1)
        a2 = vocabulary_conversion.convert(t, "v", "a")
        print(a2)
        a4 = vocabulary_conversion.convert(t, "r", "a")
        print(a4)
        # a = vocabulary_conversion.noun_2_verb('Field')

    a = vocabulary_conversion.convert('PutField', 'n', 'v')
    print(a)
#     # vocabulary_conversion.convert('writer', 'n', 'v')
#     # vocabulary_conversion.convert('quickly', 'r', 'a')
#     vocabulary_conversion.convert('parse', 'n', 'v')
#     a = vocabulary_conversion.noun_2_verb('writer')
#     print(a)
#     print("a")
