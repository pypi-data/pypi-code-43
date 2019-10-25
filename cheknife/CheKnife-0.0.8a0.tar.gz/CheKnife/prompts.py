import sys


def ask(message='Are you sure you want to continue [y/n]?', yes={'yes', 'y', 'ye', 'si', 's'}, no={'no', 'n'}):
    choice = input("{} ".format(message))

    error_count = 0
    while choice not in yes.union(no):
        error_count += 1
        input("Invalid option. \n{}".format(message))
        if error_count >= 4:
            break

    if choice in yes:
        return True
    elif choice in no:
        return False
