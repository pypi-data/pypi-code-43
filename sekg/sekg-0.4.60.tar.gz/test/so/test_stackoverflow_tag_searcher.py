from unittest import TestCase
from sekg.so.stackoverflow_tag_searcher import SOTagSearcher


class TestSoTagSearcher(TestCase):

    def test_so_tag_searcher(self):
        searcher = SOTagSearcher()
        print(searcher.get_tag_item_for_one_tag("javascript"))
        print(searcher.synonyms_dic)
        print(searcher.get_tag_item_for_one_tag("dotnet"))
        print(searcher.get_tag_item_for_one_tag("vanillajs"))
        searcher.run()
