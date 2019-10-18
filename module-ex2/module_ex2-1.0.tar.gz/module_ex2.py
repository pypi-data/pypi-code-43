import collections

def print_rlist(lst):
    for elt in lst :
       if (isinstance(elt,list)) : 
          print_rlist(elt)
       else:
           print("##",elt)



