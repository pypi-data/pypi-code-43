



def range(uinput, collection):
    if uinput == '':
        return True

    try:
        for choice in uinput.split(' '):
            if int(choice) < 1 or int(choice) > len(collection):
                return False
        return True
    except:
        return False