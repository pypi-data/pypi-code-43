from nltk import WordNetLemmatizer
from sekg.text.extractor.domain_entity.word_util import WordUtil
from spacy.tokens.doc import Doc


class SoftwareTextPOSFixer:
    __se_text_fixer = 'se_text_fixer'
    lemmatizer = WordNetLemmatizer()
    verb_set = {'appends', 'reads'}
    @staticmethod
    def fixer_for_pos(doc: Doc):
        if doc is None or len(doc) == 0:
            return doc
        first_token = doc[0]

        attrs = None
        if first_token.text.lower() == "return":
            attrs = {"LEMMA": "return", "TAG": "VB", "POS": "VERB"}
        if first_token.text.lower() == "returns":
            attrs = {"LEMMA": "return", "TAG": "VBZ", "POS": "VERB"}
        # if first_token.text.lower() == "appends":
        #     attrs = {"LEMMA": "append", "TAG": "VBZ", "POS": "VERB"}

        if attrs != None:
            with doc.retokenize() as retokenizer:
                retokenizer.merge(doc[0:1], attrs=attrs)
            return doc
        # todo: 考虑动词被动？
        if WordUtil.couldBeVerb(doc[0].text) and doc[0].pos_ == "ADV":
            lemma = SoftwareTextPOSFixer.lemmatizer.lemmatize(first_token.text, "v")
            if lemma == first_token.text.lower():
                tag = "VB"
            else:
                tag = "VBZ"

            attrs = {"LEMMA": lemma, "POS": "VERB",
                     "TAG": tag}
            with doc.retokenize() as retokenizer:
                retokenizer.merge(doc[0:1], attrs=attrs)
            return doc

        # 被动形式
        # if WordUtil.couldBeVerb(doc[0].text) and doc[0].tag_ == "VBD":
        #     lemma = SoftwareTextPOSFixer.lemmatizer.lemmatize(first_token.text, "v")
        #     if lemma == first_token.text.lower():
        #         tag = "VB"
        #     else:
        #         tag = "VBZ"
        #
        #     attrs = {"LEMMA": lemma, "POS": "VERB",
        #              "TAG": tag}
        #     with doc.retokenize() as retokenizer:
        #         retokenizer.merge(doc[0:1], attrs=attrs)
        #     return doc

        return doc
