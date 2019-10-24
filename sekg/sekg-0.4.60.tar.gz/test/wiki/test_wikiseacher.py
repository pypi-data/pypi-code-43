from unittest import TestCase

from sekg.wiki.search_domain_wiki.wikidata_searcher import AsyncWikiSearcher


class TestWikiSearcher(TestCase):

    def test_wiki_searcher(self):
        test_set = set()
        test_set.add("Peer alarm")
        searcher = AsyncWikiSearcher(proxy_server="http://127.0.0.1:1080")
        searcher.init_from_cache()
        ids = ['Q1670525']
        titles = ['Shoutbox']
        searcher.search_title(titles)
        print(searcher.get_title_cache())
        title_path = "title.bin"
        searcher.save(title_save_path=title_path)
        searcher.update(title_path, type=searcher.TYPE_TITLE)

        searcher.fetch_item(ids)
        print(searcher.get_item_cache())
        item_path = "item.bin"
        searcher.save(item_save_path=item_path)
        searcher.update(item_path, type=searcher.TYPE_ITEM)

        searcher.fetch_item_neighbor(["Q21028"])
        print(searcher.get_item_cache())

        searcher.fetch_wikipedia_context(titles)
        print(searcher.get_wikipedia_cache())
        wiki_path = "wikipedia_context.bin"
        searcher.save(wikipedia_save_path=wiki_path)
        searcher.update(wiki_path, type=searcher.TYPE_WIKIPEDIA)

        searcher.fetch_wikipedia_context_for_wikidata(ids)
        print(searcher.get_wikidata_wikipedia_context_cache())
        wiki_path = "wikidata_wikipedia_context.bin"
