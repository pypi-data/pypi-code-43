

def print_list_all(lst):
    for elt in lst:
        if(isinstance(elt, list)):
            print_list_all(elt2)
        else:
            print(elt)

