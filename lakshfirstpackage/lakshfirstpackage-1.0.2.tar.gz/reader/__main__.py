from configparser import ConfigParser
from importlib import resources
import sys

from reader import feed
from reader import viewer

def main():
    cfg = ConfigParser()
    cfg.read_string(resources.read_text("reader","config.txt"))
    url = cfg.get("feed", "url")

    if len(sys.argv) > 1:
        article = feed.get_article(url, sys.argv[1])
        viewer.show(article)

    else:
        site = feed.get_site(url)
        titles = feed.get_titles(url)
        viewer.show_list(site, titles)

if __name__ == "__main__":
    main()

