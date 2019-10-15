# feed.py

import feedparser
import html2text

_CACHED_FEEDS = dict()

def _feed(url):
    if url not in _CACHED_FEEDS:
        _CACHED_FEEDS[url] = feedparser.parse(url)
    return _CACHED_FEEDS[url]

def get_site(url):
    info = _feed(url).feed
    return f"{info.title} ({info.link})"

def get_titles(url):
    articles = _feed(url).entries
    return [a.title for a in articles]

def get_article(url, article_id):
    articles = _feed(url).entries
    article = articles[int(article_id)]
    html = article.content[0].value
    text = html2text.html2text(html)
    return f"# {article.title}\n\n{text}"
