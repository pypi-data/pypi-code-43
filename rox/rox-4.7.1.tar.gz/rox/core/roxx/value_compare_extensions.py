import numbers
from distutils.version import LooseVersion

from rox.core.utils.type_utils import is_string


class ValueCompareExtensions:
    def __init__(self, parser):
        self.parser = parser

    def extend(self):
        self.parser.add_operator('lt', lt)
        self.parser.add_operator('lte', lte)
        self.parser.add_operator('gt', gt)
        self.parser.add_operator('gte', gte)
        self.parser.add_operator('semverNe', semver_ne)
        self.parser.add_operator('semverEq', semver_eq)
        self.parser.add_operator('semverLt', semver_lt)
        self.parser.add_operator('semverLte', semver_lte)
        self.parser.add_operator('semverGt', semver_gt)
        self.parser.add_operator('semverGte', semver_gte)


def lt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not isinstance(op1, numbers.Number) or not isinstance(op2, numbers.Number):
        stack.push(False)
    else:
        stack.push(op1 < op2)


def lte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not isinstance(op1, numbers.Number) or not isinstance(op2, numbers.Number):
        stack.push(False)
    else:
        stack.push(op1 <= op2)


def gt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not isinstance(op1, numbers.Number) or not isinstance(op2, numbers.Number):
        stack.push(False)
    else:
        stack.push(op1 > op2)


def gte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not isinstance(op1, numbers.Number) or not isinstance(op2, numbers.Number):
        stack.push(False)
    else:
        stack.push(op1 >= op2)


def semver_ne(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) != LooseVersion(op2))


def semver_eq(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) == LooseVersion(op2))


def semver_lt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) < LooseVersion(op2))


def semver_lte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) <= LooseVersion(op2))


def semver_gt(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) > LooseVersion(op2))


def semver_gte(parser, stack, context):
    op1 = stack.pop()
    op2 = stack.pop()
    if not is_string(op1) or not is_string(op2):
        stack.push(False)
    else:
        stack.push(LooseVersion(op1) >= LooseVersion(op2))
