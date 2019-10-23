from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import TEST_USER_NAME
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
from zope.interface import Interface


class FtwContentnavLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.contentnav
        xmlconfig.file('configure.zcml', ftw.contentnav,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.contentnav:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


class ISampleDX(Interface):
    title = schema.TextLine(
        title=u'Title',
        required=False)

alsoProvides(ISampleDX, IFormFieldProvider)


class SampleBuilder(DexterityBuilder):
    portal_type = 'Sample'

registry.builder_registry.register('sample', SampleBuilder)


FTW_CONTENTNAV_FIXTURE = FtwContentnavLayer()
FTW_CONTENTNAV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_CONTENTNAV_FIXTURE,), name="FtwContentnav:Integration")
FTW_CONTENTNAV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_CONTENTNAV_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="FtwContentnav:Functional")
