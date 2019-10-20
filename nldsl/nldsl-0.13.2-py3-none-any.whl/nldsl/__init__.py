# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

""" NLDSL is a tool to create DSLs for data science, which can be translated into executable code.

A new DSL is created by deriving from the CodeGenerator class and rules are added to it via simple
python functions.
Besides providing code generation NLDSL allows the user to define DSL-level function,
which are then treated as first-class rules.
Currently we provide extensions for Pandas and PySpark.

Example:
    We are going to use the PandasCodeGenerator for this example::

        from nldsl import PandasCodeGenerator, grammar

        code_gen = PandasCodeGenerator

    Define a DSL statement and create executable code::

        dsl_stmt = "## x = on df | rename columns old1 to new1, old2 to new2"
        python_code = code_gen(dsl_stmt)

    Add a new rule to the DSL and use it to create executable code::

        new_rule = "#$ my rule $x = rename columns old to $x | drop duplicates"
        dsl_stmt = "## x = on df | my rule new"
        python_code = code_gen(new_rule + dsl_stmt)

    Implement a new rule via python::

        def rename_columns(code, args):
            col_map = {args[i]:args[i+2] for i in range(0, len(args), 3)}
            return code + ".rename(columns={})".format(col_map)

    Implement the "rename columns" rule using the @grammar decorator::

        @grammar
        def rename_columns(code, args):
            \"\"\"Desc...
            Grammar:
	            rename columns $my_var[$old to $new]
            \"\"\"
            return code + ".rename(columns={})".format(dict(args["my_var"]))

    New rule can either be added to a certain instance of code_generator or to the class itself::

        code_gen["rename columns"] = rename_columns
        PandasCodeGenerator.register_function("rename colummns", rename_columns)
"""

from .core import CodeGenerator, Recommendation, grammar
from .pandas_extension import PandasCodeGenerator
from .spark_extension import SparkCodeGenerator
