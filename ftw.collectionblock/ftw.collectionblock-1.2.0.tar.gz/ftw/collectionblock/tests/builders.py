from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders


class CollectionBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.collectionblock.CollectionBlock'

    def with_default_query(self):
        self.arguments['query'] = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'ContentPage',
        }]
        return self


builder_registry.register('sl collectionblock', CollectionBlockBuilder)
