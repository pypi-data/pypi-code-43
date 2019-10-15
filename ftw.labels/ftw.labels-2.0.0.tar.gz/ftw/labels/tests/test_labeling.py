from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelRoot
from ftw.labels.interfaces import ILabelSupport
from ftw.labels.interfaces import ILabeling
from ftw.labels.labeling import Labeling
from ftw.labels.testing import ADAPTERS_ZCML_LAYER
from ftw.testing import MockTestCase
from plone.app.testing import TEST_USER_ID
from zope.annotation import IAttributeAnnotatable
from zope.component import queryAdapter


def label_titles(labels):
    return [label['title'] for label in labels]


class TestLabeling(MockTestCase):
    layer = ADAPTERS_ZCML_LAYER

    def setUp(self):
        super(TestLabeling, self).setUp()
        Labeling.user_id = lambda x: TEST_USER_ID  # needed to avoid plone.api.portal.get error
        self.root = self.providing_stub([ILabelRoot, IAttributeAnnotatable])
        self.document = self.providing_stub([ILabelSupport,
                                             IAttributeAnnotatable])
        self.set_parent(self.document, self.root)
        self.replay()
        self.jar = ILabelJar(self.root)

    def test_adapter(self):
        self.assertTrue(
            queryAdapter(self.document, ILabeling),
            'The labeling adapter is not registered for ILabeling')

    def test_available_labels(self):
        self.jar.add('Question', '#00FF00', False)
        self.jar.add('Read', 'red', True)
        labeling = ILabeling(self.document)
        self.assertEqual(
            [[{'label_id': 'read',
             'title': 'Read',
             'color': 'red',
             'active': False,
             'by_user': True}],
             [{'label_id': 'question',
             'title': 'Question',
             'color': '#00FF00',
             'active': False,
             'by_user': False}]],
            list(labeling.available_labels()))

    def test_available_labels_empty(self):
        labeling = ILabeling(self.document)
        self.assertEqual([[], []], labeling.available_labels())

    def test_available_label(self):
        self.jar.add('Question', '#00FF00', False)
        self.jar.add('Read', 'red', True)
        labeling = ILabeling(self.document)

        labeling.update(['question'])
        labeling.pers_update(['read'], True)
        self.assertEqual(
            [[{'label_id': 'read',
             'title': 'Read',
             'color': 'red',
             'active': True,
             'by_user': True}],
             [{'label_id': 'question',
              'title': 'Question',
              'color': '#00FF00',
              'active': True,
              'by_user': False}]],
            list(labeling.available_labels()))

    def test_update__enable_labels(self):
        self.jar.add('Bug', 'red', False)
        self.jar.add('Question', 'green', True)
        self.jar.add('Feature', 'purple', True)

        labeling = ILabeling(self.document)
        self.assertEqual([], labeling.active_labels())

        labeling.update(['bug'])
        labeling.pers_update(['feature'], True)
        self.assertItemsEqual(['Bug', 'Feature'],
                              label_titles(labeling.active_labels()))

    def test_update__disable_labels(self):
        self.jar.add('Bug', 'red', False)
        self.jar.add('Question', 'green', False)
        self.jar.add('Feature', 'purple', True)

        labeling = ILabeling(self.document)
        labeling.update(['bug', 'question'])
        labeling.pers_update(['feature'], True)
        self.assertItemsEqual(['Bug', 'Feature', 'Question'],
                              label_titles(labeling.active_labels()))

        labeling.update(['bug'])
        labeling.pers_update(['feature'], False)
        self.assertItemsEqual(['Bug'],
                              label_titles(labeling.active_labels()))

        labeling.update([])
        self.assertEqual([], labeling.active_labels())

    def test_update_raises_LookupError_when_label_not_in_jar(self):
        self.assertEqual(0, len(self.jar.list()))
        self.jar.add('Question', '', False)
        labeling = ILabeling(self.document)
        with self.assertRaises(LookupError) as cm:
            labeling.update(['something'])

        self.assertEqual(
            'Cannot activate label: the label'
            ' "something" is not in the label jar. '
            'Following labels ids are available: question',
            str(cm.exception))

    def test_active_labels(self):
        self.jar.add('Question', '', False)
        self.jar.add('Bug', '', False)
        self.jar.add('Duplicate', '', True)

        labeling = ILabeling(self.document)
        labeling.update(['bug'])
        labeling.pers_update(['duplicate'], True)
        self.assertListEqual(
            [{'label_id': 'bug',
              'title': 'Bug',
              'color': '',
              'by_user': False},
             {'label_id': 'duplicate',
              'title': 'Duplicate',
              'color': '',
              'by_user': True}],
            labeling.active_labels())

    def test_active_labels_is_sorted(self):
        self.jar.add('Zeta-0', '', False)
        self.jar.add('zeta-1', '', False)
        self.jar.add('alpha-0', '', False)
        self.jar.add('\xc3\x84lpha-1', '', False)
        self.jar.add('Alpha-2', '', False)

        labeling = ILabeling(self.document)
        labeling.update([
            'zeta-0',
            'zeta-1',
            'alpha-0',
            'alpha-1',
            'alpha-2',
        ])

        self.assertEqual(
            ['alpha-0', '\xc3\x84lpha-1', 'Alpha-2', 'Zeta-0', 'zeta-1'],
            [label.get('title') for label in labeling.active_labels()])

    def test_active_labels_filters_deleted_labels(self):
        self.jar.add('Question', 'blue', False)
        self.jar.add('Bug', 'red', False)

        labeling = ILabeling(self.document)
        labeling.update(['question', 'bug'])

        self.jar.remove('bug')

        self.assertEqual(
            [{'label_id': 'question',
             'title': 'Question',
             'color': 'blue',
             'by_user': False}],
            list(labeling.active_labels()))
