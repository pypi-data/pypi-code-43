import pytest
import logging
from django_kck.cache import Cache
from django_kck.models import DataProduct

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class BaseCacheTest(object):
    @pytest.fixture
    def f_cache(self):
        return lambda: Cache.get_instance(new_instance=True)

    def simulate_cache_entry(self, cache_entry):
        DataProduct(**cache_entry).save()

    def update_cache_entry(self, key, **kwargs):
        cache = Cache.get_instance()
        current_cache_entry = cache.get(key)
        data_product = DataProduct.objects.get(key=current_cache_entry['key'])
        for key, val in kwargs.items():
            setattr(data_product, key, val)
        data_product.save()

    def assert_current_cache_entry_value(self, cache, key, value):
        cache_entry = cache.get(key)
        logger.info('comparing values: {}, {}'.format(cache_entry['value'], value))
        assert cache_entry['value'] == value
