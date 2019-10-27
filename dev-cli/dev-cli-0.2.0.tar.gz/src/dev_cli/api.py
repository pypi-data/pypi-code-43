from enum import Enum
from typing import Any, Iterator, List, Optional, Text

from httpx import models as hm
from typefit import api

from .errors import DevApiError
from .models import ListArticle, MeArticle, SingleArticle, WriteArticle
from .parser import DevKey, DevParser


def kwargs_params(**kwargs):
    """
    Several methods will just add their arguments as GET params if not None,
    this is a factorization of that
    """

    return {k: v for k, v in kwargs.items() if v is not None}


def parser_to_article(parser: DevParser):
    """
    Transforms a parsed article to a minimal set of parameters you can use to
    create/update an article
    """

    if "title" not in parser.front_matter:
        raise DevApiError(
            "Cannot create an article with no `title` in the front matter"
        )

    return {"title": parser.front_matter["title"], "body_markdown": parser.file_content}


class PublishingStatus(Enum):
    """
    Allowed publishing status, see method below
    """

    published = "published"
    unpublished = "unpublished"
    all = "all"

    def __str__(self):
        return self.value


class ArticleState(Enum):
    """
    Allowed article states, see method below
    """

    fresh = "fresh"
    rising = "rising"
    all = "all"

    def __str__(self):
        return self.value


class DevApi(api.SyncClient):
    """
    A class to access the dev.to API
    """

    BASE_URL = "https://dev.to/api/"

    def __init__(self, api_key: Text):
        super().__init__()
        self.api_key = api_key

    def headers(self) -> Optional[hm.HeaderTypes]:
        """
        Put the API key in the headers for all requests
        """

        return {"Api-Key": self.api_key}

    @api.get("articles", params=kwargs_params)
    def list_articles(
        self,
        page: Optional[int] = None,
        tag: Optional[Text] = None,
        username: Optional[Text] = None,
        state: Optional[ArticleState] = None,
        top: Optional[int] = None,
    ) -> List[ListArticle]:
        """
        Lists public articles

        See https://docs.dev.to/api/#operation/getArticles
        """

    @api.post("articles", json=parser_to_article)
    def create_article(self, parser: DevParser) -> WriteArticle:
        """
        Creates an article

        See https://docs.dev.to/api/#operation/createArticle
        """

    @api.put("articles/{article_id}", json=parser_to_article)
    def update_article(self, parser: DevParser, article_id: int) -> WriteArticle:
        """
        Updates an existing article

        See https://docs.dev.to/api/#operation/updateArticle
        """

    @api.get("articles/{article_id}")
    def get_article(self, article_id: int) -> SingleArticle:
        """
        Returns the content of a single article

        See https://docs.dev.to/api/#operation/getArticleById
        """

    @api.get("articles/me", params=kwargs_params)
    def list_my_articles(
        self, page: int = None, per_page: int = None
    ) -> List[MeArticle]:
        """
        Lists current user's articles

        See https://docs.dev.to/api/#operation/getUserArticles
        """

    @api.get("articles/me/{status}", params=kwargs_params)
    def list_my_articles_by_status(
        self, status: PublishingStatus = None, page: int = None, per_page: int = None
    ) -> List[MeArticle]:
        """
        Lists current user's articles based on their publishing status

        See https://docs.dev.to/api/#operation/getUserPublishedArticles
        See https://docs.dev.to/api/#operation/getUserUnpublishedArticles
        See https://docs.dev.to/api/#operation/getUserAllArticles
        """

    def iterate_my_articles_by_status(
        self, status: PublishingStatus = PublishingStatus.all
    ) -> Iterator[MeArticle]:
        """
        Returns an iterator over all the articles corresponding to the
        publication filter.
        """

        class NoMorePages(Exception):
            """
            A way to communicate that there is no more page coming up from the
            API and that the polling of pages should stop now.
            """

        def get_page(page: int):
            """
            Returns a given page. Pages are 1-indexed.
            """

            stop = True

            for article in self.list_my_articles_by_status(status=status, page=page):
                stop = False
                yield article

            if stop:
                raise NoMorePages

        for i in range(1, 1000):
            try:
                yield from get_page(i)
            except NoMorePages:
                return

    def find_article(self, key: DevKey) -> Optional[MeArticle]:
        """
        Finds the first article matching they key. Let's take a moment to note
        that this method is really approximate but since we can't retrofit the
        API ID into the Markdown file it's the only decent way to go.
        """

        for article in self.iterate_my_articles_by_status():
            if getattr(article, key.name) == key.value:
                return article
