#! python3

# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

import sys
import argparse
import re
from enum import Enum
from textx.exceptions import TextXSyntaxError
from nldsl import PandasCodeGenerator, SparkCodeGenerator, Recommendation




class StmtConfig(Enum):
    EVAL_PREFIX = "##"
    DEFINE_PREFIX = "#$"
    SHEBANG_PREFIX = "#!"
    IMPORT_STRING = "import"


class Stmt:
    def __init__(self, value, indent):
        self.value = value
        self.indent = indent


class PythonStmt(Stmt): pass
class CodeStmt(PythonStmt): pass
class ImportStmt(PythonStmt): pass
class ShebangStmt(PythonStmt): pass


class DSLStmt(Stmt): pass
class DefineStmt(DSLStmt): pass
class EvalStmt(DSLStmt): pass


def make_stmt(value, indent):
    if value.startswith(StmtConfig.EVAL_PREFIX.value):
        return EvalStmt(value, indent)

    if value.startswith(StmtConfig.DEFINE_PREFIX.value):
        return DefineStmt(value, indent)

    if value.startswith(StmtConfig.SHEBANG_PREFIX.value):
        return ShebangStmt(value, indent)

    if StmtConfig.IMPORT_STRING.value in value:
        return ImportStmt(value, indent)

    return CodeStmt(value, indent)


def is_python(stmt):
    return isinstance(stmt, PythonStmt)

def is_code(stmt):
    return isinstance(stmt, CodeStmt)

def is_import(stmt):
    return isinstance(stmt, ImportStmt)

def is_shebang(stmt):
    return isinstance(stmt, ShebangStmt)

def is_dsl(stmt):
    return isinstance(stmt, DSLStmt)

def is_define(stmt):
    return isinstance(stmt, DefineStmt)

def is_eval(stmt):
    return isinstance(stmt, EvalStmt)

    


class NLDSLCompiler:
    TARGET_PATTERN = re.compile(r"\s?##\starget_code\s=")

    def __init__(self, code_gen, auto_import):
        self.code_gen = code_gen
        self.imports = auto_import


    def compile(self, input_file, output_file):
        with open(input_file, "r") as code:
            stmts = []
            for idx, line in enumerate(code):
                # skip target annotations
                if self.TARGET_PATTERN.match(line):
                    continue
                sline = line.lstrip().rstrip("\n")
                stmts.append(make_stmt(sline, len(line) - len(sline) - 1))

            try:
                dsl_code = self.code_gen("\n".join([s.value for s in stmts if is_dsl(s)]))
            except TextXSyntaxError:
                print("ERROR: No NLDSL Code found --- aborting compilation.", file=sys.stderr)
                sys.exit(1)

        result = self._compile(self._add_imports(stmts), dsl_code)

        with open(output_file, "w") as code:
            code.write("\n".join(result))
    

    @classmethod
    def substitute_code(cls, stmt, dsl_code):
        if is_eval(stmt):
            dsl_stmt = dsl_code.pop(0)
            if isinstance(dsl_stmt, Recommendation):
                raise SyntaxError("Invalid DSL statement.")
            return " " * stmt.indent + dsl_stmt
        return " " * stmt.indent + stmt.value if stmt.value else ""


    def _add_imports(self, stmts): 
        idx, indent = next(((i, s.indent) for i, s in enumerate(stmts) if is_import(s)), (0, 0))
        idx = idx + 1 if idx == 0 and is_shebang(stmts[0]) else idx
        return stmts[0:idx] + [ImportStmt(imp, indent) for imp in self.imports] + stmts[idx:]




class PandasCompiler(NLDSLCompiler):
    def __init__(self, auto_import=False, **kwargs):
        prefix = ""
        if "import_name" in kwargs and kwargs["import_name"] != "pandas":
            prefix = " as " + kwargs["import_name"]
 
        auto_import = ["import pandas" + prefix] if auto_import else []
        super().__init__(PandasCodeGenerator(**kwargs), auto_import)


    def _compile(self, stmts, dsl_code):
        return [self.substitute_code(stmt, dsl_code) for stmt in stmts if not is_define(stmt)]




class SparkCompiler(NLDSLCompiler):
    def __init__(self, auto_import=False, **kwargs):
        prefix = ""
        if "import_name" in kwargs and kwargs["import_name"] != "SparkSession":
            prefix = " as " + kwargs["import_name"]

        auto_import = ["from pyspark.sql import SparkSession" + prefix] if auto_import else []
        super().__init__(SparkCodeGenerator(**kwargs), auto_import)


    def _compile(self, stmts, dsl_code):
        if self.code_gen.start_session_named:
            stmts = self._insert_start_stmt(stmts)
        if self.code_gen.stop_session:
            stmts = self._insert_stop_stmt(stmts)
        return [self.substitute_code(stmt, dsl_code) for stmt in stmts if not is_define(stmt)]


    def _insert_start_stmt(self, stmts):
        idx, indent = next(((i, s.indent) for i, s in enumerate(stmts) if is_dsl(s)), (0, 0))
        stmts.insert(idx, EvalStmt("", indent))
        stmts.insert(idx + 1, CodeStmt("", indent))
        return stmts
         

    def _insert_stop_stmt(self, stmts):
        idx, indent = next(((i, s.indent) for i, s in enumerate(stmts[::-1]) if is_dsl(s)), (0, 0))
        stmts.insert(len(stmts) - idx, EvalStmt("", indent))
        stmts.insert(len(stmts) - idx - 1, CodeStmt("", indent))
        return stmts




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile NLDSL code to python code.")

    parser.add_argument("input_file", help="A python file containing DSL code.")
    parser.add_argument("output_file", help="The file in which the compiled code shall be stored.")

    parser.add_argument("--target", "-t", dest="target", required=True,
                        help="The target framework, must be either pandas or spark).")
    parser.add_argument("--start-session", "-s", dest="start", default="",
                        help="(spark only) If provided this will start a session under the given name.")
    parser.add_argument("--stop-session", "-o", action="store_true", dest="stop",
                        help="(spark only) If provide a stop session statement will be added.")
    parser.add_argument("--spark-variable", "-v", dest="spark_variable", default="spark",
                        help="(spark only) The name of the variable which holds/should hold the session.")
    parser.add_argument("--auto-import", "-a", action="store_true", dest="auto_import",
                        help="Whether or not import statements shall be added if necessary")
    parser.add_argument("--import-name", "-n", dest="import_name", default="infer",
                        help="The name under which the target framework is/should be imported")

    args = parser.parse_args()
   
    if args.target == "spark":
        args.import_name = "SparkSession" if args.import_name == "infer" else args.import_name
        spark_args = {
            "start_session_named": args.start,
            "stop_session": args.stop,
            "import_name": args.import_name,
            "spark_name": args.spark_variable
        }
        compiler = SparkCompiler(args.auto_import, **spark_args)

    elif args.target == "pandas":
        args.import_name = "pandas" if args.import_name == "infer" else args.import_name
        pandas_args = {"import_name": args.import_name}
        compiler = PandasCompiler(args.auto_import, **pandas_args)

    compiler.compile(args.input_file, args.output_file)
