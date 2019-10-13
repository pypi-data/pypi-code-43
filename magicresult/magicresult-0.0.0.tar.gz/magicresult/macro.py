import codecs
import ast
import string
import random
import astor

VAR_PREFIX = "python_macro_var_"

def secure_rand():
    r = random.SystemRandom()
    return ''.join([r.choice(string.ascii_letters) for _ in range(20)])

class Rewrite(ast.NodeTransformer):
    def visit_Assign(self, node: ast.Assign):
        ast.NodeVisitor.generic_visit(self, node)

        val = node.value
        if not isinstance(val, ast.Call):
            return node

        if isinstance(val.func, ast.Attribute):
            func_name = val.func.value.id
        else:
            func_name = val.func.id
        logging.warning(f"func_name={func_name}")
        if func_name != "attempt":
            return node
        if VAR_PREFIX in func_name:
            return node

        args_to_attempt = val.args
        assert len(args_to_attempt) == 1
        assert len(val.keywords) == 0
        arg_to_attempt = args_to_attempt[0]
        temp_var_name = VAR_PREFIX + secure_rand()
        final_vars_name = node.targets
        assert len(final_vars_name) == 1
        final_var_name = final_vars_name[0].id

        new_code = f"{temp_var_name} = {astor.to_source(arg_to_attempt).strip()}\nif {temp_var_name}.is_error(): return error({temp_var_name}.error())\n{final_var_name} = {temp_var_name}.value()"
        new_node = ast.parse(new_code)

        return new_node

class MacroCodec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return (codecs.encode(input, 'utf-8'), len(input))

    def decode(self, input: bytes, errors='strict'):
        file_has_not_been_processed = VAR_PREFIX.encode('utf-8') not in bytes(input)
        file_is_encoded = b"coding: macro" in bytes(input)

        if file_has_not_been_processed and file_is_encoded:
            try:
                tree = ast.parse(bytes(input))
                tree = Rewrite().visit(tree)
                output = astor.to_source(tree)
                return (output, len(input))
            except Exception:
                # logging.exception("Debug: Ignored crash is:")
                pass
        return codecs.decode(input, 'utf-8'), len(input)

class MacroIncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return MacroCodec().encode(input)

class MacroIncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return MacroCodec().decode(input)

class MacroStreamReader(MacroCodec, codecs.StreamReader):
    pass

class MacroStreamWriter(MacroCodec, codecs.StreamWriter):
    pass

def search(encoding):
    if encoding == "macro":
        return codecs.CodecInfo(
            name='macro',
            encode=MacroCodec().encode,
            decode=MacroCodec().decode,
            incrementalencoder=MacroIncrementalEncoder,
            incrementaldecoder=MacroIncrementalDecoder,
            streamreader=MacroStreamReader,
            streamwriter=MacroStreamWriter,
        )
    return None

codecs.register(search)
