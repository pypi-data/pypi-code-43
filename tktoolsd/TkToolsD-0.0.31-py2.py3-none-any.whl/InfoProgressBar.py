# -*- coding:utf-8 -*-
# 创建时间：2019-03-01 11:42:00
# 创建人：  Dekiven

import os
from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *

tk, ttk = getTk()


class InfoProgressBar(ttk.Frame) :
    '''InfoProgressBar configure keys: ('cursor', 'length', 'maximum', 'mode', 'orient', 'style', 'takefocus')
    '''
    def __init__(self, *args, **dArgs) :
        deleteKeys = ('cursor', 'length', 'maximum', 'mode', 'orient', 'style', 'takefocus')
        newArgs = {}
        for key in deleteKeys :
            if key in list(dArgs.keys()) :
                v = dArgs.pop(key)
                if v :
                    newArgs[key] = v
        ttk.Frame.__init__(self, *args, **dArgs)

        self.confKeys = deleteKeys

        label = ttk.Label(self, text='', justify=tk.CENTER)
        label.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.CENTER, padx=10, pady=1)
        self.label = label

        pbv = tk.DoubleVar()
        self.pbv = pbv
        pb = ttk.Progressbar(self, variable=pbv, **newArgs)
        pb.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, padx=10, pady=5)
        self.pb = pb

    def start(self, interval=None) :
        self.pb.start(interval)

    def step(self, delta=None) :
        self.pb.step(delta)

    def stop(self) :
        self.pb.stop()

    def setPercent(self, value) :
        self.pbv.set(value)

    def getPercent(self) :
        return self.pbv.get()

    def setInfo(self, info) :
        self.label.configure(text=info)

    def config(self, **conf) :
        for k in list(conf.keys()) :
            if k not in self.confKeys :
                conf.pop(k)
                raise NameError('InfoProgressBar has not attribute named :'+k)
        self.pb.configure(**conf)

def __main() :
    m = InfoProgressBar(None, mode='determinate')
    m.pack(expand=YES,fill=BOTH)
    m.setInfo('hhhhhhhhhhhhhh')
    # m.setPercent(80)
    m.config(mode='indeterminate')
    m.step(90)
    m.start(5)
    m.mainloop()

if __name__ == '__main__' :
    __main()
