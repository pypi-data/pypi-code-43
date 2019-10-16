#Function to print elements

def print_list(lst):
    for elt in lst:
        if isinstance(elt, list):
            print_list(elt)
        else:
            print(elt)