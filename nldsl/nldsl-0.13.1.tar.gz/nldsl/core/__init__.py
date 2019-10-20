# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""The core package implements every aspect of nldsl that is not target dependent.

Its primary interface is the CodeGenerator class, which serves as a common base
class for every CodeGenerator with a specific target. The CodeGenerator also
implements the dictonary API via inheritance from the CodeMap.

Adding new grammar rules via python is implemented by the GrammarFunction
and its associated GrammarParser. The grammar decorator provides syntactic sugar
for generating instances of GrammarFunction from normal python functions.

The PipeFunction is called into action once a DSL statement, which defines a new
grammar rule, is observed by the CodeGenerator. The PipeFunction then synthesizes a
new pipeline using the already exist dynamic grammar rules.
"""

from .types import (OperatorType, Type, Value, Keyword, Variable, Expression, VarList,
                    is_type, is_value, is_keyword, is_variable, is_expression, is_var_list)
from .utils import decorator_factory, cast_down, convert_function, split_code, list_to_string
from .rules import KeywordRule, VariableRule, VarListRule, ExpressionRule, GrammarRule
from .external import GrammarParser, GrammarFunction, grammar
from .internal import IdentityConverter, NameConverter, ListConverter, PipeFunction
from .exceptions import DSLError, DSLArgumentError, DSLFunctionError
from .codegen import CodeMap, CodeGenerator, Recommendation
