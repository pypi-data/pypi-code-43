from unittest import TestCase

from sekg.ir.preprocessor.ngram import NGramPreprocessor
from sekg.graph.util.name_searcher import KGNameSearcher


class TesNGramPreprocessor(TestCase):

    def test_get_n_gram_list(self):
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
            print(preprocessor.get_n_gram_list(query))
