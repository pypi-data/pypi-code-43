from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed


class BlogIndexFeed(Feed):

    def __init__(self, blog_index_page):
        self.blog_index_page = blog_index_page
        super(BlogIndexFeed, self).__init__()

    def get_object(self, request):
        """Get the object given in object initializing"""
        return self.blog_index_page

    def title(self, blog_index_page):
        """Get the title of the blog_index_page"""
        return blog_index_page.title

    def link(self, blog_index_page):
        """Get the link to the blog_index_page"""
        return blog_index_page.full_url
        
    def description(self, blog_index_page):
        """Get the description of the blog_index_page"""
        return blog_index_page.intro

    def items(self, blog_index_page):
        """Get all the articles descendants to the index blog_index_page"""
        return blog_index_page.all_articles()

    def item_title(self, blog_article_page):
        """Get blog article page title"""
        return blog_article_page.title

    def item_author_name(self, blog_article_page):
        """Get blog article page author's name"""
        return ' '.join(
            blog_article_author.person.specific.name
            for blog_article_author
            in blog_article_page.authors.all()
        )

    def item_link(self, blog_article_page):
        """Get blog article page link"""
        return blog_article_page.full_url

    def item_description(self, blog_article_page):
        """Get blog article page description"""
        return blog_article_page.intro
        
    def item_pubdate(self, blog_article_page):
        """Get blog article page publication date"""
        return blog_article_page.first_published_at
        
        
    
    

    

