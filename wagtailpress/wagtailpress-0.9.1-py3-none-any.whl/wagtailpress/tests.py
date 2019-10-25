from django.test import TestCase
from django.contrib.auth.models import User

from datetime import date, timedelta

from wagtail.core.models import Page
from wagtailpress.models import (
    BlogIndexPage,
    BlogArticlePage,
    BlogArticlePageTag
)


class BlogIndexPageTests(TestCase):
    """Test the Blog Index (BlogIndexPage)"""
    def setUp(self):
        """Setup the Database"""
        self.home = Page.objects.get(slug='home')
        self.user = User.objects.create_user('test', 'test@test.test', 'pass')
        self.blog_index = self.home.add_child(
            instance=BlogIndexPage(
                title='Blog Index',
                slug='blog',
                owner=self.user,
            ),
        )
        self.tags = [
            'test1',
            'test2',
        ]
        self.blog_page_1 = BlogArticlePage(
            title='Blog Page 1',
            slug='blog_page1',
            owner=self.user,
            date=date.today() - timedelta(days=3),
            intro='A test of article, page 1',
        )
        self.blog_page_1.tags.add(self.tags[0])
        self.blog_page_2 = BlogArticlePage(
            title='Blog Page 2',
            slug='blog_page2',
            owner=self.user,
            date=date.today(),
            intro='A test of article, page 1',
        )
        self.blog_page_2.tags.add(self.tags[1])
        self.blog_index.add_child(instance=self.blog_page_1)
        self.blog_index.add_child(instance=self.blog_page_2)

    def test_all_articles(self):
        """Test the property BlogIndexPage.all_articles to get all descendants
        Articles of an Index"""
        # Get all the descendants articles of the index
        descendants_articles = self.blog_index.all_articles()

        # Test if we get the 2 pages in the descendants_articles
        self.assertTrue(
            descendants_articles.filter(
                id=self.blog_page_1.id
            ).exists()
        )
        self.assertTrue(
            descendants_articles.filter(
                id=self.blog_page_2.id
            ).exists()
        )

    def test_all_articles_order(self):
        """Test if articles returned by BlogIndexPage.all_articles are
        chronologicaly ordered"""
        # Get all the descendants articles of the index
        descendants_articles = self.blog_index.all_articles()

        # Test if we get the 2 pages in the descendants_articles
        self.assertTrue(
            (
                descendants_articles[0].date
                >
                descendants_articles[1].date
            )
        )

    def test_index_of_article(self):
        """Test if we can get the index of an article"""
        self.assertTrue(
            self.blog_page_1.index().id == self.blog_index.id
        )

    def test_index_all_articles_tags(self):
        """Test if the index can get all tags of its descendants articles"""
        self.assertTrue(
            all(
                (
                    tag_name in self.tags
                    for tag_name in self.blog_index.all_articles_tags()
                )
            )
        )

    def test_all_articles_tagges_as(self):
        """Test if we can get all articles of a tag from an index"""
        self.assertTrue(
            self.blog_index.all_articles_tagged_as(self.tags[0])[0].id == self.blog_page_1.id
        )
