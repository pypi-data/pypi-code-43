"""
transform information from global block of cif file to class Global
"""
__author__="ikibalin"
__version__="29/08/2019"

from .item import str_to_comment, Item
from .items import Items
from .loop import Loop, find_name_comment_in_block
from .data import Data, delete_name_from_prefix


class Global(object):
    """
    container for objects Items, list of Loop and Data
    """

    def __init__(self, name="", items=None, loops=[], datas=[], comment=""):
        self.__name = None
        self.__comment = None
        self.__items = None
        self.__loops = None
        self.__datas = None
        self.name = name
        self.comment = comment
        self.items = items
        self.loops = loops
        self.datas = datas

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
    def datas(self):
        return self.__datas
    @datas.setter
    def datas(self, l_x):
        if isinstance(l_x, Data):
            l_x_in = [l_x]
        elif isinstance(l_x, str):
            l_x_in = [l_x]
        l_cif_data = []
        l_name = []
        for x in l_x:
            if isinstance(x, Data):
                if x.name in l_name:
                    _ind = l_name.index(x.name)
                    l_cif_data[_ind] = l_cif_data[_ind] + x
                else:
                    l_name.append(x.name)
                    l_cif_data.append(x)
            elif isinstance(x, str):
                data = Data()
                flag_out = data.take_from_string(x)
                if flag_out:
                    if data.name in l_name:
                        _ind = l_name.index(data.name)
                        l_cif_data[_ind] = l_cif_data[_ind] + data
                    else:
                        l_name.append(data.name)
                        l_cif_data.append(data)
                else:
                    self._show_message("Can not convert list of strings to object 'Data'")
            else:
                self._show_message("Can not define the type of input data to convert it to object 'Data'")
        self.__datas = l_cif_data


    @property
    def is_values(self):
        return (self.items is not None)

    def __repr__(self):
        res = str(self)
        return res

    def __str__(self):
        ls_out = ["global_{:} {:}\n".format(self.name, self.comment)]
        ls_out.append("\n")
        if self.is_values:
            ls_out.append(str(self.items))
        for cif_loop in self.loops:
            ls_out.append("\n\n")
            ls_out.append(str(cif_loop))
        for data in self.datas:
            ls_out.append("\n\n")
            ls_out.append(str(data))
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
        if res is None:
            for cif_loop in self.loops:
                flag_1 = cif_loop.is_value(str_1)
                flag_2 = cif_loop.is_prefix(str_1)
                if flag_1:
                    res = cif_loop[str_1]
                    break
                elif flag_2:
                    res = cif_loop
                    break
        if res is None:
            for data in self.datas:
                flag_1 = data.is_value(str_1)
                flag_2 = data.is_prefix(str_1)
                flag_3 = (str_1 == ("_"+data.name.lower()))
                if (flag_1 | flag_2):
                    res = data[str_1]
                    break
                if flag_3:
                    res = data
                    break
        if res is None:
            self._show_message("Item is not found")
        return res

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
        for data in self.datas:
            flag_1 = data.is_value(str_1)
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
        for data in self.datas:
            flag_1 = data.is_prefix(str_1)
            if flag_1:
                return flag_1
        return flag_1



    def take_from_string(self, string):
        if isinstance(string, str):
            l_string = string.split("\n")
        else:
            l_string = string

        name, comment, i_global = find_name_comment_in_block(l_string, "global_")
        self.name = name
        self.comment = comment

        flag_loop_read_name = False
        flag_loop_read_array = False
        flag_data_read = False
        l_string_values, l_string_loops = [], []
        l_string_loop = []
        i_data = -1
        for i_line, line in enumerate(l_string[(i_global+1):]):
            str_1 = line.strip()
            cond_1 = any([str_1.lower().startswith(key_word) for key_word in ["data_", "global_"]])
            cond_2 = (str_1 == "")
            cond_3 = str_1.lower().startswith("loop_")
            cond_4 = str_1.lower().startswith("_")
            cond_5 = str_1.lower().startswith("#")
            if cond_1:
                if str_1.lower().startswith("data_"):
                    i_data = i_line+i_global+1
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

        if (i_data != -1):
            l_string_datas, l_string_data = [], []
            for line in l_string[i_data:]:
                str_1 = line.strip()
                cond_1 = str_1.lower().startswith("global_")
                cond_2 = str_1.lower().startswith("data_") 
                if cond_1:
                    break
                elif cond_2:
                    if l_string_data != []:
                        l_string_datas.append("\n".join(l_string_data))
                    l_string_data = [str_1]
                else:
                    l_string_data.append(str_1)

            if l_string_data != []:
                l_string_datas.append("\n".join(l_string_data))
            if l_string_datas != []:
                self.datas = l_string_datas

        return True

    def __add__(self, x):
        if isinstance(x, Global):
            res = Global()
            if x.name != "":
                res.name = x.name
                res.comment = x.comment
            else:
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

            l_name_1 = [_1.name for _1 in self.datas]
            l_name_2 = [_1.name for _1 in x.datas]
            l_name_12 = list(set(l_name_1+l_name_2))
            l_res_data = []
            for _1 in l_name_12:
                if (_1 in l_name_1) & (_1 in l_name_2):
                    ind_1 = l_name_1.index(_1)
                    ind_2 = l_name_2.index(_1)
                    res_data = self.datas[ind_1]+x.datas[ind_2]
                elif (_1 in l_name_1):
                    ind_1 = l_name_1.index(_1)
                    res_data = self.datas[ind_1]
                else:
                    ind_2 = l_name_2.index(_1)
                    res_data = x.datas[ind_2]
                l_res_data.append(res_data)
            res.datas = l_res_data
        else:
            res = None
            self._show_message("Sum operation is defined only for Global type")
        return res
    def __radd__(self, x):
        return self+x

    def to_file(self, f_name):
        with open(f_name, "w") as fid:
            fid.write(str(self))