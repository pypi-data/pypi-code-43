#!/usr/bin/env python
"""
Try to create a style-based string object.
"""

# For the binary operations, we need to be able to call _simplify (and others)
# on the second parameter. This protected access needs to be allowed, and it
# is easiest just to turn the check off throughout the file.
# pylint: disable=protected-access

import re
import functools
import string


try:
    unicode
    def join_string(parts):
        """
        Join the list of parts together, to make a single string.

        If any of the parts are mismatched (unicode/str), then we try to upgrade
        the string to a unicode. This ensures that we don't get any 'UnicodeDecodeError'
        exceptions when trying to append UTF-8 encoded strings with unicode strings.
        """
        new_list = []
        any_unicode = False
        for part in parts:
            if isinstance(part, unicode):
                if not any_unicode:
                    # There was no unicode until now, and this part is a unicode.
                    # So now to ensure that the whole string is a unicode.
                    new_list = [s.decode('utf-8', 'replace') for s in new_list]
                    any_unicode = True
            elif isinstance(part, str):
                if any_unicode:
                    part = part.decode('utf-8', 'replace')

            new_list.append(part)

        return ''.join(new_list)
except NameError:
    unicode = str       # pylint: disable=redefined-builtin
    def join_string(parts):
        return ''.join(parts)

try:
    basestring
except NameError:
    basestring = str       # pylint: disable=redefined-builtin


class Rendition(object):
    """
    Base class to perform a rendering of the contents of a StyledString
    for a given set of properties.
    """
    # List of property expansions to use, keyed by the property name.
    # The key '*' may be used to match any unknown properties.
    # The value is a tuple of (add, remove) strings.
    # The strings may include:
    #   '%v' to include the value to be expanded.
    #   '%p' to include the property name.
    expansions = {}

    def __init__(self):
        # Current properties in use
        self.properties = {}

    def start(self):
        self.properties = {}
        return ''

    def render(self, our_str, properties):
        """
        Render the specified string with a set of properties.
        """
        added = {}
        removed = {}
        changed = {}
        for prop, value in sorted(properties.items()):
            if prop not in self.properties:
                added[prop] = value
            elif value != self.properties[prop]:
                changed[prop] = (self.properties[prop], value)
        for prop, value in sorted(self.properties.items()):
            if prop not in properties:
                removed[prop] = value

        parts = []

        # See if we can do all the changes in one go
        if added or removed or changed:
            delta = self.properties_delta(self.properties, properties, added, removed, changed)
            if delta is not None:
                parts.extend(delta)
            else:
                # We've now worked out what has been added, what has been removed,
                # and what has changed.
                if changed:
                    change = self.properties_change(changed)
                    if change is not None:
                        parts.extend(change)
                    else:
                        # Change method not supported, so instead use remove and add.
                        for prop in changed:
                            removed[prop] = changed[prop][0]
                            added[prop] = changed[prop][1]

                if removed:
                    parts.extend(self.properties_remove(removed))
                if added:
                    parts.extend(self.properties_add(added))

        if our_str is not None:
            parts.append(our_str)

        self.properties = properties
        return parts

    def end(self):
        return self.render(None, {})

    def properties_delta(self, old_properties, new_properties, added, removed, changed):  # pylint: disable=W0613,R0201
        return None

    def properties_change(self, changed):  # pylint: disable=W0613,R0201
        return None

    def properties_add(self, added):
        parts = []
        for prop, value in sorted(added.items()):
            parts.append(self.property_add(prop, value))
        return parts

    def properties_remove(self, removed):
        parts = []
        for prop, value in sorted(removed.items(), reverse=True):
            parts.append(self.property_remove(prop, value))
        return parts

    def property_add(self, prop, value):
        exp_name = prop
        if prop not in self.expansions:
            exp_name = '*'

        if exp_name in self.expansions:
            expansions = self.expansions[exp_name]
            if value is None and len(expansions) > 2:
                add = expansions[2] or ''
            else:
                add = expansions[0] or ''
            if '%v' in add:
                add = add.replace('%v', str(value))
            if '%p' in add:
                add = add.replace('%p', str(prop))
            return add

        raise NotImplementedError

    def property_remove(self, prop, value):
        exp_name = prop
        if prop not in self.expansions:
            exp_name = '*'

        if exp_name in self.expansions:
            expansions = self.expansions[exp_name]
            if value is None and len(expansions) > 3:
                remove = expansions[3] or ''
            else:
                remove = expansions[1] or ''
            if '%v' in remove:
                remove = remove.replace('%v', str(value))
            if '%p' in remove:
                remove = remove.replace('%p', str(prop))
            return remove

        raise NotImplementedError


class RenditionExampleMarkup(Rendition):
    expansions = {
        'fg': ("<fg colour='%v'>", '</fg>'),
        'bg': ("<bg colour='%v'>", '</bg>'),
        '*': ("<%p value='%v'>", '</%p>', '<%p>'),
    }


class RenditionIdentity(Rendition):
    expansions = {
        '*': ('', ''),
    }


@functools.total_ordering
class Rule(object):

    def __init__(self, rule, properties):
        """
        Construct a styling rule.

        Rules are matched by strings with the format:

        ```
        .?<class>[.<class>]*
        ```
        """
        self.rule = rule
        self.properties = properties

    def __repr__(self):
        props = ', '.join('%s: %s' % (key, value) for key, value in self.properties.items())
        if props:
            props = ', %s' % (props,)
        return "%s('%s'%s)" % (self.__class__.__name__, self.rule, props)

    def segments(self):
        nsegs = len(self.rule.split('.'))
        if self.rule[0] == '.':
            nsegs -= 1
        return nsegs

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            # We can only compare against instances of ourselves
            return False
        return self.rule == other.rule

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            # We can only compare against instances of ourselves
            return False
        return self.rule != other.rule

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            # We can only compare against instances of ourselves
            return False

        ns_segments = self.segments()
        no_segments = other.segments()
        if ns_segments < no_segments:
            return True
        if ns_segments > no_segments:
            return False

        ns_anchored = self.rule[0] != '.'
        no_anchored = other.rule[0] != '.'
        if ns_anchored != no_anchored:
            return not ns_anchored

        return self.rule < other.rule

    def match(self, context):
        if self.rule.startswith('.'):
            # Preceding the rule by '.' means it can appear anywhere
            if context.startswith(self.rule[1:]):
                return True
            ind = context.find(self.rule + '.')
            if ind != -1 or context.endswith(self.rule):
                return True
            return False

        # Not preceded by '.' means that it must be at the start
        if context.startswith(self.rule):
            return True

        return False


class Styling(object):

    def __init__(self):
        self.rules = []
        self.sorted = False

    def __repr__(self):
        return "%s(%s rules)" % (self.__class__.__name__, len(self.rules))

    def add_rule(self, rule):
        self.rules.append(rule)
        self.sorted = False

    def __iadd__(self, other):
        if not isinstance(other, Rule):
            raise ValueError('Cannot add %r to %s' % (other, self.__class__.__name__))

        self.add_rule(other)
        return self

    @property
    def sorted_rules(self):
        """
        Sort rules, from least specific to most specific,
        so that we keep the properties that are the most
        relevant.
        """
        if not self.sorted:
            self.rules.sort()
            self.sorted = True
        return self.rules

    def match(self, context):
        properties = {}
        for rule in self.sorted_rules:
            if rule.match(context):
                properties.update(rule.properties)
        return properties

    def __len__(self):
        return len(self.rules)


class StyledString(object):
    style_rules = Styling()
    render_class = RenditionExampleMarkup

    def __init__(self, s, style=None):
        self.sequence = []
        if s is not None and s != '':
            if isinstance(s, StyledString):
                # If it was a StyledString container, we can remove a level of
                # the container to make it simpler to manage.
                s = s.copy()
                if s.style is None:
                    self.sequence = s.sequence
                    s = None
            elif not isinstance(s, basestring):
                s = unicode(s)
            if s is not None:
                self.sequence.append(s)
        self.style = style
        self.simplified = False

    def __repr__(self):
        # We indicate with the first letter of the bracketted content whether the
        # sequence has been simplified or is raw.
        # Most operations will try to keep the content relatively simple, but they
        # only when the strings must be simplified should this be performed.
        return "%s(%s<%s>, %r)" % (self.__class__.__name__,
                                   'S' if self.simplified else 'r',
                                   self.style,
                                   self.sequence)

    def __str__(self):
        rendered = self.render(self.style_rules)
        if unicode is not str and isinstance(rendered, unicode):
            rendered = rendered.encode('utf-8')
        return rendered

    def plain(self):
        """
        Return the plain string, with no styling at all.
        """
        self._simplify()
        flat = []
        for s in self.sequence:
            if isinstance(s, StyledString):
                # We need to recurse into the nested string
                more = s.plain()
                flat.append(more)
            else:
                flat.append(s)

        return join_string(flat)

    def flatten(self, context=None):
        self._simplify()
        if context:
            context = context[:]
        else:
            context = []
        if self.style:
            context.append(self.style)
        context_label = '.'.join(context)
        flat = []
        for s in self.sequence:
            if isinstance(s, StyledString):
                # We need to recurse into the nested string
                more = s.flatten(context)
                flat.extend(more)
            else:
                flat.append((s, context_label))

        return flat

    def render(self, style_rules=None, render_class=None):
        style_rules = style_rules or self.style_rules
        render_class = render_class or self.render_class
        rendition = render_class()

        flat = self.flatten()
        str_list = [rendition.start()]
        for s, context_label in flat:
            properties = style_rules.match(context_label)
            str_list.extend(rendition.render(s, properties))
        str_list.extend(rendition.end())
        return join_string(str_list)

    def __iadd__(self, other):
        if isinstance(other, basestring):
            other = self.__class__(other)
        elif self is other:
            other = other.copy()
        elif not isinstance(other, StyledString):
            other = self.__class__(unicode(other))

        if self.style == other.style:
            other = other.copy()
            self.sequence.extend(other.sequence)
            self.simplified = False
            return self

        new_ss = self.__class__(None)
        if self.style is None:
            new_ss.sequence.extend(self.sequence)
        else:
            new_ss.sequence.append(self)
        if other.style is None:
            new_ss.sequence.extend(other.sequence)
        else:
            new_ss.sequence.append(other)
        new_ss.simplified = False
        return new_ss

    def __add__(self, other):
        if isinstance(other, basestring):
            other = self.__class__(other)
        elif not isinstance(other, StyledString):
            other = self.__class__(unicode(other))

        if self.style == other.style:
            new_ss = self.copy()
            new_ss.sequence.extend(other.sequence)
            new_ss.simplified = False
            return new_ss

        new_ss = self.__class__(None)
        if self.style is None:
            new_ss.sequence.extend(self.sequence)
        else:
            new_ss.sequence.append(self)
        if other.style is None:
            new_ss.sequence.extend(other.sequence)
        else:
            new_ss.sequence.append(other)
        new_ss.simplified = False
        return new_ss

    def __radd__(self, other):
        if isinstance(other, basestring):
            other = self.__class__(other)
        else:
            other = self.__class__(unicode(other))

        if self.style == other.style:
            new_ss = other.copy()
            new_ss.sequence.extend(self.sequence)
            new_ss.simplified = False
            return new_ss

        new_ss = self.__class__(None)
        if other.style is None:
            new_ss.sequence.extend(other.sequence)
        else:
            new_ss.sequence.append(other)
        new_ss.sequence.append(self.copy())
        new_ss.simplified = False
        return new_ss

    def copy(self):
        new_ss = self.__class__(None)
        new_ss.style = self.style
        new_ss.sequence = [ss if isinstance(ss, basestring) else ss.copy() for ss in self.sequence]
        new_ss.simplified = self.simplified
        return new_ss

    def __len__(self):
        return sum((len(ss) for ss in self.sequence), 0)

    def _simplify(self):
        """
        Attempt to reduce the bare strings in the object to simpler ones, and remove nesting
        if possible.
        """
        if self.simplified:
            # Already simplified, or the sequence is short enough it must be simple
            return self

        new_sequence = []
        last = None
        changed = False
        for item in self.sequence:
            if isinstance(item, StyledString):
                item._simplify()
                if len(item.sequence) == 0:
                    # Any items that have been simplified into a string with no elements
                    # is clearly redundant, and we can skip it from the simplified result.
                    continue
            if last is not None:
                if isinstance(last, basestring) and \
                   isinstance(item, basestring):
                    new_sequence[-1] += item
                    changed = True
                elif isinstance(last, StyledString) and \
                     isinstance(item, StyledString) and \
                     last.style == item.style:
                    new_sequence[-1] += item
                    changed = True
                else:
                    new_sequence.append(item)
            else:
                new_sequence.append(item)
            last = item

        if changed:
            # We have changed the elements in the sequence, so we must
            # try to simplify them again. The '+=' accumulation of items
            # may have made it possible to simplify the inner elements
            # more.
            for item in new_sequence:
                if isinstance(item, StyledString):
                    item._simplify()

        self.sequence = new_sequence

        while self.style is None and \
              len(self.sequence) == 1 and \
              isinstance(self.sequence[0], StyledString):
            # A None style enclosing a single element can be simplified to just
            # that one element.
            self.style = self.sequence[0].style
            self.sequence = self.sequence[0].sequence

        self.simplified = True

        # It may be handy to return ourselves when complete
        return self

    def __eq__(self, other):
        if isinstance(other, StyledString):
            self._simplify()
            other._simplify()

            if self.style != other.style:
                return False

            return self.sequence == other.sequence

        if isinstance(other, basestring):
            if self.style is not None:
                # A string that is styled is not equal to any string
                return False

            return self.plain() == other

        return False

    def __ne__(self, other):
        # Fun python fact: Prior to Python 3.4, __ne__ was not implicitly the inverse of
        # __eq__. With 3.4, the default behaviour for __ne__ is to negate __eq__.
        return not (self == other)

    def __mul__(self, number):
        number = int(number)
        if number <= 0:
            return self.__class__('')

        if number == 1:
            return self.copy()

        if len(self.sequence) == 1:
            if isinstance(self.sequence[0], basestring):
                # We're repeating a string, so we can simplify this right now
                lots = self.sequence[0] * number
                ss = StyledString(lots, style=self.style)
                return ss

        self_copy = self.copy()
        ss = StyledString(None, style=self.style)
        # It is safe to repeat the contents of the sequence here without copying
        # them many times because we know that any operations on this string will
        # require a copy (or will follow the same rules).
        ss.sequence = self_copy.sequence * number
        ss.simplified = False

        return ss

    def __getitem__(self, given):
        # A couple of fast operations for the simple cases
        if len(self.sequence) <= 1:
            value = ''
            if len(self.sequence) == 1:
                value = self.sequence[0]
            return self.__class__(value[given], style=self.style)

        if isinstance(given, slice):
            is_range = True
            index_from = given.start
            index_to = given.stop
            if given.step and given.step != 1:
                raise TypeError('Slice not supported with arbitrary step values: step=%s' % (given.step,))
        else:
            is_range = False
            index_from = given
            index_to = int

        if index_from is None:
            index_from = 0

        if index_from < 0 or index_to is None or index_to is int or index_to < 0:
            total_len = len(self)
            if index_from < 0:
                index_from = index_from + total_len
            if index_to is int:
                index_to = index_from + 1
            if index_to is None:
                index_to = total_len
            elif index_to < 0:
                index_to = max(0, index_to + total_len)

        if index_from < 0 and not isinstance(given, slice):
            # The negative index check only applies to a bare index, not a slice
            raise IndexError("StyledString index out of range (index %s is " \
                             "before the start of the string)" % (index_from,))

        if index_from == 0 and index_to == len(self):
            # The range they were after was the entire string, so better to just make a copy.
            return self.copy()

        accumulator = StyledString(None, self.style)
        if index_from == index_to:
            return accumulator

        index_current = 0
        for component in self.sequence:
            if index_current >= index_from:
                # The content of this component is being copied, at least partially
                if isinstance(component, basestring):
                    # Simple string, so simple to copy.
                    if index_current + len(component) <= index_to:
                        accumulator.sequence.append(component)
                    else:
                        accumulator.sequence.append(component[0:index_to - index_current])
                    index_current += len(component)
                else:
                    # Another styled string, so we will need to get a substring from it
                    more = component[0:index_to - index_current]
                    accumulator.sequence.append(more)
                    index_current += len(more)
            else:
                # The start index does not start in this component
                component_len = len(component)
                if index_current + component_len <= index_from:
                    # Nothing to do for this component
                    pass
                else:
                    start = index_from - index_current
                    end = index_to - index_current
                    more = component[start:end]
                    if (isinstance(more, basestring) and more != '') or \
                       (isinstance(more, StyledString) and more.sequence):
                        accumulator.sequence.append(more)
                index_current += component_len

            if index_current >= index_to:
                break

        if index_current <= index_from and not is_range:
            raise IndexError("StyledString index out of range (index %s is " \
                             "beyond the end of the string)" % (index_from,))

        # We have directly manipulated the sequence, so this is not a simplified string.
        accumulator.simplified = False

        return accumulator

    def join(self, iterable):
        """
        Join together the values of the iterable to make a string of the same
        style as this current string.
        """
        conjunction = self
        if len(self) == 0:
            conjunction = None

        ss = self.__class__(None)
        first = True
        for value in iterable:
            if not first:
                if conjunction is not None:
                    ss += conjunction
            ss += value
            first = False

        return ss

    def _starts_or_ends(self, ending, truncatef):
        """
        Check whether a StyledString starts or ends with a given string.

        The truncation function is able to cut the string to a requested number of
        characters, given the string and the number.
        """
        if isinstance(ending, tuple):
            # Tuple comparisons can be done differently, which may be more
            # efficient.
            if len(ending) == 0:
                # Empty tuple never matches.
                return False

            if len(ending) == 1:
                # There's only a single element in the tuple, so we can treat
                # as a bare string
                ending = ending[0]
            else:
                # We're going to do a bunch of calculations with the length
                # of the strings, so let's get them in a form we can manipulate
                # easily without having to return to calculate the lengths
                # many times. [StyledString.len() is not optimised]
                ending_and_length = [(end, len(end)) for end in ending]

                # Omit any strings longer than ourselves
                our_length = len(self)
                ending_and_length = [end for end in ending_and_length if end[1] <= our_length]

                longest = ending_and_length[0][1]
                shortest = longest
                for end in ending_and_length[1:]:
                    end_len = end[1]
                    shortest = min(end_len, shortest)
                    longest = max(end_len, longest)

                if shortest == 0:
                    # If any of the tuple elements was an empty string, it
                    # matches.
                    return True

                # Sort the list so that we work our way down from the longest to the
                # shortest. This means we just trim the strings we are searching each
                # time.
                ending_and_length = sorted(ending_and_length,
                                           key=lambda end: end[1],
                                           reverse=True)

                compare_string = truncatef(self, longest)
                compare_plain = None
                our_length = longest
                for end in ending_and_length:
                    end_string = end[0]
                    end_len = end[1]
                    if end_len < our_length:
                        # If the end string has shortened, reduce the string to just that
                        # length.
                        compare_string = truncatef(compare_string, end_len)
                        if compare_plain:
                            compare_plain = truncatef(compare_plain, end_len)
                        our_length = end_len

                    if isinstance(end_string, basestring):
                        # If the end_string is a regular string, we compare as a plain string.
                        if compare_plain is None:
                            # We haven't calculated a plain string yet, so get one.
                            compare_plain = compare_string.plain()

                        if compare_plain == end_string:
                            return True
                    else:
                        # The ending is a StyledString, so we need to compare with the styled
                        # version.
                        if compare_string == end_string:
                            return True

                    # Did not match this element in the string, so we'll try some more

                # Finally, did not match anything, so we give up.
                return False

        length = len(ending)
        if length == 0:
            # Regardless of the styles, etc, everything ends with an empty string
            return True

        our_length = len(self)
        if length > our_length:
            # If the expected string is longer, we cannot match
            return False

        our_ending = truncatef(self, length)

        if isinstance(ending, basestring):
            our_ending = our_ending.plain()

        return our_ending == ending

    def endswith(self, ending):
        """
        Check whether a StyledString ends with a given string.
        """

        # Try the simple implementation first
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring) and \
           isinstance(ending, basestring):
            return self.sequence[0].endswith(ending)

        def truncate(string_to_truncate, number_of_chars):
            return string_to_truncate[-number_of_chars:]

        return self._starts_or_ends(ending, truncate)

    def startswith(self, beginning):
        """
        Check whether a StyledString starts with a given sting
        """

        # Try the simple implementation first
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring) and \
           isinstance(beginning, basestring):
            return self.sequence[0].startswith(beginning)

        def truncate(string_to_truncate, number_of_chars):
            return string_to_truncate[:number_of_chars]

        return self._starts_or_ends(beginning, truncate)

    def splitlines(self, keepends=False):
        """
        Split lines at a line ending boundary. Keep the line endings if keepends is set
        """
        # Simple implementation first
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring):
            parts = self.sequence[0].splitlines(keepends)
            return [self.__class__(part, style=self.style) for part in parts]

        lines = []
        ss = self.__class__(None, self.style)
        ss.simplified = False
        for value in self.sequence:
            sublist = value.splitlines(True)
            for line in sublist:
                if line.endswith('\n'):
                    if keepends:
                        ss.sequence.append(line)
                    else:
                        ss.sequence.append(line[:-1])
                    lines.append(ss)
                    ss = self.__class__(None, self.style)
                    ss.simplified = False
                else:
                    ss.sequence.append(line)

        if ss != '':
            lines.append(ss)

        if not keepends:
            lines = [line[:-1] if line.endswith('\n') else line for line in lines]

        return lines

    def lstrip(self, chars=None):
        """
        Strip the specified characters from the string (at the left)
        """
        our_string = self.plain()
        stripped = our_string.lstrip(chars)
        if our_string == stripped:
            return self
        stripped_len = len(our_string) - len(stripped)
        return self[stripped_len:]

    def rstrip(self, chars=None):
        """
        Strip the specified characters from the string (at the right)
        """
        our_string = self.plain()
        stripped = our_string.rstrip(chars)
        if our_string == stripped:
            return self
        stripped_len = len(our_string) - len(stripped)
        return self[:-stripped_len]

    def strip(self, chars=None):
        """
        Strip the specified characters from the string (at both ends)
        """
        return self.lstrip(chars).rstrip(chars)

    def format(self, *args, **kwargs):
        format_string = self
        return Formatter().vformat(format_string, args, kwargs)

    def upper(self):
        """
        Return a copy of the string, converted to uppercase.
        """
        upper = lambda s: s.upper()
        return self._transform(upper)

    def lower(self):
        """
        Return a copy of the string, converted to uppercase.
        """
        lower = lambda s: s.lower()
        return self._transform(lower)

    def swapcase(self):
        """
        Return a copy of the string, swapping the case of all the letters.
        """
        swapper = lambda s: s.swapcase()
        return self._transform(swapper)

    def _transform(self, transformer):
        """
        Perform a transformation on the string components of the StyledString.
        """
        if len(self.sequence) == 1:
            new_str = transformer(self.sequence[0])
            return self.__class__(new_str, style=self.style)

        new_str = self.copy()
        # We've copied the string. Now let's convert each part into upper cased
        # strings.

        # We'll do this iteratively, by keeping a stack of the sequences that
        # we are processing, and popping them off.
        seqs = [new_str.sequence]
        while seqs:
            sequence = seqs.pop()
            for index, item in enumerate(sequence):
                if isinstance(item, basestring):
                    sequence[index] = transformer(item)
                elif isinstance(item, StyledString):
                    seqs.append(item.sequence)

        return new_str

    def ljust(self, width, fill=' '):
        """
        Return S left-justified in a string of length width. Padding is
        done using the specified fill character (default is a space).
        If the string is longer than the width specified, it is returned
        unchanged.
        """
        our_len = len(self)
        if our_len >= width:
            return self

        new_str = self.copy()
        pad_len = width - our_len
        new_str += fill * pad_len
        return new_str

    def rjust(self, width, fill=' '):
        """
        Return S right-justified in a string of length width. Padding is
        done using the specified fill character (default is a space).
        If the string is longer than the width specified, it is returned
        unchanged.
        """
        our_len = len(self)
        if our_len >= width:
            return self

        new_str = self.copy()
        pad_len = width - our_len
        new_str = (fill * pad_len) + new_str
        return new_str

    def center(self, width, fill=' '):
        """
        Return S centered in a string of length width. Padding is
        done using the specified fill character (default is a space).
        If the string is longer than the width specified, it is returned
        unchanged.
        """
        our_len = len(self)
        if our_len >= width:
            return self

        new_str = self.copy()
        pad_len = width - our_len
        left_pad_len = int(pad_len / 2)
        right_pad_len = pad_len - left_pad_len

        new_str = (fill * left_pad_len) + new_str + (fill * right_pad_len)
        return new_str

    def zfill(self, width):
        """
        Pad a numeric string S with zeros on the left, to fill a field
        of the specified width.  The string S is never truncated.
        """
        return self.rjust(width, fill='0')

    def capitalize(self):
        """
        Return a copy of the string, with the first character capitalized.
        """
        if len(self) == 0:
            return self
        return self[0].upper() + self[1:]

    def title(self):
        """
        Return a copy of the string, with the letters capitalised.
        """
        if len(self) == 0:
            return self

        # First we get the titling of the plain string
        titled = self.plain().title()

        # Let's shortcut the manual reconstruction if possible
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring):
            return self.__class__(titled, style=self.style)

        # Then we step through all the sequence items, from the end toward the start, and
        # replace the strings with the matching end sections of the titled string
        new_str = self.copy()
        stack = [(new_str.sequence, index, item) for index, item in enumerate(new_str.sequence)]
        while stack:
            (sequence, index, item) = stack.pop()
            if isinstance(item, StyledString):
                # This element is a styled string itself, so we need to append all its sequence to the list.
                stack.extend([(item.sequence, subindex, subitem)
                              for subindex, subitem in enumerate(item.sequence)])
            else:
                # This is a bare string. So we should just be able to replace its content from our
                # titled string.
                itemlen = len(item)
                item = titled[-itemlen:]
                titled = titled[:-itemlen]
                sequence[index] = item

        return new_str

    def count(self, substring):
        """
        Count the number of instances of a substring
        """
        if len(self) == 0:
            return 0

        plain = self.plain()
        if isinstance(substring, StyledString):
            substring = substring.plain()

        return plain.count(substring)

    def find(self, sub, start=None, end=None):
        """
        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Return -1 on failure.
        """
        plain = self.plain()
        if isinstance(sub, StyledString):
            sub = sub.plain()

        return plain.find(sub, start, end)

    def index(self, sub, start=None, end=None):
        """
        As for find, but raise ValueError if not found.
        """
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError("Substring not found")
        return result

    def __contains__(self, sub):
        """
        As for find, but returns True or False on finding the string, or failure.
        """
        return self.find(sub) != -1

    def rfind(self, sub, start=None, end=None):
        """
        Return the highest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Return -1 on failure.
        """
        plain = self.plain()
        if isinstance(sub, StyledString):
            sub = sub.plain()

        return plain.rfind(sub, start, end)

    def rindex(self, sub, start=None, end=None):
        """
        As for rfind, but raise ValueError if not found.
        """
        result = self.rfind(sub, start, end)
        if result == -1:
            raise ValueError("Substring not found")
        return result

    def partition(self, sep):
        """
        Search for the separator sep in S, and return the part before it,
        the separator itself, and the part after it.  If the separator is not
        found, return S and two empty strings.
        """
        index = self.find(sep)
        if index == -1:
            return (self, '', '')

        left = self[:index]
        middle = self[index:index + len(sep)]
        right = self[index + len(sep):]
        return (left, middle, right)

    def rpartition(self, sep):
        """
        Search backwards for the separator sep in S, and return the part before it,
        the separator itself, and the part after it.  If the separator is not
        found, return S and two empty strings.
        """
        index = self.rfind(sep)
        if index == -1:
            return (self, '', '')

        left = self[:index]
        middle = self[index:index + len(sep)]
        right = self[index + len(sep):]
        return (left, middle, right)

    def _styledstring_at_offset(self, offset):
        """
        Return a template string in the style of a given offset in the string.

        The template string will be returned as a nested set of StyledStrings
        which match the styling of that offset, but with nothing in the sequence.
        We return a tuple of the newly created string, and the sequence into
        which new strings can be added to use this style.
        """

        if len(self) == 0:
            char = self.copy()
        else:
            char = self[offset:offset+1]
        # Does not matter what the char is, just that we get the nested styles for
        # that character. Now we find the deepest sequence element as this is where
        # we will operate.
        last_ss = char
        while len(last_ss.sequence) != 0 and isinstance(last_ss.sequence[0], StyledString):
            last_ss.simplified = False
            last_ss = last_ss.sequence[0]

        last_ss.sequence = []

        # Return the pair so that we can modify them (if needed)
        return (char, last_ss.sequence)

    def split(self, sep=None, maxsplit=None):
        """
        Split the string at the separator (or whitespace if None), up to a limited number of splits.
        """

        # We use the implementation of the base string split to perform the splitting as
        # required, and then we select the sections of the string as requested in order to
        # construct the list of styled elements.
        plain = self.plain()
        if maxsplit is None:
            # It is not defined what the absent 'maxsplit' value is, so we must call this separately.
            splitted = plain.split(sep)
        else:
            splitted = plain.split(sep, maxsplit)

        # Fast handling for the simple case
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring):
            return [StyledString(part, style=self.style) for part in splitted]

        index = 0
        split_list = []
        for split in splitted:
            if sep is None:
                # if we're doing whitespace skipping, skip any leading separators
                while plain[index].isspace():
                    index += 1
            splitlen = len(split)
            split_list.append(self[index:index + splitlen])
            index += splitlen
            if sep is not None:
                index += len(sep)

        return split_list

    def rsplit(self, sep=None, maxsplit=None):
        """
        Split the string at the separator (or whitespace if None), up to a limited number of splits.
        """

        # We use the implementation of the base string split to perform the splitting as
        # required, and then we select the sections of the string as requested in order to
        # construct the list of styled elements.
        plain = self.plain()
        if maxsplit is None:
            # It is not defined what the absent 'maxsplit' value is, so we must call this separately.
            splitted = plain.rsplit(sep)
        else:
            splitted = plain.rsplit(sep, maxsplit)

        # Fast handling for the simple case
        if len(self.sequence) == 1 and isinstance(self.sequence[0], basestring):
            return [StyledString(part, style=self.style) for part in splitted]

        index = 0
        split_list = []
        for split in splitted:
            if sep is None:
                # if we're doing whitespace skipping, skip any leading separators
                while plain[index].isspace():
                    index += 1
            splitlen = len(split)
            split_list.append(self[index:index + splitlen])
            index += splitlen
            if sep is not None:
                index += len(sep)

        return split_list

    def re_sub(self, regex, replacement, count=0, flags=0):
        """
        Perform a regular exression substitution on the string.

        We attempt to retain all the styling from the original in the resulting
        output.
        """
        self._simplify()
        if len(self.sequence) == 0 or (len(self.sequence) == 1 and isinstance(self.sequence[0], basestring)):
            # The string is simple, containing only a basestring.
            # This means that we can just do a simple regular expression operation
            # and all will be well.
            our_str = ''
            if len(self.sequence) == 1:
                our_str = self.sequence[0]

            new_string = re.sub(regex, replacement, our_str, count, flags)
            return StyledString(new_string, style=self.style)

        # A more complex operation, which we're going to perform by
        # splitting up the string according to the plain representation
        # then reconstructing the styled version.

        plain = self.plain()
        accumulator = self.__class__('')
        last_index = 0
        match_style_offset = None
        for match in re.finditer(regex, plain):

            # Everything from the 'last_index' to the current match position is to be copied.
            (match_start, match_end) = match.span()
            if last_index != match_start:
                accumulator += self[last_index:match_start]

            # Find the style of the section we just removed.
            match_style_offset = match_start
            if match_start == match_end:
                # The match is of 0 characters, so we take the style of the character before
                match_style_offset = max(match_start - 1, 0)

            def match_styled_string(our_str):
                """
                Add a string in the style of the match point itself.
                """
                match_style, match_style_sequence = self._styledstring_at_offset(match_style_offset)
                match_style_sequence.append(our_str)
                match_style.simplified = False
                return match_style

            # Escaped characters that result in simple replacements
            escaped_characters = {
                '\\': '\\',
                'a': '\a',
                'b': '\b',
                'f': '\f',
                'n': '\n',
                'r': '\r',
                't': '\t',
                'v': '\v',
                '\n': '',
                "'": "'",
                '"': '"',
                # Now the unsupported replacements
                'o': None,
                'x': None,
                'N': None,
                'u': None,
                'U': None,
            }

            # Step through the replacement string, working out what substitutions
            # should be performed
            rep = replacement
            while rep != '':
                (before, escape, after) = rep.partition('\\')
                if before:
                    # We have a string to put in the style of the bare match.
                    accumulator += match_styled_string(before)
                if after:
                    escape = after[0]
                    after = after[1:]
                    if escape in escaped_characters:
                        if escaped_characters[escape] is None:
                            raise TypeError(("Escape '\\%s' is not supported within StyledString "
                                             "regular expression replacements") % (escape,))

                        # Simple replacement, so we can just add it.
                        accumulator += match_styled_string(escaped_characters[escape])
                    else:
                        # This may be a backreference in the form \<number> or \g<number> or \g<name>
                        backref = None
                        if escape.isdigit():
                            backref = escape
                            while after and after[0].isdigit():
                                backref += after[0]
                                after = after[1:]
                            backref = int(backref)
                        elif escape == 'g':
                            # the \g<name> or \g<number> form
                            if after[0] != '<':
                                raise TypeError("Escape '\\g' must be followed by '<#>' or '<name>'. "
                                                "Missing opening '<'")

                            (name, arrow, after) = after[1:].partition('>')
                            if arrow != '>':
                                raise TypeError("Escape '\\g' must be followed by '<#>' or '<name>'. "
                                                "Missing closing '>'.")

                            if name[0].isdigit():
                                backref = int(name)
                            else:
                                backref = name

                        if backref is None:
                            raise TypeError(("Escape '\\%s' is not recognised within StyledString "
                                             "regular expression replacements") % (escape,))

                        (group_start, group_end) = match.span(backref)

                        # We have located the group, so all that is left is to
                        # accumulate it into the output string.
                        group = self[group_start:group_end]
                        accumulator += group

                        if len(match.groups()) > 1:
                            match_style_offset = group_end

                    # The remaining text may include other replacements...
                    rep = after

                else:
                    # There is no following text, so we are now done.
                    rep = ''

            # After the match, update our last_index
            last_index = match_end

        # Finally, accumulate the remaining text
        if last_index != len(plain):
            accumulator += self[last_index:len(plain)]

        return accumulator

# Create all the 'is*' functions.
for var_name in dir(str):
    if not var_name.startswith('is'):
        continue

    if not callable(getattr('', var_name, None)):
        # It isn't a method
        continue

    def issomething(self, _method_name=var_name):
        plain = self.plain()
        converter = getattr(plain, _method_name)
        return converter()

    issomething.__name__ = var_name

    setattr(StyledString, var_name, issomething)

# Fix up the regular expression module to handle our strings
_re__sub = re.sub
def _styledstring_re_sub(regex, replacement, our_str, count=0, flags=0):
    if isinstance(our_str, StyledString):
        return our_str.re_sub(regex, replacement, count, flags)
    return _re__sub(regex, replacement, our_str, count, flags)
re.sub = _styledstring_re_sub


try:
    # CPython 3 implementation specific
    import _string

    def formatter_parser(format_string):
        if isinstance(format_string, StyledString):
            format_string = format_string.plain()
        return _string.formatter_parser(format_string)

    def formatter_field_name_split(field_name):
        first, rest = _string.formatter_field_name_split(field_name)
        return (first, rest)

except ImportError:
    # CPython implementation specific
    def formatter_parser(format_string):
        if isinstance(format_string, StyledString):
            format_string = format_string.plain()
        return format_string._formatter_parser()

    def formatter_field_name_split(field_name):
        first, rest = field_name._formatter_field_name_split()
        return (first, rest)

try:
    long
except NameError:
    long = int  # pylint: disable=redefined-builtin


########################################################################
# the Formatter class
# see PEP 3101 for details and purpose of this class

# The hard parts are reused from the C implementation.  They're exposed as "_"
# prefixed methods of str.

# The overall parser is implemented in _string.formatter_parser.
# The field name parser is implemented in _string.formatter_field_name_split

class Formatter(object):

    def format(self, *args, **kwargs):
        if not args:
            raise TypeError("descriptor 'format' of 'Formatter' object needs an argument")
        args = list(args)
        self = args.pop(0)  # allow the "self" keyword be passed
        try:
            format_string = args.pop(0) # allow the "format_string" keyword be passed
        except IndexError:
            raise TypeError("format() missing 1 required positional argument: 'format_string'")
        return self.vformat(format_string, args, kwargs)

    def vformat(self, format_string, args, kwargs):
        # See if we can deal with this as a plain string
        if len(format_string.sequence) == 1 and isinstance(format_string, basestring):
            if '{(' not in format_string:
                # Our format string is extended with the styling, so we cannot handle those cases
                if all(isinstance(arg, basestring) for arg in args) and \
                   all(isinstance(arg, basestring) for arg in kwargs.values()):
                    # All of the things we're dealing with are simple, so we can just call the
                    # regular string handling.
                    result = string.Formatter().vformat(format_string.sequence[0], args, kwargs)
                    result = StyledString(result)
                    return result

        used_args = set()
        result, _ = self._vformat(format_string, args, kwargs, used_args, 2)
        self.check_unused_args(used_args, args, kwargs)
        result._simplify()
        return result

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth,
                 auto_arg_index=0):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                # handle arg indexing when empty field_names are given.
                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # given the field_name, find the object it references
                #  and the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth-1,
                    auto_arg_index=auto_arg_index)

                # format the object and append to the result
                formatted = self.format_field(obj, format_spec)
                result.append(formatted)

        style_class = StyledString
        if isinstance(format_string, StyledString):
            style_class = format_string.__class__

        result = sum(result, style_class(None))
        if isinstance(format_string, StyledString):
            result = style_class(result, style=format_string.style)

        return result, auto_arg_index

    def get_value(self, key, args, kwargs):  # pylint: disable=no-self-use
        if isinstance(key, (int, long)):
            return args[key]
        else:
            return kwargs[key]

    def check_unused_args(self, used_args, args, kwargs):
        pass

    def format_field(self, value, format_spec):
        """
        Format the field, using the standard spec, but with extensions for StyledString.

        format_spec can be preceded by '(<style_spec>)'.
        The 'style-spec' can consists of comma separated fields. Any fields may be omitted.

        Field 0:    Style to apply to the value.
        Field 1:    Style to apply to the whole formatted field
        """

        # Work out what class we should apply - either the format, or the value,
        # depending on which is styled (or falling back to the default)
        style_class = StyledString
        if isinstance(format_spec, StyledString):
            style_class = format_spec.__class__
        elif isinstance(value, StyledString):
            style_class = value.__class__

        if isinstance(format_spec, StyledString):
            # The formatting will be handled by the top level vformat,
            # so the spec is always a plain string
            format_spec = format_spec.plain()

        if format_spec.startswith('('):
            # They supplied a style name to apply to this element

            # Trim out the style name
            format_spec_end = format_spec.find(')')
            style_spec = format_spec[1:format_spec_end]
            format_spec = format_spec[format_spec_end + 1:]

            style_fields = style_spec.split(',')
            if len(style_fields) < 2:
                style_fields = list(style_fields)
                style_fields.extend([''] * (2 - len(style_fields)))

            if style_fields[0] == '':
                # No styling on the field, so we can just format.
                result = self._format_field(value, format_spec)
            else:
                if isinstance(value, (basestring, StyledString)):
                    # This is a simple styling of the value
                    value = style_class(value, style_fields[0])
                    result = self._format_field(value, format_spec)
                else:
                    # This might be a number which we're formatting
                    # or something else, like a DateTime with its
                    # own formatting. We cannot tell if the latter
                    # is the case from here, so we'll just ignore
                    # it as a problem and assume that the formatting
                    # is the standard one.
                    padding = ' '
                    sign = None  # pylint: disable=unused-variable
                    align = None
                    alternate_form = False  # pylint: disable=unused-variable
                    our_spec = format_spec
                    if len(our_spec) >= 1 and our_spec[0] in '<>=^':
                        align = our_spec[0]
                        our_spec = our_spec[1:]
                    elif len(our_spec) >= 2 and our_spec[1] in '<>=^':
                        align = our_spec[1]
                        padding = our_spec[0]
                        our_spec = our_spec[2:]
                    if len(our_spec) >= 1 and our_spec[0] in '+- ':
                        sign = our_spec[0]
                        our_spec = our_spec[1:]
                    if len(our_spec) >= 1 and our_spec[0] == '#':
                        alternate_form = True
                        our_spec = our_spec[1:]
                    if len(our_spec) >= 1 and our_spec[0] == '0':
                        if align is None:
                            align = '='
                            padding = '0'
                        our_spec = our_spec[1:]

                    # We have now decoded enough of the format specification to
                    # try to format the output as expected.
                    result = self._format_field(value, format_spec)
                    if align == '=':
                        # The '=' alignment means that the whole result is to be
                        # formatted (the padding is part of the result)
                        result = style_class(result, style_fields[0])
                    else:
                        left = ''
                        right = ''
                        if align is None or align in '>^':
                            # Left padding should not be styled
                            new_result = result.lstrip(padding)
                            # FIXME: We could strip too much if the padding was
                            # '+' or '-' or ' ' and the sign was forced. For
                            # now we ignore this.
                            left = padding * (len(result) - len(new_result))
                            result = new_result

                        if align is None or align in '<^':
                            # Right padding should not be styled
                            new_result = result.rstrip(padding)
                            # FIXME: We could strip too much if the padding was
                            # '+' or '-' or ' ' and the sign was forced. For
                            # now we ignore this.
                            right = padding * (len(result) - len(new_result))
                            result = new_result

                        result = left + style_class(result, style_fields[0]) + right
            if style_fields[1] != '':
                result = style_class(result, style=style_fields[1])

            return result

        return self._format_field(value, format_spec)

    def _format_field(self, value, format_spec):  # pylint: disable=no-self-use

        if not isinstance(value, StyledString):
            return format(value, format_spec)

        # Empty format specification is a pass-through.
        # With the regular formatter, it means str(value), but for us, we just
        # return the value.
        if format_spec == '':
            return value

        # We'll simplify the value now so that processing is easier.
        value._simplify()

        # The value formatted, however, needs to be given as a given
        # as a string, and then having the result styled. Unfortunately,
        # the 'format' function cannot handle anything but strings.
        # So we must instead process parts of this ourselves.
        if len(value.sequence) == 0:
            # Empty strings are simple.
            return StyledString(format('', format_spec), style=value.style)

        # We now know that at least one of the elements of the sequence is
        # a styled string.

        # There are a number of ways to attack this, but the one we're
        # going to use is to template the string. We will generate a
        # string that is as long as the original, and supply it to the
        # format function. Then we'll extract the template from the
        # result, and use that to give the styled string result.

        value_len = len(value)
        if value_len == 1:
            template = 'T'
        elif value_len == 2:
            template = 'ac'
        else:
            template = 'a' + ('b' * (value_len-2)) + 'c'

        templated = format(template, format_spec)
        index = templated.find(template)
        if index != -1:
            # The template was present in its entirety, so we just substitute
            # our value in.
            return templated[0:index] + value + templated[index+value_len:]

        if value_len == 1:
            # Strange to not have the template in, but may not be impossible.
            return templated

        elif value_len == 2:
            index = templated.find('a')
            if index != -1:
                return templated[0:index] + value[0] + templated[index+1:]

            index = templated.find('c')
            if index != -1:
                return templated[0:index] + value[1] + templated[index+1:]

            # No template present, so there is no substitution to perform.
            return templated

        # We might have just the start of the string. Or just the end.
        # I'm not sure if (with 'centre') we couldn't have just the middle,
        # but for now, I shall assume not.
        index = templated.find('a')
        if index != -1:
            # The string only had a left side of our value.
            left = templated[0:index]
            after_left = templated[index + 1:]
            right = after_left.lstrip('b')
            middle_length = len(after_left) - len(right)
            value_left = value[0:middle_length + 1]
            return left + value_left + right

        index = templated.find('c')
        if index != -1:
            # The string only had a right side of our value
            right = templated[index + 1:]
            before_right = templated[0:index-1]
            left = before_right.rstrip('b')
            middle_length = len(before_right) - len(left)
            value_right = value[-middle_length:]
            return left + value_right + right

        raise TypeError(("StyledString.format broke - templated string '%s' does " \
                         "not contain our template '%s'") % (templated, template))

    def convert_field(self, value, conversion):     # pylint: disable=no-self-use
        # do any conversion on the resulting object
        if conversion is None:
            return value
        elif conversion == 's':
            return str(value)
        elif conversion == 'r':
            return repr(value)
        elif conversion == 'a':
            try:
                return ascii(value)  # pylint: disable=undefined-variable
            except NameError:
                # Python 2 doesn't have ascii
                return str(value)
        raise ValueError("Unknown conversion specifier {0!s}".format(conversion))

    # returns an iterable that contains tuples of the form:
    # (literal_text, field_name, format_spec, conversion)
    # literal_text can be zero length
    # field_name can be None, in which case there's no
    #  object to format and output
    # if field_name is not None, it is looked up, formatted
    #  with format_spec and conversion and then used
    def parse(self, format_string):  # pylint: disable=no-self-use
        return formatter_parser(format_string)

    # given a field_name, find the object it references.
    #  field_name:   the field being looked up, e.g. "0.name"
    #                 or "lookup[3]"
    #  used_args:    a set of which args have been used
    #  args, kwargs: as passed in to vformat
    def get_field(self, field_name, args, kwargs):
        first, rest = formatter_field_name_split(field_name)

        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj[i]

        return obj, first


def show_missing_methods():
    # Report on how complete the implementation is.
    strobj = ""
    str_methods = []
    for method_name in dir(strobj):
        imp = getattr(strobj, method_name, None)
        if not callable(imp):
            # Not a method, so we can skip
            continue
        str_methods.append(method_name)

    ss_methods = []
    obj = object()
    ss = StyledString('')
    for method_name in dir(ss):
        imp = getattr(ss, method_name, None)
        base_imp = getattr(obj, method_name, None)
        if not callable(imp):
            # Not a method, so we can skip
            continue
        if base_imp is not None:
            if callable(base_imp):
                base_func = getattr(base_imp, '__func__', None)
                if base_func is not None:
                    if imp.__func__.__code__ == base_imp.__func__.__code__:
                        # This is the implementation from the base object, so we can skip it.
                        continue

        ss_methods.append(method_name)

    str_methods = set(str_methods)
    ss_methods = set(ss_methods)

    print("Unimplmented str methods:")
    for method_name in sorted(str_methods - ss_methods):

        # Skip any private methods
        if method_name.startswith('_') and not method_name.startswith('__'):
            continue

        print("  %s" % (method_name,))


if __name__ == '__main__':
    show_missing_methods()
