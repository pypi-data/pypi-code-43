import itertools

from enum import Enum
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict

_first_checkpoint_name = 'start'
_default_checkpoint_name = 'checkpoint'
_start_column = '-start-'
_duration_column = '-duration-'
_count_column = '-count-'
_average_column = '-average-'

_sep_summary_start = '    '  # 4 chars preferred
_sep_name_to_columns = ': '  # 2 chars preferred
_del_one_count = '-'  # 1 char preferred


class Timer:
    _name = None
    _output_format = None
    _decimals = None
    _checkpoints = None
    _start_checkpoint = None
    _end_checkpoint = None
    _current_checkpoint = None
    _show_count = None
    _show_average = None
    _default_checkpoint_count = 0

    @classmethod
    def __new__(cls, *args, name='timer', output_format=str, print_decimals=2, **kwargs):
        if not hasattr(cls, '_timer') or cls._timer is None:
            cls._timer = super(Timer, cls).__new__(cls)

            cls._name = name
            cls._output_format = output_format
            cls._decimals = print_decimals
            cls._show_count = 'infer'
            cls._show_average = 'infer'

            cls._checkpoints = Checkpoints()
            cls._checkpoints.new_checkpoint(name=_first_checkpoint_name, created_by=CheckpointType.method)
            cls._start_checkpoint = cls._checkpoints[_first_checkpoint_name][-1]
            cls._current_checkpoint = None
            cls._end_checkpoint = None

        return cls._timer

    def __call__(self, description=None):
        return self._describe_time(description=description)

    @classmethod
    def _describe_time(cls, description=None):
        if cls._output_format == str:
            return cls._describe_time_as_string(description=description)
        elif cls._output_format == float:
            return cls._describe_time_as_float()
        else:
            raise NotImplementedError()

    @classmethod
    def _describe_time_as_string(cls, show_checkpoint=True, description=None):
        min_length = 2 + cls._decimals + (cls._decimals > 0)

        name = f'{cls._name}: '
        time = f'{cls.duration().total_seconds():{min_length}.{cls._decimals}f}s'

        time_as_string = name + time
        if show_checkpoint and cls._current_checkpoint is not None:
            checkpoint_name = f'    {cls._current_checkpoint.name}: ' if cls._current_checkpoint.name else '    '
            checkpoint_time = f'{cls._current_checkpoint.duration().total_seconds():{min_length}.{cls._decimals}f}s'
            time_as_string += checkpoint_name + checkpoint_time

        if description is not None:
            time_as_string += '    ' + description

        return time_as_string

    @classmethod
    def _describe_time_as_float(cls):
        return cls.duration().total_seconds()

    @classmethod
    def _time_from_start(cls, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        return timestamp - cls._start_checkpoint.start

    @classmethod
    def new_checkpoint(cls, name=None):
        if name is None:
            name = f'{_default_checkpoint_name}_{cls._default_checkpoint_count}'
            cls._default_checkpoint_count += 1

        return cls._new_checkpoint(name=name, created_by=CheckpointType.method)

    @classmethod
    def _new_checkpoint(cls, *, name, created_by):
        cls.end_checkpoint()
        cls._checkpoints.new_checkpoint(name=name, created_by=created_by)
        checkpoint = cls._checkpoints.last_active_checkpoint(name)

        cls._current_checkpoint = checkpoint
        return checkpoint

    @classmethod
    def duration(cls):
        start_time = cls._start_checkpoint.start
        end_time = datetime.now()
        if cls._end_checkpoint is not None:
            raise
            end_time = cls._end_checkpoint.end or end_time
        return end_time - start_time

    @classmethod
    def set_unit(cls, unit=str):
        pass

    @classmethod
    def end_timer(cls):
        pass

    @classmethod
    def end_checkpoint(cls, name=None):
        if name is None:
            active_checkpoints = [cls._checkpoints.last_active_checkpoint(name) for name in cls._checkpoints]
            active_checkpoints = [c for c in active_checkpoints if c is not None and c._created_by == CheckpointType.method]
            if len(active_checkpoints) == 1:
                active_checkpoints[0].end_checkpoint()
                if active_checkpoints[0] == cls._current_checkpoint:
                    cls._current_checkpoint = None
            elif len(active_checkpoints) > 1:
                raise ValueError('attempted to `end_checkpoint` implicitly while having multiple active checkpoints '
                                 'that have been created by the timers `new_checkpoint()` method. ')
            return

        if cls._current_checkpoint == cls._checkpoints.last_active_checkpoint(name):
            cls._current_checkpoint = None
        cls._checkpoints.end_checkpoint(name)

    @classmethod
    def _has_checkpoint(cls):
        return len(cls._checkpoints) > 1

    @classmethod
    def _has_active_checkpoint(cls):
        active_checkpoints = [cls._checkpoints.last_active_checkpoint(name) for name in cls._checkpoints]
        return len(active_checkpoints) > 0

    @classmethod
    def summary(cls):
        cs = cls._checkpoints.summary()

        length_name = max(len(name) for name in cs)

        max_start_time = cls.duration().total_seconds()
        length_start_time = max(len(_start_column), len(f'{max_start_time:.0f}') + cls._decimals + (cls._decimals > 0))
        length_start_time_header = max(len(_start_column), 1 + len(f'{max_start_time:.0f}') + cls._decimals + (cls._decimals > 0))

        max_duration = max(v['total_duration'].total_seconds() for v in cs.values())
        length_duration = max(len(_duration_column), len(f'{max_duration:.0f}') + cls._decimals + (cls._decimals > 0))
        length_duration_header = max(len(_duration_column), 1 + len(f'{max_duration:.0f}') + cls._decimals + (cls._decimals > 0))

        max_count = max(v['count'] for v in cs.values())
        length_count = max(len(_count_column), len(str(max_count)))

        max_average = max((v['total_duration'] / v['count']).total_seconds() for v in cs.values())
        length_average = max(len(_average_column), len(f'{max_average:.0f}') + cls._decimals + (cls._decimals > 0))
        length_average_header = max(len(_average_column), 1 + len(f'{max_average:.0f}') + cls._decimals + (cls._decimals > 0))

        # Header
        _summary = f'{cls._name} summary\n'
        _summary += f'{"":{length_name}}'
        _summary += f'   {_duration_column:>{length_duration_header}}'
        if cls._show_average and max_count > 1:
            _summary += f'    {_average_column:>{length_average_header}}'
        if cls._show_count and max_count > 1:
            _summary += f'   {_count_column:>{length_count}}'
        _summary += f'{_sep_summary_start} {_start_column:>{length_start_time_header}}'
        _summary += '\n'

        # Checkpoint entries
        name_first = next(iter(cs))
        v_first = cs[name_first]
        length_until_start = len(_sep_name_to_columns) + \
                             length_duration + 1 + \
                             (length_average + 4 if cls._show_average and max_count > 1 else 0) + \
                             (length_count + 3 if cls._show_count and max_count > 1 else 0) + \
                             len(_sep_summary_start)

        _summary += f'{name_first:{length_name}}'
        _summary += f'{" ":{length_until_start}}{v_first["total_duration"].total_seconds():{length_start_time}.{cls._decimals}f}s\n'

        for name, v in itertools.islice(cs.items(), 1, None):
            time_from_start = cls._time_from_start(timestamp=v["first_start_time"]).total_seconds()

            _summary += f'{name:{length_name}}'
            _summary += f'{_sep_name_to_columns}{v["total_duration"].total_seconds():{length_duration}.{cls._decimals}f}s'
            if cls._show_average and max_count > 1:
                _summary += f'   {(v["total_duration"] / v["count"]).total_seconds(): {length_average}.{cls._decimals}f}s'
            if cls._show_count and max_count > 1:
                count = str(v['count']) if v['count'] > 1 else _del_one_count
                _summary += f'   {count:>{length_count}}'
            _summary += f'{_sep_summary_start}{time_from_start: {length_start_time}.{cls._decimals}f}s'
            _summary += '\n'

        # Final line
        _summary += f'{"end":{length_name}}{" ":{length_until_start}}{cls.duration().total_seconds(): {length_start_time}.{cls._decimals}f}s\n'
        return _summary

    @classmethod
    def restart(cls):
        cls._checkpoints.clear()
        cls._checkpoints.new_checkpoint(name=_first_checkpoint_name, created_by=CheckpointType.method)
        cls._start_checkpoint = cls._checkpoints.last_active_checkpoint(_first_checkpoint_name)
        cls._end_checkpoint = None
        cls._current_checkpoint = None
        cls._default_checkpoint_count = 0
        return cls._timer


def time_this_method(method=None, name=None):
    def wrapper(method):
        def _time_this_method(*args, **kwargs):
            _name = name or method.__name__
            timer._new_checkpoint(name=_name, created_by=CheckpointType.wrapper)
            returned_from_method = method(*args, **kwargs)
            timer.end_checkpoint(name=_name)
            return returned_from_method
        return _time_this_method

    # decorator call, i.e. `@time_this_method`
    if method is not None:
        return wrapper(method)

    # factory call, i.e.`@time_this_method()`
    return wrapper


class Checkpoint:
    def __init__(self, name=None, start=None, created_by=None):
        if created_by is None:
            created_by = CheckpointType.method
        else:
            if created_by not in CheckpointType:
                raise ValueError(f'unsupported creation type: {created_by}. Select from {CheckpointType.__name__}')

        self.name = name or _default_checkpoint_name
        self.start = start or datetime.now()
        self.end = None
        self._created_by = created_by

    def __eq__(self, other):
        return type(other) == type(self) and \
               other.start == self.start and \
               other.end == self.end and \
               other.name == self.name

    def duration(self):
        if self.end is None:
            return datetime.now() - self.start

        return self.end - self.start

    def end_checkpoint(self):
        if self.end is None:
            self.end = datetime.now()

    def is_active(self):
        return self.end is None

    def has_ended(self):
        return self.end is not None

    def is_recurrent(self):
        return self._created_by == CheckpointType.recurrent


class Checkpoints(OrderedDict):
    def new_checkpoint(self, *, name, created_by):
        if name not in self:
            self[name] = list()

        if self._is_recurrent_checkpoint(name=name):
            created_by = CheckpointType.recurrent

        checkpoint = Checkpoint(name=name, created_by=created_by)
        self[name].append(checkpoint)

    def _is_recurrent_checkpoint(self, name):
        checkpoints = self.get(name, list())
        recurrent_checkpoints = list()
        for c in reversed(checkpoints):
            if c.has_ended() and not c.is_recurrent():
                break
            recurrent_checkpoints.append(c)

        return len(recurrent_checkpoints) > 0

    def end_checkpoint(self, name):
        checkpoints = self.get(name, list())
        active_checkpoints = [c for c in reversed(checkpoints) if c.is_active() or c.is_recurrent()]
        if len(active_checkpoints) > 0:
            active_checkpoints[0].end_checkpoint()

    def last_active_checkpoint(self, name):
        checkpoints = self.get(name, list())
        active_checkpoints = [c for c in reversed(checkpoints) if c.is_active() or c.is_recurrent()]
        if len(active_checkpoints) > 0:
            return active_checkpoints[0]

    def total_duration(self, name):
        durations = (c.duration() for c in self.get(name, []) if not c.is_recurrent())
        duration = sum(durations, timedelta(0))
        return duration

    def count(self, name):
        count = len(self.get(name, []))
        return count

    def summary(self):
        summary = OrderedDict()
        for name in self.keys():
            summary[name] = dict(first_start_time=self[name][0].start,
                                 total_duration=self.total_duration(name),
                                 count=self.count(name))
        return summary


class CheckpointType(Enum):
    wrapper = 'wrapper'
    method = 'method'
    recurrent = 'recurrent'


timer = Timer()
