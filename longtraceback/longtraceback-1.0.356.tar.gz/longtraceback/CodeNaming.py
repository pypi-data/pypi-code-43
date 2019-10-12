#!/usr/bin/env python
"""
Resolve the code elements within a module.

Expected usage::

    code_elements = CodeElements('mymodule.name')
    code_element = code_elements.resolve(some_code_object)
    print "Element: %s  [%s]" % (code_element, code_element.codetype)
    print "Lines: %s - %w" % (code_element.line_low, code_element.line_high)
"""

import inspect
import sys
import types


code_line_bounds_cached = {}


def code_line_bounds(code):
    """
    Given a co_code, return the low and high bounds of the lines
    that the code covers.
    """
    if not isinstance(code, types.CodeType):
        return (None, None)

    code_key = (hash(code), code.co_filename, code.co_firstlineno)
    if code_key in code_line_bounds_cached:
        return code_line_bounds_cached[code_key]

    firstlineno = code.co_firstlineno

    # The line number table consists of octet pairs:
    #  (bytecode offset, line offset)
    # So the last line of a function would be around sum of those
    # line offsets.
    if code.co_lnotab:
        try:
            line_limit = sum(ord(byte) for byte in code.co_lnotab[1::2])
        except TypeError:
            # In Python 3 the lnotab contains ints, not bytes.
            line_limit = sum(code.co_lnotab[1::2])

        line_range = (firstlineno, firstlineno + line_limit)
    else:
        # In synthesised tracebacks there will not be a line number table,
        # so we want to return a block that is 'the entire file', in order
        # to allow us to display some context
        line_range = (firstlineno, None)

    code_line_bounds_cached[code_key] = line_range

    return line_range


def get_class_that_defined_method(method):
    """
    Return the class which defined the method supplied.

    The class which defined the method may differ from the class that it is being
    applied on. For example, if inherited, we may find that the method called is
    one of the lower implementations.

    @param method:  The method we are looking for, as a method function object

    @return: The class in the hierarchy in which it was defined, or None if not found
    """
    name = method.__name__
    # __self__ only exists on bound methods
    cls_to_inspect = getattr(method, '__self__', None)
    if cls_to_inspect is None:
        cls_to_inspect = getattr(method, 'im_class', None)

    # __bases__ is only present on classes, not on objects, so get the base class
    if not getattr(cls_to_inspect, '__bases__', None):
        # Old style classes won't have '__bases__'
        if getattr(cls_to_inspect, '__class__', None):
            cls_to_inspect = cls_to_inspect.__class__

    if cls_to_inspect:
        method_code = getattr(method, '__code__', None)
        try:
            for cls in inspect.getmro(cls_to_inspect):
                if name in cls.__dict__:
                    clsmethod = cls.__dict__[name]
                    if getattr(clsmethod, '__func__', None):
                        # Class methods have an __func__ that references the method
                        if getattr(clsmethod.__func__, '__code__', None) == method_code:
                            return cls
                        return cls
                    if getattr(clsmethod, '__code__', None) == method_code:
                        return cls
        except Exception as exc:
            #print("Exception processing %r: %s" % (method, exc))
            raise
            # And return None to keep things happy.

    return None


def get_class_that_defined_function(cls, func):
    """
    Return the class which defined the function supplied (which differs from method)

    The class which defined the function may differ from the class that it is being
    applied on, which is a different issue to the above, as there are no 'methods' on
    class declarations in Python 3.

    @param func:  The method we are looking for, as a method function object

    @return: The class in the hierarchy in which it was defined, or None if not found
    """
    if func is None:
        return None

    if cls is None:
        return None

    if not getattr(cls, '__bases__', None):
        # Either it's not a class, or it is a class that contains nothing.
        # In both cases, there cannot be a containing class
        return None

    name = func.__name__
    cls_to_inspect = cls

    func_code = getattr(func, '__code__', None)
    for cls in inspect.getmro(cls_to_inspect):
        if name in cls.__dict__:
            clsmethod = cls.__dict__[name]
            if getattr(clsmethod, '__code__', None) == func_code:
                return cls

    return None


class CodeElement(object):
    """
    Describes a block of code.

    @var name:          Name of the code, as presentable to user
    @var codetype:      Capitalised name of the type of code referenced
    @var name_self:     Name of the code, as it calls itself
    @var name_parts:    List of the names of the parts leading to this code
    @var line_low:      Low line for the code block (or None if not understood)
    @var line_high:     High line for the code block (or None if no end recognised)
    @var contains:      A list of the other code elements that exist within this one
    """
    element_indexes = {
        0: 'name',
        1: 'codetype',
    }

    def __init__(self, code, parts=None, name=None, codetype='INNERFUNC'):
        co_name = getattr(code, 'co_name', '<not code: %s>' % (code,))
        if name is None:
            name = co_name

        if not isinstance(code, types.CodeType):
            codetype = 'NOTCODE'

        parts = parts or []
        lines = code_line_bounds(code)

        if name[0] == '<' and name[-1] == '>' and lines[0] is not None:
            if name == '<genexpr>':
                name = '<genexpr at line %s>' % (lines[0],)
            if name == '<lambda>':
                name = '<lambda at line %s>' % (lines[0],)

        self.code = code
        self.codetype = codetype
        self.name_self = co_name
        if name == '<module>':
            self.name_parts = parts
        else:
            self.name_parts = parts + [name]
        self.name = ".".join(self.name_parts)
        self.line_low = lines[0]
        self.line_high = lines[1]
        self.contains = []

    def __str__(self):
        return self.name

    def __iadd__(self, other):
        if not isinstance(other, CodeElement):
            raise ValueError("Can only add CodeElements to CodeElements")
        self.contains.append(other)
        return self

    def __getitem__(self, index):
        attr = CodeElement.element_indexes.get(index, None)
        if attr is None:
            raise IndexError("Index %s is not value for CodeElement" % (index,))
        return getattr(self, attr)


class CodeElements(object):
    _initialised = False
    _cache = {}

    def __new__(cls, module_name):
        cached = CodeElements._cache.get(module_name, None)
        if cached:
            if cached[0] == id(sys.modules.get(module_name, None)):
                return cached[1]

        try:
            # Python < 3.3
            return super(CodeElements, cls).__new__(cls, module_name)
        except TypeError:
            # Python >= 3.3
            return super(CodeElements, cls).__new__(cls)

    def __init__(self, module_name):
        if not self._initialised:
            self.module_name = module_name
            self.module = sys.modules.get(module_name, None)
            if self.module:
                self.file_name = getattr(self.module, '__file__', '<unknown>')
            else:
                self.file_name = None
            self.code_naming = {}
            if self.module:
                self._fetch_names()
            self._initialised = True
            self._cache[module_name] = (id(self.module), self)

    def __str__(self):
        return "<%s(module_name=%r, %i code object(s))>" % (self.__class__.__name__,
                                                            self.module_name,
                                                            len(self.code_naming))

    def _add_codeblocks(self, code, parts, name=None, codetype='INNERFUNC'):
        """
        Remember any functions that we can find referenced within the
        code blocks.
        """

        if code not in self.code_naming:
            co_name = getattr(code, 'co_name', '<not code: %s>' % (code,))
            if co_name == '<lambda>':
                codetype = 'LAMBDA'
            elif co_name == '<genexpr>':
                codetype = 'GENERATOR'
            co_flags = getattr(code, 'co_flags', 0)
            if co_flags & 0x20:
                codetype = 'GENERATOR'

            code_element = CodeElement(code, parts, name, codetype)
            self.code_naming[code] = code_element

            for const in code.co_consts:
                if isinstance(const, types.CodeType):
                    codetype = 'INNERFUNC'

                    sub_element = self._add_codeblocks(const, code_element.name_parts, codetype=codetype)
                    code_element += sub_element

        return self.code_naming[code]

    def _fetch_names(self):
        # Check for functions
        symbols = inspect.getmembers(self.module, inspect.isfunction)
        for symbol_name, symbol_info in symbols:
            if hasattr(symbol_info, '__code__'):
                # Regular functions
                self._add_codeblocks(symbol_info.__code__, [self.module_name], name=symbol_name, codetype='FUNCTION')

        # Check module's classes.
        symbols = inspect.getmembers(self.module, inspect.isclass)
        for class_name, class_info in symbols:

            # Check class' methods.
            members = inspect.getmembers(class_info, inspect.ismethod)
            for method_name, method_info in members:
                if hasattr(method_info.__func__, '__code__'):
                    # Find the class that defined this method, so that we're not saying that the function is in
                    # one class when actually it's defined elsewhere due to inheritance.
                    method_class = get_class_that_defined_method(method_info)
                    if method_class is class_info:
                        self._add_codeblocks(method_info.__func__.__code__,
                                             [self.module_name, class_name], name=method_name, codetype='METHOD')
                    else:
                        # Method <class_info>.<method_info> is inherited from <method_class>
                        # (and if <method_class> was defined in this module, it will have been declared
                        # already).
                        pass

            # Check class' functions.
            funcs = inspect.getmembers(class_info, inspect.isfunction)
            for func_name, func_info in funcs:
                method_class = get_class_that_defined_function(class_info, func_info)
                if method_class is class_info:
                    self._add_codeblocks(func_info.__code__,
                                         [self.module_name, method_class.__name__], name=func_name, codetype='FUNCTION')
                elif method_class is None:
                    self._add_codeblocks(func_info.__code__,
                                         [self.module_name, class_name], name=func_name, codetype='FUNCTION')

            properties = inspect.getmembers(class_info, inspect.isdatadescriptor)
            for prop_name, prop_info in properties:
                if hasattr(prop_info, 'fget') and hasattr(prop_info.fget, '__code__'):
                    self._add_codeblocks(prop_info.fget.__code__,
                                         [self.module_name, class_name], name=prop_name, codetype='GETTER')

                if hasattr(prop_info, 'fset') and hasattr(prop_info.fset, '__code__'):
                    self._add_codeblocks(prop_info.fset.__code__,
                                         [self.module_name, class_name], name=prop_name, codetype='SETTER')

                if hasattr(prop_info, 'fdel') and hasattr(prop_info.fdel, '__code__'):
                    self._add_codeblocks(prop_info.fdel.__code__,
                                         [self.module_name, class_name], name=prop_name, codetype='DELETER')

    def dump(self):
        lines = []
        lines.append("Code elements in '%s' ('%s')" % (self.module_name, self.file_name))
        lines.append("")
        for code, element in self.code_naming.items():
            lines.append("  %s  [%s-%s]" % (code, element.line_low, element.line_high))
            lines.append("    Name: %s" % (element,))
            lines.append("    Type: %s" % (element.codetype,))

            if element.contains:
                lines.append("    Contains:")
                for sub_element in element.contains:
                    lines.append("      %s" % (sub_element,))
            lines.append("")

        return "".join("%s\n" % line for line in lines)

    def resolve(self, code):
        """
        Resolve the scope name for a code object provided its module name.

        @return: CodeElement, which strs to the name of the function, as qualified as possible.
                 Type of function ('UNKNOWN', 'FUNCTION', 'METHOD', 'GETTER', 'SETTER', 'DELETER', 'INNERFUNC',
                 'GENERATOR', 'LAMBDA', 'MODULE')
        """

        code_element = self.code_naming.get(code, None)
        if not self.module or not code_element:
            mod = self.module_name or 'unknown module'
            if self.module:
                if getattr(code, 'co_name', '') == '<module>':
                    code_element = CodeElement(code, parts=[mod],
                                               codetype='MODULE')
            if not code_element:
                code_element = CodeElement(code, parts=["(%s)" % (mod,)],
                                           codetype='UNKNOWN')

        return code_element
