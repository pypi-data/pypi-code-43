

def print_Movies(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_Movies(item)
        else:
            print(item)




