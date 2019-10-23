from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.interface import directlyProvides
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm


def contentcategories_vocabulary(context):
    normalizer = queryUtility(IIDNormalizer)
    catalog = getToolByName(context, 'portal_catalog')
    terms = []
    for term in catalog.uniqueValuesFor("get_content_categories"):
        terms.append(
            SimpleTerm(
                value=term.decode('utf8'),
                token=normalizer.normalize(term.decode('utf8')),
                title=term.decode('utf8')))
    return vocabulary.SimpleVocabulary(terms)

directlyProvides(contentcategories_vocabulary, IVocabularyFactory)
