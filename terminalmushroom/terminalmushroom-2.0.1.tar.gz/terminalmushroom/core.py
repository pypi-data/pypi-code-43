import enum
from typing import List, Union, Dict, Tuple
import warnings
from . import treetable_pb2

__all__ = [
    'tokenize',
    'validate_token_stream',
    'build_trees_from_token_stream',
    'build_trees_from_table',
    'traverse_tree',
    'serialize_tree_table',
    'deserialize_tree_table'
]


class TokenType(enum.Enum):
    NODE_BEGIN = 'node_begin'
    LITERAL = 'literal'
    NODE_END = 'node_end'

    def __repr__(self):
        return self.name


class Tree(object):

    class Leaf(object):

        def __init__(self, key, contents):
            self.key = key
            self.contents = contents

        def flatten(self):
            return repr(self.contents)

        def __repr__(self):
            return self.flatten()

    def __init__(self, key, identifier, children=None):
        self.key = key
        self.identifier = identifier
        self.children = children or []

    def flatten(self):
        assert self.children, 'Node must have at least one child.'
        children_repr = ', '.join(child.flatten() for child in self.children)
        return '{identifier}({children})'.format(identifier=self.identifier,
                                                 children=children_repr)

    def __repr__(self):
        return self.flatten()


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


def build_trees_from_token_stream(token_stream: List[Union[str, TokenType]]) -> List[Tree]:
    """Convert a token stream to a proper tree structure."""

    key = 0
    stack = []
    results = []
    token_iter = iter(token_stream)
    while True:
        try:
            token = next(token_iter)

            if token is TokenType.NODE_BEGIN:
                identifier = next(token_iter)
                new_node = Tree(key, identifier)
                key += 1
                stack.append(new_node)

            elif token is TokenType.LITERAL:
                contents = next(token_iter)
                leaf = Tree.Leaf(key, contents)
                key += 1
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


def build_trees_from_table(index: List[int], table: Dict[int, Tuple[str, List[int]]]) \
        -> List[Tree]:

    def _build_tree(node_key) -> Union[Tree, Tree.Leaf]:
        identifier_or_contents, children = table[node_key]

        if children:
            # Nonterminal node
            return Tree(
                node_key,
                identifier_or_contents,
                [_build_tree(child_key) for child_key in children])

        else:
            # Terminal leaf
            return Tree.Leaf(node_key, identifier_or_contents)

    result: List[Tree] = []

    for key in index:
        tree = _build_tree(key)
        assert isinstance(tree, Tree)
        result.append(tree)

    return result


def traverse_tree(tree: Tree) -> List[Tuple[int, str, List[int]]]:
    """Flatten a single tree down to a row representation."""

    stack = [tree]
    lines = []

    while stack:
        node = stack.pop()

        if isinstance(node, Tree.Leaf):
            lines.append((node.key, node.contents, []))
        elif isinstance(node, Tree):
            lines.append((node.key, node.identifier, node.children))
            stack.extend(reversed(node.children))

    return lines


def serialize_tree_table(list_of_trees: List[Tree]) -> bytes:

    table = treetable_pb2.Table()
    for tree in list_of_trees:
        table.index.append(tree.key)

        flattened_tree = traverse_tree(tree)
        for key, identifier_or_contents, children in flattened_tree:
            node = table.nodes.get_or_create(key)
            node.identifier_or_contents = identifier_or_contents
            node.children.extend(child.key for child in children)

    return table.SerializeToString()


def deserialize_tree_table(serialized: bytes) \
        -> Tuple[List[int], Dict[int, Tuple[str, List[int]]]]:

    table = treetable_pb2.Table.FromString(serialized)
    index: List[int] = list(table.index)
    nodes: Dict[int, Tuple[str, List[int]]] = dict()

    for key, node in table.nodes.items():
        nodes[key] = (node.identifier_or_contents, list(node.children))

    return index, nodes


