
def print_list(lst):
    for elt in lst:
        if(isinstance(elt,list)):#to get type of element
            #for elt1 in elt:
            #   print(elt1)
             print_list(elt)
        else:
            print(elt)
