import csv
import annofetch.lib.configuration.config as config
from pkg_resources import resource_filename

### Read in the Cog-Files ###
def get_cognames():
    cognames = {}
    cognames_path = resource_filename(__name__, config.PATH_TO_COGNAMES)
    with open(cognames_path) as f:
        for line in f:
            (key,value) = line.strip('\t').split()
            cognames[key] = value
    return cognames

def get_cog_fun():
    fun = {}
    fun_path = resource_filename(__name__, config.PATH_TO_FUN)
    with open(fun_path) as f:
        for line in f:
            (key, value) = line.strip().split('\t')
            fun[key] = value
    return fun

def get_functional_category(cognames, cogID):
    if cogID in cognames:
        return cognames[cogID]

def get_description(fun, category):
    list = []
    """ As there can be more than one character and therefore category we iterate
    over the given string """
    for char in category:
        list.append(fun[category])

    return list


def cog_part(mydict, cognames, fun):
    """ Check weather COG is asked or weather a COG id was found. """
    if "COGID" not in mydict or len(mydict["COGID"]) == 0 or mydict["COGID"] ==  "":
        return mydict

    cog_acc = mydict["COGID"][0]
    category = get_functional_category(cognames, cog_acc)
    mydict["COG category"] = category

    """ Add description if asked. """
    if "COG description" in mydict:
        descr = get_description(fun, category)
        mydict["COG description"] = descr

    return mydict
