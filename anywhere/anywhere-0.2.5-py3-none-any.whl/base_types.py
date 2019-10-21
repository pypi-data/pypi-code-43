# -*- coding:utf-8 -*-
"""
Classes serving as a common representation of where queries.

All new formats or third-party libraries support should be implemented
by working with these classes (Operator, Primitive, Condition).

Third-party implementation means:
 1. Serializing them to desired format (protobuf binary, SQL query).
 2. Loading them from desired format (protobuf binary, graphql query).
"""
import enum
import typing
from dataclasses import dataclass


class Operator(enum.Enum):
    """
    Logical operators available in where queries.
    """
    AND = 'AND'
    OR = 'OR'

    def __repr__(self):
        return f'Operator.{self.value}'


@dataclass
class Primitive:
    """
    Primitive is a leaf value in grapqhql where query argument. It consists of field name, operator, and value.

    For example:

    ```
    { title: "Pinokio" }
    ```

    `eq` operator is used by default. Different operators might are used by adding postfix to field name:

    ```
    { title__neq: "Pinokio" }
    ```
    """
    field: str
    op: str  # pylint: disable=invalid-name
    value: typing.Union[str, float, int, bool]

    def __repr__(self):
        return f'Primitive(field={repr(self.field)}, op={repr(self.op)}, value={repr(self.value)})'

    def __str__(self):
        return f'{self.field} {self.op} {repr(self.value)}'

    def __eq__(self, other):
        if not isinstance(other, Primitive):
            return NotImplemented

        return (
            self.field == other.field and
            self.op == other.op and
            self.value == other.value
        )


@dataclass
class Condition:
    """
    Logical conjunction of Primitives or other Operators.

    For example:

    ```
    { OR: [{ title: "Pinokio"}, { title: "Little Prince"}] }
    ```
    """
    op: Operator  # pylint: disable=invalid-name
    values: typing.Iterable[typing.Union[Primitive, 'Condition']]

    def __repr__(self):
        return f'Condition(op={repr(self.op)}, values={repr(self.values)})'

    def __str__(self):
        operator = ' & ' if self.op == Operator.AND else ' | '

        return '(' + (operator.join([str(v) for v in self.values])) + ')'

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return NotImplemented

        return self.op == other.op and self.values == other.values
