import inspect
import logging
import importlib
import pickle
import datetime
import random

from django.apps import AppConfig

from django_kck.parameters import BaseParameter
from django.apps import apps
from .hints import HintsManager
from .exceptions import EmptyQuerysetError
from .models import DataProduct, RefreshQueue

from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)

_cache_instance = None

CACHE_ENTRY_FIELDS = ['key', 'value', 'primer_name', 'version', 'modified', 'soft_expire', 'hard_expire']
KEYSEP = '/'
MAX_EXPECTED_REFRESH_SECONDS = 4 * 60 * 60  # four hours


class KeyParameterMismatch(Exception):
    pass


class UnregisteredPrimer(Exception):
    pass


class UnknownParameterType(Exception):
    pass


class UnpickleableData(Exception):
    pass


class VersionMismatch(Exception):
    pass


class Primer(object):

    prime_on_cache_miss = False
    key_base = None
    key = None
    soft_expire_seconds = None
    hard_expire_seconds = None
    hooks = ()
    parameters = None

    def __init__(self, key):
        self.key = key

    @property
    def soft_expire(self):
        if self.soft_expire_seconds:
            return datetime.datetime.utcnow() + datetime.timedelta(seconds=self.soft_expire_seconds)
        return None

    @property
    def hard_expire(self):
        if self.hard_expire_seconds:
            return datetime.datetime.utcnow() + datetime.timedelta(seconds=self.hard_expire_seconds)
        return None

    @classmethod
    def register_all_primers(cls, cache_instance):
        logger.debug('Primer.register_all_primers() entered')
        for installed_app_module in apps.get_app_configs():
            installed_app_module_as_string = installed_app_module.name
            logger.debug(f'Primer.register_all_primers() - examining module: {installed_app_module_as_string}')

            primers_module_as_string = f'{installed_app_module_as_string}.primers'
            try:
                primers_module = __import__(primers_module_as_string, fromlist=[''])
            except ModuleNotFoundError:
                continue

            logger.debug('Primer.register_all_primers() - type(primers_module): {}'.format(type(primers_module)))
            # logger.debug('Primer.register_all_primers() - primers_module.__dict__: {}'.format(primers_module.__dict__))

            for name, pcls in primers_module.__dict__.items():
                logger.debug('Primer.register_all_primers() - inspecting {}, {}'.format(name, pcls))
                if pcls == Primer or not type(pcls) == type or not issubclass(pcls, Primer):
                    continue
                logger.debug(f'Primer.register_all_primers() - registering {pcls.__name__}')
                pcls.register(cache_instance)

    @classmethod
    def register(cls, cache_instance):
        cache_instance.register_primer(cls)

    def compute(self, hints=None, cache=None):
        return None

    def prime(self, cache=None, hints=None):
        cache = cache or Cache.get_instance()
        hints = hints or HintsManager(cache)

        self.do_hooks('pre-prime', hints=hints, cache=cache)

        new_value = self.compute(hints=hints, cache=cache)
        cache_entry = cache.cache_entry(
            key=self.key,
            value=new_value,
            primer_name=self.key_base,
            soft_expire=self.soft_expire,
            hard_expire=self.hard_expire)

        hints.set_hint_key(cache_entry)
        self.do_hooks('post-prime', hints=hints, cache=cache)

        logger.info('Primer.prime() - calling set with: **{}'.format(cache_entry))
        cache.set(**cache_entry)

        return cache_entry

    def do_hooks(self, hook_type, cache, hints, **kwargs):
        logger.info('Primer.do_hooks({}) - entered'.format(hook_type))
        if not self.hooks:
            logger.info('Primer.do_hooks({}) - no hooks found'.format(hook_type))
            return

        for hook in self.hooks:
            logger.info('processing {} hook'.format(hook.__class__.__name__))
            hook.key(self.key)
            hook.run_if_type_matches(hook_type, cache=cache, hints=hints, **kwargs)

    def parameter_dict(self):
        if KEYSEP not in self.key:
            return {}
        parts = self.key.split(KEYSEP)[1:]
        if len(parts) != len(self.parameters):
            raise KeyParameterMismatch(self.key)
        parameters = {}
        for n, p in enumerate(self.parameters):
            parameters[p.name] = p.from_str(parts[n])
        return parameters


class Cache(object):

    _primers = {}

    @classmethod
    def key_base(cls, key):
        if KEYSEP in key:
            return key.split(KEYSEP)[0]
        return key

    @classmethod
    def get_instance(cls, new_instance=False):
        global _cache_instance
        if not _cache_instance or new_instance:
            logger.info('initializing new cache')
            _cache_instance = cls()
        return _cache_instance

    def __init__(self):
        Primer.register_all_primers(self)

    def run_processes(self):
        logger.info('Cache.run_processes() - entered')
        for key_base, primer_cls in self._primers.items():
            logger.info('Cache.run_processes() - examining {}, {}'.format(key_base, primer_cls.__name__))
            if hasattr(primer_cls, 'processes'):
                for process_cls in primer_cls.processes:
                    process_cls(self, key_base).run()

    def build_key(self, key_base, **kwargs):
        logger.debug('Cache.build_key() entered')
        primer_cls = self.primer(key_base)
        logger.debug('Cache.build_key() found primer (type: {}) for {}'.format(type(primer_cls), key_base))
        if not hasattr(primer_cls, 'parameters') or not primer_cls.parameters:
            logger.debug('Cache.build_key() - no parameters found, returning: {}'.format(key_base))
            return key_base
        parts = [key_base]
        logger.debug('iterating over {} parameters'.format(len(primer_cls.parameters)))
        for p in primer_cls.parameters:
            if not issubclass(p.__class__, BaseParameter):
                raise UnknownParameterType(p)
            parts.append(p.to_str(kwargs[p.name]))
        logger.debug('Cache.build_key() - returning: {}'.format(KEYSEP.join(parts)))
        return KEYSEP.join(parts)

    def build_system_key(self, key_type, key=None):
        parts = ['KCK', key_type]
        if key:
            parts.append(key)
        return KEYSEP.join(parts)

    def register_primer(self, primer_cls):
        self._primers[primer_cls.key_base] = primer_cls

    def primer(self, key):
        keybase = self.key_base(key)
        if keybase in self._primers and issubclass(self._primers[keybase], Primer):
            return self._primers[keybase]
        return None

    def primer_instance(self, key):
        return self.primer(key)(key)

    def unset(self, key):
        DataProduct.objects.filter(key=key).delete()

    def get(self, key, prime_on_cache_miss=None):

        current_time = datetime.datetime.utcnow()

        # try to return cached version
        queryset = DataProduct.objects.filter(
            Q(key=key) & (Q(hard_expire=None) | Q(hard_expire__gt=current_time)))

        try:
            cache_entry = self.cache_entry(queryset=queryset, key=key)

            # if soft expire is defined and in the past, request a refresh
            if cache_entry['soft_expire'] and cache_entry['soft_expire'] < datetime.datetime.utcnow():
                self.refresh(key, queued=True)

            return cache_entry

        # try to prime
        except (DataProduct.DoesNotExist, EmptyQuerysetError):

            # if a primer does not exist, raise KeyError
            primer_cls = self.primer(key)
            if not primer_cls:
                raise KeyError(key)

            # if prime_on_cache_miss is True on primer or in param to this method, then prime
            if (primer_cls.prime_on_cache_miss and prime_on_cache_miss is not False) or prime_on_cache_miss:
                return primer_cls(key).prime(cache=self)

            # failing all else, raise KeyError
            raise KeyError(key)

    def set(self, key, value, primer_name=None, modified=None, version=None,
            soft_expire=None, hard_expire=None, hints=None, check_version=None,
            inhibit_hooks=None):
        inhibit_hooks = inhibit_hooks or []
        params = dict(
            key=key,
            value=value,
            primer_name=primer_name,
            soft_expire=soft_expire,
            hard_expire=hard_expire,
            modified=modified if modified else datetime.datetime.utcnow())
        if version:
            params['version'] = version
        logger.info(f'set() - params: {params}')
        primer_obj = None
        hints = hints or HintsManager(self)
        primer_cls = self.primer(key)
        if primer_cls:
            primer_obj = primer_cls(key)

            try:
                cache_entry = self.get(key, prime_on_cache_miss=False)
                hints.set_hint_key(cache_entry)
            except KeyError:
                pass

            if 'pre-set' not in inhibit_hooks:
                primer_obj.do_hooks('pre-set', hints=hints, cache=self, **params)

        # version checking
        if check_version:

            try:
                if DataProduct.objects.filter(key=key, version=check_version).update(**params) < 1:
                    raise VersionMismatch((key, check_version))
            except AttributeError:
                raise UnpickleableData(params['value'])

            cache_entry = self.cache_entry(**params)

        else:

            data_product = DataProduct(**params)

            # look for errors saving
            #
            #   note:
            #     AttributeErrors read something like
            #       "AttributeError: 'Query' object has no attribute 'contains_aggregate'"
            #     and this basically means that the value is a QuerySetResult or something
            #     that Pickle is having trouble dealing with
            #
            try:
                data_product.save()
            except AttributeError:
                raise UnpickleableData(params['value'])

            cache_entry = self.cache_entry(data_product=data_product)

        if primer_cls and 'post-set' not in inhibit_hooks:
            primer_obj.do_hooks('post-set', hints=hints, cache=self, **params)

        return cache_entry

    def cache_entry(self, data_product=None, queryset=None, key=None, value=None, primer_name=None,
                    version=None, soft_expire=None, hard_expire=None, modified=None):
        if queryset is not None:
            ret = queryset.values(*CACHE_ENTRY_FIELDS)
            if ret:
                return ret[0]
            raise EmptyQuerysetError(key)

        if data_product:
            rec = {}
            for fld in CACHE_ENTRY_FIELDS:
                rec[fld] = getattr(data_product, fld)
            return rec

        ret = dict(key=key, value=value, primer_name=primer_name,
                   soft_expire=soft_expire, hard_expire=hard_expire)
        ret['modified'] = modified if modified else datetime.datetime.utcnow()
        ret['version'] = version if version else random.randint(0, 999999999)

        return ret

    @staticmethod
    def cmp_cache_entries(a, b, disregard_keys=None, value_filters=None):
        disregard_keys = disregard_keys or []
        if not disregard_keys and not value_filters:
            return a == b
        if len(a.keys()) != len(b.keys()):
            return False
        for k, v in a.items():
            if k in disregard_keys:
                continue
            if not value_filters:
                if v != b[k]:
                    return False
            try:
                f = value_filters[k]
                fv = f(v)
                if fv != f(b[k]):
                    return False
            except (TypeError, KeyError):
                if v != b[k]:
                    return False
        return True

    def is_set(self, key):
        try:
            cache_entry = self.get(key)
            return True
        except KeyError:
            return False

    def refresh(self, key, queued=True, hints=None):
        # refresh non-queued requests immediately
        if not queued:
            primer_class = self.primer(key)
            try:
                primer_obj = primer_class(key)
            except TypeError:
                raise UnregisteredPrimer(key)

            syskey_refresh = self.build_system_key('refreshing', key=key)
            curr_time = datetime.datetime.utcnow()
            logger.info('setting refresh syskey: {}'.format(syskey_refresh))
            self.set(
                **self.cache_entry(
                    key=syskey_refresh,
                    value={'start': curr_time},
                    hard_expire=curr_time + datetime.timedelta(seconds=MAX_EXPECTED_REFRESH_SECONDS)))
            logger.info('post-set refresh syskey: {}'.format(syskey_refresh))
            ret = primer_obj.prime(hints=hints)
            logger.info('unsetting refresh syskey: {}'.format(syskey_refresh))
            self.unset(syskey_refresh)

            return ret

        # save a refresh request
        new_refresh_queue_entry = RefreshQueue(
            key=key,
            primer_name=Cache.key_base(key),
            hints=hints.to_dict() if hints else None)
        new_refresh_queue_entry.save()

    def is_refreshing(self, key):
        system_key = self.build_system_key('refreshing', key=key)
        try:
            cache_entry = self.get(system_key)
        except KeyError:
            return False
        return ('start' in cache_entry['value'] and
                cache_entry['value']['start'] < datetime.datetime.utcnow())

    def refresh_requests(self, claimant=None, primer_names=None):
        queryset = RefreshQueue.objects
        if primer_names:
            queryset = queryset.filter(primer_name__in=primer_names)
        if claimant:
            queryset = queryset.filter(claimant=claimant)
        return queryset

    def claim_refresh_requests(self, claimant, max_requests=None, primer_names=None):

        # build a queryset of refresh requests
        queryset = RefreshQueue.objects
        if primer_names:
            queryset = queryset.filter(primer_name__in=primer_names)
        ordered_queryset = queryset.order_by('requested')

        # build the key list
        key_list = []
        for rec in ordered_queryset.values('key'):
            if rec['key'] in key_list:
                continue
            key_list.append(rec['key'])
            if max_requests and len(key_list) >= max_requests:
                break

        # claim the refresh requests
        queryset.filter(key__in=key_list).filter(claimant=None).update(claimant=claimant, claimed=datetime.datetime.utcnow())

    def perform_claimed_refreshes(self, claimant):
        logger.info('Cache.perform_claimed_refreshes({}) - entered'.format(claimant))
        queryset = RefreshQueue.objects.filter(claimant=claimant).order_by('key')
        current_key = None
        current_hints = None
        del_entries = []
        for refresh_queue_entry in queryset:

            if current_key is None:
                current_hints = HintsManager(self)
                current_key = refresh_queue_entry.key

            elif current_key != refresh_queue_entry.key:
                self.refresh(current_key, hints=current_hints, queued=False)
                for entry in del_entries:
                    entry.delete()
                current_hints = HintsManager(self)
                current_key = refresh_queue_entry.key
                del_entries = []
            if refresh_queue_entry.hints:
                current_hints.import_from_dict(refresh_queue_entry.hints)
            del_entries.append(refresh_queue_entry)

        if current_key:
            self.refresh(current_key, hints=current_hints, queued=False)
            for entry in del_entries:
                entry.delete()
