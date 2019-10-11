import os

import spacy
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize.treebank import TreebankWordTokenizer

from errant import AlignText
from errant import CatRules
from errant import Toolbox


class ErrorType:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Edit:
    def __init__(self, original_start, original_end, category, correction, correction_start, correction_end):
        self.original_start = original_start
        self.original_end = original_end
        self.correction = correction
        self.category = category
        self.correction_start = correction_start
        self.correction_end = correction_end

    def __str__(self):
        return Toolbox.format_edit(
            [self.original_start, self.original_end, self.category, self.correction, self.correction_start,
             self.correction_end])

    def __repr__(self):
        return Toolbox.format_edit(
            [self.original_start, self.original_end, self.category, self.correction, self.correction_start,
             self.correction_end])


class Checker:

    __instance = None

    @staticmethod
    def get_instance():
        if Checker.__instance is None:
            Checker()
        return Checker.__instance

    def __init__(self, nlp=None):
        if Checker.__instance is not None:
            raise Exception("Checker class is a singleton!")
        else:
            self.tokenizer = TreebankWordTokenizer()
            # Get base working directory.
            basename = os.path.dirname(os.path.realpath(__file__))
            # Load Tokenizer and other resources
            self.nlp = nlp
            if not self.nlp:
                self.nlp = spacy.load("en")
            # Lancaster Stemmer
            self.stemmer = LancasterStemmer()
            # GB English word list (inc -ise and -ize)
            self.gb_spell = Toolbox.load_dictionary(basename + "/resources/en_GB-large.txt")
            # Part of speech map file
            self.tag_map = Toolbox.load_tag_map(basename + "/resources/en-ptb_map")

            Checker.__instance = self

    def check_tokenized(self, original_tokenized_sentence, corrected_tokenized_sentence, merge_strategy='rules', levenshtein=False):
        """
        :param original_tokenized_sentence: original tokenized sentence
        :param corrected_tokenized_sentence: corrected tokenized sentence
        :param merge_strategy: Choose a merging strategy for automatic alignment, possible values:
                                rules: Use a rule-based merging strategy (default)
                                all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
                                all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
                                all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I
        :param levenshtein: Use standard Levenshtein to align sentences
        :return: errors list of class ErrorType, edits list of class Edit
        """
        orig_sent = original_tokenized_sentence.strip()
        cor_sent = corrected_tokenized_sentence.strip()

        # ensure sentences are not empty
        if orig_sent and cor_sent:
            errors = []
            edits = []
            # Markup the original sentence with spacy (assume tokenized)
            proc_orig = Toolbox.apply_spacy(orig_sent, self.nlp)
            # Identical sentences have no edits, so just write noop.
            if orig_sent == cor_sent:
                return errors, edits
            # Otherwise, do extra processing.
            else:
                # Markup the corrected sentence with spacy (assume tokenized)
                proc_cor = Toolbox.apply_spacy(cor_sent, self.nlp)
                # Auto align the parallel sentences and extract the edits.
                auto_edits = AlignText.get_auto_aligned_edits(proc_orig, proc_cor, merge_strategy, levenshtein)
                # Loop through the edits.
                for auto_edit in auto_edits:
                    # Give each edit an automatic error type.
                    cat = CatRules.auto_type_edit(auto_edit, proc_orig, proc_cor, self.gb_spell, self.tag_map, self.nlp, self.stemmer)
                    errors.append(ErrorType(cat))
                    edits.append(Edit(auto_edit[0], auto_edit[1], cat, auto_edit[3], auto_edit[4], auto_edit[5]))
                return errors, edits

    def check(self, original_sentence, corrected_sentence, merge_strategy='rules', levenshtein=False):
        """
        :param original_sentence: original sentence
        :param corrected_sentence: corrected sentence
        :param merge_strategy: Choose a merging strategy for automatic alignment, possible values:
                                rules: Use a rule-based merging strategy (default)
                                all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
                                all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
                                all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I
        :param levenshtein: Use standard Levenshtein to align sentences
        :return: errors list of class ErrorType, edits list of class Edit
        """
        original_tokenized_sentence = ' '.join(self.tokenizer.tokenize(original_sentence)).strip()
        corrected_tokenized_sentence = ' '.join(self.tokenizer.tokenize(corrected_sentence)).strip()
        return self.check_tokenized(original_tokenized_sentence, corrected_tokenized_sentence, merge_strategy, levenshtein)