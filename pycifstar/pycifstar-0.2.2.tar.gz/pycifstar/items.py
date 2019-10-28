"""
container of Item
"""
__author__="ikibalin"
__version__="2019/09/12"

from .item import Item, str_to_comment

class Items(object):
    """
    container for objects Item
    """

    def __init__(self, items=[], comment=""):
        self.__items = None
        self.__comment = None
        self.comment = comment
        self.items = items

    @property    
    def items(self):
        return tuple(self.__items)
    @items.setter
    def items(self, l_x):
        l_res = []
        try:
            if isinstance(l_x, str):
                l_x_in = [l_x]
            else:
                _ = [x for x in l_x]
                l_x_in = l_x
        except:
            l_x_in = [l_x]
        for x in l_x_in:
            if isinstance(x, Item):
                l_res.append(x)
            else:
                item = Item()
                flag_out = item.take_from_string(str(x))
                if flag_out:
                    l_res.append(item)
        self.__items = l_res
    @property    
    def comment(self):
        return self.__comment
    @comment.setter
    def comment(self, x):
        if isinstance(x, str):
            x_in = str_to_comment(x)
        else:
            x_in = str("\n".join([str_to_comment(hh) for hh in x]))
        self.__comment = x_in

    @property    
    def names(self):
        return tuple([hh.name for hh in self.items])
    def __repr__(self):
        res = str(self)
        return res

    def __str__(self):
        if self.is_defined:
            ls_out = [self.comment]
            ls_out.extend([str(item) for item in self.items])
            return "\n".join(ls_out)
        return "The object 'Items' is not defined"

    @property
    def is_defined(self):
        cond = (self.items is not None)
        return cond

    def is_value(self, key_):
        str_1 = key_.strip().lower()
        if not(str_1.startswith("_")):
            str_1 = "_"+str_1
        l_name = [hh.name for hh in self.items]
        cond = (str_1 in l_name)
        return cond

    def is_prefix(self, key_):
        str_1 = key_.strip().lower()
        if not(str_1.startswith("_")):
            str_1 = "_"+str_1
        l_res = self.items_with_prefix(str_1)
        cond = (len(l_res) > 0)
        return cond

    def add_item(self, x):
        if isinstance(x, Item):
            x_in = [x]
        elif isinstance(x, str):
            _1 = Item()
            flag = _1.take_from_string(x)
            if flag:
                x_in = [_1]
        else:
            x_in = []
            self._show_message("Introduced object was not identified as an item")
        self.__items.extend(x_in)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key_):
        res = None
        str_1 = key_.lower().strip()
        if not(str_1.startswith("_")):
            str_1 = "_"+str_1
        for item in self.items:
            if item.name == str_1:
                res = item
                break
        l_res = self.items_with_prefix(str_1)
        if ((res is None) & (len(l_res) > 0)):
            res = l_res
        elif (res is None):
            self._show_message("Name '{:}' is not found".format(key_))
        return res

    def items_with_prefix(self, s_type: str):
        str_1 = s_type.lower().strip()
        if not(str_1.startswith("_")):
            str_1 = "_"+str_1
        l_res = Items(items=[])
        l_type = str_1.split("_")
        len_l_type = len(l_type)
        for item in self.items:
            l_type_name = item.name.split("_")
            if len_l_type <= len(l_type_name):
                flag = all([hh_1 == hh_2 for hh_1, hh_2 in zip(l_type, l_type_name[:len_l_type])])
                if flag:
                    l_res.add_item(item)
        return l_res

    def take_from_string(self, string):
        if isinstance(string, str):
            l_string_in = string.split("\n")
        else:
            l_string_in = string
        l_value_string, l_comment = [], []
        s_val = []
        flag_in = False
        for i_line, line in enumerate(l_string_in):
            if line.strip().startswith(";"):
                s_val.append(line.strip())
                flag_in = not(flag_in)
            elif line.strip().startswith("#"):
                if flag_in:
                    s_val.append(line.strip())
                else:
                    l_comment.append(line.strip())
            elif line.strip().startswith("_"):
                if flag_in:
                    s_val.append(line.strip())
                else:
                    if s_val != []:
                        l_value_string.append("\n".join(s_val))
                    s_val = [line.strip()]
            elif flag_in:
                s_val.append(line.strip())
        if s_val != []:
            l_value_string.append("\n".join(s_val))
        self.comment = "\n".join(l_comment)
        self.items = l_value_string
        return True

    def _show_message(self, s_out: str):
        print("***  Error ***")
        print(s_out)

    def __add__(self, x):
        if isinstance(x, Items):
            l_items = [_ for _ in self.items]
            l_items.extend([_ for _ in x.items])
            res = Items(items = l_items)
            if self.comment != "":
                res.comment = self.__comment
            if x.comment != "":
                if res.comment != "":
                    res.comment += "\n"+x.comment
                else:
                    res.comment = x.comment
        else:
            res = None
            self._show_message("Sum operation is defined only for Items type")
        return res
    def __radd__(self, x):
        return self+x
