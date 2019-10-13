from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Tuple


class Statement:
    def to_line(self) -> str:
        ''' Returns the line that can be parsed to this statement. '''
        return str(self)


class Storage:
    parsing_functions = {}


def parse_function(f: Callable) -> Callable:
    _, token = f.__name__.split('_', maxsplit=1)
    Storage.parsing_functions[token] = f
    return f


@dataclass
class NewOType(Statement):
    type_name: str
    title: Optional[str] = None


@dataclass
class Comment(Statement):
    line: str


@parse_function
def parse_REM(rest: str) -> Tuple[Statement, str]:
    return Comment(rest), ''


@dataclass
class ShowState(Statement):
    pass


@parse_function
def parse_SHOW_STATE(rest: str) -> Tuple[Statement, str]:
    return ShowState(), ''


@parse_function
def parse_TYPE(rest: str) -> Tuple[Statement, str]:
    type_name, rest = get_one_token(rest)
    return NewOType(type_name=type_name), rest


@dataclass
class NewAbility(Statement):
    'ABILITY domain domain-create-organization '
    type_name: str
    ability_name: str
    title: Optional[str] = None


@parse_function
def parse_ABILITY(rest: str) -> Tuple[Statement, str]:
    type_name, rest = get_one_token(rest)
    ability_name, rest = get_one_token(rest)
    return NewAbility(type_name=type_name, ability_name=ability_name), rest


@dataclass
class NewParentRelation(Statement):
    "PARENT type_name parent_name"
    type_name: str
    parent_name: str
    compulsory: bool


@parse_function
def parse_PARENT(rest: str) -> Tuple[Statement, str]:
    type_name, rest = get_one_token(rest)
    parent_name, rest = get_one_token(rest)
    return NewParentRelation(type_name=type_name, parent_name=parent_name, compulsory=False), rest


@dataclass
class NewProperty(Statement):
    ''' PROPERTY type_name name title '''
    type_name: str
    property_name: str
    title: Optional[str] = None


@parse_function
def parse_PROPERTY(rest: str) -> Tuple[Statement, str]:
    type_name, rest = get_one_token(rest)
    property_name, rest = get_one_token(rest)
    return NewProperty(type_name=type_name, property_name=property_name), rest


@dataclass
class SetProperty(Statement):
    ''' FOR <> SET property_name IN <> '''
    resource_match: 'ResourceMatch'
    property_name: str
    context: 'ResourceMatch'


@parse_function
def parse_FOR(rest0: str) -> Tuple[Statement, str]:
    resource_match, rest = parse_resource_match(rest0)
    rest = skip_one_token('SET', rest)
    property_name, rest = get_one_token(rest)
    if rest:
        rest = skip_one_token('IN', rest)
        context, rest = parse_resource_match(rest)
    else:
        context = ByPattern('*', '*')

    return SetProperty(resource_match, property_name, context), rest


@dataclass
class NewRelation(Statement):
    relation_name: str
    types: List[str]


@dataclass
class NewObject(Statement):
    ''' NEW challenge 12 aido-admin aido-admin '''
    type_name: str
    identifiers: List[str]


@parse_function
def parse_NEW(rest0: str) -> Tuple[NewObject, str]:
    type_name, rest = parse_until(' ', rest0)
    identifiers = rest.split(' ')
    return NewObject(type_name, identifiers), ''


class ResourceMatch:
    pass


@dataclass
class SingleResourceMatch(ResourceMatch):
    type_name: str
    identifier: str

    def __post_init__(self):
        if '*' in self.identifier:
            msg = 'Expected a single resource, not a pattern here.'
            raise ValueError(msg)


# class ByIdentifier(ResourceMatch):
#     ''' challenge:12  '''
#     type_name: str
#     identifier: str
#

@dataclass
class ByPattern(ResourceMatch):
    ''' challenge:aido*  '''
    type_name: str
    pattern: str

    def __post_init__(self):
        if not self.type_name or not self.pattern:
            raise ValueError(self)


@dataclass
class HasAttributes(ResourceMatch):
    attributes: List[str]


@dataclass
class AndMatch(ResourceMatch):
    ops: List[ResourceMatch]


def parse_single_resource_match(rest0) -> Tuple[SingleResourceMatch, str]:
    type_name, rest = parse_until(':', rest0, required=True)
    identifier, rest = parse_until(' ', rest)
    return SingleResourceMatch(type_name=type_name, identifier=identifier), rest


def parse_resource_match(rest0: str) -> Tuple[ResourceMatch, str]:
    if not rest0:
        raise ValueError(rest0)
    type_name, rest = parse_until(':', rest0, required=True)
    pattern, rest = parse_until(' ', rest)

    if '*' in type_name or '*' in pattern:
        bp = ByPattern(type_name, pattern)
    else:
        bp = SingleResourceMatch(type_name, pattern)
    if rest.startswith('['):
        n = rest.index(']')

        interesting = rest[1:n]
        attributes = interesting.strip().split()

        rest = rest[n + 1:]

        bp = AndMatch([HasAttributes(attributes), bp])

    try:
        return bp, rest
    except ValueError as e:
        msg = f'Cannot parse resource match {rest0!r}'
        raise ValueError(msg) from e


@dataclass
class SetChildParentRelation(Statement):
    ''' SUB group:one organization:aido '''
    child_match: ResourceMatch
    parent_match: ResourceMatch


@parse_function
def parse_SUB(rest0) -> Tuple[Statement, str]:
    child_match, rest = parse_resource_match(rest0)
    parent_match, rest = parse_resource_match(rest)
    return SetChildParentRelation(child_match, parent_match), rest


"""

 
        SUB challenge:* domain:1
        
        ALLOW <name> TO <Ability> IN <context> IF challenge-owner  

"""


class Query0(Statement):
    pass


@dataclass
class QueryIS(Query0):
    ''' IS <res> ALLOWED ability IN <context> '''
    user: 'SingleResourceMatch'
    ability: str
    context: 'SingleResourceMatch'


@parse_function
def parse_IS(rest0) -> Tuple[QueryIS, str]:
    user, rest = parse_single_resource_match(rest0)
    rest = skip_one_token('ALLOWED', rest)
    ability, rest = get_one_token(rest)
    rest = skip_one_token('IN', rest)
    context, rest = parse_single_resource_match(rest)
    return QueryIS(user, ability, context), rest


@dataclass
class QueryHAS(Query0):
    ''' HAS <res> PROPERTY ability IN <context> '''
    user: 'SingleResourceMatch'
    property: str
    context: 'SingleResourceMatch'


@parse_function
def parse_HAS(rest0) -> Tuple[QueryHAS, str]:
    user, rest = parse_single_resource_match(rest0)
    rest = skip_one_token('PROPERTY', rest)
    property, rest = get_one_token(rest)
    rest = skip_one_token('IN', rest)
    context, rest = parse_single_resource_match(rest)
    return QueryHAS(user, property, context), rest


@dataclass
class QueryGetProperties(Query0):
    ''' PROPERTIES <r> IN <context> '''
    user: 'SingleResourceMatch'
    context: 'SingleResourceMatch'


@parse_function
def parse_PROPERTIES(rest0) -> Tuple[QueryGetProperties, str]:
    user, rest = parse_single_resource_match(rest0)
    rest = skip_one_token('IN', rest)
    context, rest = parse_single_resource_match(rest)
    return QueryGetProperties(user, context), rest


class AbilityMatch:
    pass


@dataclass
class AbilityMatchByPattern(AbilityMatch):
    pattern: str

    def __post_init__(self):
        if ':' in self.pattern:
            raise ValueError(self)


def parse_ability_match(rest) -> Tuple[AbilityMatch, str]:
    pattern, rest = get_one_token(rest)
    return AbilityMatchByPattern(pattern), rest


class ConditionMatch:
    pass


@dataclass
class AttributeMatch(ConditionMatch):
    pattern: str

    def __post_init__(self):
        if ':' in self.pattern:
            raise ValueError(self)


def parse_condition_match(rest) -> Tuple[ConditionMatch, str]:
    pattern, rest = get_one_token(rest)
    return AttributeMatch(pattern), rest


class Always(ConditionMatch):
    pass


@dataclass
class Allow(Statement):
    ''' ALLOW <user match> TO <ability match> IN <resource match> [IF <condition match>] '''
    user_match: ResourceMatch
    ability_match: AbilityMatch
    context_match: ResourceMatch
    condition: ConditionMatch


@parse_function
def parse_ALLOW(rest0) -> Tuple[Allow, str]:
    user_match, rest = parse_resource_match(rest0)
    rest = skip_one_token('TO', rest)
    ability_match, rest = parse_ability_match(rest)
    rest = skip_one_token('IN', rest)
    context_match, rest = parse_resource_match(rest)
    if rest:

        rest = skip_one_token('IF', rest)
        condition_match, rest = parse_condition_match(rest)
    else:
        condition_match = Always()
    return Allow(user_match, ability_match, context_match, condition_match), rest


def remove_comment(line: str) -> str:
    try:
        i = line.index('#')
    except:
        return line
    else:
        return line[:i]


def parse_string(s) -> Iterator[Tuple[str, Statement]]:
    s = s.strip()
    lines = s.split('\n')

    lines = [remove_comment(_) for _ in lines]
    lines = [_.strip() for _ in lines]
    lines = [_ for _ in lines if _]

    for line in lines:
        token, rest = get_one_token(line)

        functions = Storage.parsing_functions
        if token not in functions:
            raise NotImplementedError((token, line))
        f = functions[token]
        try:
            statement, rest = f(rest)
        except ValueError as e:
            msg = f'Cannot parse line {line!r}.'
            raise ValueError(msg) from e
        yield line, statement


def get_one_token(line: str):
    line = line.lstrip()
    return parse_until(' ', line)


def skip_one_token(expect: str, line: str):
    token, rest = get_one_token(line)
    if expect != token:
        msg = f'Expected {expect!r} at the beginning of {line!r}.'
        raise ValueError(msg)
    return rest


def parse_until(sep: str, rest: str, required=False) -> Tuple[str, str]:
    rest = rest.lstrip()
    if not sep in rest:
        if required:
            msg = f'Could not find separator {sep!r} in {rest!r}.'
            raise ValueError(msg)
        return rest, ''
        # msg = f'Cannot find separator {sep!r} in {rest!r}.'
        # raise ValueError(msg)

    tokens = rest.split(sep, maxsplit=1)
    return tokens[0], tokens[1]
