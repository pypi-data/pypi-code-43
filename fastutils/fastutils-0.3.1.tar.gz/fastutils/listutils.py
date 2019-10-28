
def pad(thelist, size, padding):
    if len(thelist) < size:
        for _ in range(size - len(thelist)):
            thelist.append(padding)
    return thelist

def chunk(thelist, size, with_padding=False, padding=None):
    data = []
    start = 0
    while True:
        if len(thelist) < size:
            if with_padding:
                pad(thelist, size, padding)
            data.append(thelist)
            break
        data.append(thelist[start:start+size])
        thelist = thelist[start+size:]
        if not thelist:
            break
    return data

def clean_none(thelist):
    """Remove None or empty element in thelist.
    """
    return [element for element in thelist if element]

def unique(thelist):
    """Remove duplicated elements from the list.
    """
    result = []
    for element in thelist:
        if not element in result:
            result.append(element)
    return result

def replace(thelist, map, inplace=True):
    """Replace element in thelist, the map is collection of {old_value: new_value}.
    
    inplace == True, will effect the original list.
    inplace == False, will create a new list to return.
    """
    thelist = list(thelist)
    if inplace:
        for index in range(len(thelist)):
            value = thelist[index]
            if value in map:
                thelist[index] = map[value]
        return thelist
    else:
        newlist = []
        for index in range(len(thelist)):
            value = thelist[index]
            if value in map:
                newlist.append(map[value])
            else:
                newlist.append(value)
        return newlist
