# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""The Pandas extension provides the code generator, which targes Pandas.

Examples:
    Create an instance of a SparkCodeGenerator::

        from nldsl import SparkCodeGenerator

        self.code_gen = SparkCodeGenerator()

    Generated code: x = y.filter(y.col1 == m & y.col3.isin([v1, v2, v3]))::

        model = "## x = on y | select rows y.col1 == m and y.col3 in [v1, v2, v3]"
        result = self.code_gen(model)

    Generated code: x = df.dropDuplicates()::

        model = "## x = on df | drop duplicates"
        result = self.code_gen(model)

    DSL statement that adds new rules to the grammer::

        model_def = #$ sort and clean $x = sort by $x | drop duplicates
        model_eval = ## x = on df | sort and clean col1
        result = self.code_gen(model_def + mode_eval)
"""

from nldsl.core import CodeGenerator, ExpressionRule, OperatorType, grammar, list_to_string
from nldsl import docs




class SparkCodeGenerator(CodeGenerator):
    """ A SparkCodeGenerator translates DSL statements into executable spark code.

    There are two kind of DSL statements, the ones which can be evaluate to executable code
    and the ones, which extend the DSL Grammer.
    As a result parsing a set of DSL statements usually has two impacts.
    Executable code is generate and the SparkCodeGenerator modifies itself in such a way
    that he is capable of parsing statements according to the new Grammer rules.

    Furthermore the SparkCodeGenerator derives from the CodeMap class and his grammer can also
    be extended by rules, which can not be expressed within the DSL.
    This is done with the __setitem__ and registerFunction methods.

    Example:
        Adding new rules::

            def show(code, args):
                return "print({})".format(code)

        SparkCodeGenerator.registerFunction("show entire table", show) # Add to class
        myCodeGen = SparkCodeGenerator();
        myCodeGen["show entire table"] = show # only add to this instance

    Args:
        recommend (bool): Whether to return a Recommendation if possible or always raise an error.
        spark_name (str): The name of the variable which holds/should hold the spark session
        import_name (str): The name under which the spark session is imported.
        start_session_named (str): If not empty a SparkSession with this name will be created.
        stop_session (bool): If True code will be added to stop the SparkSession
        kwargs (dict): Additional keyword argument, which will be added to the environment
    """

    def __init__(self, recommend=True, spark_name="spark", import_name="SparkSession",
                 start_session_named="", stop_session=False, **kwargs):
        """Please see help(SparkCodeGenerator)."""
        super().__init__(recommend=recommend, spark_name=spark_name,
                         import_name=import_name, **kwargs)
        self.start_session_named = start_session_named
        self.stop_session = stop_session


    def postprocessing(self, code_list):
        """ Optionally adds lines of code, which create and stop a SparkSession.
        The behavior of this function is determined by the `start_session_named`
        and `stop_session` parameters of the __init__ method.

        Args:
            code_list (list): A list of string containing executable code.
        Returns:
            (list) The modified code list
        """
        if self.start_session_named:
            spark_str = self.env["spark_name"] + " = " + self.env["import_name"]
            spark_str += ".builder.appName('{}').getOrCreate()".format(self.start_session_named)
            code_list = [spark_str] + code_list
        if self.stop_session:
            code_list.append(self.env["spark_name"] + ".stop()")
        return code_list


    def extract_environment(self, source_lines):
        """Extract the name of the spark session from `source_lines` if it exists.

        Args:
            source_lines (list): A list of strings containing source code.
        """
        imps = []
        for line in source_lines:
            sline = line.strip()
            if ".builder." in line and ".getOrCreate()" in line and not sline.startswith("#"):
                imps.append(sline)
        if imps:
            self.env["spark_name"] = imps[-1].split("=")[0].strip()




class SparkExpressionRule(ExpressionRule):
    """An ExpressionRule dedicated to parsing Spark expressions.

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
    return code + env["spark_name"] + ".createDataFrame({}, schema={})".format(args["data"], cols)


@grammar(docs.LOAD_FROM_DOC)
def load_from(code, args, env):
    return code + "{}.read.format('{}').load({})".format(env["spark_name"], args["type"], args["path"])


@grammar(docs.SAVE_TO_DOC)
def save_to(code, args):
    return code + ".write.format('{}').save({})".format(args["type"], args["path"])


@grammar(docs.UNION_DOC)
def union(code, args):
    return code + ".unionByName({})".format(args["table"])


@grammar(docs.DIFFERENCE_DOC)
def difference(code, args):
    return code + ".subtract({})".format(args["table"])


@grammar(docs.INTERSECTION_DOC)
def intersection(code, args):
    return code + ".intersect({})".format(args["table"])


@grammar(docs.SELECT_COLUMNS_DOC)
def select_columns(code, args):
    return code + ".select({})".format(list_to_string(args["columns"]))


@grammar(docs.SELECT_ROWS_DOC, SparkExpressionRule)
def select_rows(code, args):
    return code + ".filter({})".format(args["condition"])


@grammar(docs.DROP_COLUMNS_DOC)
def drop_columns(code, args):
    return code + ".drop({})".format(list_to_string(args["columns"]))


@grammar(docs.JOIN_DOC)
def join(code, args):
    cols = list_to_string(args["columns"])
    return code + ".join({}, on={}, how='{}')".format(args["table"], cols, args["how"])


@grammar(docs.GROUP_BY_DOC)
def group_by(code, args):
    cols = list_to_string(args["columns"])
    return code + ".groupBy({}).{}()".format(cols, args["aggregation"])


@grammar(docs.REPLACE_VALUES_DOC)
def replace_values(code, args):
    return code + ".replace({}, {})".format(args["old_value"], args["new_value"])


@grammar(docs.APPEND_COLUMN_DOC)
def append_column(code, args):
    cols_str = ".withColumn({})"
    return code + "".join(cols_str.format(", ".join([args["col_name"], args["col_expr"]])))


@grammar(docs.SORT_BY_DOC)
def sort_by(code, args):
    cols, order = zip(*args["columns"])
    cols = list_to_string(cols)
    order = [o == "ascending" for o in order]
    return code + ".sort({}, ascending={})".format(cols, order)


@grammar(docs.DROP_DUPLICATES_DOC)
def drop_duplicates(code):
    return code + ".dropDuplicates()"


@grammar(docs.RENAME_COLUMNS_DOC)
def rename_columns(code, args):
    ops = ["withColumnRenamed({}, {})".format(o, n) for o, n in args["columns"]]
    return code + "." + ".".join(ops)


@grammar(docs.SHOW_DOC)
def show(code):
    return code + ".show()"


@grammar(docs.SHOW_SCHEMA_DOC)
def show_schema(code):
    return code + ".printSchema()"


@grammar(docs.DESCRIBE_DOC)
def describe(code):
    return code + ".describe()"


@grammar(docs.HEAD_DOC)
def head(code, args):
    return code + ".head({})".format(args["num_rows"])


@grammar(docs.COUNT_DOC)
def count(code):
    return code + ".count()"



SparkCodeGenerator.register_function(expression_only)
SparkCodeGenerator.register_function(on_dataframe)
SparkCodeGenerator.register_function(create_dataframe)
SparkCodeGenerator.register_function(load_from)
SparkCodeGenerator.register_function(save_to)
SparkCodeGenerator.register_function(union)
SparkCodeGenerator.register_function(difference)
SparkCodeGenerator.register_function(intersection)
SparkCodeGenerator.register_function(select_columns)
SparkCodeGenerator.register_function(select_rows)
SparkCodeGenerator.register_function(drop_columns)
SparkCodeGenerator.register_function(join)
SparkCodeGenerator.register_function(group_by)
SparkCodeGenerator.register_function(replace_values)
SparkCodeGenerator.register_function(append_column)
SparkCodeGenerator.register_function(sort_by)
SparkCodeGenerator.register_function(drop_duplicates)
SparkCodeGenerator.register_function(rename_columns)
SparkCodeGenerator.register_function(show)
SparkCodeGenerator.register_function(show_schema)
SparkCodeGenerator.register_function(describe)
SparkCodeGenerator.register_function(head)
SparkCodeGenerator.register_function(count)
