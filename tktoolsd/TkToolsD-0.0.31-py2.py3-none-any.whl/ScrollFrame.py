# -*- coding:utf-8 -*-
# 创建时间：2019-03-05 15:40:07
# 创建人：  Dekiven

import os
from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
tk, ttk = getTk()


class ScrollFrame(ttk.Frame) :
    '''ScrollFrame
    '''
    BarDir_V = 0b0001
    # scrollbar orientation horizontal
    BarDir_H = 0b0010
    # scrollbar orientation both vertical and horizontal
    BarDir_B = 0b0011

    __keySetLeft = ('Left')
    __keySetRight = ('Right')
    __keySetUp = ('Up')
    __keySetDown = ('Down')
    def __init__(self, *args, **dArgs) :
        ttk.Frame.__init__(self, *args, **dArgs) 
        self.scrollbarV = None
        self.scrollbarH = None
        self.center = None
        self.barOrient = self.BarDir_B

        # 设置canvas所在单元格(0, 0)可缩放
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        

    def setCenter(self, center) :
        if self.center :
            self.center.destroy()
        if center :
            self.center = center
            center.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
            # 默认显示两个方向的滚动条
            self.setBarOrientation()

    def getCenter(self) :
        return self.center

    # ---------------------------------scrollbar begin-----------------------------------------
    # TODO:dekiven 将scrollbar相关抽象到一个基类当中
    def setBarOrientation(self, orientation=None):
        if orientation :
            self.barOrient = orientation
        else :
            orientation = self.barOrient
        # 有竖直方向的滚动条
        scrollbar = self.scrollbarV

        if orientation & self.BarDir_V > 0:
            if scrollbar is None:
                scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
                scrollbar.configure(command=self.__yview)
                self.center.configure(yscrollcommand=scrollbar.set)
                self.scrollbarV = scrollbar
                scrollbar.grid(column=1, row=0,sticky=tk.N+tk.S)
            else :
                config = scrollbar.grid_info()
                # scrollbar.grid()
                scrollbar.grid(**config)
        elif scrollbar is not None:
            scrollbar.grid_remove()

        # 有水平方向的滚动条
        scrollbar = self.scrollbarH
        if orientation & self.BarDir_H > 0:
            if scrollbar is None:
                scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
                scrollbar.configure(command=self.__xview)
                self.center.configure(xscrollcommand=scrollbar.set)
                self.scrollbarH = scrollbar
                scrollbar.grid(column=0, row=1, sticky=tk.W+tk.E)
            else :
                config = scrollbar.grid_info()
                # scrollbar.grid()
                scrollbar.grid(**config)
        elif scrollbar is not None:
            scrollbar.grid_remove()

    def movetoPercentV(self, percent) :
        self.yview('moveto', str(percent/100.0))

    def movetoPercentH(self, percent) :
        self.xview('moveto', str(percent/100.0))

    def moveToTop(self) :
        self.movetoPercentV(0)

    def moveToBottom(self) :
        self.movetoPercentV(100)

    def movetToLeft(self) :
        self.movetoPercentH(0)

    def movetToRight(self) :
        self.movetoPercentH(100)

    def moveUpOneStep(self) :
        self.yview(tk.SCROLL, -1, tk.UNITS)

    def moveDownOneStep(self) :
        self.yview(tk.SCROLL, 1, tk.UNITS)

    def moveLeftOneStep(self) :
        self.xview(tk.SCROLL, -1, tk.UNITS)

    def moveRightOneStep(self) :
        self.xview(tk.SCROLL, 1, tk.UNITS)

    def __yview(self, *args, **dArgs) :
        # print('yview', args, dArgs)
        self.center.yview(*args, **dArgs)

    def __xview(self, *args, **dArgs) :
        # print('xview', args, dArgs)
        self.center.xview(*args, **dArgs)


def __main() :
    sv = ScrollFrame()

    # self.setCenter(center)
    l = tk.Listbox(sv)
    for x in range(20):
        l.insert(tk.END, str(x)+'dekiven '*x)
    sv.setCenter(l)

    sv.pack(expand=YES,fill=BOTH)
    sv.mainloop()

if __name__ == '__main__' :
    __main()
