import os
# 3rd party modules
import papermill as pm
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from IPython.core.display import display, HTML
# internal modules
import mvb.pdh as pdh
import mvb.g as g

def defaults(**kwargs):
  """
  calls mvb.pdh.set_options() and passes along any arguments

  @input full_width: bool, default true
  @input show_all_rows: bool, default true
  @input show_all_cols: bool, default true
  @input show_full_col: bool, default true
  """
  full_width()
  pdh.set_options(**kwargs)

def full_width():
  """
  insert html to set container width to 100%
  """
  display(HTML("<style>.container { width:100% !important; }</style>"))

def nb_to_html(nb,
               exclude_input=True,
               exclude_prompts=True):
  """
  convert notebook to html
  
  @input nb : notebook
  @input exclude_input (bool default:True) : exclude input cells from output
  @input exclude_prompts (bool default:True) : exclude prompts from ouput
  
  @returns string : html body
  """
  html_exporter = HTMLExporter()
  html_exporter.exclude_input = exclude_input
  html_exporter.exclude_input_prompt = exclude_prompts
  html_exporter.exclude_output_prompt = exclude_prompts
  (body, _) = html_exporter.from_notebook_node(nb)
  return body

def publish(input_ipynb_path,
            output_dir=None,
            output_name=None,
            parameters={},
            output_html=True,
            output_ipynb=False,
            exclude_input=True,
            exclude_prompts=True):
  if output_dir == None:
    output_dir = '.'# os path to current directory?
  if output_name == None:
    notebook_base_name = input_ipynb_path.split('/')[-1].replace('.ipynb','')
    params_string = g.dict_to_file_name(parameters)
    output_name = f"{notebook_base_name}.{params_string}"
  output_ipynb_path=f"{output_dir}/{output_name}.ipynb"
  pm.execute_notebook(
    input_ipynb_path,
    output_ipynb_path,
    parameters
  )
  if output_html:
    output_html_path = f"{output_dir}/{output_name}.html"
    output_ipynb_nb = nbformat.read(output_ipynb_path, as_version=4)
    html = nb_to_html(output_ipynb_nb,
                      exclude_input=exclude_input,
                      exclude_prompts=exclude_prompts)
    f = open(output_html_path, "w")
    f.write(html)
    f.close()
  if not output_ipynb:
    print(f'removing {output_ipynb_path}')
    os.remove(output_ipynb_path)
