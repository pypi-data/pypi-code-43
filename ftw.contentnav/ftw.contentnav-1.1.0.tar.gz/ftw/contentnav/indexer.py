from ftw.contentnav.behaviors.content_categories import IContentCategories
from ftw.contentnav.interfaces import ICategorizable
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer


@indexer(ICategorizable)
def categories(obj, **kw):
    if IDexterityContent.providedBy(obj) and ICategorizable.providedBy(obj):
        return [item.encode('utf-8') for item in
                IContentCategories(obj).content_categories]

    return ()
