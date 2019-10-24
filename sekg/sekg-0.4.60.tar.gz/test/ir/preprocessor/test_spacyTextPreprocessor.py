from unittest import TestCase

from sekg.ir.preprocessor.spacy import SpacyTextPreprocessor
from sekg.graph.util.name_searcher import KGNameSearcher

class TestSpacyTextPreprocessor(TestCase):
    def test_extract_keyword(self):
        name_searcher = KGNameSearcher.load(
            "E:\PycharmProjects\KGFeatureLocation\output\graph\jedite-4.3\\NameSearcher\jedite-4.3.v4.1.namesearcher"
        )
        preprocessor = SpacyTextPreprocessor(kg_name_searcher=name_searcher)
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
            preprocessor.extract_concept_and_operation(query)

    def test_extract_words_for_query(self):
        preprocessor = SpacyTextPreprocessor()
        test_case_list = [
            (
                "folding bug, text is in a black hole."
                , ['bug',
                   'text',
                   'black hole']
            ),

            (
                "how to get File's MD5 checksum",
                ['File', 'md5', 'checksum']

            )

        ]

        for old_str, new_str in test_case_list:
            team = preprocessor.extract_words_for_query(old_str)
            self.assertEqual(team, new_str)

    def test_clean(self):

        test_case_list = [
            (
                "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."
                ,
                ['arraylist',
                 'contain',
                 'class',
                 'create',
                 'user',
                 'interface',
                 'painting',
                 'graphic',
                 'image']
            ),

            ("how to get File's MD5 checksum",
             ["file", "md5", "checksum"])
        ]
        preprocessor = SpacyTextPreprocessor()

        for old_str, keywords in test_case_list:
            self.assertEqual(keywords, preprocessor.clean(old_str))
