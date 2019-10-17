import datetime
import logging
import dateutil

logger = logging.getLogger(__name__)


class HintsManager(object):
    """
    The HintsManager addresses the issue that has come up where the concept of a 'hint'
    is used to suggest some bit of information that is being propagated to avoid a
    relatively-expensive query, but the implementation varies enough to where it's
    getting tricky to keep track of exactly what a hint means.

    This class nails down the concept of a hint to mean exactly a substitution of a result
    for a specific key that would otherwise have been resolved via a cache hit.

    ***Further, the sets record the timestamp and the get method can restrict its use of the
    hints by time range.***

    The hint can handle both sets and deletes.
    """

    _hints_by_key = {}
    _hints_by_timestamp = {}
    _purged = {}
    _cache_obj = None

    def __init__(self, cache_obj):
        self._cache_obj = cache_obj

    def import_from_dict(self, hints_dict):

        # import hints
        for key, cache_records in hints_dict['hints'].items():
            for cache_record in cache_records:
                if key not in self._hints_by_key:
                    self.set_hint_key(cache_record)
                    continue

        # import purged
        for key, datetime_list in hints_dict['purged'].items():
            self.unset_hint_key(key, max(datetime_list))

    def set_hint_key(self, cache_entry=None):
        """setter for values"""

        if cache_entry['key'] not in self._hints_by_key:
            self._hints_by_key[cache_entry['key']] = [cache_entry]
        else:
            self._hints_by_key[cache_entry['key']].append(cache_entry)

        # self._hints_by_key[cache_entry['key']] = (cache_entry, cache_entry['modified'])

        if cache_entry['modified'] not in self._hints_by_timestamp:
            self._hints_by_timestamp[cache_entry['modified']] = []
        self._hints_by_timestamp[cache_entry['modified']].append(cache_entry)

    def unset_hint_key(self, key=None, unset_datetime=None):
        """setter for deletions"""
        unset_datetime = unset_datetime or datetime.datetime.utcnow()
        if key not in self._purged:
            self._purged[key] = [unset_datetime]
        else:
            self._purged[key].append(unset_datetime)

    def count(self, since=None, exclude_keys=None):
        """ count number of hints with or without since param """
        ret = 0
        for ts in self._hints_by_timestamp.keys():
            if not since or ts >= since:
                ret += len(self._hints_by_timestamp[ts])

        if exclude_keys:
            for key in exclude_keys:
                if key in self._hints_by_key:
                    ret -= 1

        return ret

    def hinted_keys(self):
        return self._hints_by_key.keys()

    def get(self, key, prime_on_cache_miss=False, hints_only=False):
        last_purge = None
        if key in self._purged:
            last_purge = max(self._purged[key])
        max_modified_date = None
        most_recent_cache_record = None

        if key not in self._hints_by_key:

            if hints_only:
                raise KeyError(key)

            cache_entry = self._cache_obj.get(key, prime_on_cache_miss=prime_on_cache_miss)
            if ('modified' in cache_entry and cache_entry['modified'] and
                    last_purge and last_purge > cache_entry['modified']):
                raise KeyError()
            self.set_hint_key(cache_entry)
            return cache_entry

        for cache_record in self.get_all_hints(key):
            logger.debug('cache record for key: {} - {}'.format(key, cache_record))

            if type(cache_record['modified']) is str:
                cache_record['modified'] = dateutil.parser.parse(cache_record['modified'])
            if last_purge and cache_record['modified'] < last_purge:
                continue
            if max_modified_date is None or max_modified_date < cache_record['modified']:
                max_modified_date = cache_record['modified']
                most_recent_cache_record = cache_record

        if most_recent_cache_record:
            return most_recent_cache_record

        return self._cache_obj.get(key, prime_on_cache_miss=prime_on_cache_miss)

    def get_all_hints(self, key):
        return self._hints_by_key[key]

    def find_hint(self, key, match_entry, sort_key=None, index=0, invert=False,
                  value_filters=None, disregard_keys=None):
        try:
            unsorted_cache_entries = self.get_all_hints(key)
        except KeyError:
            return None
        if not unsorted_cache_entries:
            return None
        if invert:
            cache_entries = sorted(
                filter(
                    lambda e: not self._cache_obj.cmp_cache_entries(
                        e,
                        match_entry,
                        value_filters=value_filters,
                        disregard_keys=disregard_keys),
                    unsorted_cache_entries),
                key=sort_key)
        else:
            cache_entries = sorted(
                filter(
                    lambda e: self._cache_obj.cmp_cache_entries(
                        e,
                        match_entry,
                        value_filters=value_filters,
                        disregard_keys=disregard_keys),
                    unsorted_cache_entries),
                key=sort_key)
        try:
            return cache_entries[index]
        except IndexError:
            return None

    def to_dict(self):
        """dump to dict"""
        return {'hints': self._hints_by_key, 'purged': self._purged}

    def from_dict(self, d):
        """load dict"""
        if 'hints' in d:
            self._hints_by_key = d['hints']
        if 'purged' in d:
            self._purged = d['purged']

    def update_from_dict(self, d):
        """add keys from dict d to internal dict"""
        if 'hints' in d:
            self._hints_by_key = {**self._hints_by_key, **d['hints']}
        if 'purged' in d:
            self._purged = {**self._purged, **d['purged']}
