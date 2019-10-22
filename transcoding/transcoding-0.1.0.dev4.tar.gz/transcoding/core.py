"""
Known Problems:
    * Numbers with trailing floating point but no number behind the point like
        '0. 1. ' can not be produced and thus not be parsed with format patterns.
    * format spec ' .4e', '+.4e' not registered -> # show a space or a + for positive numbers
"""
from transcoding import Trigger, LooseTrigger, time_shift
from transcoding import BasePattern, Pattern, Margin, Conditional, ParseError

from past.builtins import basestring
from six import itervalues
import os
from more_itertools import peekable
import logging
import io
import sys


def is_buffer(path):
    """
    Args:
        path (str or buffer)
    Returns:
        bool
    """
    try:
        # python2
        file_types = (file, io.IOBase)
    except NameError:
        # python3
        file_types = (io.IOBase,)

    # The tarfile.ExFileObject is a buffer, too
    if 'tarfile' in sys.modules.keys():
        import tarfile
        file_types += (tarfile.ExFileObject,)

    # check buffer instance
    if isinstance(path, file_types):
        return True
    
    return False


class Block(object):
    def __init__(self, *patterns, **kwargs):
        """
        Abstract base class for blocks in a file.
        Each file can be fully described by an arbitrary amount of Blocks.

        Args:
            *patterns (tc.BasePattern subclass | str):
                str will be cast to tc.Pattern
            **kwargs
                start (Trigger): defines from where to read/write
                stop (Trigger): defines until where to read/write
                barrier (Trigger): like stop but will also trigger if not yet
                    started
                default (dict): default to return if nothing was read

        Attrs:
            _counter (int): points to currently active pattern / variable
            _patterns (list): patterns to parse / format in read/write mode

        Examples:
        """
        start = kwargs.pop('start', None)
        stop = kwargs.pop('stop', None)
        barrier = kwargs.pop('barrier', None)
        default = kwargs.pop('default', None)

        log = logging.getLogger()
        self.patterns = patterns
        self.start = start
        self.stop = stop
        self.barrier = barrier
        self.default = default
        self._counter = 0
        if len(kwargs) != 0:
            log.error("kwargs {kwargs} were not "
                           "consumed.".format(**locals()))

    def copy(self):
        kwargs = {}
        for attr in dir(self.__class__):
            if isinstance(getattr(self.__class__, attr), property):
                val = getattr(self, attr)
                if hasattr(val, 'copy'):
                    val = val.copy()
                kwargs[attr] = val
        return self.__class__(*kwargs.pop('patterns'),
                              **kwargs)

    @property
    def patterns(self):
        """
        list of str: patterns to parse / format in read/write mode
        """
        return self._patterns

    @patterns.setter
    def patterns(self, patterns):
        log = logging.getLogger()
        if not hasattr(patterns, '__iter__'):
            patterns = [patterns]
        self._patterns = []
        for p in patterns:
            if issubclass(type(p), BasePattern):
                self._patterns.append(p)
            else:
                self._patterns.append(Pattern(p))

    @property
    def start(self):
        """
        transcodings.Trigger: Start trigger
        """
        return self._start
    
    @start.setter
    def start(self, start):
        if start is None:
            start = LooseTrigger(lambda x: True, delay=0)
        else:
            # copy triggers in order to not work on the initial instance.
            start = start.copy()
        self._start = start

    @property
    def stop(self):
        """
        transcodings.Trigger: Stop trigger
        """
        return self._stop

    @stop.setter
    def stop(self, stop):
        if stop is None:
            stop = LooseTrigger(lambda x: True, delay=len(self.patterns))
        else:
            # copy triggers in order to not work on the initial instance.
            stop = stop.copy()
        self._stop = stop

    @property
    def barrier(self):
        """
        transcodings.Trigger: Barrier. If this trigger turns on, finish this
            block.
        """
        return self._barrier

    @barrier.setter
    def barrier(self, barrier):
        if barrier is None:
            barrier = LooseTrigger(lambda x: False, delay=0)
        else:
            barrier = barrier.copy()
        self._barrier = barrier

    @property
    def default(self):
        """
        dict: default values of this block
        """
        return dict(self._default)

    @default.setter
    def default(self, default):
        if default is None:
            default = {}
        self._default = default

    def startswith(self, string):
        """
        Check wether first pattern starts with string
        """
        return self.patterns[0].startswith(string)

    def _expired(self):
        """
        Returns
                False: started but not stopped / not yet started
                True: started and stopped again
        """
        return (self._stop.active() and self._start.active()) or self._barrier.active()

    def _get_line(self, iterator):
        """
        Args:
            iterator (peekable)
        Returns:
            line (None / str): None if the trigger is not met
        """
        log = logging.getLogger()
        next_line = iterator.peek(None)

        # feed triggers
        self._start(next_line)
        self._barrier(next_line)
        if self._barrier.active():
            return None

        if self._start.found():
            # stop will not be checked untill start trigger has been found
            self._stop(next_line)

        if self._stop.active():
            return None

        line = next(iterator)
        if self._start.active():
            return line
        else:
            log.warning("Unprocessed line '{line}'"
                        .format(**locals()))
            return None

    def _get_pattern(self):
        """
        Returns:
            str: the pattern at counter
        """
        pattern = self.patterns[self._counter]
        return pattern

    def reset(self):
        self._start.reset()
        self._stop.reset()
        self._barrier.reset()
        self._counter = 0

    def _write_line(self, values):
        """
        Args:
            values (dict)
        """
        pattern = self._get_pattern()
        line = pattern.write(values)
        return line

    def _write(self, values):
        log = logging.getLogger()
        while not self._expired():
            # create line with format
            line = self._write_line(values)
            self._start(line)
            self._stop(line)
            if line is not None:
                yield line
            self._counter += 1
        if not self._start.active():
            log.error("Block did not trigger before terminating.\n"
                      "\t\t\tpatterns:\t%r" % ([str(p) for p in self.patterns]))

    def write(self, values):
        """
        Args:
            values (dict): content to write. needs to fulfill the pattern
        """
        self.reset()
        with time_shift(-1, self._start, self._stop):
            lines = list(self._write(values))
        return lines

    def _read_line(self, line, **kwargs):
        return self._get_pattern().read(line, **kwargs)

    def _read(self, iterator, **kwargs):
        log = logging.getLogger()
        while not self._expired():
            line = self._get_line(iterator)
            if line is not None:
                val = self._read_line(line, **kwargs)
                if val is not None:
                    yield val
                self._counter += 1
        if not self._start.active():
            log.error("Block did not trigger before terminating.\n"
                      "\t\t\tpatterns:\t%r" % ([str(p) for p in self.patterns]))

    def read(self, iterator, **kwargs):
        """
        Args:
            iterator (peekable): iterator containing strings to process
            **kwargs:
                dependencies: already proecessed parts of iterator
                    This is only necessary if your processing pattern depends on any
                    value that was already processed
        """
        self.reset()
        vals = self.default
        for newVals in self._read(iterator, **kwargs):
            vals.update(newVals)
        return vals


class Table(Block):
    def __init__(self, *args, **kwargs):
        """
        Square form for table in/outputs
        Examples:
            >>> from more_itertools import peekable
            >>> import transcoding as tc
            >>> pattern = " {d} = {x:.4e} {y:.4e}"
            >>> start = tc.Trigger(lambda x: 'RAXIS' in x, delay=0)
            >>> stop = tc.Trigger(lambda x: not bool(x), delay=0)

            >>> inp =  " RAXIS = 5.6102e+00 3.7067e-01\\n"
            >>> inp += " ZAXIS = -0.0000e+00 -2.9784e-01"
            >>> inp = inp.split("\\n")

            reading with the same pattern
            >>> iterator = peekable(inp)

            >>> t = tc.Table(pattern, start=start, stop=stop)
            >>> values = t.read(iterator)
            >>> values['y'] == [0.37067, -0.29784]
            True

            write
            >>> outp = t.write(values)
            >>> assert(all([a == b for a, b in zip(inp, outp)]))

        """
        stop = kwargs.get('stop', None)
        if stop is None:
            raise ValueError("stop is a mandatory attribute for Table.")
        super(Table, self).__init__(*args, **kwargs)

    def _get_pattern(self):
        pattern = self.patterns[0]
        return pattern

    def _write_line(self, values):
        """
        Args:
            values (dict)
        """
        pattern = self._get_pattern()
        any_variable = list(self._get_pattern().get_variables(dependencies=values))[0]
        length = len(values[any_variable])
        if self._counter >= length:
            self._stop.activate()
            line = None
        else:
            line = pattern.write({var: values[var][self._counter]
                                  for var in pattern.get_variables(dependencies=values)})
        return line

    def read(self, iterator, **kwargs):
        self.reset()
        read_dicts = self._read(iterator, **kwargs)
        output = self.default
        merged = merge(read_dicts,
                       self._get_pattern().get_variables(**kwargs))
        output.update(merged)
        return output


def merge(dicts, variables):
    """
    Merge multiple dicts to one dict with lists
    Returns:
        dict: dictionary with keys = variables and values = list of all merged
            dict values
    """
    vals = {attr: [] for attr in variables}
    for d in dicts:
        if d is None or d == {}:
            continue
        for attr in variables:
            vals[attr].append(d[attr])
    return vals


def divide(dictionary, variables):
    """
    Args:
        dictionary (dict): dict of the sheme
            {v1: [...], v2: [...] , ...for v1, v2, ... in <variables>}
        variables (set): subset of keys in <dictionary>
    Returns:
        list of dicts
    """
    if len(variables) == 0:
        return []
    dicts = []
    # pick the first variable entry of the set variables
    for any_variable in variables:
        break
    for i in range(len(dictionary[any_variable])):
        dicts.append({var: dictionary[var][i] for var in variables})
    return dicts


class List(Block):
    def __init__(self, *args, **kwargs):
        """
        First partially parse pre- and suffix, then split the remaining line
        by seperator and read the chunks with pattern afterwards.
        Note:
            No seperator expected between prefix and body as well as body and suffix
            If a seperator should be included in these positions, include it at
            the end of prefix / the beginning of suffix.
        Args:
            seperator (str)
            prefix (None | str | Pattern)
            suffix (None | str | Pattern)
            rigid (bool): Default: True.
                If rigid is set to False, at reading time, two seperators
                following each other will not result in a 'None' entry in the
                list
            **kwargs: passed to Block __init__
        Examples:
            Simplest possible version - e.g. a line of a csv file:
            >>> import transcoding as tc
            >>> from more_itertools import peekable
            >>> b_csv_line = tc.List('{val:d}', separator=',')
            >>> content = {'val': [1, 2, None, 4]}
            >>> csv_line = b_csv_line.write(content)
            >>> csv_line
            ['1,2,,4']
            >>> assert b_csv_line.read(peekable(csv_line)) == content
    
            Including pre and suffix
            >>> l = tc.List('v-{val:.3f}',
            ...             separator=' ',
            ...             prefix='values of {name}: ',
            ...             suffix=' :end')
            >>> res = l.read(peekable(['values of test: v-2.000 v-1.234 :end']))
            >>> sorted(list(res))
            ['name', 'val']
            >>> res['val']
            [2.0, 1.234]
            >>> res['name']
            'test'

        """
        self.separator = kwargs.pop('separator')
        self.prefix = kwargs.pop('prefix', None)
        self.suffix = kwargs.pop('suffix', None)
        self.rigid = kwargs.pop('rigid', True)
        super(List, self).__init__(*args, **kwargs)

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, separator):
        self._separator = separator

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        if prefix is not None:
            if isinstance(prefix, basestring):
                prefix = Pattern(prefix)
        if prefix is not None:
            if issubclass(type(prefix), Pattern):
                prefix = Margin(prefix, left=True)
            if not isinstance(prefix, Margin) and prefix.left:
                raise ValueError("prefix must be Margin with left=True")
        self._prefix = prefix

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, suffix):
        if suffix is not None:
            if isinstance(suffix, basestring):
                suffix = Pattern(suffix)
        if suffix is not None:
            if issubclass(type(suffix), Pattern):
                suffix = Margin(suffix, left=False)
            if not isinstance(suffix, Margin) and not suffix.left:
                raise ValueError("suffix must be Margin with left=False")
        self._suffix = suffix

    @property
    def rigid(self):
        return self._rigid

    @rigid.setter
    def rigid(self, value):
        self._rigid = bool(value)

    def _get_pattern(self):
        pattern = self.patterns[0]
        return pattern

    def _read_line(self, line, **kwargs):
        """
        Examples
            Example from vmec_input file
            >>> import transcoding as tc
            >>> from more_itertools import peekable
            >>> line = ' FTOL_ARRAY = 1.00E-05 1.00E-08 3.70E-10 9.50E-11 3.0E-11'
            >>> l_tolerance = tc.List(
            ...     tc.Pattern("{forceToleranceLevels:.2e}"),
            ...     separator=' ',
            ...     prefix=tc.Margin.alternatives('FTOL_ARRAY = ', ' FTOL_ARRAY = ',
            ...                                   ' Wrong FTOL_ARRAY = '))
            >>> l_tolerance.read(peekable([line]))
            {'forceToleranceLevels': [1e-05, 1e-08, 3.7e-10, 9.5e-11, 3e-11]}

        """
        log = logging.getLogger()
        vals = {}
        if self.prefix is not None:
            pre_vals = self.prefix.read(line, **kwargs)
            if pre_vals is None:
                return None
            line = pre_vals.pop('REST')
            vals.update(pre_vals)
        if self.suffix is not None:
            suf_vals = self.suffix.read(line, **kwargs)
            if suf_vals is None:
                return None
            line = suf_vals.pop('REST')
            vals.update(suf_vals)

        split_line = line.split(self.separator)
        variables = self.patterns[0].get_variables(**kwargs)
        list_vals = []
        for entry in split_line:
            if entry == '':
                if self.rigid:
                    list_vals.append({k: None for k in variables})
            else:
                list_vals.append(super(List, self)._read_line(entry, **kwargs))
        list_vals = merge(list_vals,
                          variables)

        # while '' in split_line:
        #     split_line.remove('')
        #     # log.warning("'' in split_line!")
        # list_vals = merge([super(List, self)._read_line(entry, **kwargs)
        #                    for entry in split_line],
        #                   self.patterns[0].get_variables(**kwargs))
        vals.update(list_vals)
        return vals

    def _write_line(self, values):
        pattern = self._get_pattern()

        line = ''
        # prefix
        if self.prefix is not None:
            line += self.prefix.write(values)
        # mid patterns
        variables = pattern.get_variables(dependencies=values)
        sub_values = divide(values, variables)
        for i, sub_values in enumerate(sub_values):
            if i != 0 or self.prefix is not None:
                line += self.separator
            if not all([v is None for v in itervalues(sub_values)]):
                line += pattern.write(sub_values)
        # suffix
        if self.suffix is not None:
            line += self.separator
            line += self.suffix.write(values) or ''
        return line


class Jump(Block):
    def __init__(self, trigger):
        """
        Jump the iterator to the trigger and immediate stop.
        This will destroy bijectivity of a transcoding,
        ie reading and writing again will produce a
        different file.

        Args:
            trigger (transcodings.Trigger): 
        """
        start = trigger
        stop = trigger
        super(Jump, self).__init__(None, start=start, stop=stop)


class Loop(object):
    """
    Collection of repeating structures
    Args:
        name
        blocks (list of Block instances)
        **kwargs:
            head (Bock instance): header of loop
            foot (Bock instance): footer of loop

    Notes:
        * Reading the loop will only work, if the first block triggers directly
        the first line after the last block has been processed

    Examples:
        >>> from more_itertools import peekable
        >>> import transcoding as tc
        >>> start = tc.Trigger(lambda x: 'RAXIS' in x, delay=0)
        >>> stop = tc.Trigger(lambda x: not bool(x), delay=0)

        >>> inp =  "Start - Name: Looping Lui\\n"
        >>> inp += "Loop 1\\n"
        >>> inp += "Fly high\\n"
        >>> inp += "Fly low\\n"
        >>> inp += "Fly high\\n"
        >>> inp += "Loop 2\\n"
        >>> inp += "Fly low\\n"
        >>> inp += "Fly high\\n"
        >>> inp += "Fly low\\n"
        >>> inp += "Stop - Status: dizzy"
        >>> inp = inp.split("\\n")

        reading with the same pattern
        >>> iterator = peekable(inp)

        >>> l = tc.Loop("looping lui",
        ...             [tc.Block("Loop {loop_no:d}"),
        ...              tc.Table("Fly {fly_value}",
        ...                       stop=tc.Trigger(lambda x: 'Loop' in x or 'Stop' in x))
        ...             ],
        ...             head=tc.Block("Start - Name: {loop_name}"),
        ...             foot=tc.Block("Stop - Status: {loop_status}",
        ...                           start=tc.Trigger(lambda x: 'Stop' in x)))

        >>> values = l.read(iterator)
        >>> values['looping lui'][1]['fly_value']
        ['low', 'high', 'low']
        >>> values['loop_status']
        'dizzy'

        writing creates the exact same output as input
        >>> outp = l.write(values)
        >>> assert(all([a == b for a, b in zip(inp, outp)]))

    """
    def __init__(self, name, blocks, **kwargs):
        self._name = name
        if not blocks:
            raise ValueError("Trivial Loop without Blocks.")
        self.blocks = blocks
        self.stop_iter = kwargs.pop('stop_iter', None)
        self.head = kwargs.pop('head', None)
        self.foot = kwargs.pop('foot', None)

    @property
    def name(self):
        return self._name

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        self._blocks = [b.copy() for b in blocks]

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, head):
        if head is not None:
            head = head.copy()
        self._head = head

    @property
    def foot(self):
        return self._foot

    @foot.setter
    def foot(self, foot):
        if foot is not None:
            foot = foot.copy()
            if not issubclass(type(foot._start), LooseTrigger):
                if self.stop_iter is None:
                    self.stop_iter = foot._start
        self._foot = foot
    
    @property
    def stop_iter(self):
        """
        (Trigger): if stop_iter triggers, this is the signal for the loop to
            terminate
        """
        return self._stop_iter

    @stop_iter.setter
    def stop_iter(self, stop_iter):
        if stop_iter is not None:
            stop_iter = stop_iter.copy()
            stop_iter.reset()
        self._stop_iter = stop_iter

    def _get_first_block(self):
        """
        Returns:
            first occuring block
        """
        if self.head:
            block = self.head
        else:
            block = self.blocks[0]
        return block

    def __getattr__(self, attr):
        if attr == 'startswith':
            return self._get_first_block().startswith
        else:
            raise AttributeError("'{cls}' object has no attribute '{attr}'"
                                 .format(attr=attr, cls=type(self).__name__))

    def _read_body(self, iterator, **kwargs):
        dependencies = kwargs.get('dependencies', {})
        body = []
        start_iter = self.blocks[0]._start.copy()
        if self.stop_iter is None:
            raise ValueError("Please define the end of iteration with the "
                             "stop_iter attribute")
        while True:
            next_line = iterator.peek(None)

            # feed triggers
            start_iter(next_line)
            self.stop_iter(next_line)
            if self.stop_iter.active():
                break
            if start_iter.pending():
                next(iterator)
                continue

            # read blocks
            loop_iteration_dict = {}
            for block in self.blocks:
                loop_iteration_dict.update(block.read(iterator, **kwargs))
                if self.name not in dependencies:
                    dependencies[self.name] = [loop_iteration_dict]
                else:
                    dependencies[self.name].append(loop_iteration_dict)
            body.append(loop_iteration_dict)

            start_iter.reset()
                
        body_dict = {self.name: body}
        return body_dict

    def read(self, iterator, **kwargs):
        """
        Read in order head, body, foot
        """
        out_dict = dict()
        if self.head is not None:
            out_dict.update(self.head.read(iterator, **kwargs))

        body_dict = self._read_body(iterator, **kwargs)

        out_dict.update(body_dict)
        if self.foot is not None:
            out_dict.update(self.foot.read(iterator, **kwargs))
        return out_dict

    def write(self, values):
        """
        Write in order head, body, foot
        """
        lines = []
        if self.head:
            lines.extend(self.head.write(values))
        for loop_values in values[self.name]:
            for block in self.blocks:
                lines.extend(block.write(loop_values))
        if self.foot:
            lines.extend(self.foot.write(values))
        return list(lines)


class Transcoding(object):
    """
    Abstract Class that handles transcodings.
    Transcodings are ordered blocks that describe a whole file format.
    See ./transcodings/*.py as examples.

    Examples:
        >>> import transcoding as tc
        >>> lines = ['test', ' AC = 0.00 0.10 0.20', ' asdf']

        >>> b_current_profile = tc.List(
        ...     '{currentProfileCoefficients:.2f}',
        ...     separator=' ',
        ...     prefix=tc.Margin.alternatives('AC = ', ' AC = ', 'AC_AUX_F = '),
        ...     start=tc.Trigger(lambda x: 'AC' in x),
        ...     default={'currentProfileCoefficients': []})
        >>> trans = tc.Transcoding(b_current_profile)
        >>> trans.read(lines)
        {'currentProfileCoefficients': [0.0, 0.1, 0.2]}

    """
    def __init__(self, *blocks, **kwargs):
        self._blocks = blocks

    @property
    def blocks(self):
        return self._blocks

    def read(self, inp):
        """
        inp will be file object or iterable
        """
        log = logging.getLogger()
        if isinstance(inp, basestring):
            path = os.path.realpath(os.path.abspath(os.path.expanduser(inp)))
            with open(path, 'rb') as f:
                return self.read(f)
        if is_buffer(inp):
            inp = inp.read().decode()
            inp = inp.split('\n')
            if inp[-1] == '':
                inp = inp[:-1]
        if isinstance(inp, list):
            iterator = peekable(inp)
        else:
            raise ValueError("Input must either be str, buffer or list but is"
                             " {tpe}".format(tpe=type(inp)))
        content_dict = dict()
        for i, block in enumerate(self.blocks):
            try:
                block_content = block.read(iterator, dependencies=content_dict)
                content_dict.update(block_content)
            except Exception as err:
                log.exception("Error in block {i}:\n".format(**locals()) +
                              str(err))
                raise err
        while True:
            try:
                line = next(iterator)
            except StopIteration:
                break
            log.warning("Unprocessed line '{line}'"
                        .format(**locals()))
        return content_dict


def importTranscoding(filePath):
    import importlib
    if os.path.exists(filePath):
        transMod = importlib.load_source(os.path.basename(filePath).rstrip('.py'), filePath)
    else:
        predefined = "transcodings.{extension}".format(extension=filePath)
        filePath = predefined
        transMod = __import__(filePath, fromlist=[''])
    return transMod


def get_transcoding(filePath):
    transMod = importTranscoding(filePath)
    return transMod.transcoding


if __name__ == '__main__':
    # import transcoding as tc
    # from more_itertools import peekable
    # l = tc.List('v-{val:.3f}',
    #             separator=' ',
    #             prefix='values of {name}:',
    #             suffix=':end')
    # res = l.read(peekable(['values of test: v-2.000 v-1.234 :end']))
    # res['val']
    # quit()

    # import loggingTools as lt
    # lt.setLevel(0)
    import doctest
    doctest.testmod()
