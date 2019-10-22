import enum
from typing import List, Union
import warnings

__all__ = [
    'tokenize',
    'validate_token_stream',
    'build_trees',
    'flatten_tree',
    'build_indexed_tree_table'
]


class TokenType(enum.Enum):
    NODE_BEGIN = 'node_begin'
    LITERAL = 'literal'
    NODE_END = 'node_end'

    def __repr__(self):
        return self.name


class Tree(object):

    class Leaf(object):

        def __init__(self, index, contents):
            self.index = index
            self.contents = contents

        def __repr__(self):
            return repr(self.contents)

    def __init__(self, index, identifier, children=None):
        self.index = index
        self.identifier = identifier
        self.children = children or []

    def __repr__(self):
        assert self.children, 'Node must have at least one child.'
        children_repr = ', '.join(repr(child) for child in self.children)
        return '{identifier}({children})'.format(identifier=self.identifier,
                                                 children=children_repr)


def tokenize(flat_string: str) -> List[Union[str, TokenType]]:
    """converts the input grammar to a token stream."""

    result = []
    accum = ''
    active_quote = False

    for character in flat_string:
        if active_quote:
            if character == active_quote:
                result.extend([TokenType.LITERAL, accum])
                accum = ''
                active_quote = False
            else:
                accum += character
        elif character.isspace() or character == ',':
            continue
        elif character in '\'"':
            active_quote = character
        elif character == '(':
            result.extend([TokenType.NODE_BEGIN, accum])
            accum = ''
        elif character == ')':
            # NB accum is ignored here
            result.append(TokenType.NODE_END)
            accum = ''
        else:
            accum += character

    assert not active_quote, 'Unterminated literal at end of string.'
    if accum:
        warnings.warn('Some input was not tokenized.')

    return result


def validate_token_stream(token_stream: List[Union[str, TokenType]]):
    depth = 0
    last_token = []
    token_iter = iter(token_stream)
    while True:
        try:
            token = next(token_iter)
        except StopIteration:
            break

        try:
            if token is TokenType.NODE_BEGIN:
                depth += 1
                identifier = next(token_iter)
                assert isinstance(identifier, str), 'Expected identifier; got token.'
                assert identifier.isalpha(), 'Identifier has an invalid character'
            elif token is TokenType.LITERAL:
                contents = next(token_iter)
                assert isinstance(contents, str), 'Expected literal contents; got token marker.'
            elif token is TokenType.NODE_END:
                depth -= 1
                assert last_token is not TokenType.NODE_BEGIN, \
                    'Empty nodes are not permitted.'
            elif isinstance(token, str):
                raise AssertionError('Expected token; got a string.')
            else:
                raise AssertionError('Got an unexpected item.')
        except StopIteration:
            raise AssertionError('Stream ended too early.')

        last_token = token

    assert depth == 0, 'Depth was not zero at stream end.'


def build_trees(token_stream: List[Union[str, TokenType]]) -> List[Tree]:
    """Convert a token stream to a proper tree structure."""

    index = 0
    stack = []
    results = []
    token_iter = iter(token_stream)
    while True:
        try:
            token = next(token_iter)

            if token is TokenType.NODE_BEGIN:
                identifier = next(token_iter)
                new_node = Tree(index, identifier)
                index += 1
                stack.append(new_node)

            elif token is TokenType.LITERAL:
                contents = next(token_iter)
                leaf = Tree.Leaf(index, contents)
                index += 1
                if not stack:
                    return leaf
                else:
                    stack[-1].children.append(leaf)

            elif token is TokenType.NODE_END:
                top_node = stack.pop()
                if not stack:
                    results.append(top_node)
                else:
                    stack[-1].children.append(top_node)

        except StopIteration:
            break

    if stack:
        raise RuntimeError('Stream ended before a complete tree could be built.')

    return results


def flatten_tree(tree: Tree) -> List[str]:
    """Flatten a single tree down to a row representation."""

    stack = [tree]
    lines = []

    while stack:
        node = stack.pop()

        if isinstance(node, Tree.Leaf):
            lines.append('{leaf.index}, \'terminal\', {leaf.contents!r}'.format(leaf=node))
        elif isinstance(node, Tree):
            children_indices = ', '.join(str(subnode.index) for subnode in node.children)
            lines.append('{node.index}, \'node\', {node.identifier!r}, {children}'.format(
                node=node, children=children_indices))
            stack.extend(reversed(node.children))

    return lines


def build_indexed_tree_table(list_of_trees: List[Tree], separator='===') -> str:
    """Combine a list of trees into a full"indexed tree table."""

    indices = []
    lines = []
    for tree in list_of_trees:
        indices.append(str(tree.index))
        lines.extend(flatten_tree(tree))
        if separator:
            lines.append(separator)

    lines = [', '.join(indices), separator] + lines

    return '\n'.join(lines) + '\n'
