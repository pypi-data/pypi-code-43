"""tregex is a package for handling regular expressions and other string-related tasks more smoothly.

For usage examples, see https://github.com/tobiasli/tregex
"""
from tregex.tregex import TregexCompiled
from tregex.tregex import to_tuple, to_dict, to_object
from tregex.tregex import similarity, find, find_best, find_scores

__all__ = ['TregexCompiled', 'to_tuple', 'to_dict', 'to_object', 'similarity', 'find', 'find_best', 'find_scores']
