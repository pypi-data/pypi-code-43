"""
transform information from loop of cif file to class Loop
"""
__author__="ikibalin"
__version__="28/08/2019"

from .item import print_string, str_to_comment

class Loop(object):
    """
    class to store loop from .cif
    """

    def __init__(self, name=None, names = None, values = None, comment=None, names_comment = None, values_comment = None):
        self.__name = None
        self.__comment = None
        self.__names = None
        self.__values = None
        self.__values_comment = None
        self.__names_comment = None
        self.name = name
        self.names = names
        self.values = values
        self.comment = comment
        self.names_comment = names_comment
        self.values_comment = values_comment

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
    def values(self):
        return self.__cif_value_array
    @values.setter
    def values(self, ll_x):
        if ll_x is not None:
            try:
                try:
                    self.__cif_value_array = [[str(x).strip().strip("\"").strip("'") for x in l_x] for l_x in ll_x]
                except:
                    self.__cif_value_array = [[str(l_x).strip().strip("\"").strip("'")] for l_x in ll_x]
            except:
                self.__cif_value_array = [[str(ll_x).strip()]]
        else:
            self.__cif_value_array = None
    @property    
    def table(self):
        return self.values
    @table.setter
    def table(self, ll_x):
        self.values= ll_x


    @property    
    def names(self):
        return self.__names if self.__names is None else tuple(self.__names)
    @names.setter
    def names(self, l_x):
        if l_x is not None:
            try:
                l_name = [str(x).strip().lower() for x in l_x]
            except:
                l_name = [str(l_x).strip().lower()]
        else:
            l_name = None
        self.__names = l_name
    @property    
    def values_comment(self):
        return self.__values_comment
    @values_comment.setter
    def values_comment(self, l_x):
        if l_x is not None:
            
            try:
                self.__values_comment = [str_to_comment(x) for x in l_x]
            except:
                self.__values_comment = [str_to_comment(l_x)]
        else:
            if self.values is not None:
                nx, ny = self.size_values
                if ny > 0:
                    self.__values_comment = ny*[""]
            self.__values_comment = None

    @property    
    def table_comment(self):
        return self.values_comment
    @table_comment.setter
    def table_comment(self, ll_x):
        self.values_comment= ll_x

    @property    
    def names_comment(self):
        return self.__names_comment
    @names_comment.setter
    def names_comment(self, l_x):
        if l_x is not None:
            try:
                l_res = [str_to_comment(x) for x in l_x]
            except:
                l_res = [str_to_comment(l_x)]
            if len(l_res) == self.len_names:
                self.__names_comment = l_res
            else:
                self._show_message("Lens of name comment is not in agreement with lens of names")
        else:
            if self.len_names > 0:
                self.__names_comment = self.len_names*['']
            else:
                self.__names_comment = None

    @property    
    def len_names(self):
        if self.names is None:
            res = 0
        else:
            res = len(self.__names)
        return res
    @property    
    def size_values(self):
        if self.values is None:
            nx, ny = 0, 0
        else:
            ll_x = self.values
            ny = len(ll_x)
            nx = len(ll_x[0])
            if ny > 1:
                for l_x in ll_x[1:]:
                    if len(l_x) != nx:
                        self._show_message("Size of data values is not constant")
                        nx = None
                        break
        return (nx, ny)

    @property    
    def size_table(self):
        return self.size_values

    @property    
    def _check_object(self):
        if self.is_defined:
            nx_name = self.len_names
            nx, ny = self.size_values
            if nx is None:
                return False
            if nx != nx_name:
                self._show_message("Disagreement between number of name and number of elements in table")
                return False
            l_values_comment = self.values_comment
            if  l_values_comment is None:
                l_values_comment = ny*['']
            if len(l_values_comment) < ny:
                l_values_comment.extend((ny-len(l_values_comment))*[""])
            self.values_comment = l_values_comment
            return True
        return False
    
    def __str__(self):
        flag = self._check_object
        if not(flag):
            self._show_message("Data introduced incorrectly")
            return ""
        l_line_1 = ["loop_"]
        if self.name is not None:
            l_line_1.append("{:}".format(self.name))
        if self.comment is not None:
            l_line_1.append(" {:}".format(self.comment))
        if self.is_defined:
            ls_out = ["".join(l_line_1)]
            if self.len_names > 0:
                ls_out.extend(["{:}  {:}".format(hh_1, hh_2) for hh_1, hh_2 in zip(self.names, self.names_comment)])
                ll_x = self.values
                l_values_comment = self.values_comment
                for l_x, comment in zip(ll_x, l_values_comment):
                    l_line_1 = ["{:}".format(print_string(x)) for x in l_x]
                    l_line_1.append(comment)
                    ls_out.append(" ".join(l_line_1))
        return "\n".join(ls_out)

    def _show_message(self, s_out: str):
        print("***  Error ***")
        print(s_out)

    def __repr__(self):
        res = str(self)
        return res

    @property
    def is_defined(self):
        cond = ((self.names is not None) & (self.values is not None))
        return cond
    @property
    def is_value_comment(self):
        cond = (self.values_comment is not None)
        return cond
    @property
    def prefix(self):
        if self.is_defined:
            l_name = self.names
            l_first_type = l_name[0].split("_")
            if self.len_names == 1:
                res = "_".join(l_first_type)
            else: #if more than 1
                ind_smallest = len(l_name[0].split("_"))
                for name in l_name[1:]:
                    l_type = name.split("_")
                    len_1 = min([len(l_first_type), len(l_type)])
                    l_help = [hh_1 == hh_2 for hh_1, hh_2 in zip(l_first_type[:len_1], l_type[:len_1])]
                    if False in l_help:
                        ind_0 = l_help.index(False)
                    else:
                        ind_0 = len(l_help)
                    ind_smallest = min([ind_0, ind_smallest])
                res = "_".join(l_first_type[:ind_smallest])
        else:
            self._show_message("Object is not defined")
            res = None
        return res
    def is_prefix(self, key_):
        str_1 = key_.strip().lower()
        prefix = self.prefix
        cond = (str_1==prefix)
        return cond

    def __getitem__(self, key_):
        if self.is_defined:
            str_1 = key_.strip().lower()
            if not(str_1.startswith("_")):
                str_1 = "_"+str_1
            if str_1 in self.names:
                key_ind = self.names.index(str_1)
                ll_x = self.values
                l_res = [l_x[key_ind] for l_x in ll_x]
                return l_res
            else:
                self._show_message("The name {:} is not found".format(key_))    
        else:
            self._show_message("Object is not defined")

    def is_value(self, key_):
        str_1 = key_.strip().lower()
        if not(str_1.startswith("_")):
            str_1 = "_"+str_1
        cond = (str_1 in self.names)
        return cond

    def take_from_string(self, string):
        """
        should be formatted as

        loop_name # comment of loop
        _coeff_1 # comment name
        _coeff_2
        _coeff_3
        1  2  3  # comment 1
        5  4  1
        7  8  6  # other comment
        """
        if isinstance(string, str):
            l_string = string.split("\n")
        else:
            l_string = string
        
        name, comment, i_loop = find_name_comment_in_block(l_string, "loop_")
        self.name = name
        self.comment = comment

        l_name, l_name_comment = [], []
        for i_line, line in enumerate(l_string[i_loop+1:]):
            str_1 = line.strip()
            if str_1.startswith("_"):
                ind_1= str_1.find(" ")
                if ((ind_1 != -1)):
                    l_name.append(str_1[:ind_1])
                    l_name_comment.append(str_1[ind_1:])
                else:
                    l_name.append(str_1)
                    l_name_comment.append("")
            else:
                i_table = i_line+i_loop+1
                break
        len_name = len(l_name)

        l_values, l_values_comment = [], []
        for i_line, line in enumerate(l_string[i_table:]):
            str_1 = line.strip()
            cond = any([str_1.startswith(key_word) for key_word in ["loop_", "data_", "global_", "_", "#"]])
            if (cond | (str_1 == '')):
                break
            ind_1 = str_1.find("#")
            if ind_1 == -1:
                comment = ""
                line_value = str_1
            else:
                comment = str_1[ind_1:]
                line_value = str_1[:ind_1]

            l_value = smart_split(line_value)
            if len(l_value) < len_name:
                l_value.extend((len_name-len(l_value))*["."])

            l_values.append(l_value[:len_name])
            l_values_comment.append(comment)
                
        self.names = l_name
        self.names_comment = l_name_comment
        self.values = l_values
        self.values_comment = l_values_comment
        return True



def smart_split(line):
    """
    split string like:
    "C C 0.0033 0.0016 'International Tables Vol C Tables 4.2.6.8 and 6.1.1.4'"
    in the list like:
    ['C', 'C', '0.0033', '0.0016', 'International Tables Vol C Tables 4.2.6.8 and 6.1.1.4']
    """
    flag_in = False
    l_val, val = [], []
    for hh in line.strip():
        if (hh == " ") & (not flag_in):
            if val != []:
                l_val.append("".join(val))
            val = []
        elif (hh == " ") & (flag_in):
            val.append(hh)
        elif ((hh == "'")|(hh == "\"")):
            flag_in = not flag_in
        else:
            val.append(hh)
    if val != []:
        l_val.append("".join(val))
    return l_val


def find_name_comment_in_block(l_string, block_name):
    block_name_l = block_name.strip().lower()
    if not(block_name_l.endswith("_")):
        block_name_l = block_name_l + "_"
    len_bn = len(block_name_l)
    l_help = [i_line for i_line, line in enumerate(l_string) if line.strip().lower().startswith(block_name_l)]
    if len(l_help) > 0:
        i_block = l_help[0]
        str_1 = l_string[i_block].strip()
        ind_1= str_1.find(" ")
        if ((ind_1 != -1)):
            name = str_1[len_bn:ind_1]
            comment = str_1[ind_1:]
        else:
            name = str_1[len_bn:]
            comment = ""
    else:
        i_block = -1
        name = ""
        comment = ""
    return name, comment, i_block
