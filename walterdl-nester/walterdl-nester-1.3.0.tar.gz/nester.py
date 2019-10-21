"""
My first python function that prints recursively arrays nested in arrays
"""
def print_recursively_lists(the_var, indent=False, indent_level=0):
  for item in the_var:
    if isinstance(item, list):
      print_recursively_lists(item, indent, indent_level * 2)
    else:
      if indent:
        for indent_step in range(indent_level):
          print("\t", end="")
      print(item)
