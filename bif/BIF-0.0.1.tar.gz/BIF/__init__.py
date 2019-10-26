# -*- coding: utf-8 -*-


class String(str):
    def __new__(cls, iterable, sep : str="",
                is_join : bool=True, convert_to_string : bool=False):
        """
        返回一个 String 对象

        参数
        ----------
        iterable：可迭代对象
        sep：分隔符
        is_join：是否使用 str.join() 连接可迭代对象的元素
        convert_to_string：是否将 iterable 的元素转化成字符串（只有 is_join 为 True 时才有效）
        """
        if is_join:
            if not convert_to_string:
                return str.__new__(cls, str.join(sep, iterable))
            return str.__new__(cls, str.join(sep, [str(i) for i in iterable]))
        else:
            return str.__new__(cls, iterable)

    @classmethod
    def from_asciis(cls, asciis: list):
        """
        将 ASCII 码列表转化成字符串

        参数
        ----------
        asciis：ASCII 码列表
        """
        string = cls("")
        for i in asciis:
            string += chr(i)
        return string

    def to_asciis(self):
        """
        将字符串转化成 ASCII 码列表
        """
        return [ord(i) for i in self]


def count(n):
    """
    统计元素出现的次数

    参数
    ----------
    n：可迭代对象
    """
    d = {}
    for i in n:
        if i not in d:
            d[i] = 1
        else:
            d[i] += 1

    return sorted(d.items(), reverse=True, key=lambda x: x[1])


class List(list):
    def push(self, value):
        """
        将元素推进列表顶部

        参数
        ----------
        value：元素
        """
        self.insert(0, value)

    def poptop(self):
        """
        删除列表顶部元素并返回
        """
        return self.pop(0)

    def min(self):
        """
        返回列表的最小值
        """
        return min(self)

    def max(self):
        """
        返回列表的最大值
        """
        return max(self)

    def sum(self):
        """
        返回列表数字的总和
        """
        return sum(self)

    def find(self, value, start=0, stop=None):
        """
        寻找值，如果值不存在返回 -1

        参数
        ----------
        value：值
        start：查找的开始位置
        stop：查找的结束位置（不包括此下标）
        """
        if stop is not None:
            return self.index(value, start, stop) if value in self else -1
        return self.index(value, start) if value in self else -1


class Clipboard:
    @staticmethod
    def copy(text: str):
        """
        向剪贴板拷贝文本

        参数
        ----------
        text：文本
        """
        import pyperclip
        pyperclip.copy(text)

    @staticmethod
    def paste():
        """
        从剪贴板粘贴文本
        """
        import pyperclip
        return pyperclip.paste()


def sert(x, n):
    """
    返回数字的任意次方

    参数
    ----------
    x：数字
    n：次方
    """
    return x ** (1 / n)
