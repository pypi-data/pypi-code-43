from ftw.contentnav.behaviors.content_categories import IContentCategories
from ftw.contentnav.interfaces import ICategorizable
from plone.app.layout.viewlets import ViewletBase
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize import instance
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentNavListingViewlet(ViewletBase):
    """Lists content by categories"""

    render = ViewPageTemplateFile('contentnavlisting.pt')

    def available(self):
        return bool(self.get_content())

    @instance.memoize
    def get_content(self):
        query = {
            'sort_on': 'sortable_title',
            'object_provides': 'ftw.contentnav.interfaces.ICategorizable'}
        contents = self.context.getFolderContents(contentFilter=query,
                                                  full_objects=True)
        return self._create_resultmap(contents)

    def _create_resultmap(self, contents=None):
        resultmap = {}
        categories = []
        for obj in contents:
            if IDexterityContent.providedBy(obj) and \
                    ICategorizable.providedBy(obj):
                categories = [item.encode('utf-8') for item in
                              IContentCategories(obj).content_categories]

            for cat in categories:
                if cat not in resultmap:
                    resultmap[cat] = []
                resultmap[cat].append((obj.title_or_id(),
                                       obj.absolute_url(),
                                       obj.Description()))

        items = resultmap.items()
        items.sort(key=lambda x: x[0].lower())
        return items
