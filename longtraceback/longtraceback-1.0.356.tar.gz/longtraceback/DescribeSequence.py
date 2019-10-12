#!/usr/bin/env python
"""
Handle repetitions in a sequence, to describe how the sequence changes.
"""

import decimal
import fractions
import math
import numbers

import collections
Constant = collections.namedtuple('Constant', 'value name symbol')


# Ensure that we can check basestring on Python 2 and 3.
try:
    basestring
except NameError:
    basestring = str  # pylint: disable=redefined-builtin


class DescribeOptions(object):

    def __init__(self):

        # Show symbols for constants
        self.constant_symbols = False


options = DescribeOptions()


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
    Determine whether two numbers are close to one another.
    """
    try:
        largest_magnitude = max(abs(a), abs(b))
        try:
            epsilon = max(rel_tol * largest_magnitude, abs_tol)
        except TypeError:
            # The calculation has failed, probably because largest_magnitude cannot be multiplied.
            if isinstance(largest_magnitude, decimal.Decimal):
                rel_tol = decimal.Decimal(rel_tol)
                epsilon = max(rel_tol * largest_magnitude, abs_tol)
            else:
                # Do not know the type, so say these are not close
                return False

        try:
            return abs(a - b) <= epsilon
        except TypeError:
            # Applying the a-b is probably unhappy; we may need to convert some types
            if isinstance(a, decimal.Decimal) or isinstance(b, decimal.Decimal):
                a = decimal.Decimal(a)
                b = decimal.Decimal(b)
                return abs(a - b) <= epsilon

            # Not sure about the types - we'll play safe and say they're not close
            return False

    except (TypeError, ValueError, ArithmeticError):
        return False


def isnumber(value):
    """
    Determine if the value given is like a number.
    """
    return isinstance(value, numbers.Number)


def isinteger(value, exact=True):
    """
    Determine if the value given is an integer value.
    """
    if isinstance(value, numbers.Integral):
        return True
    if isinstance(value, numbers.Real):
        if isinstance(value, float):
            if value.is_integer():
                return True
        if exact:
            return value - int(value) == 0

        return isclose(value, round(value, 0))

    return False


def sequenceproperty(func):
    """
    Mark this function as a 'sequence property'.

    Sequence properties will cache their results, and are flagged as available for returning as part of the
    determination of a sequence.
    """
    def wrapper(self, *args, **kwargs):
        cache = getattr(self.desc, "%s__cache" % (func.__name__), None)
        if cache is None:
            cache = {}
            setattr(self.desc, "%s__cache" % (func.__name__), cache)
        # FIXME: These key elements probably ought to be a tuple, rather than a
        #        concatenated string.
        key = "#~#".join(str(arg) for arg in args)
        if kwargs:
            key += '//+//' + "#~#".join("%s{[]}%s" % (kw, arg) for kw, arg in kwargs.items())
        if key in cache:
            return cache[key]
        cache[key] = func(self, *args, **kwargs)
        return cache[key]

    wrapper.sequenceproperty = True
    return wrapper


class Sequence(object):
    constant_fields = None
    constant_derivations = None

    def __init__(self, desc):
        self.desc = desc
        self.sequence = desc.sequence
        # use the Sequence class object as a marker that we've not got anything yet
        self.result = Sequence

    def match(self):
        if self.result is Sequence:
            result = self._match()
            self.result = result
        return self.result

    def check_type(self, types):  # pylint: disable=unused-argument,no-self-use
        return False

    def _match(self):  # pylint: disable=no-self-use
        return None

    def get(self, name):
        return self.desc.get_property(name)

    def __str__(self):
        return "%r" % (self.sequence,)


class SequenceTruncated(Sequence):

    def check_type(self, types):  # pylint: disable=unused-argument
        return len(self.sequence) > self.desc.max_items

    def _match(self):
        first = self.sequence[:self.desc.max_items_first]
        last = self.sequence[-self.desc.max_items_last:]
        omitted = len(self.sequence) - self.desc.max_items_first - self.desc.max_items_last
        return {
            'name': 'truncated',
            'first_items': first,
            'last_items': last,
            'omitted': omitted
        }

    def __str__(self):
        parts = ['[']

        first = True
        for item in self.result['first_items']:
            if not first:
                parts.append(', ')
            first = False
            parts.append(repr(item))

        parts.append(' ... %s omitted ... ' % (self.result['omitted'],))

        first = True
        for item in self.result['last_items']:
            if not first:
                parts.append(', ')
            first = False
            parts.append(repr(item))

        parts.append(']')
        return "".join(parts)


class SequenceFallback(Sequence):

    def check_type(self, types):  # pylint: disable=unused-argument,no-self-use
        return True

    def _match(self):  # pylint: disable=no-self-use
        return {
            'name': 'unknown'
        }

    def __str__(self):
        return "%r" % (self.sequence,)


class SequenceShort(Sequence):

    def check_type(self, types):  # pylint: disable=unused-argument
        return len(self.sequence) < 3

    def _match(self):  # pylint: disable=no-self-use
        return {
            'name': 'too-short'
        }

    def __str__(self):
        return "%r" % (self.sequence,)


class SequenceConstant(Sequence):
    constant_fields = ('value',)

    def check_type(self, types):  # pylint: disable=unused-argument,no-self-use
        return True

    def _match(self):
        first = self.sequence[0]
        if all(first is value or
               first == value for value in self.sequence):
            return {
                'name': 'constant',
                'value': first
            }

        return None

    def __str__(self):
        value = self.result['value']
        if isnumber(value):
            value_str = str(value)
        else:
            value_str = repr(value)
        return "%s %s" % (self.result['name'], value_str)


class SequencePattern(Sequence):
    max_length = 5

    def check_type(self, types):
        return True

    def _match(self):
        for pattern_len in range(2, self.max_length+1):
            if len(self.sequence) < pattern_len * 2:
                break

            pattern = self.sequence[0:pattern_len]
            match = True
            for i, v in enumerate(self.sequence[pattern_len:]):
                if v != pattern[i % pattern_len]:
                    match = False
                    break

            if match:
                return {
                    'name': 'pattern',
                    'length': pattern_len,
                    'value': pattern,
                    'iterations': int(len(self.sequence) / pattern_len),
                    'leftover': len(self.sequence) % pattern_len,
                }

        return None

    def __str__(self):
        value = self.result['value']
        pattern_len = self.result['length']
        if pattern_len == 2:
            label = 'alternating'
        else:
            label = 'repeating'
        return "%s: %r (%s times)" % (label, value, self.result['iterations'])


class SequenceConstantNumberChange(Sequence):
    constant_fields = ('by',)
    constant_derivations = {'by': ('first', 'last')}

    def check_type(self, types):
        if len(types) == 1 and isnumber(self.sequence[0]):
            return True
        if all(typ in (int, float, decimal.Decimal, fractions.Fraction) for typ in types):
            return True
        return False

    @sequenceproperty
    def deltas(self):
        delta_list = [self.sequence[i + 1] - self.sequence[i] for i in range(len(self.sequence) - 1)]
        return delta_list

    def _match(self):
        deltas = self.get('deltas')

        compare = lambda a, b: a == b
        if not all(isinteger(seq) for seq in self.sequence):
            compare = isclose

        if all(compare(deltas[0], delta) for delta in deltas):
            # Every delta is the same
            if deltas[0] > 0:
                direction = 'incrementing'
            else:
                direction = 'decrementing'

            return {
                'name': direction,
                'by': deltas[0],
                'first': self.sequence[0],
                'last': self.sequence[-1]
            }

        return None

    def __str__(self):
        if self.result['by'] in (1, -1):
            return "%s %s .. %s" % (self.result['name'],
                                    self.result['first'],
                                    self.result['last'])
        else:
            # Round decimals if we can, to avoid rounding issues in Python 3.4
            delta = self.result['by']
            if isnumber(delta):
                delta = abs(delta)
                if not isinteger(delta):
                    if isinstance(delta, fractions.Fraction):
                        pass
                    else:
                        delta = '%.8f' % (delta,)
                        delta = delta.rstrip('0')
                        if delta.endswith('.'):
                            delta = delta[:-1]
            return "%s %s .. %s by %s" % (self.result['name'],
                                          self.result['first'],
                                          self.result['last'],
                                          delta)


class SequencePowers(Sequence):

    def check_type(self, types):
        return len(types) == 1 and \
               isnumber(self.sequence[0]) and \
               self.sequence[0] > 0

    @sequenceproperty
    def logs(self):
        return [math.log(value) if value > 0 else None for value in self.sequence]

    def _match(self):
        if any(value <= 0 for value in self.sequence):
            return None

        logs = self.get('logs')
        log_deltas = [logs[i + 1] - logs[i] for i in range(len(logs) - 1)]

        if all(isclose(log_deltas[0], delta) for delta in log_deltas):
            # Every delta of the logs is the same
            base = math.exp(abs(log_deltas[0]))
            if isclose(base, round(base, 1)):
                base = int(round(base, 1))
            name = 'powers of %s' % (base,)
            direction = math.copysign(1.0, log_deltas[0])
            first = self.sequence[0]
            last = self.sequence[-1]
            if direction > 0:
                direction_name = 'ascending'
                if first == 1:
                    first_power = 0
                    multiplier = 1
                else:
                    # We aren't starting at 1, so see if we're instead starting at a power
                    first_power = math.log(first) / math.log(base)
                    if isclose(first_power, round(first_power, 1)):
                        multiplier = 1
                        first_power = int(round(first_power, 1))
                    else:
                        multiplier = first
                        first_power = 0
                last_power = math.log(last / multiplier) / math.log(base)
            else:
                direction_name = 'descending'
                if last == 1:
                    last_power = 0
                    multiplier = 1
                else:
                    # We aren't starting at 1, so see if we're instead starting at a power
                    last_power = math.log(last) / math.log(base)
                    if isclose(last_power, round(last_power, 1)):
                        multiplier = 1
                        last_power = int(round(last_power, 1))
                    else:
                        multiplier = last
                        last_power = 0
                first_power = math.log(first / multiplier) / math.log(base)

            if isclose(first, round(first, 1)):
                first = int(round(first, 1))
            if isclose(last, round(last, 1)):
                last = int(round(last, 1))
            if isclose(first_power, round(first_power, 1)):
                first_power = int(round(first_power, 1))
            if isclose(last_power, round(last_power, 1)):
                last_power = int(round(last_power, 1))

            return {
                'name': name,
                'direction': direction,
                'direction_name': direction_name,
                'base': base,
                'multiplier': multiplier,
                'first_power': first_power,
                'last_power': last_power,
                'first': first,
                'last': last
            }

        return None

    def __str__(self):
        first_calc = "%s^%s" % (self.result['base'],
                                self.result['first_power'])
        last_calc = "%s^%s" % (self.result['base'],
                               self.result['last_power'])
        if self.result['multiplier'] != 1:
            first_calc = "%s * %s" % (self.result['multiplier'], first_calc)
            last_calc = "%s * %s" % (self.result['multiplier'], last_calc)
        name = self.result['name']
        if self.result['multiplier'] != 1:
            name = "%s * %s" % (name, self.result['multiplier'])
        if self.result['direction'] < 0:
            name = "%s descending" % (name,)
        return "%s: %s (%s) .. %s (%s)" % (name,
                                           self.result['first'], first_calc,
                                           self.result['last'], last_calc)


class SequenceStringCharacterIncrement(Sequence):

    def check_type(self, types):
        return len(types) == 1 and isinstance(self.sequence[0], basestring)

    @sequenceproperty
    def string_corpus(self):
        if all(i.isdigit() for i in self.sequence):
            return 'digits'
        if all(i.isalpha() for i in self.sequence):
            return 'alphabetic'
        if all(i != '' and i.translate(None, '0123456789abcdefABCDEF') == '' for i in self.sequence):
            return 'hex-digits'
        if all(i.isalphanum() for i in self.sequence):
            return 'alphanumeric'

        return 'unknown'

    def _match(self):
        if any(len(i) != len(self.sequence[0]) for i in self.sequence):
            return None

        corpus = self.get('string_corpus')
        if corpus != 'alphabetic':
            return None

        # We only handle the last letter changing for now
        first_prefix = self.sequence[0][:-1]
        if any(i[:-1] != first_prefix for i in self.sequence):
            return None

        deltas = [ord(self.sequence[i + 1][-1]) - ord(self.sequence[i][-1]) for i in range(len(self.sequence)- 1)]

        if all(deltas[0] == delta for delta in deltas):
            # Every delta is the same
            if deltas[0] > 0:
                direction = 'incrementing'
            else:
                direction = 'decrementing'

            return {
                'name': 'alphabetic %s' % (direction,),
                'direction': direction,
                'by': deltas[0],
                'first': self.sequence[0],
                'last': self.sequence[-1]
            }

        return None

    def __str__(self):
        sequence = "%s: '%s' .. '%s'" % (self.result['name'],
                                         self.result['first'],
                                         self.result['last'])
        if self.result['by'] not in (1, -1):
            sequence += " by %s characters" % (abs(self.result['by']),)

        return sequence


class SequenceSpecialisation(Sequence):
    """
    Specialise the calculated values from sequences.

    A sequence specialisation is able to convert the match values from an existing sequence
    to give a more succinct (or specific) definition of the matched sequence.
    """

    def __init__(self, sequence, matchdata):
        """
        Create a new sequence specialisation for a given sequence value.
        """
        super(SequenceSpecialisation, self).__init__(sequence)
        self.sequence = sequence
        self.matchdata = matchdata
        self.result = Sequence

    def check_sequence(self):  # pylint: disable=no-self-use
        return False


class DerivedValue(object):

    def __init__(self, value):
        self.value = value
        self.derived = None
        self.name = None
        self.symbol = None
        self.multiplier = None
        self.divisor = None

    def __str__(self):
        if self.derived:
            return self.derived

        if self.symbol and options.constant_symbols:
            s = self.symbol
            if self.multiplier:
                s = '%s%s' % (self.multiplier, s)
        else:
            s = self.name or ""
            if self.multiplier:
                s = '%s*%s' % (self.multiplier, s)

        if self.divisor:
            s = '%s/%s' % (s, self.divisor)

        self.derived = s
        return s

    def __repr__(self):
        return str(self)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __long__(self):
        return float(self.value)


def constant_factorisation(value, constant):
    """
    Factorise a value using a constant.

    @return: Returns a DerivedValue using a constant to factorise the value,
             or returns None if there is no simple factorisation.
    """
    if not isnumber(value):
        return None
    if value == 0:
        return None

    dv = DerivedValue(value)
    dv.name = constant.name
    dv.symbol = constant.symbol
    if isclose(value, constant.value):
        return dv

    constant_v = constant.value
    if isinstance(value, decimal.Decimal):
        constant_v = decimal.Decimal(constant_v)

    divisor = constant_v / value

    if divisor > 1:
        if not isclose(divisor, round(divisor, 0)):
            # If it's not close to being divided by an integer, we won't factorise
            return None

        dv.divisor = int(round(divisor, 0))
    else:
        multiplier = value / constant_v
        if not isclose(multiplier, round(multiplier, 0)):
            # If it's not close to being multiplied by an integer, skip this specialisation
            return None

        dv.multiplier = int(round(multiplier, 0))

    return dv


class SequenceSpecialisationConstant(SequenceSpecialisation):

    constants = (Constant(math.pi, 'pi', u'\u03C0'),
                 Constant(math.e, 'e', u'\u212F'))

    def check_sequence(self):
        return bool(self.sequence.constant_fields)

    def _match(self):
        for field in self.sequence.constant_fields:
            value = self.matchdata.get(field, None)
            if value is None:
                continue

            for constant in self.constants:
                value_replacement = constant_factorisation(value, constant)
                if value_replacement is None:
                    continue

                self.matchdata[field] = value_replacement

                # Perform replacements on any related fields
                if self.sequence.constant_derivations:
                    derived_fields = self.sequence.constant_derivations.get(field, None)
                    new_constant = Constant(value, value_replacement, None)

                    for derived_field in derived_fields:
                        value_replacement = constant_factorisation(self.matchdata[derived_field], new_constant)
                        if value_replacement is not None:
                            self.matchdata[derived_field] = value_replacement

        return self.matchdata

    def __str__(self):
        return str(self.sequence)


class DescribeSequence(object):
    recogniser_classes = [
        SequenceShort,
        SequenceConstant,
        SequencePattern,
        SequenceConstantNumberChange,
        SequencePowers,
        SequenceStringCharacterIncrement,
        SequenceTruncated,
        SequenceFallback
    ]
    specialisation_classes = [
        SequenceSpecialisationConstant
    ]

    max_items = 10
    max_items_first = 5
    max_items_last = 5

    def __init__(self, sequence=None):
        self.sequence = sequence or []
        self.properties = {}
        if sequence is not None:
            self.sequence = sequence[:]
        self.recognisers = []
        self._recogniser = None

    def __add__(self, other):
        newdesc = DescribeSequence(self.sequence)
        newdesc.sequence.append(other)
        return newdesc

    def __iadd__(self, other):
        self._recogniser = None
        self.properties = {}
        self.sequence.append(other)
        return self

    def __str__(self):
        return str(self.recogniser)

    def get_property(self, name):
        if not self.properties:
            for recogniser in self.recognisers:
                for rname in dir(recogniser):
                    if not rname.startswith('_'):
                        class_func = getattr(type(recogniser), rname, None)
                        if class_func and \
                           not isinstance(class_func, property) and \
                           getattr(class_func, 'sequenceproperty', False):
                            func = getattr(recogniser, rname, None)
                            if func is not None:
                                self.properties[rname] = func

        if name in self.properties:
            return self.properties[name]()
        return None

    @property
    def recogniser(self):
        if self._recogniser is not None:
            return self._recogniser

        # Check whether the types are the same
        sequence_types = set(type(item) for item in self.sequence)

        self.recognisers = [recogniser(self) for recogniser in self.recogniser_classes]
        self.recognisers = [recogniser for recogniser in self.recognisers if recogniser.check_type(sequence_types)]
        for recogniser in self.recognisers:
            if recogniser.match():
                self._recogniser = recogniser
                break

        # Check the specialisations from the recognisers
        specialisations = [specialisation(recogniser, recogniser.match())
                           for specialisation in self.specialisation_classes]
        specialisations = [specialisation for specialisation in specialisations if specialisation.check_sequence()]
        for specialisation in specialisations:
            if specialisation.match():
                self._recogniser = specialisation
                break

        return self._recogniser

    def describe(self):
        """
        Given a list of values, describe the sequence that they follow.
        """
        recogniser = self.recogniser
        if recogniser:
            return str(recogniser)

        return repr(self.sequence)
