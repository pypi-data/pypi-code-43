import datetime
import logging

from django_kck.hints import HintsManager

logger = logging.getLogger(__name__)


class BaseProcess(object):
    cache = None
    key_base = None
    domain_key = None

    def __init__(self, cache, key_base):
        self.cache = cache
        self.key_base = key_base

    def run(self, hints=None):
        return

    def domain(self, hints=None):
        hints = hints or HintsManager(self.cache)
        if self.domain_key:
            try:
                domain_list = hints.get(self.domain_key, prime_on_cache_miss=True)['value']
                logger.info('BaseProcess.domain() - returning domain_list: {}'.format(domain_list))
                return domain_list
            except KeyError:
                logger.warning(
                    'IntervalRefreshProcess({}) - attempt to fetch domain key {} failed'
                    .format(self.key_base, self.domain_key))
        return []


class IntervalRefreshProcess(BaseProcess):
    interval = datetime.timedelta(seconds=60)

    def run(self, hints=None):
        hints = hints or HintsManager(self.cache)
        domain = self.domain(hints=hints)
        if domain:
            for key in domain:
                cache_entry = hints.get(key, prime_on_cache_miss=True)
                if datetime.datetime.utcnow() - cache_entry['modified'] >= self.interval:
                    self.cache.refresh(key, queued=True, hints=hints)
