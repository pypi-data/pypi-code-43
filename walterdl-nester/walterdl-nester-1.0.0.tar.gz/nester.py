"""
My first python function that prints recursively arrays nested in arrays
"""
def print_recursively_lists(the_var):
  for item in the_var:
    if isinstance(item, list):
      print_recursively_lists(item)
    else:
      print(item)

