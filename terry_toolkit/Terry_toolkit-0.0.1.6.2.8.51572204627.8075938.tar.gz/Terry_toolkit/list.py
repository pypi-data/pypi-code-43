# -*- coding: utf-8 -*-
# 对文件进行预处理


class List:
    """列表操作



    """
    def __init__(self):
        pass
    def remove_empty(self,list):
        """删除多余空元素
        
        >>> remove_empty(array)

        """
        while '' in list:
            list.remove('')
        return list


