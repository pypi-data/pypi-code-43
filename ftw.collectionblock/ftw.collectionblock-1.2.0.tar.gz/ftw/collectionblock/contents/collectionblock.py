from ftw.collectionblock import _
from ftw.collectionblock.contents.interfaces import ICollectionBlock
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.content import Collection
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.browser.syndication.adapters import CollectionFeed
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements


class ICollectionBlockSchema(model.Schema):
    """Collection block for simplelayout
    """

    title = schema.TextLine(
        title=_(u'collectionblock_title_label', default=u'Title'),
        required=True,
    )

    directives.order_before(title='*')

    show_title = schema.Bool(
        title=_(u'collectionblock_show_title_label', default=u'Show title'),
        default=False,
        required=False,
    )

    directives.order_after(show_title='title')

    block_amount = schema.Int(
        title=_(u'label_block_amount', default=u'Amount of entries on block'),
        default=5,
        required=False)

    show_rss_link = schema.Bool(
        title=_(u'label_show_rss_link',
                default=u'Link to RSS feed'),
        default=False,
    )

    show_more_link = schema.Bool(
        title=_(u'label_show_more_link', default=u'Show "more" link'),
        default=True,
    )

    more_link_label = schema.TextLine(
        title=_(u'label_more_link_label',
                default=u'Label for the "more" link'),
        required=False,
    )


alsoProvides(ICollectionBlockSchema, IFormFieldProvider)


class CollectionBlock(Collection):
    implements(ICollectionBlock)


class ISyndicatableCollection(ISyndicatable):
    """Marker interface for syndicatable collection blocks.
    """


@implementer(IFeed)
class CollectionBlockFeed(CollectionFeed):

    def _brains(self):
        return ICollection(self.context).results(batch=False)[:self.limit]
