import sys

"""
My first python function that prints recursively arrays nested in arrays
"""
def print_recursively_lists(the_var, indent=False, indent_level=0, output_channel=sys.stdout):
  for item in the_var:
    if isinstance(item, list):
      print_recursively_lists(item, indent, indent_level * 2, output_channel)
    else:
      if indent:
        for indent_step in range(indent_level):
          print("\t", end="", file=output_channel)
      print(item, file=output_channel)
