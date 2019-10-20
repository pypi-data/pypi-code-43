# -*- coding:utf-8 -*-
# 创建时间：2018-10-27 23:51:00
# 创建人：  Dekiven

import os
from DKVTools.Funcs import *

if isPython3() :
    import tkinter as tk  
    from tkinter import ttk     
else :
    import Tkinter as tk  
    import  ttk

event_cbb = '<<ComboboxSelected>>'

class Combobox(ttk.Frame) :
    '''下拉框，对ttk.combobox的简单封装
    '''
    def __init__(self, root, leftTitle='', values=[], current = 0, callbcak=None, *args, **dArgs) :
        ttk.Frame.__init__(self, root, *args, **dArgs)
        self.callbcak = callbcak

        self.columnconfigure(1, weight=1)
        lb = ttk.Label(self, text=leftTitle)
        lb.grid(column=0, row=0, padx=5, pady=5)

        sv = tk.StringVar()  
        self.sv = sv
        cbb = ttk.Combobox(self, textvariable=sv, takefocus=True)  
        cbb['values'] = values
        if len(values) > current :
            cbb.current(current)  #设置初始显示值，值为元组['values']的下标  
        cbb.grid(column=1, row=0, sticky='nswe', padx=5, pady=5)
        cbb.config(state='readonly')  #设为只读模式 
        cbb.bind(event_cbb, self.__getEventCallFunc(cbb, event_cbb))
        self.cbb = cbb

        self.current = cbb.current
        self.get = cbb.get
        self.set = sv.set

    def setCurIndex(self, index) :
        self.current = index

    def setValues(self, v) :
        self.cbb['values'] = v

    def setValue(self, value) :
        self.set(value)

    def getValue(self) :
        return self.get()

    def setOnSelectedCallback(self, callbcak) :
        self.callbcak = callbcak

    def focus(self) :
        self.cbb.focus()

    def __getEventCallFunc(self, sender, evenStr) :
        params = (sender, evenStr)
        def func(*args):
            self.__onEvent(params[0], params[1], *args)
        return func

    def __onEvent(self, sender, evenStr, *args) :
        if evenStr == event_cbb and sender == self.cbb :
            if isFunc(self.callbcak) :
                self.callbcak(self.getValue())
            


def __main() :
    # print('Module named:'+str(Combobox))
    root = tk.Tk()
    def p (c) :
        print(c)
    c = Combobox(root, callbcak = p, values=['1','2'], leftTitle='leftTitle')
    c.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == '__main__' :
    __main()
