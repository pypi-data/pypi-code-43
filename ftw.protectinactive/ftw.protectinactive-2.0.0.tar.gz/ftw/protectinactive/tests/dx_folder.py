from ftw.builder.dexterity import DexterityBuilder
from ftw.builder import registry
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.dexterity.fti import DexterityFTI
from plone.supermodel import model
from zope.interface.declarations import alsoProvides
from zope.interface import implements
from zope.interface import Interface


class IDexterityContainerSchema(model.Schema):
    pass

alsoProvides(IDexterityContainerSchema, IFormFieldProvider)


class IDexterityFolder(Interface):
    pass


class DexterityFolder(Container):
    implements(IDexterityFolder)


class DexterityFolderBuilder(DexterityBuilder):
    portal_type = 'DexterityFolder'


registry.builder_registry.register('dx folder', DexterityFolderBuilder)


def setup_dx_folder(portal):

    types_tool = portal.portal_types

    # Simplelayout Container
    fti = DexterityFTI('DexterityFolder')
    fti.schema = 'ftw.protectinactive.tests.dx_folder.IDexterityContainerSchema'
    fti.klass = 'ftw.protectinactive.tests.dx_folder.DexterityFolder'
    fti.behaviors = (
        'plone.app.dexterity.behaviors.metadata.IBasic',
        'plone.app.content.interfaces.INameFromTitle',
        'plone.app.dexterity.behaviors.metadata.IPublication')
    types_tool._setObject('DexterityFolder', fti)

    site_fti = types_tool.get('Plone Site')
    site_fti.allowed_content_types = ('DexterityFolder')
