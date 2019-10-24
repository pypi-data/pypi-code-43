with __import__('importnb').Notebook():
    try: from . import __doctest_post_run_cell, __interactive_markdown_cells, __nline_code, __interactive_jinja_templates, __xonsh_compiler
    except: import __doctest_post_run_cell, __interactive_markdown_cells, __nline_code, __interactive_jinja_templates, __xonsh_compiler
    
    
def unload_ipython_extension(shell): [x.unload_ipython_extension(shell) for x in (__doctest_post_run_cell, __interactive_markdown_cells, __nline_code, __interactive_jinja_templates, __xonsh_compiler)]
def load_ipython_extension(shell): [x.load_ipython_extension(shell) for x in (__doctest_post_run_cell, __interactive_markdown_cells, __nline_code, __interactive_jinja_templates, __xonsh_compiler)]
  