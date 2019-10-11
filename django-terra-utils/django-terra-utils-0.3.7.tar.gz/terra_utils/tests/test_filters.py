from django.test import TestCase

from terra_utils.tests.test_app.models import DummyModel
from terra_utils.tests.test_app.serializers import DummySerializer

from rest_framework import generics
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from terra_utils.filters import JSONFieldOrderingFilter

factory = APIRequestFactory()


class JSONOrderingTestCase(TestCase):

    def setUp(self):
        for idx in range(3):
            data = {
                'name': 'a' * (idx + 1),
                'properties': {
                    'key': idx,
                }
            }
            # using Layer model as fake tests models needs lot of development
            DummyModel.objects.create(**data)

    def test_json_ordering(self):
        class OrderingListView(generics.ListAPIView):
            permission_classes = ()
            queryset = DummyModel.objects.all().order_by('pk')
            serializer_class = DummySerializer
            filter_backends = (JSONFieldOrderingFilter, )
            ordering_fields = ['properties', ]

        view = OrderingListView.as_view()

        # testing ascending
        request = factory.get('/',
                              {api_settings.ORDERING_PARAM: 'properties__key'})
        response = view(request)

        self.assertListEqual(
            [0, 1, 2],
            [i['properties']['key'] for i in response.data['results']])

        # testing descending
        request = factory.get('/',
                              {api_settings.ORDERING_PARAM: '-properties__key'})
        response = view(request)

        self.assertListEqual(
            [2, 1, 0],
            [i['properties']['key'] for i in response.data['results']])

        request = factory.get('/', {api_settings.ORDERING_PARAM: 'name'})
        response = view(request)

        # testing normal field
        self.assertListEqual(
            [0, 1, 2],
            [i['properties']['key'] for i in response.data['results']])
