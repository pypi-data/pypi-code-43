import sys
from copy import copy

__version__ = "0.3.0"
__all__ = (
    "OptionError",
    "ArgsError",
    "MissingOption",
    "Opt",
    "Argv",
    "argv",
    "take_debug",
    "take_verbose",
    "print_if",
)


class OptionError(Exception):
    """Superclass of ArgsError and MissingOption"""

    pass


class ArgsError(OptionError):
    """Too few arguments provided to an option"""

    pass


class MissingOption(OptionError):
    """Expecting an option, but unable to find it"""

    pass


def dashed(text: str) -> str:
    """Add leading dashes to the text dependent on the length of the input

    Args:
        text: The text to add dashes to

    Returns:
        `text`, stripped and with leading dashes. If `text` is less than 2
        characters after being stripped of leading and trailing whitespace,
        it will have a single leading dash, otherwise will have 2 leading
        dashes.
    """
    string = str(text).strip()
    if not string:
        return ""
    dashes = "--" if len(string) > 1 else "-"
    return "{}{}".format(dashes, text)


def kebabcase(text: str) -> str:
    """Replace whitespace with a single `-`

    Args:
        text: String to kebab

    Returns:
        The kebab'd string
    """
    return "-".join(str(text).strip().split())


def skewer(text: str) -> str:
    """Convert a given string to --skewered-kebab-case / -s

    Args:
        text: A string of any length

    Returns:
        A string with whitespace replaced by a single '-', and leading hyphens
        depending on the length of the input after whitespace replacement.
        If the string is 1 character long, it will have a leading '-',
        otherwise it will be lead by '--'.

    Example:
        `skewer` is used for automatically converting text to an option-like
        format.

        >>> print(skewer('my  text'))
        --my-text
        >>> print(skewer('m'))
        -m
    """
    return dashed(kebabcase(text))


def greedy(value) -> bool:
    """Return a boolean representing whether a given value is "greedy"

    Args:
        value: Anything

    Returns:
        True if the value is greedy, False if not.
    """
    return value in GREEDY_VALUES


def take(start: int, n: int, lst: list) -> list:
    """Return `offset` values from the start index, removing from the list

    Args:
        start: The starting index
        n: The number of values to take from the list
        lst: The list to take from (will be mutated)

    Returns:
        The list of items from `start` to `start+n`. No validation will be
        performed to ensure the returned list has the correct number of items.
    """
    end = start + n
    out = lst[start:end]
    del lst[start:end]
    return out


GREEDY_VALUES = frozenset([..., any, greedy, "*"])


class Opt:
    """Define an option to take it from a list of arguments"""

    def __init__(self, *names):
        if names:
            self.names = set(map(skewer, names))
        else:
            self.names = set()
        self.arg_amt = 0
        self.converter = None

    def __iter__(self):
        return iter(self.names)

    def __copy__(self):
        new = self.__class__()
        new.names = copy(self.names)
        new.arg_amt = self.arg_amt
        new.converter = self.converter
        return new

    def __str__(self):
        if not self.names:
            return ""

        names = "|".join(self.names)

        if greedy(self.arg_amt):
            vals = "[value]..."
        elif self.arg_amt > 0:
            vals = " ".join(["<value>"] * self.arg_amt)
        else:
            return names

        return "{} {}".format(names, vals)

    def __repr__(self):
        qname = self.__class__.__qualname__
        mapped = map(lambda x: repr(x.replace("-", " ").strip()), self)
        names = ", ".join(mapped)
        return "<{}({}).takes({})>".format(qname, names, self.arg_amt)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.names == other.names and self.arg_amt == other.arg_amt
        else:
            return NotImplemented

    def takes(self, n, converter=None):
        """Set the number of arguments the instance takes

        Args:
            n: Number of arguments the option should take (must be a positive
                integer)
            converter (callable, optional): A callable used to convert values
                from `Opt.take_args` before returning the result.

        Returns:
            The current instance, which allows chaining to another method.
        """
        if isinstance(n, int) and n < 0:
            msg = "The number of arguments ({}) must be positive"
            raise ArgsError(msg.format(n))

        self.arg_amt = n
        self.converter = converter
        return self

    def new_takes(self, n, converter=None):
        """Copy the instance and set the number of arguments it takes

        Args:
            n: Number of arguments the option should take (must be a positive
                integer)
            converter (callable, optional): A callable used to convert values
                from `Opt.take_args` before returning the result.

        Returns:
            The current instance, which allows chaining to another method.
        """
        return copy(self).takes(n, converter)

    def find_in(self, args: list):
        """Search `args` for this option and return an index if it's found

        Returns:
            int, optional: The index of the first occurrence of this
                option, if found. If the option is not found, return None.
        """
        for name in self:
            try:
                return args.index(name)
            except ValueError:
                continue
        return None

    def take_flag(self, args: list) -> bool:
        """Search args for the option, if it's found return True and remove it

        Args:
            args: A list to search for the option. The first occurrence of the
                option will be removed from the list if it is found, otherwise
                no mutation will occur.

        Returns:
            True if the option was found in `args`.
        """
        idx = self.find_in(args)
        if idx is not None:
            args.pop(idx)
            return True
        else:
            return False

    def take_args(self, args: list, default=None, raises: bool = False):
        """Search `args`, remove it if found and return this option's value(s)

        Args:
            args: The list of arguments to mutate
            default: If provided, this value will be returned when the option
                is not found in `args`.
            raises: Boolean indicating whether to raise instead of returning
                the default value. Takes priority over specifying `default`.

        Returns:
            If `default` is None,

        Raises:
            ArgsError: Too few arguments were provided
            MissingOption: If `raises` is True, don't return the default
        """
        amt = self.arg_amt

        # Taking less than 1 argument will do nothing, better to use take_flag
        if amt == 0:
            msg = "{} takes {} arguments - did you mean to use `take_flag`?"
            raise ArgsError(msg.format(self, amt))

        # Is this option in the list?
        index = self.find_in(args)

        # Option not found in args, skip the remaining logic and return the
        # default value. No list mutation will occur
        if index is None:
            if raises:
                msg = "{} was not found in {}"
                raise MissingOption(msg.format(self, args))

            # if default is None, handle it specially, else return the default
            if greedy(amt):
                return [] if default is None else default
            elif default is None and amt != 1:
                return [None] * amt
            else:
                return default

        # The `take` call needs a start index, offset, and list
        if greedy(amt):
            # Number of indices after the starting index
            offset = len(args) - index
        else:
            # Start index is the option name
            offset = amt + 1

            # Don't mutate the list if there are too few arguments
            end_idx = index + offset
            if end_idx > len(args):
                # Highest index (length - 1) minus this option's index
                n_found = len(args) - 1 - index
                plural = "" if amt == 1 else "s"
                found = ", ".join(map(repr, args[index + 1:end_idx]))
                msg = "expected {} argument{} for '{}', found {} ({})"
                formatted = msg.format(amt, plural, self, n_found, found)
                raise ArgsError(formatted)

        # The list mutation happens here. If anything goes wrong, this is
        # probably why.
        taken = take(index, offset, args)[1:]

        if amt == 1:
            # Single value if amt is 1
            if callable(self.converter):
                return self.converter(taken[0])
            return taken[0]
        elif greedy(amt) or amt > 1:  # Short circuit if greedy
            # List of values (`taken` will always be a list)
            if callable(self.converter):
                return [self.converter(x) for x in taken]
            return taken
        else:
            # amt is (somehow) invalid
            # maybe it was manually set to a negative value?
            msg = "{!r} was found, but {!r} arguments could not be retreived."
            raise ArgsError(msg.format(self, amt))

    @staticmethod
    def is_short(text: str) -> bool:
        """Naively determine whether `text` is a short option (eg. '-a')

        Args:
            text: Check whether this string is a short option

        Returns:
            True if `text` is a short option, otherwise False
        """
        try:
            return text.startswith("-") and text[1] != "-" and len(text) == 2
        except IndexError:
            return False

    @staticmethod
    def is_long(text: str) -> bool:
        """Naively determine whether `text` is a long option (eg. '--long')

        Args:
            text: Check whether this string is a long option

        Returns:
            True if `text` is a long option, otherwise False
        """
        try:
            return text.startswith("--") and text[2] != "-" and len(text) > 3
        except IndexError:
            return False


class _ListSubclass(list):
    """Subclassable `list` wrapper

    Implements __getitem__ and __add__ in a subclass-neutral way.
    """

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            try:
                return self.__class__(result)
            except TypeError:
                pass
        return result

    def __add__(self, rhs):
        return self.__class__(list.__add__(self, rhs))


class Argv(_ListSubclass):
    """Extensible subclass of `list` with functionality for option parsing"""

    def opts(self) -> tuple:
        """Yield index/option tuples

        Yields:
            tuple of int, str: If the list item is deemed to be an option, it
                and its index will be returned in a tuple.
        """
        for index, item in enumerate(self):
            if Opt.is_long(item):
                yield index, item
            elif Opt.is_short(item):
                yield index, item

    @classmethod
    def from_argv(cls):
        """Return a copy of sys.argv as an instance of `Argv`"""
        return cls(copy(sys.argv))


# Lethargy provides its own argv so you don't have to also import sys. The
# additional functionality provided by its type lets you more easily create a
# custom solution.
argv = Argv.from_argv()


# The following functions are such a frequent usage of this library that it's
# reasonable to provide them automatically, and remove even more boilerplate.

take_debug = Opt("debug").take_flag
take_verbose = Opt("v", "verbose").take_flag


def print_if(condition):
    """Return `print` if `condition` is true, else a dummy function"""
    return print if condition else lambda *_, **__: None
