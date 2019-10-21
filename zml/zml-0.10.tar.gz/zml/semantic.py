import math
from pyparsing import *
import operator


exprStack = []

variables = {}


def pushFirst(strg, loc, toks):
    exprStack.append(toks[0])


def pushUMinus(strg, loc, toks):
    for t in toks:
        if t == '-':
            exprStack.append('unary -')
            # ~ exprStack.append( '-1' )
            # ~ exprStack.append( '*' )
        else:
            break


bnf = None


def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        # point = Literal(".")
        e = CaselessLiteral("E")
        # ~ fnumber = Combine( Word( "+-"+nums, nums ) +
        # ~ Optional( point + Optional( Word( nums ) ) ) +
        # ~ Optional( e + Word( "+-"+nums, nums ) ) )
        fnumber = Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
        ident = Word(alphas, alphas + nums + "_$")

        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")

        expr = Forward()
        atom = ((0, None) * minus + (pi | e | fnumber | ident + lpar + expr + rpar | ident).setParseAction(pushFirst) | Group(lpar + expr + rpar)).setParseAction(pushUMinus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left
        # exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))

        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        bnf = expr
    return bnf


# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = {"+": operator.add,
       "-": operator.sub,
       "*": operator.mul,
       "/": operator.truediv,
       "^": operator.pow}
fn = {"sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "abs": abs,
      "trunc": lambda a: int(a),
      "round": round,
      "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}


def evaluateStack(s):
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack(s)
    if op in "+-*/^":
        op2 = evaluateStack(s)
        op1 = evaluateStack(s)
        return opn[op](op1, op2)
    elif op == "PI":
        return math.pi  # 3.1415926535
    elif op == "E":
        return math.e  # 2.718281828
    elif op in fn:
        return fn[op](evaluateStack(s))
    elif op[0].isalpha():
        if op in variables:
            return variables[op]
        raise Exception("invalid identifier '%s'" % op)
    elif '.' in op:
            return float(op)
    else:
        return int(op)


def named(marker):
    def parse_action_impl(s, l, t):
        return (marker, t)
    return parse_action_impl


void_elements = [
    '', 'area', 'base', 'br', 'col', 'command',
    'embed', 'hr', 'img', 'input', 'keygen',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
]

inline_elements = [
    'h1', 'a', 'b', 'strong', 'i', 'em', 'title', 'label', 'button'
]


# general node semantics
ARITH_EXPRESSION = BNF()
COLON = Literal(':')

ALL = Word(printables + ' ', excludeChars=":")('all')

UNQUOTED_WORDS = Word(printables + ' ', excludeChars="'{}<>")

DESCRIPTOR = Word(alphanums + '_')
NAMESPACE_DESCRIPTOR = DESCRIPTOR('namespace') + '-' + DESCRIPTOR('namespaced_descriptor')
GLYPH = Word('*$&~!+%#@|', max=1)('glyph')

DESCRIPTOR_LINE = Optional(GLYPH)('glyph') + DESCRIPTOR('descriptor')
NAMESPACE_DESCRIPTOR_LINE = Optional(GLYPH)('glyph') + NAMESPACE_DESCRIPTOR('namespace_descriptor')
EMPTY = Empty()

LIST_ITEM_LINE = Literal('-')('list_item_glyph')
LINE = Optional(LIST_ITEM_LINE | NAMESPACE_DESCRIPTOR_LINE | DESCRIPTOR_LINE | EMPTY('descriptor')) + Optional(COLON)

NUMBER = Word(nums)
QUOTED_STRING = QuotedString(quoteChar="'")
TRANSLATION = Suppress('!') + DESCRIPTOR('language_code')
PROPERTY_ACCESSOR = Suppress('.') + Word(alphanums + '_')
META_ACCESSOR = Suppress('&') + Word(alphanums + '_')
TRANSLATION_ACCESSOR = Suppress('!') + DESCRIPTOR('translation_descriptor') + ZeroOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')))('properties')
MODEL = Literal('+')('glyph') + DESCRIPTOR('model_descriptor')
FIELD = Optional(Literal('.')('glyph')) + DESCRIPTOR('field_descriptor')
COMPONENT_DESCRIPTOR = Suppress('*') + DESCRIPTOR('component_descriptor')
CONTEXT_ACCESSOR = Literal('_context')('context_accessor')
CONTEXT_ITEM = Optional('.') + DESCRIPTOR('context_item')

UID = Suppress('#') + Word(alphanums, excludeChars='# : .')
CLS = Suppress('.') + Word(alphanums, excludeChars='. : #')
CLASSES = ZeroOrMore(CLS)('classes')
ID_CLASSES = Optional(UID)('uid') + CLASSES
ATTRIBUTE_KEY = Word(alphanums + '_' + '-', excludeChars=": = '")
# PARAM = (CONTEXT_ITEM('context_item') | CONTEXT('context')) + Optional(',')
# PARAM_LIST = ZeroOrMore(PARAM)
# FRAMEWORK_COMPONENT = Suppress('*core-') + DESCRIPTOR('framework_component') + PARAM_LIST('param_list')
VALUE_ACCESSOR = Literal('_value')('value_accessor')
LIST = Literal('[]')('list')
DICT = Literal('{}')('dict')
BOOLEAN = (Literal('True') or Literal('False'))('boolean')
LITERAL = (quotedString.addParseAction(removeQuotes) ^ pyparsing_common.number)('literal')
EXPRESSION = Forward()

code = \
"""
#ciphertext: '
----BEGIN PGP MESSAGE-----

jA0EBwMCKFOWDIApgLLx0o8BOb85gzkxIdVAE3tSIX9R/3yXthBUd5QPemx1Lfiz
pHpjmG/DOKJ1aN9ZwqzksAlgqLTf8UPRG9Ch/MPZoy9Q1R5KJv6QKlMPbn5XHqqo
NW5jSV5g2bX6pcl1FUqbCI9yfyDCw99Rxap01qWXxmlkD7uTp5tL2CFmg3SlDVKb
hAX8YpCjSYNDKlXL56O6rg==
=0C/y
-----END PGP MESSAGE-----
'
"""


# ParserElement.setDefaultWhitespaceChars(" \t")
INLINE_CONTENT = Forward()

DATA_NODE_ACCESSOR = Literal('#')('glyph') + DESCRIPTOR('data_node_descriptor')
SLOT_NODE = Literal('|')('glyph') + DESCRIPTOR('descriptor')
SLOT_NODE_INLINE = Literal('|')('glyph') + DESCRIPTOR('slot_descriptor')
RESOURCE_ACCESSOR = Suppress('@') + DESCRIPTOR('resource')
COMBINED_ACCESSOR = Optional(RESOURCE_ACCESSOR) + (DATA_NODE_ACCESSOR | MODEL | CONTEXT_ITEM) + ZeroOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')) | META_ACCESSOR.setParseAction(named('meta_data')))('properties')  # noqa
CID = Combine(Literal('Q') + DESCRIPTOR)
SEGMENT = (DATA_NODE_ACCESSOR |
           MODEL |
           META_ACCESSOR |
           CONTEXT_ITEM |
           OneOrMore(PROPERTY_ACCESSOR.setParseAction(named('property')))('properties'))
FULL_PATH = Optional(CID('resource')) + OneOrMore(SEGMENT.setParseAction(named('segment')))('segments')  # noqa
MOUSTACHE_EXPRESSION = CONTEXT_ACCESSOR | COMBINED_ACCESSOR | CONTEXT_ITEM | COMPONENT_DESCRIPTOR
MOUSTACHE_ATTRIBUTE_VALUE = NUMBER('number') | QUOTED_STRING('quoted_string') | MOUSTACHE_EXPRESSION
MOUSTACHE_ATTRIBUTE = ATTRIBUTE_KEY('moustache_attribute_key') + Optional(Literal('=') + MOUSTACHE_ATTRIBUTE_VALUE('moustache_attribute_value'))
MOUSTACHE_ATTRIBUTES = ZeroOrMore(Group(MOUSTACHE_ATTRIBUTE('moustache_attribute')))
FRAMEWORK_COMPONENT = Suppress('*core-') + DESCRIPTOR('framework_component') + MOUSTACHE_ATTRIBUTES('moustache_attributes')
MOUSTACHE = Suppress('{')
MOUSTACHE += EXPRESSION
MOUSTACHE += Suppress('}')
ATTRIBUTE_VALUE = Optional(Literal("'") | Literal('"')) + MOUSTACHE('moustache') + Optional(Literal("'") | Literal('"')) | NUMBER('number') | QUOTED_STRING('quoted_string') | EXPRESSION
ATTRIBUTE = ATTRIBUTE_KEY('attribute_key') + Optional(Literal('=') + ATTRIBUTE_VALUE('attribute_value'))
ATTRIBUTES = ZeroOrMore(Group(ATTRIBUTE('attribute')))
EXPRESSION << (
    BOOLEAN ^ LITERAL ^ LIST ^ DICT ^ VALUE_ACCESSOR ^ FRAMEWORK_COMPONENT
    ^ RESOURCE_ACCESSOR
    ^ COMBINED_ACCESSOR('context_item_with_property') ^ CONTEXT_ITEM
    ^ MODEL ^ COMPONENT_DESCRIPTOR ^ ARITH_EXPRESSION('arith_expression')
    ^ TRANSLATION_ACCESSOR('translation_accessor'))

INLINE_SEMANTICS_CONTENT = ZeroOrMore(UNQUOTED_WORDS.leaveWhitespace()('inline_semantic_content_words') | TRANSLATION_ACCESSOR('translation_accessor') | MOUSTACHE('moustache'))
INLINE_SEMANTICS_ELEMENT = DESCRIPTOR('descriptor') + Optional(' ') + ID_CLASSES('id_classes') + Optional(' ')
INLINE_SEMANTICS_ELEMENT += ATTRIBUTES('attributes') + Optional(' ')
INLINE_SEMANTICS_ELEMENT += Optional(COLON('colon') + Suppress(Optional(' ')) +
                                     INLINE_SEMANTICS_CONTENT('inline_semantics_content'))
INLINE_SEMANTICS = Suppress('<') + INLINE_SEMANTICS_ELEMENT + Optional(' ') + Suppress('>') + Optional(' ')('trailing_space')

INLINE_CONTENT << \
    (Suppress("'") + ZeroOrMore(LineEnd()).setParseAction(named('inline_content_newlines')) + ZeroOrMore((Literal(' ')('space')
    ^ INLINE_SEMANTICS.leaveWhitespace().setParseAction(named('inline_semantics'))
    ^ UNQUOTED_WORDS.setParseAction(named('inline_content_words'))
    ^ MOUSTACHE.setParseAction(named('moustache'))) + ZeroOrMore(LineEnd()).setParseAction(named('inline_content_newlines'))) + Suppress("'")
    ) | SLOT_NODE_INLINE('slot_node')

ELEMENT = Optional(DESCRIPTOR('descriptor')) + ID_CLASSES('id_classes')
ELEMENT += ATTRIBUTES('attributes') + Optional(COLON)('colon') + Optional(' ')
ELEMENT += Optional(INLINE_CONTENT.leaveWhitespace()('inline_content') ^ EXPRESSION('expression'))

# instruction semantics
FILENAME = DESCRIPTOR('filename')
URL = Word(printables, excludeChars='* "  : # { }' + "'")

RESOURCE = Suppress('@') + DESCRIPTOR('resource') + COLON + "'" + (URL | DESCRIPTOR)('source') + "'"

INHERIT = Suppress('%') + Literal('inherit')('instruction')
INHERIT += FILENAME('documentfile') | RESOURCE_ACCESSOR

IMPORT = Suppress('%') + Literal('import')('instruction')
IMPORT += FILENAME('documentfile') | RESOURCE_ACCESSOR('resource_accessor')

INCLUDE = Suppress('%') + Literal('include')('instruction')
INCLUDE += FILENAME('documentfile')

NAMESPACE = Suppress('%') + Literal('namespace')('instruction')
NAMESPACE += DESCRIPTOR('namespace') + '=' + URL

INSTRUCTION = INHERIT | IMPORT | INCLUDE | NAMESPACE


# route semantics
url_chars = alphanums + '-_.~%+'
PATH_SEGMENT = Word(url_chars)
PATH_VARIABLE = Suppress('{') + DESCRIPTOR('variable_descriptor') + Suppress('}')
PATH_ITEM = Suppress(Optional('/'))('leading_slash') + (PATH_SEGMENT.setParseAction(named('path_segment'))
                         | PATH_VARIABLE.setParseAction(named('path_variable')))
PATH_ITEMS = ZeroOrMore(PATH_ITEM('path_item'))
ROUTE_PATH = PATH_ITEMS('path_items')
ROUTE_PATH += Optional('/')('trailing_slash')
ROUTE = DESCRIPTOR('descriptor') + COLON + Optional(' ') + Suppress("'") + ROUTE_PATH('route_path') + Suppress("'")


# code semantics
SOMETHING = Suppress('%') + Word(printables + ' ')('some_thing')
ITERATOR = COMBINED_ACCESSOR | CONTEXT_ITEM
IF_STATEMENT = Suppress('%') + Suppress('if') + EXPRESSION('expression') + Suppress(':')
FOR_LOOP = Suppress('%') + Suppress('for') + DESCRIPTOR('variable') + Suppress('in')
FOR_LOOP += ITERATOR('iterator') + Suppress(':')
CODE = INHERIT | IMPORT | INCLUDE | NAMESPACE | IF_STATEMENT('if_statement') | FOR_LOOP('for_loop') | SOMETHING('some_thing')

COMPONENT_CALL_BODY = DESCRIPTOR('namespace') - Suppress('-') - DESCRIPTOR('component_descriptor')
COMPONENT_CALL = COMPONENT_CALL_BODY + ATTRIBUTES('attributes')
COMPONENT_CALL += Optional(COLON)('colon') + Optional(' ') + Optional(INLINE_CONTENT.leaveWhitespace()('inline_content') ^ EXPRESSION('expression'))
EGG = Optional(ALL('key')) + Optional(COLON)('colon') + Optional(ALL('value'))

# list items
LIST_ITEM = Literal('-')('list_item_glyph') + Optional(INLINE_CONTENT.leaveWhitespace())

ASSIGNMENT_VALUE = Optional(EXPRESSION('expression') ^ INLINE_CONTENT.leaveWhitespace()('inline_content'))
ASSIGNMENT = Optional(GLYPH) + DESCRIPTOR('descriptor') + COLON('colon') + Optional(' ') + ASSIGNMENT_VALUE('assignment_value')
# we have to definde DATA_NODE_VALUE containig INLINE_CONTENT here (not using Forward definition for INLINE_CONTENT,
# because using Forward definition seem to cause missing items in named label "inline_content" in parseResults
DATA_NODE_VALUE = Optional(EXPRESSION('expression') ^ INLINE_CONTENT.leaveWhitespace()('inline_content'))
DATA_NODE = Literal('#')('glyph') + DESCRIPTOR('data_descriptor') + COLON('colon') + Optional(' ') + DATA_NODE_VALUE('data_node_value')

# reintroduce newline to whitespace after last usage of INLINE_CONTENT, as INLINE_CONTENT is the only place where we use newlines in syntax
# ParserElement.setDefaultWhitespaceChars(" \n\t")

URL_PATH_VARIABLE = Suppress('{') + DESCRIPTOR('descriptor') + Suppress('}')
# URL_PATH = Suppress(Optional('/')) + ZeroOrMore((DESCRIPTOR.setParseAction(named('segment')) |
#                       URL_PATH_VARIABLE.setParseAction(named('variable'))) + Suppress(Optional('/')))('segments')
URL_PATH = Suppress(Optional('/')) + ZeroOrMore(DESCRIPTOR('segment') + Suppress(Optional('/')))('segments')
url_chars = alphanums + '-_.~%+'
fragment = Combine((Suppress('#') + Word(url_chars)))('fragment')
scheme = oneOf('http https ftp file')('scheme')
host = Combine(delimitedList(Word(url_chars), '.'))('host')
port = Suppress(':') + Word(nums)('port')
user_info = (Word(url_chars)('username') + Suppress(':') + Word(url_chars)('password') + Suppress('@'))

query_pair = Group(Word(url_chars) + Suppress('=') + Word(url_chars))
query = Group(Suppress('?') + delimitedList(query_pair, '&'))('query')

path = Combine(Suppress('/') + OneOrMore(~query + Word(url_chars + '/')))('path') + Optional(query) + Optional(fragment)

# url_parser = (scheme + Suppress('://') + Optional(user_info) + host + Optional(port) + Optional(path) + Optional(query) + Optional(fragment))
url_parser = (Optional(path) + Optional(query) + Optional(fragment))

BEGIN_MULTILINE = Combine(LINE + ' ' + Literal("'") + LineEnd())
END_MULTILINE = Literal("'") + LineEnd()
