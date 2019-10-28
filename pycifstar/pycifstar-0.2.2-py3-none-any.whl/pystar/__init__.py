name = "pystar"

from .item import Item
from .items import Items
from .loop import Loop
from .data import Data
from .global_ import Global

def read_star_file(f_name):
    return to_global(f_name)

def read_file(f_name):
    return to_global(f_name)

def to_global(f_name):
    fid = open(f_name, "r")
    string = fid.read()
    fid.close()
    global_ = Global()
    flag = global_.take_from_string(string)
    if not flag:
        print("Error at file reading")
    return global_

def to_data(f_name):
    fid = open(f_name, "r")
    string = fid.read()
    fid.close()
    data = Data()
    flag = data.take_from_string(string)
    if not flag:
        print("Error at file reading")
    return data

def to_loop(f_name):
    fid = open(f_name, "r")
    string = fid.read()
    fid.close()
    loop = Loop()
    flag = loop.take_from_string(string)
    if not flag:
        print("Error at file reading")
    return loop

def to_values(f_name):
    fid = open(f_name, "r")
    string = fid.read()
    fid.close()
    items = Items()
    flag = items.take_from_string(string)
    if not flag:
        print("Error at file reading")
    return items
