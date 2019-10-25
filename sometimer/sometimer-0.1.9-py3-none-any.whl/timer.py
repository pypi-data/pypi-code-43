from datetime import datetime


_first_checkpoint_name = 'start'


class Timer:
    _checkpoints = []
    _name = None
    _output_format = None
    _decimals = None
    _start_checkpoint = None
    _current_checkpoint = None
    _end_checkpoint = None

    @classmethod
    def __new__(cls, *args, name='timer', output_format=str, print_decimals=3, **kwargs):
        if not hasattr(cls, '_timer') or cls._timer is None:
            cls._timer = super(Timer, cls).__new__(cls)

            cls._name = name
            cls._output_format = output_format
            cls._decimals = print_decimals
            cls._start_checkpoint = Checkpoint(name=_first_checkpoint_name)
            cls._current_checkpoint = cls._start_checkpoint
            cls._end_checkpoint = None
            cls._checkpoints.append(cls._start_checkpoint)
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
        if show_checkpoint and cls._has_checkpoint() and cls._current_checkpoint is not None:
            checkpoint_name = f'    {cls._current_checkpoint.name}: ' if cls._current_checkpoint.name else '    '
            checkpoint_time = f'{cls._current_checkpoint.total_duration().total_seconds():{min_length}.{cls._decimals}f}s'
            time_as_string += checkpoint_name + checkpoint_time

        if description is not None:
            time_as_string += '    ' + description

        return time_as_string

    @classmethod
    def _describe_time_as_float(cls):
        return cls.duration().total_seconds()

    @classmethod
    def _time_since_start(cls, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        return timestamp - cls._start_checkpoint.start

    @classmethod
    def _time_since_checkpoint(cls, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        return timestamp - cls._current_checkpoint.start

    @classmethod
    def new_checkpoint(cls, name=None):
        if cls._has_active_checkpoint():
            cls._current_checkpoint.end_checkpoint()

        checkpoint = Checkpoint(name=name)
        cls._current_checkpoint = checkpoint
        cls._checkpoints.append(checkpoint)
        return checkpoint

    @classmethod
    def duration(cls):
        start_time = cls._checkpoints[0].start
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
    def end_checkpoint(cls):
        cls._current_checkpoint.end_checkpoint()
        cls._current_checkpoint = None

    @classmethod
    def _has_checkpoint(cls):
        return len(cls._checkpoints) > 1

    @classmethod
    def _has_active_checkpoint(cls):
        return cls._current_checkpoint is not None

    @classmethod
    def summary(cls):
        max_start_time_length = len(f'{cls.duration().total_seconds():.0f}') + cls._decimals + (cls._decimals > 0)
        longest_checkpoint_name = max((len(c.name) for c in cls._checkpoints))
        longest_duration = max((len(f'{c.total_duration().total_seconds():.0f}') for c in cls._checkpoints)) + cls._decimals + (cls._decimals > 0)

        _summary = f'{cls._name} summary\n'
        _summary += f'{"":{longest_checkpoint_name + 2}}{"-start-":{max_start_time_length}}   {" " if max_start_time_length > (1 + cls._decimals + (cls._decimals > 0)) else ""}-duration-\n'
        for checkpoint in cls._checkpoints:
            name = f'{checkpoint.name + ": " if checkpoint.name is not None else "":{longest_checkpoint_name + 2}}'
            time = f'{cls._time_since_start(timestamp=checkpoint.start).total_seconds():{max_start_time_length}.{cls._decimals}f}s    '
            duration = f'{checkpoint.total_duration().total_seconds():{longest_duration}.{cls._decimals}f}s\n'
            _summary += name + time + duration

        end_name = f'{"end:":{longest_checkpoint_name + 2}}'
        end_duration = f'{cls.duration().total_seconds():{max_start_time_length}.{cls._decimals}f}s\n'
        _summary += end_name + end_duration

        return _summary

    @classmethod
    def restart(cls):
        cls._start_checkpoint = Checkpoint(name=_first_checkpoint_name)
        cls._current_checkpoint = cls._start_checkpoint
        cls._checkpoints = [cls._start_checkpoint]
        return cls._timer


def time_this_method(method=None, name=None):
    def wrapper(method):
        def _time_this_method(*args, **kwargs):
            _name = name or method.__name__
            timer.new_checkpoint(name=_name)
            returned_from_method = method(*args, **kwargs)
            timer.end_checkpoint()
            return returned_from_method
        return _time_this_method

    # decorator call, i.e. `@time_this_method`
    if method is not None:
        return wrapper(method)

    # factory call, i.e.`@time_this_method()`
    return wrapper


class Checkpoint:
    def __init__(self, name=None, start=None):
        self.start = start or datetime.now()
        self.end = None
        self.name = name

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


timer = Timer()
