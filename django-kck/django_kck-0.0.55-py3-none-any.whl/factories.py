import factory
from .models import DataProduct, RefreshQueue


class DataProductFactory(factory.django.DjangoModelFactory):
    value = {'somedata': f'{factory.Sequence(lambda n: n)} is what it is'}
    key = f'KEY-{factory.Sequence(lambda n: n)}'

    class Meta:
        model = DataProduct


class RefreshQueueFactory(factory.django.DjangoModelFactory):
    key = f'KEY-{factory.Sequence(lambda n: n)}'

    class Meta:
        model = RefreshQueue
