# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""The Pandas extension provides the code generator, which targes Pandas.

Examples:
    Create an instance of a PandasCodeGenerator::

        from nldsl import PandasCodeGenerator()
        code_gen = PandasCodeGenerator()

    Generate the code: x = y[y.col1 == m & y.col3.isin([v1, v2, v3])]::

        model = "## x = on y | select rows y.col1 == m and y.col3 in [v1, v2, v3]"
        result = self.code_gen(model)[0]

    Generate the code: print(df.rename(columns={'old1': 'new1', 'old2': 'new2'}))::

        model = "## on df | rename columns old1 to new1, old2 to new2 | show"
        result = self.code_gen(model)[0]

    Define a new rule and use it to generate code::

        model_def = "#$ my pipeline $[$old to $new] = rename columns $[$old to $new] | show"
        model_eva = "## on df | my pipeline old1 from new1, old2 from new2"
        result = self.code_gen(model_def + model_eva)[0]
"""

import re
from nldsl.core import (CodeGenerator, ExpressionRule, OperatorType, grammar,
                        split_code, list_to_string)
from nldsl import docs




class PandasCodeGenerator(CodeGenerator):
    """ A PandasCodeGenerator translates DSL statements into executable pandas code.

    There are two kind of DSL statements, the ones which can be evaluate to executable code
    and the ones, which extend the DSL Grammer.
    As a result parsing a set of DSL statements usually has two impacts.
    Executable code is generate and the PandasCodeGenerator modifies itself in such a way
    that he is capable of parsing statements according to the new Grammer rules.

    Furthermore the PandasCodeGenerator derives from the CodeMap class and his grammer can also
    be extended by rules, which can not be expressed within the DSL.
    This is done with the __setitem__ and registerFunction methods.

    Example:
        Adding new rules::

            def show(code, args):
                return "print({})".format(code)

            PandasCodeGenerator.registerFunction("show entire table", show) # Add to class

            myCodeGen = PandasCodeGenerator();
            myCodeGen["show entire table"] = show # only add to this instance

    Args:
        recommend (bool): Whether to return a Recommendation if possible or always raise an error.
        import_name (str): The name under which the Pandas module is imported
        kwargs (dict): Additional keyword argument, which will be added to the environment
    """
    pandas_import_regex = re.compile(r"^\s*import\s*pandas\s*as\s*[a-zA-Z_][a-zA-Z_0-9]*\s*$")


    def __init__(self, recommend=True, import_name="pandas", **kwargs):
        """Please see help(PandasCodeGenrator)."""
        super().__init__(recommend=recommend, import_name=import_name, **kwargs)


    def extract_environment(self, source_lines):
        """Extract the name under which pandas is import from `source_lines` if it exists.

        Args:
            source_lines (list): A list of strings containing source code.
        """
        imps = [l for l in source_lines if self.pandas_import_regex.match(l)]
        if imps:
            self.env["import_name"] = imps[-1].split(" as ")[-1].strip()




class PandasExpressionRule(ExpressionRule):
    """An ExpressionRule dedicated to parsing Pandas expressions.

    Args:
        expr_name (str): The name of the expression.
        next_keyword (str): The keyword following the expression or None
    """
    def __init__(self, expr_name, next_keyword):
        super().__init__(expr_name, next_keyword)
        self.operator_map["and"] = " & "
        self.operator_map["or"] = " | "
        self.operator_map["in"] = ".isin"
        self.operator_map["not"] = "~"

        self.operator_type["in"] = OperatorType.UNARY_FUNCTION


@grammar(docs.EXPRESSION_ONLY_DOC)
def expression_only(code, args):
    return code + args["expr"]


@grammar(docs.ON_DF_DOC)
def on_dataframe(code, args):
    return code + args["dataframe"]


@grammar(docs.CREATE_DF_DOC)
def create_dataframe(code, args, env):
    cols = list_to_string(args["header"])
    return code + env["import_name"] + ".DataFrame({}, columns={})".format(args["data"], cols)


@grammar(docs.LOAD_FROM_DOC)
def load_from(code, args, env):
    read_fun = ".read_csv(" if args["type"] == "csv" else ".read_json("
    return code + env["import_name"] + read_fun + args["path"] + ")"


@grammar(docs.SAVE_TO_DOC)
def save_to(code, args):
    read_fun = ".to_csv(" if args["type"] == "csv" else ".to_json("
    return code + read_fun + args["path"] + ")"


@grammar(docs.UNION_DOC)
def union(code, args, env):
    lhs, rhs = split_code(code, " = on ")
    return lhs + env["import_name"] + ".concat([{}, {}])".format(rhs, args["table"])


@grammar(docs.DIFFERENCE_DOC)
def difference(code, args):
    _, rhs = split_code(code, " = on ")
    return code + "[~{}.isin({}).all(1)]".format(rhs, args["table"])


@grammar(docs.INTERSECTION_DOC)
def intersection(code, args):
    return code + ".merge({})".format(args["table"])


@grammar(docs.SELECT_COLUMNS_DOC)
def select_columns(code, args):
    return code + "[{}]".format(list_to_string(args["columns"]))


@grammar(docs.SELECT_ROWS_DOC, PandasExpressionRule)
def select_rows(code, args):
    return code + "[{}]".format(args["condition"])


@grammar(docs.DROP_COLUMNS_DOC)
def drop_columns(code, args):
    return code + ".drop(columns={})".format(list_to_string(args["columns"]))


@grammar(docs.JOIN_DOC)
def join(code, args):
    cols = list_to_string(args["columns"])
    return code + ".join({}, on={}, how='{}')".format(args["table"], cols, args["how"])


@grammar(docs.GROUP_BY_DOC)
def group_by(code, args):
    cols = list_to_string(args["columns"])
    return code + ".groupby({}).{}()".format(cols, args["aggregation"])


@grammar(docs.REPLACE_VALUES_DOC)
def replace_values(code, args):
    return code + ".replace({}, {})".format(args["old_value"], args["new_value"])


@grammar(docs.APPEND_COLUMN_DOC)
def append_column(code, args):
    _, rhs = split_code(code, " = ")
    expr = re.sub(re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*\."), r"row.", args["col_expr"])
    col = rhs + ".apply(lambda row: {}, axis=1).values".format(expr)
    return code + ".assign(**{" + args["col_name"] + ": " + col + "})"


@grammar(docs.SORT_BY_DOC)
def sort_by(code, args):
    cols, order = zip(*args["columns"])
    cols = list_to_string(cols)
    order = [o == "ascending" for o in order]
    return code + ".sort_values({}, axis='index', ascending={})".format(cols, order)


@grammar(docs.DROP_DUPLICATES_DOC)
def drop_duplicates(code):
    return code + ".drop_duplicates()"


@grammar(docs.RENAME_COLUMNS_DOC)
def rename_columns(code, args):
    cols_map = "{" + ", ".join([k + ": " + v for k, v in args["columns"]]) + "}"
    return code + ".rename(columns={})".format(cols_map)


@grammar(docs.SHOW_DOC)
def show(code):
    return "print({})".format(code)


@grammar(docs.SHOW_SCHEMA_DOC)
def show_schema(code):
    return code + ".info(verbose=False)"


@grammar(docs.DESCRIBE_DOC)
def describe(code):
    return code + ".describe()"


@grammar(docs.HEAD_DOC)
def head(code, args):
    return code + ".head({})".format(args["num_rows"])


@grammar(docs.COUNT_DOC)
def count(code):
    return code + ".shape[0]"




PandasCodeGenerator.register_function(expression_only)
PandasCodeGenerator.register_function(on_dataframe)
PandasCodeGenerator.register_function(create_dataframe)
PandasCodeGenerator.register_function(load_from)
PandasCodeGenerator.register_function(save_to)
PandasCodeGenerator.register_function(union)
PandasCodeGenerator.register_function(difference)
PandasCodeGenerator.register_function(intersection)
PandasCodeGenerator.register_function(select_columns)
PandasCodeGenerator.register_function(select_rows)
PandasCodeGenerator.register_function(drop_columns)
PandasCodeGenerator.register_function(join)
PandasCodeGenerator.register_function(group_by)
PandasCodeGenerator.register_function(replace_values)
PandasCodeGenerator.register_function(append_column)
PandasCodeGenerator.register_function(sort_by)
PandasCodeGenerator.register_function(drop_duplicates)
PandasCodeGenerator.register_function(rename_columns)
PandasCodeGenerator.register_function(show)
PandasCodeGenerator.register_function(show_schema)
PandasCodeGenerator.register_function(describe)
PandasCodeGenerator.register_function(head)
PandasCodeGenerator.register_function(count)
