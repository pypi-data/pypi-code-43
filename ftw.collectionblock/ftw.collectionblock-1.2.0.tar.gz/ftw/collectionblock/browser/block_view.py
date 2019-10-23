from Acquisition import aq_inner
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.utils import safe_callable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.collectionblock import _
from plone.app.collection import PloneMessageFactory as PMF
from ftw.collectionblock import utils
from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone.app.contenttypes.behaviors.collection import ICollection
from zope.component import getMultiAdapter
from zope.i18n import translate


class CollectionBlockView(BaseBlock):
    """Collection block view, which provides several features from the
    plone.app.contenttypes.browser.folder.FolderView"""

    template = ViewPageTemplateFile('templates/block_view.pt')

    _pas_member = None

    def __init__(self, context, request):
        super(CollectionBlockView, self).__init__(context, request)

        self.plone_view = getMultiAdapter((context, request), name=u"plone")
        self.portal_state = getMultiAdapter(
            (context, request), name=u"plone_portal_state")

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        return self.plone_view.toLocalizedTime(time, long_format, time_only)

    def block_results(self):
        if self.context.block_amount > 0:
            return self.context.results(b_size=self.context.block_amount)
        return self.context.results()

    def get_title_link_target(self, item):
        """This method may return a target attribute value (e.g. "_blank").
        It can be customized by subclasses.
        The "item" is a content listing object wrapper item.
        """
        return None

    def get_author(self, item):
        author = ''
        if utils.can_view_about():
            author = utils.get_creator(item)
        return author

    def get_block_info(self):
        """
        This method returns a dict containing information to be used in
        the block's template.
        """

        rss_link_url = ''
        if self.context.show_rss_link and self.rss_enabled:
            rss_link_url = '/'.join([self.context.absolute_url(), 'RSS'])

        more_link_url = '/'.join([self.context.absolute_url(), 'listing_view'])

        more_link_label = (
            self.context.more_link_label or
            translate(_('more_link_label', default=u'More'),
                      context=self.request)
        )

        info = {
            'title': self.context.title,
            'show_title': self.context.show_title,
            'more_link_url': more_link_url,
            'more_link_label': more_link_label,
            'rss_link_url': rss_link_url or '',
            'show_more_link': self.context.show_more_link,
        }

        return info

    def tabular_fields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        context = aq_inner(self.context)
        fields = ICollection(context).selectedViewFields()
        fields = [field[0] for field in fields]
        return fields

    def tabular_fielddata(self, item, fieldname):
        value = getattr(item, fieldname, '')
        if safe_callable(value):
            value = value()
        if fieldname in [
                'CreationDate',
                'ModificationDate',
                'Date',
                'EffectiveDate',
                'ExpirationDate',
                'effective',
                'expires',
                'start',
                'end',
                'created',
                'modified',
                'last_comment_date']:
            value = self.toLocalizedTime(value, long_format=1)

        return {
            'title': PMF(fieldname),
            'value': value
        }

    @property
    def pas_member(self):
        if not self._pas_member:
            self._pas_member = getMultiAdapter(
                (self.context, self.request),
                name=u'pas_member'
            )
        return self._pas_member

    @property
    def navigation_root_url(self):
        return self.portal_state.navigation_root_url()

    @property
    def rss_enabled(self):
        rss_settings = IFeedSettings(self.context)
        return rss_settings.enabled
