from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.shortcuts import render

from wagtail.contrib.routable_page.models import (
    RoutablePageMixin,
    route,
)

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtailpress.utils import items_at_page
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.blocks import (
    RichTextBlock,
    BlockQuoteBlock,
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtailpress.blocks import (
    HeaderBlock,
    ImageTextOverlayBlock,
    LinkBlock,
)
from wagtailpress.views import BlogIndexFeed
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
    InlinePanel,
    PageChooserPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel


class BlogArticlePageTag(TaggedItemBase):
    """A blog article tag"""
    content_object = ParentalKey(
        'BlogArticlePage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )


class BlogArticlePage(Page):
    """A blog article"""
    subpage_types = []

    date = models.DateField(
        verbose_name=_('Publication date'),
        help_text=_('Only for visitor display'),
    )
    tags = ClusterTaggableManager(
        through=BlogArticlePageTag,
        blank=True,
        verbose_name=_('Tags'),
    )
    intro = models.CharField(
        verbose_name=_('Introduction'),
        max_length=250,
    )
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('header image'),
        null=True,
        blank=True,
    )

    content = StreamField(
        [
            ('heading', HeaderBlock()),
            ('paragraph', RichTextBlock()),
            ('quote', BlockQuoteBlock()),
            ('image', ImageChooserBlock()),
            ('imagetextoverlay', ImageTextOverlayBlock()),
            ('link', LinkBlock()),
            ('document', DocumentChooserBlock()),
            ('embed', EmbedBlock()),
        ],
        blank=True,
        verbose_name=_('content'),
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel('authors', label=_('Authors')),
                FieldPanel('date'),
                FieldPanel('tags'),
                FieldPanel('intro'),
            ],
            heading=_('Article informations'),
        ),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('content'),
    ]

    class Meta:
        verbose_name = _("Blog article")
        verbose_name_plural = _("Blog articles")

    def __str__(self):
        return self.title

    def index(self):
        """Get the index of this article"""
        return BlogIndexPage.objects.ancestor_of(
            self
        ).live().public()[0]


class BlogArticleAuthor(Orderable):
    """A Blog article author, linked to a person page"""
    page = ParentalKey(
        BlogArticlePage,
        on_delete=models.CASCADE,
        related_name='authors',
    )
    person = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='article_authors',
        verbose_name=_('Person page'),
    )

    panels = [
        PageChooserPanel('person', 'wagtailperson.PersonPage'),
    ]

    class Meta:
        verbose_name = _("Blog article author")
        verbose_name_plural = _("Blog article authors")

    def __str__(self):
        return self.person.specific.name


class BlogIndexPage(RoutablePageMixin, Page):
    """An index for a blog: The start page of a blog"""
    subpage_types = [
        'BlogArticlePage',
    ]

    intro = RichTextField(
        verbose_name=_('Introduction'),
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    class Meta:
        verbose_name = _("Blog index")
        verbose_name_plural = _("Blog index")

    def __str__(self):
        return self.title

    def all_articles(self):
        """Get all descendants articles"""
        return BlogArticlePage.objects.descendant_of(
            self
        ).live().public().order_by(
            '-date'
        )

    def all_articles_tags(self):
        """Get all descendants articles tags"""
        all_tags = list(
            self.all_articles().values_list('tags__name', flat=True)
        )
        if None in all_tags:
            all_tags.remove(None)
        return all_tags

    def all_articles_tagged_as(self, tag=None):
        if not tag:
            return self.all_articles()
        else:
            return self.all_articles().filter(tags__name=tag)

    @route(r'^feed/$', name='feed')
    def articles_feed(self, request):
        """Get articles as feed"""
        feed = BlogIndexFeed(self)
        return feed(request)
    
    @route(r'^tagged/(\w+)/$', name='articles_tagged_as')
    def articles_tagged_as_view(self, request, tag=None):
        """View method for the articles tagged as given tag"""
        context = self.get_context(request, tag=tag)
        return render(request, self.template, context)

    def get_context(self, request, tag=None):
        """Overload the original Page.get_context() to customize the
        BlogIndexPage context by adding descendants Article pages page
        to it.
        """
        context = super(BlogIndexPage, self).get_context(request)
        articles_per_pages = getattr(
            settings,
            'BLOG_ARTICLES_PER_PAGES',
            10,
        )
        page = request.GET.get('page')
        articles = items_at_page(
            self.all_articles_tagged_as(tag),
            articles_per_pages,
            page,
        )
        context['articles'] = articles
        context['tag'] = tag
        return context

    
