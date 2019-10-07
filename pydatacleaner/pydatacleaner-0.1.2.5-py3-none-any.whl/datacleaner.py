# file datacleaner/datacleaner.py

# Copyright (c) 2019 Kevin Crouse
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# @license: http://www.apache.org/licenses/LICENSE-2.0
# @author: Kevin Crouse (krcrouse@gmail.com)

"""datacleaner is the main class definition for the datacleaner package."""

import re
import math
import datetime
import dateutil.parser
import copy

intfloatre = re.compile(r'(-?([1-9]\d+|\d)?)(\.(\d+))?$')
expnotation = re.compile(r'-?(([1-9]\d+|\d)?(\.\d+)?)[eE]((-?)\d+)$')
blankspacere = re.compile(r'\s*$')
intdatere = re.compile(r'(\d\d\d\d)(\d\d)(\d\d)(\.0*)?$')
inteqfloatre = re.compile(r'\d+\.0*$')

alphanumbreakre = re.compile(r'(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])')

camelre = re.compile(r'([a-z])([A-Z])')
acronymre = re.compile(r'([A-Z]+)([A-Z]([a-r,t-z]|s(?:[a-zA-Z])))')
interiornum = re.compile(r'([a-zA-Z])([0-9])')
precedingnum = re.compile(r'([0-9])([a-zA-Z])')
underscorejoin = lambda m: m.group(1) + '_' + m.group(2)

COMMON_LATIN1_TRANSLITERATIONS = (
    ('\xe2\x80\x99', "'"),
    ('\xc3\xa9', 'e'),
    ('\xe2\x80\x90', '-'),
    ('\xe2\x80\x91', '-'),
    ('\xe2\x80\x92', '-'),
    ('\xe2\x80\x93', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x98', "'"),
    ('\xe2\x80\x9b', "'"),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9d', '"'),
    ('\xe2\x80\x9e', '"'),
    ('\xe2\x80\x9f', '"'),
    ('\xe2\x80\xa6', '...'),
    ('\xe2\x80\xb2', "'"),
    ('\xe2\x80\xb3', "'"),
    ('\xe2\x80\xb4', "'"),
    ('\xe2\x80\xb5', "'"),
    ('\xe2\x80\xb6', "'"),
    ('\xe2\x80\xb7', "'"),
    ('\xef\xbe\x8d', "'"),
    ('\xe2\x81\xba', "+"),
    ('\xe2\x81\xbb', "-"),
    ('\xe2\x81\xbc', "="),
    ('\xe2\x81\xbd', "("),
    ('\xe2\x81\xbe', ")"),
    ('\xef\x82\xa7', ','),
    # Blanks?
    ('\xe2\x96\xa1', ''),
    ('\xc2\xa0', ' '),
    ('\xa0', ' '),
    ('\xc2\xad', ''),
    ('\xcd\xbe', ''),
    ('\xc2', ''),
)


class DataCleaner():

    """DataCleaner is a class to clean and process raw data, originally to clean and process data read in from datasets that often included random, human-introduced errors. As released, it provides a general framework to clean data as well as subclasses that translate text into snake_case and/or CamelCase. Developers can extend the Data Cleaner by subclassing and setting class variables and/or by instantiating objects and overriding or setting the properties on those objects.
    """

    default_null_values = []
    default_translations = {}
    default_transliterations = []

    convert_numbers = True
    convert_dates = False
    nullable = True

    def __init__(self, *, null_values=False, translations=False, transliterations=False, data_type=None, valid_types=None, filter_parens=False, filter_colon=False, **kwargs):
        """
        Args:
            null_values (list): A list of values that should be converted to None if found in the input. Default is <class>.default_null_values.
            translations (dict): A mapping between literal values and the values they should be assigned to. Default is <class>.default_translations.
            transliterations (list(list)): A list of 2-element lists/tuples on which regexp substituions are applied. The first element is either a regexp or a string to apply to the value to be cleaned, and the second element is the replacement value. Default is <class>.default_transliterations.
            data_type (type): A required type that the output of clean will resolve to. clean() throws a TypeError if the value cannot be coerced into data_type. Default is None, which turns off the type-checking functionality.
            valid_types (list(type)): A list of types that the output of clean resolves down to. clean() throws a TypeError if the value is not one of the valid types. Default is None, which turns off the type-checking functionality.
            filter_parens (bool): Automatically eliminates parenthetical phrases contained within string values. So, if "Yes (I'm positive)" is passed into clean(), "Yes" will be returned.
            filter_colon (bool): Automatically eliminates dependent clauses separated by a colon within string values. So, if "Yes: This is a positive value" is passed into clean(), "Yes" will be returned.
            convert_numbers (bool): Automatically attempt to convert strings to numbers. Defaults to True.
            convert_dates (bool): Automatically attempt to convert strings to dates. Defaults to False.
            nullable (bool): Always allow None as an input and return None, regardless of other type expectations. Default to True.
        """

        self.data_type = data_type
        self.valid_types = valid_types

        if translations:
            self.translations = translations
        elif translations is None:
            self.translations = None
        else:
            self.translations = self.default_translations.copy()

        self._null_values = []
        if null_values:
            self.null_values = null_values
        elif null_values is not None:
            self.null_values = self.default_null_values.copy()


        #TODO: Should default_transliterations apply if there is also a transliteration parameter passed in? Because the base class has defualt_transliterations == [], there are not use cases for having both defaults and passing in separate.

        self._transliterations = []
        if transliterations:
            self.add_transliterations(transliterations)
        if self.default_transliterations and transliterations is not None:
            self.add_transliterations(self.default_transliterations)

        if filter_parens:
            self.add_transliterations([(r'\([^\)]+\)', ''),])

        if filter_colon:
            self.add_transliterations([(r'\s*\:.*', ''),])

        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise Exception("Unknown parameter " + key)
            varname = '_' + key
            setattr(self, key, val)

    @property
    def null_values(self):
        """ null_values property: indicates a list of values that should be considered null, and will return None when parsed """
        return(self._null_values)

    @null_values.setter
    def null_values(self, values):
        self._null_values = values

    def add_null_values(self, values):
        """ add a value or list of values to append to the null list """
        if type(values) is not list:
            values = [values]
        self.null_values.extend(values)

    @property
    def translations(self):
        """ translation property: indicates a dict mapping complete strings to what they should be translated to when encountered"""
        return(self._translations)

    @translations.setter
    def translations(self, transmap):
        self._translations = transmap
        if transmap is not None and type(self._translations) is not dict:
            raise Exception("Expect translations to be a dictionary")

    def add_translations(self, new_translations):
        self._translations.update(new_translations)

    @property
    def transliterations(self):
        """ transliterations property: indicates a list of tuples or lists in which character 1 is a character or regexp to what the characters should be replaced with."""
        return(self._transliterations)

    @transliterations.setter
    def transliterations(self, transliterations):
        if transliterations is not None and type(transliterations) is not list:
            raise TypeError("Expected list for transliterations")
        self._transliterations = transliterations

    def apply_transliterations(self, val):
        """ Apply all transliterations.

        This happens before type conversion, so while the development use cases focus on single letter substitutions, it could also be leveraged to manipulate strings prior to running the type converters. """
        if not self.transliterations:
            return(val)

        for re_, result_ in self.transliterations:
            val = re_.sub(result_, val)
        return(val)

    def add_transliterations(self, new_transliterations):
        """ provide a list of tuples of additional character translations. Note that order of precedence is preserved, and so chaining of transliterations can occur [('a', 'b'), ('b', 'c'), ] will result in 'a' becoming 'c' in the end """
        if self.transliterations is None:
            self.transliterations = []
        for ch, result_char in new_transliterations:
            self.transliterations.append((re.compile(ch), result_char,))


    def prepend_transliterations(self, new_transliterations):
        """ Inserts a list of transliterations at the front of the transliteration list, so they are processed before the other/default transliterations """
        if self.transliterations is None:
            self.transliterations = []
        # we need to reverse the array so the prepending works right
        nt = new_transliterations.copy()
        nt.reverse()
        for ch, result_char in nt:
            self.transliterations.insert(0, (re.compile(ch), result_char,))

    def add_transliteration_set(self, shorthand_set_name):
        """ adds a list of predefined sets of transliterations.  COMMON_LATIN1_TRANSLITERATIONS tries to account for things typically found in rich text formatting, like angled quotes and different lengths en-dash and em-dashes"""
        if shorthand_set_name == 'latin1':
            self.add_transliterations(COMMON_LATIN1_TRANSLITERATIONS)
        else:
            raise Exception("Unknown transliteration set '"+shorthand_set_name+"'" )


    def copy(self):
        """ Returns a copy of the object so that modifications to the returned object will not affect the source. """
        return(copy.deepcopy(self))


    def join(self, values):
        """ An abstract function that takes an array of values and joins them together based on the criteria of the subclass. This is designed primarily to allow for the easy transformation between datacleaner subclass format, such as if you have values in snake_case and want to return the CamelCase version. CamelCase.join(SnakeCase.tokenize(val)) """
        raise Exception("tokenize must be implemented in a subclass.")

    def tokenize(self, val):
        """ An abstract function that takes a value (potentially cleaned) and breaks it apart based on the criteria of the subclass. This is designed primarily to allow for the easy transformation between datacleaner subclass format, such as if you have values in snake_case and want to return the CamelCase version. CamelCase.join(SnakeCase.tokenize(val)) """
        raise Exception("tokenize must be implemented in a subclass.")

    def clean(self, val):
        """Process val and return a cleaned value based on object properties. Note the following order of operations of the clean function:

        1. Any null mappings are applied.
        2. Any transliterations are applied
        3. Attempts to convert strings to more precise types (numbers, dates, etc) are done.
        4. Any translations are applied, as this should happen after all otehr conversions.

            Args:
                val (scalar|list): The value to clean. If a list, recursively processes each element.
            Returns:
                the cleaned value or a list of cleaned values.
        """

        valtype = type(val)
        if valtype in (list, tuple):
            return([self.clean(elem) for elem in val])

        if val in self.null_values:
            return(None)
        # listing order of operations in the comments


        # 1. IF STRING, strip preceding and following whitespace, run any transliterations.
        # Trasliteration mapping happen before any conversions because most transliteration use cases are to strip or convert unicode letters, non-standard quotes or hyphens, etc, which most other fields will look for.
        if valtype is str:
            val = self.apply_transliterations(val.strip())

            # 2. Do type conversions
            # 2.a. If string is just whitespace ( and the string can be null ), return None
            # TODO: verify whether "" should be tranlsated to null when nullable is False - e.g., should "" raise an error? For conversions from CSV, for instance, this is likely to be true becuase we wouldn't otherwise be able to distinguish.  For conversions from inline matrices, this may be more nuanced because "" may be valid while None may be the result of an uninitialized variable that should not be null, and so this would be a form of error checking. At present, the first case is typical and the second case seems like a convenient side effect but isn't really matrixb's job, so we don't fail on it. PLUS, nullable gets checked later
            #REJECTED: if self.nullable and blankspacere.match(val):
            if blankspacere.match(val):
                val = None
            elif not self.data_type:
                # if self.data_type. we should not attempt to autoconvert strings based on regexps, because we will explicitly attempt to convert the stirng to the type after translations are conducted

                # 3.c. Convert dates (this is false for the default datacleaner, so if this is true, check it first - also because (yyyymmdd) should be converted to the date and not an int.
                if self.convert_dates:
                    val = self.convert_date(val)
                    valtype = type(val)
                    if valtype is not str:
                        # dates are unhashable, so if a conversion happened, return now. We do not allow translation of date objects.
                        return(val)

                if self.convert_numbers:
                    intfloat = intfloatre.match(val)
                    if intfloat and val != '-':
                        intnum,ignore,wholedecimal,decval = intfloat.groups()
                        if wholedecimal:
                            # if group 1, this is a float string
                            # however, is g2 is 0, it is something like 3.0, which we'll return as an integer
                            if int(decval) == 0:
                                val = int(intnum)
                                valtype = int
                            else:
                                val = float(val)
                                valtype = float
                        else:
                            # if match but not g1, this is an integer
                            val = int(val)
                            valtype = int
                    else:
                        match = expnotation.match(val)
                        if match and len(match.group(1)):
                            # match groups explained for 9.7e-5:
                            # (coefficient 9.7, coefficient whole num 9, coeifficient decimal with point '.7', exponent -5, exponent sign)
                            #why len(match.group(3))-1 > int(match.group(4))? 10^1 accounts for 1 digit, but group 3 includes the decimal point
                            if match.group(5) == '-' or (match.group(3) and len(match.group(3))-1 > int(match.group(4))):
                                val = float(val)
                                valtype = float
                            else:
                                 val = int(float(val))
                                 valtype = int

        # 2. make translation conversions, including null translations
        #TODO: verify intended logic
        #    This happens before strings are converted to other types.
        #    Reason:
        #            - About to separate out and return non-strings, and so translations need to happen before that.
        #            - If we waited until after string -> type conversion, we run the risk of
        #              unhashable types, like dates, being tested for translation. Consider
        #              a time when the user wants to make epoch start (1970-01-01) translate to None.
        #
        #    Negative side effects:
        #       - Programmer needs to be aware of when translated non-string values may actually be rendered as strings at this point, e.g. CSV when the importer interprets as string instead of int
        #       - Manipulations later in the processing may translate the string into something that should have been translated.
        #
        #    Possible remedy: test for translation multiple times, but this can be a problem if translations overlap.

        # NOTE: we only test for one translation, so translations cannot be chained.
        # If you want 'a' -> 'prelim' and 'b'  -> 'prelim' so 'prelim' -> 'final',
        # why not just make 'a','b',and 'prelim' all go to 'final' to begin with?

        if val in self._translations:
            val = self._translations[val]
            valtype = type(val)
        elif val in self.null_values:
            val = None
            valtype = type(None)

        # 3. validate that it is acceptable and return
        if self.valid_types and valtype not in self.valid_types:
            raise Exception("Expected a value of type [" + "; ".join(str(t) for t in self.valid_types) + "], but '"
                            + str(val) + "' is a " + str(valtype))

        if val is None:
            if self.nullable:
                return(None)
            raise Exception("Expected a non-null value")

        if self.data_type:
            if valtype is self.data_type:
                return(val)

            if type(self.data_type) is str:
                # special value. Note this is not checking whether the data_type must be a str type, which would be if self.data_type is str, NOT type(self.data_type) is str
                if self.data_type == 'maybeint':
                    if valtype in (str, int):
                        return(val)
                    raise TypeError ("Expecting a value that is either an int or a string, but received '"+str(val)+"', which is of type "+str(valtype))
                raise TypeError("User set data_type to '" + self.data_type + "', which is an unknown type to process")

            elif self.data_type is datetime.datetime:
                return(self.parse_datetime(val))
            elif self.data_type is datetime.date:
                return(self.parse_date(val))
            elif self.data_type is datetime.time:
                return(self.parse_time(val))

            raise TypeError("Expecting a value of type '" + str(self.data_type)+  "'")

        return(val)

    @staticmethod
    def parse_maybeint(val):
        """Takes in a scalar and returns a string or an integer, or None.

        Args:
            x: A scalar that likely represents a string or integer value, or None.
        Returns:
            None if x is None.
            int if x appears to represent an integer value OR is a string representing a float with ".0" as the decimal.
            str if x appears to represent a non-numeric string value.
        """
        valtype = type(val)
        if valtype is None or valtype is int:
            return(val)

        if valtype is float:
            if int(val) == val:
                return(int(val))

        if intre.match(val):
            return(int(val))
        return(str(val))


    @staticmethod
    def parse_boolean(x):
        """Takes in a scalar and returns the boolean value equivalent to it, or None.

        Args:
            x: A scalar that likely represents a boolean, or None.
        Returns:
            None if x is None.
            True if x appears to represent a true value.
            False if x appears to represent a false value.
        Raises:
            ValueError if x is an unknown type.
        """

        if x is None:
            return(None)

        valtype = type(x)
        if valtype is bool:
            return(x)

        if valtype is str:
            if x == '':
                return(None)
            x = x.lower()
            if x in ('1','t','true'):
                return True
            if x in ('0','f','false'):
                return False

        if t is int:
            return(x != 0)

        raise ValueError("Cannot parse indicated boolean value " + str(x))

    @classmethod
    def parse_time(cls, string):
        """ Takes a scalar object and returns a datetime.time object after delegating to parse_datetime. See parse_datetime for further details on parsible types, acceptable args, and exceptions raised.

        Returns:
            None if s is not true.
            datetime.time of the parsed value.
        """
        dt = cls.parse_datetime(string)
        if not dt:
            return(None)
        if type(dt) is datetime.time:
            return(dt)
        return(dt.time())


    @classmethod
    def parse_date(cls, s):
        """ Takes a scalar object and returns a datetime.date object after delegating to parse_datetime. See parse_datetime for further details on parsible types, acceptable args, and exceptions raised.

        Returns:
            None if s is not true.
            datetime.date of the parsed value.
        """
        dt = cls.parse_datetime(s)
        if not dt:
            return(None)
        if type(dt) is datetime.date:
            return(dt)
        return(dt.date())


    @staticmethod
    def parse_datetime(s):
        """ Takes a scalar object and returns a datetime object if possible (or None or throws an Exception if not parsible).

        Args:
            s: A scalar to parse into a datetime object to the degree that is possible. None is an allowed parameter, but will result in None being returned.
        Return:
            None if s is None or not true.
            datetime.date or datetime.time if s is already one of these formats.
            datetime.datetime if s is parsable.
        Raises:
            ValueError if the value is not none and is unparseable.
            TypeError if the type is not recognizable.
        """
        if not s:
            return(None)

        valtype = type(s)
        # if it is already a date, return
        if valtype in (datetime.date, datetime.datetime, datetime.time):
            return(s)

        if valtype is not str:
            # current function assumes that any integer/float values
            # are in iso format - 20200101 -> Jan 1, 2020
            if valtype in (int,float) and s > 10000000 and s <= 31000000:
                intdate = intdatere.match(str(s))
                if intdate:
                    return(datetime.datetime(int(intdate.group(1)),
                                             int(intdate.group(2)),
                                             int(intdate.group(3))))
                else:
                    raise TypeError("Do not know the type of the current value: " + str(valtype) + ", value = " + str(s))
            else:
                raise TypeError("Do not know the type of the current value: " + str(valtype) + ", value = " + str(s))

        try:
            return(dateutil.parser.parse(s))
        except ValueError as ve:
            # Sometimes excel generates weird float strings like '20100601.0'
            if inteqfloatre.match(s):
                return(dateutil.parser.parse(str(int(float(s)))))
            if alphanumbreakre.search(s):
                return(dateutil.parser.parse(alphanumbreakre.sub('-', s)))
            raise
