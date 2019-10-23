# -*- coding: utf-8 -*-
import logging
from abc import ABC, abstractmethod
from itertools import chain
from pynlple.exceptions import DataSourceException


class Source(ABC):

    def __repr__(self, *args, **kwargs):
        return '{}({})'.format(str(self.__class__.__name__), repr(vars(self)))


class SkippingSource(Source):

    def __init__(self):
        self.__skips = None

    @property
    def skips(self):
        return self.__skips

    def skip(self, skip):
        if skip is None or skip < 0:
            raise DataSourceException('SkippingSource cannot skip None or negative value.')
        self.__skips = skip
        self._skip(skip)
        return self

    @abstractmethod
    def _skip(self, amount):
        raise NotImplementedError('Private method not implemented.')


class TakingSource(Source):

    def __init__(self):
        self.__takes = None

    @property
    def takes(self):
        return self.__takes

    def take(self, take):
        if take is None or take < 0:
            raise DataSourceException('TakingSource cannot take None or negative value.')
        self.__takes = take
        self._take(take)
        return self

    @abstractmethod
    def _take(self, amount):
        raise NotImplementedError('Private method not implemented.')


class SequentialSource(Source):

    def __init__(self):
        self.__slides = None
        self.__position = None
        self.__slided = 0

    @property
    def slides(self):
        return self.__slides

    @property
    def position(self):
        return self.__position

    @property
    def slided(self):
        return self.__slided

    def slide(self, slide):
        if slide is None or slide < 0:
            raise DataSourceException('SequentialSource cannot take None or negative value.')
        self.__slides = slide
        self._slide(slide)
        return self

    def reset(self):
        self.__slides = None
        self.__position = None
        self.__slided = 0
        return self

    @abstractmethod
    def _slide(self, slide):
        raise NotImplementedError('Private method not implemented.')

    def _move(self, to_position, count):
        if to_position is None:
            raise ValueError('Cannot move to None position.')
        if count is None or count < 0:
            raise ValueError('Cannot add None or negative count.')
        self.__position = to_position
        self.__slided = self.slided + count
        self._slide(self.__slides)
        return self


class BulkSource(TakingSource):

    logger = logging.getLogger(__name__)

    def _take(self, amount):
        pass

    def __init__(self, sequential_source, bulk_size=1000, reset_source=True):
        self.sequential_source = sequential_source
        if not bulk_size:
            raise ValueError('Bulk size cannot be None.')
        if bulk_size <= 0:
            raise ValueError('Bulk size must be positive number; it is: %d', bulk_size)
        self.bulk = bulk_size
        self.reset_source = reset_source
        super().__init__()

    def get_data(self):
        source = self.sequential_source
        if self.reset_source:
            source = source.reset()
            BulkSource.logger.info('Start draining sequentially %s from source %s.',
                                   str(self.takes) if self.takes is not None else 'all data',
                                   repr(source))
        else:
            BulkSource.logger.info('Continue draining sequentially %s from %s, position %s.',
                                   str(self.takes) if self.takes is not None else 'all data',
                                   repr(source), str(source.position))
        all_data = []
        try:
            if self.takes is None or self.takes > 0:
                pull = True
            else:
                pull = False
            while pull:
                take = self.__get_window_size(source.slided)
                BulkSource.logger.info('Getting %d-%d bulk from sequential source',
                                       source.slided, (source.slided + take))

                window_data = source.slide(take).get_data()
                all_data.append(window_data)

                got = len(window_data)
                if self.takes is not None and self.takes > 0:
                    pull = source.slided < self.takes and got == take
                else:
                    pull = got == take
            if self.takes is not None:
                SkippingBulkSource.logger.info('Stopped draining from source at position %s, requested count: %d',
                                               str(source.position), source.slided)
            else:
                SkippingBulkSource.logger.info('Source seems to be exhausted at position: %s, count: %d',
                                               str(source.position), source.slided)
        except Exception as e:
            raise DataSourceException('Error while dumping bulk %d-%d from %s:\n%s' %
                                      (source.slided, (source.slided + take), repr(self), repr(e)))
        return list(chain.from_iterable(all_data))

    def __get_window_size(self, got_total):
        # If there are limits on amount to take, check if we reached them
        if self.takes:
            to_limit_leftover = self.takes - got_total
            if self.bulk > to_limit_leftover:
                return to_limit_leftover
            else:
                return self.bulk
        else:
            return self.bulk


class SkippingBulkSource(TakingSource):

    logger = logging.getLogger(__name__)

    def _take(self, amount):
        pass

    def __init__(self, skip_n_taking_source, bulk_size=5000):
        self.skip_n_taking_source = skip_n_taking_source
        self.bulk = bulk_size
        super().__init__()

    def get_data(self):
        SkippingBulkSource.logger.info('Start draining %s from %s.',
                                       str(self.takes) if self.takes is not None else 'all data',
                                       repr(self.skip_n_taking_source))
        all_data = []
        total = 0
        try:
            if self.takes is None or self.takes > 0:
                pull = True
            else:
                pull = False
            while pull:
                take = self.__get_window_size(total)
                SkippingBulkSource.logger.info('Getting %d-%d bulk from the skipping source'
                                               % (total, total+take))
                data = self.skip_n_taking_source.skip(total).take(take).get_data()
                all_data.append(data)

                got = len(data)
                total += got
                pull = total < self.takes if self.takes is not None else got == take

            if self.takes is not None:
                SkippingBulkSource.logger.info('Stopped draining from source at requested point: %d',
                                               total)
            else:
                SkippingBulkSource.logger.info('Source seems to be exhausted at count: %d',
                                               total)
        except Exception as e:
            raise DataSourceException('Error while dumping bulk %d-%d from %s:\n%s' %
                                      (total, (total + take), repr(self), repr(e)))
        return list(chain.from_iterable(all_data))

    def __get_window_size(self, got_total):
        # If there are limits on amount to take, check if we reached them
        if self.takes:
            to_limit_leftover = self.takes - got_total
            if self.bulk > to_limit_leftover:
                return to_limit_leftover
            else:
                return self.bulk
        else:
            return self.bulk
