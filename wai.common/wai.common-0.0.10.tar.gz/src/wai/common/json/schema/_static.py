"""
Schema for validating JSON which require no dynamic parameters.
"""
from .constants import *

# Trivial schemas for passing and failing
TRIVIALLY_SUCCEED_SCHEMA = True
TRIVIALLY_FAIL_SCHEMA = False

# The schema for validating only the value null
NULL_SCHEMA = {TYPE_KEYWORD: NULL_TYPE}

# The schema for validating boolean values
BOOL_SCHEMA = {TYPE_KEYWORD: BOOL_TYPE}

# The schema for validating an integer
INT_SCHEMA = {TYPE_KEYWORD: INTEGER_TYPE}

# The schema for validating a float
FLOAT_SCHEMA = {TYPE_KEYWORD: NUMBER_TYPE}

# The schema for validating a plain string
STRING_SCHEMA = {TYPE_KEYWORD: STRING_TYPE}

# Schema for validating a purely-positive integer
POSITIVE_INTEGER_SCHEMA = {TYPE_KEYWORD: INTEGER_TYPE, MINIMUM_KEYWORD: 1}

# Schema for validating a non-negative integer
NON_NEGATIVE_INTEGER_SCHEMA = {TYPE_KEYWORD: INTEGER_TYPE, MINIMUM_KEYWORD: 0}

# Schema for validating a purely-negative integer
NEGATIVE_INTEGER_SCHEMA = {TYPE_KEYWORD: INTEGER_TYPE, MAXIMUM_KEYWORD: -1}

# Schema for validating a non-positive integer
NON_POSITIVE_INTEGER_SCHEMA = {TYPE_KEYWORD: INTEGER_TYPE, MAXIMUM_KEYWORD: 0}
