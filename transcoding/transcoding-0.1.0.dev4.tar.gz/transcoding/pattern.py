import logging
import parse
from past.builtins import basestring


class ParseError(Exception):
    pass


class read_method(object):
    def __init__(self, method, *args, **kwargs):
        """
        Args:
            method (callable | class with 'read' method):
                arguments of method are:
                    line (str)
                    *args: arbitrary
                    **kwargs: arbitrary
            *args: passed to method
            **kwargs: passed to method
        """
        self._pattern = None
        self.method = method
        self._args = args
        self._kwargs = kwargs
    
    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        self._pattern = pattern

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        if hasattr(method, 'read') and callable(method.read):
            self.pattern = method
            method = None
        self._method = method

    def __call__(self, line, **runtime_kwargs):
        if self.pattern is not None:
            res = self._pattern.read(line, **runtime_kwargs)
        else:
            try:
                res = self.method(line, *self._args, **self._kwargs)
            except ParseError as err:
                log = logging.getLogger()
                log.error(str(err))
        return res


class BaseReader(object):
    def __init__(self, read_method=None):
        self.read_method = read_method

    @property
    def read_method(self):
        """
        (tc.read_method | None): method to shortcut the parsing.
            Must input string and optional dependencies
            Must output a dictionary with keys = self.values
        """
        return self._read_method

    @read_method.setter
    def read_method(self, method):
        if method is not None:
            method = read_method(method)
        self._read_method = method

    def _read_pattern(self, line, **kwargs):
        raise NotImplementedError("BaseReader subclass must implement "
                                  "_read_pattern")

    def read(self, line, **kwargs):
        """
        Args:
            line (str): line of e.g. an input file to read
            **kwargs: passed to _read_pattern | _read_method
        Examples:
        """
        vals = None
        if self.read_method is None or self.read_method.pattern is not None:
            vals = self._read_pattern(line, **kwargs)
        if self.read_method is not None:
            if vals is None:
                vals = self.read_method(line, **kwargs)
        log = logging.getLogger()
        log.debug("Parsing:\n"
                  "\t\t\tline:\t\t\t%r\n"
                  "\t\t\twith format string:\t%r\n"
                  "\t\t\tyielded:\t\t%r" % (line, self._format_string, vals))
        return vals


class BaseWriter(object):
    def write(self, content):
        """
        Args:
            content (dict): keys refer to parse variables.
        """
        raise NotImplementedError("BaseWriter subclass should implement 'write'")


class BasePattern(BaseReader, BaseWriter):
    pass


class Pattern(BasePattern):
    def __init__(self, format_string, read_method=None):
        """
        String subclass dedicated to explicitly storing format strings
        Args:
            format_string (str): format_spec string
                Use variables only with explicit variable names ie.
                    'the value is {val:.2f} m'.
                Do not use implicit references ie.
                    'the value is {0}'.
            read_method (callable | pattern | None):
        Examples:
            >>> import transcoding as tc
            >>> p = tc.Pattern('Input = {inp:.4f}, Output = {outp:.4f}')
            >>> p.format(inp=42, outp=21)
            'Input = 42.0000, Output = 21.0000'

            For reading, you can define an alternative, which will be run, when
            things fail:
            >>> p = tc.Pattern('value = {val:.3f}',
            ...                read_method=tc.Pattern('val = {val:.3f}'))
            >>> p.read('val = 42.000')
            {'val': 42.0}

        """
        super(Pattern, self).__init__(read_method=read_method)
        self._format_string = format_string
        self._parser = None

    def __getattr__(self, attr):
        return getattr(self._format_string, attr)

    def __str__(self):
        return str(self._format_string)

    def _set_parser(self):
        try:
            parser = parse.Parser(self._format_string)
            self._parser = parser
        except Exception as err:
            log = logging.getLogger()
            log.error("Could not set parser with format_string"
                      " '{self._format_string}'".format(**locals()))
            raise err


    @property
    def parser(self):
        if self._parser is None:
            self._set_parser()
        return self._parser

    @property
    def variables(self):
        """
        (list of str): the variables of the format string
        """
        return set(self.parser._named_fields)

    def parse(self, string):
        """
        inverse method of format
        evaluate a full string
        Args:
            string (basestring): main pattern and alternatives

        """
        log = logging.getLogger()
        
        result = self.parser.parse(string)
        if result is None:
            vals = None
            message = ("Could not parse:\n"
                       "\t\t\tline:\t\t\t%r\n"
                       "\t\t\twith format string:\t%r" % (string,
                                                          self._format_string))
            log.error(message)
        else:
            vals = result.named
        return vals

    def get_variables(self, **kwargs):
        return set(self.parser._named_fields)

    def _read_pattern(self, line, **kwargs):
        return self.parse(line)

    def write(self, content):
        return self.format(**content)


class Conditional(Pattern):
    """
    Examples:
        >>> import transcoding as tc
        >>> pattern = tc.Conditional(('number', 'variables', -1),
        ...                          (1, 2),
        ...                          ('entry_{v0}', 'entry_{v0}_entry_{v1}'))
        >>> sorted(pattern.variables)
        ['v0', 'v1']

        >>> line = 'entry_42_entry_21'
        >>> content = {'number': {'variables': [1, 2]}}
        >>> values = pattern.read(line, dependencies=content)
        >>> values['v1'] == '21'
        True
        >>> content.update(values)
        >>> pattern.write(content) == line
        True

    """
    def __init__(self, keys, values, patterns, read_method=None):
        self._patterns = [Pattern(p) for p in patterns]
        self._keys = keys
        self._values = values
        super(Conditional, self).__init__(None, read_method)

    @property
    def variables(self):
        variables = set([])
        for pattern in self._patterns:
            variables = variables.union(pattern.variables)
        return variables

    def get_pattern(self, dependencies):
        dependency_value = dependencies
        for key in self._keys:
            dependency_value = dependency_value[key]

        for value, pattern in zip(self._values, self._patterns):
            if value == dependency_value:
                break
        return pattern

    def get_variables(self, dependencies=None):
        return self.get_pattern(dependencies).get_variables()
        
    def _read_pattern(self, line, dependencies=None, **kwargs):
        return self.get_pattern(dependencies).read(line, **kwargs)

    def write(self, content):
        pattern = self.get_pattern(content)
        return pattern.format(**content)


class Margin(BasePattern):
    def __init__(self, pattern, left=True, read_method=None):
        """
        Margins are needed in order to only process parts of an input.
        It is similar to Patterns but:
        Note:
            * Specialty is, that read will return an extra key 'REST'
        """
        super(Margin, self).__init__(read_method=read_method)
        self._left = left
        self.pattern = pattern

    def __getattr__(self, attr):
        return getattr(self._pattern, attr)

    def __str__(self):
        return str(self._pattern)

    @classmethod
    def alternatives(cls, *format_strings, **kwargs):
        """
        Examples:
            >>> import transcoding as tc
            >>> m = tc.Margin.alternatives(' val {val:d}',
            ...                            'val {val:d}',
            ...                            ' VAL{val:d}',
            ...                            ' never occuring {vald:d}')
            >>> m.read(' val 111 rest is boring')['val']
            111
            >>> res = m.read(' VAL222 rest is boring')

            Margin 'read' method returns an additional key 'REST'
            >>> res.pop('REST')
            ' rest is boring'
            >>> res
            {'val': 222}

        """
        if 'read_method' in kwargs:
            raise ValueError("read_method argument and alternatives constructor "
                             "are mutially exclusive")
        patterns = [Pattern(fs) for fs in format_strings]
        objs = [cls(pattern) for pattern in patterns]
        tmp_obj = objs[0]
        for sub_obj in objs[1:]:
            tmp_obj.read_method = sub_obj
            tmp_obj = sub_obj
        obj = objs[0]
        return obj

    @property
    def left(self):
        return self._left

    @property
    def pattern(self):
        """
        (transcoding.Pattern)
        """
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        if isinstance(pattern, basestring):
            pattern = Pattern(pattern)
        self._pattern = pattern

    def _read_pattern(self, line, **kwargs):
        """
        evaluate pre- or suffix
        """
        log_message = None
        if len(self.variables) == 0:
            if self.left and line.startswith(str(self)):
                rest = line.lstrip(str(self))
            elif not self.left and line.endswith(str(self)):
                rest = line.rstrip(str(self))
            else:
                return None
            vals = {'REST': rest}
        if len(self.variables) != 0 or log_message is not None:
            if self.left:
                format_string = str(self.pattern) + '{REST}'
            else:
                format_string = '{REST}' + str(self.pattern)
            tmp_pattern = Pattern(format_string)
            vals = tmp_pattern.read(line, **kwargs)
        return vals

    def write(self, content):
        return self.format(**content)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
