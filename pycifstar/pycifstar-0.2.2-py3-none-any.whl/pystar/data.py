"""
transform information from data block of cif file to class Data
"""
__author__="ikibalin"
__version__="28/08/2019"

from .item import str_to_comment, Item
from .items import Items
from .loop import Loop, find_name_comment_in_block


class Data(object):
    """
    container for objects Items and list of Loop
    """

    def __init__(self, name="", items=None, loops=[], comment=""):
        self.__name = None
        self.__comment = None
        self.__items = None
        self.__loops = None
        self.name = name
        self.comment = comment
        self.items = items
        self.loops = loops

    @property    
    def name(self):
        return self.__name
    @name.setter
    def name(self, x):
        if x is not None:
            name = str(x).strip()
        else:
            name = ""
        self.__name = name
    @property    
    def comment(self):
        return self.__comment
    @comment.setter
    def comment(self, x):
        comment = str_to_comment(x)
        self.__comment = comment
    @property    
    def comments(self):
        return self.items.comment

    @property    
    def items(self):
        return self.__items
    @items.setter
    def items(self, x):
        if isinstance(x, Items):
            res = x
        elif isinstance(x, str):
            cif_values = Items()
            flag = cif_values.take_from_string(x)
            if flag:
                res = cif_values
            else:
                self._show_message("Can not convert string to object 'Items'")
                res = None
        elif x is None:
            res = None
        else:
            try:
                flag_1 = isinstance(x[0], Item)
                flag_2 = isinstance(x[0], str)
            except:
                flag_1, flag_2 = False, False
            cif_values = Items()
            if flag_1:
                cif_values.items = x
                res = cif_values
            elif flag_2:
                try:
                    cif_values.items = "\n".join(x)
                    res = cif_values
                except:
                    self._show_message("Can not convert list of strings to object 'Items'")
                    res = None
            else:
                self._show_message("Can not define the type of input data to convert it to object 'Items'")
                res = None
        self.__items = res

    @property    
    def loops(self):
        return tuple(self.__loops)
    @loops.setter
    def loops(self, l_x):
        if isinstance(l_x, Loop):
            l_x_in = [l_x]
        elif isinstance(l_x, str):
            l_x_in = [l_x]
        l_cif_loop = []
        for x in l_x:
            if isinstance(x, Loop):
                l_cif_loop.append(x)
            elif isinstance(x, str):
                cif_loop = Loop()
                flag_out = cif_loop.take_from_string(x)
                if flag_out:
                    l_cif_loop.append(cif_loop)
                else:
                    self._show_message("Can not convert list of strings to object 'Loop'")
            else:
                self._show_message("Can not define the type of input data to convert it to object 'Loop'")
        self.__loops = l_cif_loop

    @property
    def is_values(self):
        return (self.items is not None)

    
    def is_value(self, key_):
        str_1 = delete_name_from_prefix(key_, self.name)

        flag_1 = False
        if self.is_values:
            flag_1 = self.items.is_value(str_1)
        if flag_1:
            return flag_1
        for cif_loop in self.loops:
            flag_1 = cif_loop.is_value(str_1)
            if flag_1:
                return flag_1
        return flag_1

    def is_prefix(self, key_):
        str_1 = delete_name_from_prefix(key_, self.name)

        flag_1 = False
        if self.is_values:
            flag_1 = self.items.is_prefix(str_1)
        if flag_1:
            return flag_1
        for cif_loop in self.loops:
            flag_1 = cif_loop.is_prefix(str_1)
            if flag_1:
                return flag_1
        return flag_1

    def add_item(self, x):
        if self.items is None:
            self.items = Items(items=[x])
        else:
            self.items.add_item(x)

    def add_loop(self, x):
        if isinstance(x, Loop):
            x_in = [x]
        elif isinstance(x, str):
            _1 = Loop()
            flag = _1.take_from_string(x)
            if flag:
                x_in = [_1]
        else:
            x_in = []
            self._show_message("Introduced object was not identified as a loop")
        self.__loops.extend(x_in)

    def __repr__(self):
        res = str(self)
        return res

    def __str__(self):
        ls_out = ["data_{:} {:}\n".format(self.name, self.comment)]
        ls_out.append("\n")
        if self.is_values:
            ls_out.append(str(self.items))
        for cif_loop in self.loops:
            ls_out.append("\n\n")
            ls_out.append(str(cif_loop))
        return "".join(ls_out)

    def _show_message(self, s_out: str):
        print("***  Error ***")
        print(s_out)

    def __getitem__(self, key_):
        str_1 = delete_name_from_prefix(key_, self.name)

        flag_1 = self.items.is_value(str_1)
        flag_2 = self.items.is_prefix(str_1)
        res = None
        if flag_1:
            res = self.items[str_1]
        elif flag_2:
            res = self.items.items_with_prefix(str_1)
        else:
            for cif_loop in self.loops:
                flag_1 = cif_loop.is_value(str_1)
                flag_2 = (cif_loop.prefix == str_1)
                if flag_1:
                    res = cif_loop[str_1]
                    break
                elif flag_2:
                    res = cif_loop
                    break
        if res is None:
            self._show_message("Item is not found")
        return res

    def take_from_string(self, string):
        if isinstance(string, str):
            l_string = string.split("\n")
        else:
            l_string = string

        name, comment, i_data = find_name_comment_in_block(l_string, "data_")
        self.name = name
        self.comment = comment

        flag_loop_read_name = False
        flag_loop_read_array = False
        l_string_values, l_string_loops = [], []
        l_string_loop = []
        for line in l_string[(i_data+1):]:
            str_1 = line.strip()
            cond_1 = any([str_1.lower().startswith(key_word) for key_word in ["data_", "global_"]])
            cond_2 = (str_1 == "")
            cond_3 = str_1.lower().startswith("loop_")
            cond_4 = str_1.lower().startswith("_")
            cond_5 = str_1.lower().startswith("#")
            if cond_1:
                break
            elif cond_2:
                pass
            elif cond_3:
                if l_string_loop != []:
                    l_string_loops.append("\n".join(l_string_loop))
                    l_string_loop = []
                flag_loop_read_name = True
                flag_loop_read_array = False
            elif (cond_4 | cond_5):
                if flag_loop_read_name:
                    l_string_loop.append(str_1)
                else:
                    flag_loop_read_name = False
                    flag_loop_read_array = False
                    l_string_values.append(str_1)
            else:
                if (flag_loop_read_name | flag_loop_read_array):
                    flag_loop_read_name = False
                    flag_loop_read_array = True
                    l_string_loop.append(str_1)
                else:
                    l_string_values.append(str_1)
        self.items = "\n".join(l_string_values)
        if l_string_loop != []:
            l_string_loops.append("\n".join(l_string_loop))
        if l_string_loops != []:
            self.loops = l_string_loops
        return True

    def __add__(self, x):
        if isinstance(x, Data):
            if self.name != x.name:
                self._show_message("Data blocks should have the same name")
                return None
            res = Data()
            res.name = self.name
            res.comment = self.comment

            res.items = self.items
            if x.items is not None:
                if res.items is None:
                    res.items = x.items 
                else: 
                    res.items = res.items + x.items
            l_loops = [_ for _ in self.loops]
            l_loops.extend([_ for _ in x.loops])
            res.loops =  l_loops
        else:
            res = None
            self._show_message("Sum operation is defined only for Data type")
        return res
    def __radd__(self, x):
        return self+x



def delete_name_from_prefix(key_: str, s_name: str):
    str_1 = key_.strip().lower()
    if str_1.startswith(s_name.lower()):
        str_1 = str_1[len(s_name):]
    elif str_1.startswith("_"+s_name.lower()):
        str_1 = str_1[(1+len(s_name)):]
    if not(str_1.startswith("_")):
        str_1 = "_"+str_1
    return str_1


