# -*- coding:utf-8 -*-
# 创建时间：2019-03-05 15:13:09
# 创建人：  Dekiven

import os
import time

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
from TkToolsD.ScrollFrame import *
from TkToolsD.Combobox import *
from TkToolsD.VersionWidget import *

tk, ttk = getTk()

# help(ttk.Treeview)

if isPython3() :
    from tkinter.font import Font
else :
    from tkFont import Font 

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class ConfigEditor(ScrollFrame) :
    def __init__(self, *args, **dArgs) :
        ScrollFrame.__init__(self, *args, **dArgs) 

        self.supportTypes = ('int', 'float', 'bool', 'string', 'version', 'dict', 'list')
        self.types = ('int', 'float', 'bool', 'string', 'version', 'dict', 'list')

        # tv = ttk.Treeview(self, show='tree', takefocus=True)
        tv = ttk.Treeview(self, takefocus=True)
        self.tv = tv
        self.setCenter(tv)
        self.__registerEvents()

        self.addBtns = KeyOptionBar(self)
        self.addBtns.setCallback(self.__onBtns)
        self.curCell = None
        self.isAdd = False
        self.items = {}
        self.data = None
        self.callback = None

        self.__setHeads(['key', 'type', 'value'])

    def setData(self, data) :
        self.clear()
        data = self.__formatData(data)
        self.__insertItem(data, '')
        self.data = data
        self.__checkEmpty()

    def setCallback(self, callback):
        self.callback = callback

    def setSupportTypes(self, types) :
        if isinstance(types, list) or isinstance(types, tuple) :
            self.types = tuple(set(self.supportTypes) & set(types))

    def clear(self, root='') :
        for i in self.tv.get_children(root) :
            self.tv.delete(i)
            self.items.pop(i)

    def __setHeads(self, heads) :
        self.heads = heads
        l = len(heads)
        if l > 0 :
            c = [str(i) for i in range(2, l+1)]
            self.tv.configure(columns=c)
            i = 0
            for h in heads :
                i += 1
                if i > 1 :
                    self.tv.column(str(i), width=200)
                    self.tv.heading(str(i), text=str(h))
                else :
                    self.tv.heading('#0', text=h)


    def __insertItem(self, data, preItem='', idx=tk.END): 
        if isinstance(data, dict) :
            for key in tuple(data.keys()) :
                d = data.get(key)
                if (isinstance(d, list) or isinstance(d, tuple)) and len(d) == 2:

                    t = d[0]
                    item = None
                    if t == 'dict' :
                        item = self.tv.insert(preItem, idx, open=False, text=key, values = [t,])
                        self.__insertItem(d[1], item)
                    elif t == 'list' :
                        item = self.tv.insert(preItem, idx, open=False, text=key, values = [t,])
                        d = d[1]
                        _d = {}
                        for i in range(len(d)):
                            _d[i] = d[i]
                        self.__insertItem(_d, item)
                    else :
                        item = self.tv.insert(preItem, idx, text=key, values=d)
                    if item :
                        self.items[item] = key                        

    def __registerEvents(self) :
        self.tv.bind('<Motion>', self.__onMotion)
        self.tv.bind('<Double-1>', self.__onDoubleClick)

    def __onMotion(self, event) :
        x = event.x
        y = event.y
        column = self.tv.identify_column(x)
        row = self.tv.identify_row(y)
        pos = (column, row)
        if not equals(pos, self.curCell) :
            self.curCell = pos
            region = self.tv.identify_region(x, y)
            if region == 'tree' or region == 'cell' :
                self.tv.selection_set(row)
                values = self.__getTVByRow(row)
                box = self.tv.bbox(row, column)
                if region == 'tree' :
                    self.addBtns.setData(row, box, values[0] in ('dict', 'list'))
            elif self.data is not None and len(self.data.keys()) > 0:
                self.addBtns.setData(None)

    def __onDoubleClick(self, event) :
        x = event.x
        y = event.y
        column = self.tv.identify_column(x)
        row = self.tv.identify_row(y)
        self.editCell(column, row)

    def editCell(self, column, row) :
        self.isAdd = False
        self.curCell = (column, row)
        # self.__getParents(row)
        p = self.tv.parent(row)
        t = 'dict'
        if p != '' :
            t = self.__getTVByRow(p)[0]
        values = self.__getTVByRow(row)
        edit = ConfEditView(self, callback=self.__onEditEnd, types=self.types, width=240, height=250)
        edit.setData(
            [self.__getKeyByRow(row),] + values + [row, tk.END], 
            focusIdx=int(column.replace('#', '')), 
            editName=t!='list'
            )

        self.wait_window(edit)

    def __onBtns(self, func, row) :
        values = self.__getTVByRow(row)
        index = tk.END
        parent = self.tv.parent(row)
        key = 'key'
        focusIdx=0
        if func == 'addItem' :
            self.isAdd = True
            index = self.tv.index(row)+1
        elif func == 'addSubItem' :
            self.isAdd = True
            parent = row
            index = len(self.tv.get_children(parent))
        elif func == 'delItem' :
            self.isAdd = False
            self.__delRow(row)
            return
        pt = 'dict'
        if parent != '' :
            pt = self.__getTVByRow(parent)[0]
        if pt == 'list' :
            key = index
            focusIdx = 2
        edit = ConfEditView(self, callback=self.__onEditEnd, types=self.types, width=240, height=250)
        edit.setData([key, 'string', 'value' , parent, index], focusIdx=focusIdx, editName=pt!='list')
        self.wait_window(edit)

    def __delRow(self, row) :
        keys = self.__getKeysFromRoot(row, False)
        data = self.__getDataByKeys(keys)
        key = self.__getKeyByRow(row)
        parent = self.tv.parent(row)
        if len(self.__getTVByRow(parent)) and self.__getTVByRow(parent)[0] == 'list' :
            idx = self.tv.index(row)
            grand = self.tv.parent(parent)
            pIdx = self.tv.index(parent)
            pKey = self.__getKeyByRow(parent)
            del data[1][(idx)]
            self.tv.delete(parent)
            self.__insertItem({pKey:data}, grand, pIdx)
        elif isinstance(data, dict) :
            # 数据根节点
            data.pop(key)
            self.tv.delete(row)
        else :
            data[1].pop(key)
            self.tv.delete(row)

        self.__notifyChange()

    def __addRow(self, row, data, index) :
        keys = self.__getKeysFromRoot(row)
        _data = self.__getDataByKeys(keys)

        key = data[0]
        value = ()
        if len(data) > 3 :
            value = data[1:3]
        else :
            value = data[1:]
        t = value[0]
        if row == '' :
            if key in tuple(_data.keys()) :
                ShowInfoDialog(u'key: "%s"已经存在！'%key)
                return False
            _data[key] = value
        elif _data[0] == 'dict' :
            if key in tuple(_data[1].keys()) :
                ShowInfoDialog(u'key: "%s"已经存在！'%key)
                return False
            _data[1][key] = value
        elif _data[0] == 'list' :
            if index == tk.END :
                _data[1].append(value)
            else :
                # 当在 不是 list 末尾的地方添加数据，删除list 所在节点，重新生成
                _data[1].insert(index, value)
            grand = self.tv.parent(row)
            pIdx = self.tv.index(row)
            pKey = self.__getKeyByRow(row)
            self.tv.delete(row)
            self.__insertItem({pKey:_data}, grand, pIdx)
            self.__notifyChange()
            return True

        self.__insertItem({key:value}, row, index)
        self.__notifyChange()
        return True

    def __editRow(self, row, data) :
        ok, ot, ov = self.__getKTVByRow(row)
        t = data[1]
        if ot != t and (t == 'dict' or t == 'list' or ot == 'dict' or ot == 'list') :
            if not ShowAskDialog(u'是否修改数据类型:\n%s---->%s\n修改后数据将丢失！！！'%(ot, t), u'确认修改') :
                return False

        pKeys = self.__getKeysFromRoot(row, False)
        pData = self.__getDataByKeys(pKeys)
        if isinstance(pData, tuple) and len(pData) == 2 :
            pData = pData[1]
        parent = self.tv.parent(row)
        keys = self.__getKeysFromRoot(row)
        _data = self.__getDataByKeys(keys)
        pt = 'dict'
        if parent != '' :
            pt = self.__getTVByRow(parent)[0]
        idx = self.tv.index(row)

        k, t, v = data
        if k == ok :
            if t == ot :
                if v != ov :
                    # 值不同的情况下
                    if t in ('dict', 'list') :
                        self.tv.item(row, text=k, values=(t,))
                    else :
                        if pt == 'dict' :
                            pData[k] = (t, v)
                        elif pt == 'list' and idx == int(k) :
                            pData[idx] = (t, v)
                            k = int(k)
                        self.tv.item(row, text=k, values=(t, v))
            else :
                # type 不同的情况下
                if t in ('dict', 'list') :
                    _v = {}
                    if t == 'list' :
                        _v = []
                    if ot != t :
                        if pt == 'dict' :
                            pData[k] = (t, _v)
                        elif pt == 'list' and idx == int(k) :
                            pData[idx] = (t, _v)
                            k = int(k)
                        self.tv.item(row, text=k, values=(t,))
                        self.clear(row)
                else :
                    if pt == 'dict' :
                        pData[k] = (t, v)
                    elif pt == 'list' and idx == int(k) :
                        pData[idx] = (t, v)
                        k = int(k)
                    self.tv.item(row, text=k, values=(t, v))
                    if ot == 'dict' or ot == 'list' :
                        self.clear(row)
        else :
            # 如果 key 都变化了
            if pt == 'dict' : 
                # _data = pData.pop(ok)
                _d = pData.pop(ok)
            elif 'list' and isinstance(pt, int) :
                pData.remove(_data)

            if t == ot :
                if v != ov :
                    # 值不同的情况下
                    if t in ('dict', 'list') :
                        if pt == 'dict' :
                            pData[k] = (t, _data)
                        elif pt == 'list' and idx == int(k) :
                            pData[idx] = (t, _data)
                            k = int(k)
                        self.tv.item(row, text=k, values=(t,))
                    else :
                        if pt == 'dict' :
                            pData[k] = (t, v)
                        elif pt == 'list' and idx == int(k) :
                            pData[idx] = (t, v)
                            k = int(k)
                        self.tv.item(row, text=k, values=(t, v))
                else :
                    # 值相同
                    if pt == 'dict' :
                        pData[k] = (t, v)
                    elif pt == 'list' and idx == int(k) :
                        pData[idx] = (t, v)
                        k = int(k)
                    self.tv.item(row, text=k, values=(t, v))
            else :
                # 类型也改变了
                if t in ('dict', 'list') :
                    _v = {}
                    if t == 'list' :
                        _v = []
                    if ot != t :
                        if pt == 'dict' :
                            pData[k] = (t, _v)
                        elif pt == 'list' and idx == int(k) :
                            # list 暂不支持更换 idx 
                            pData[idx] = (t, _v)
                        self.tv.item(row, text=k, values=(t,))
                        self.clear(row)
                else :
                    if pt == 'dict' :
                        pData[k] = (t, v)
                    elif pt == 'list' and idx == int(k) :
                        pData[idx] = (t, v)
                    self.tv.item(row, text=k, values=(t, v))
                    if ot == 'dict' or ot == 'list' :
                        self.clear(row)
        self.__notifyChange()
        return True


    def __onEditEnd(self, data, item=None, index=tk.END) :
        if self.isAdd :
            return self.__addRow(item, data, index)
        else :
            return self.__editRow(item, data)

    def __formatData(self, data) :
        def func(t, v) :
            # t, v = data.get(key)
            if t in ('int', 'float', 'bool', 'string', 'version' ) :
                d[key] = (t, v)
            elif t == 'list' and (isinstance(v, list) or isinstance(v, tuple)) :
                newV = []
                for _v in v :
                    newV.append(func(_v[0], _v[1]))
                v = newV
            elif t == 'dict' and isinstance(v, dict) :
                newV = {}
                for _k in tuple(v.keys()) :
                    _v = v.get(_k)
                    newV[_k] = func(_v[0], _v[1])
                v = newV
            return (t, v)

        d = {}
        for key in tuple(data.keys()) :
            v = data.get(key)
            d[key] = func(v[0], v[1])
        return d

    def __getParents(self, item):
        path = []
        p = self.tv.parent(item)
        while p != '' :
            path.insert(0, p)
            p = self.tv.parent(p)
        return path

    def __getKeysFromRoot(self, item, includSelf=True) :
        keys = []
        for row in self.__getParents(item) :
            keys.append(self.__getKeyByRow(row))
        if includSelf : 
            keys.append(self.__getKeyByRow(item))
        return keys

    def __getKeyByRow(self, row) :
        return self.tv.item(row, 'text')

    def __getTVByRow(self, row) :
        values = list(self.tv.item(row, 'values'))
        if len(values) > 2 :
            values = values[:2]
            self.tv.item(row, values=values)
        elif len(values) == 1 :
            if values[0] == 'dict' :
                values.append({})
            elif values[0] == 'list' :
                values.append([])
        return values

    def __getKTVByRow(self, row) :
        return [self.__getKeyByRow(row), ] + self.__getTVByRow(row)

    def __getDataByKeys(self, keyPath) :
        paths = list(keyPath)
        if len(paths) > 0 and paths[0] == '' :
            paths = paths[1:]
        data = self.data
        for key in paths :
            if data :
                if isinstance(data, tuple) or isinstance(data, list) :
                    if data[0] == 'list' :# isinstance(key, int) and  :
                        data = data[1][int(key)]
                    else :
                        data = data[1].get(key)
                # 只有数据根节点是这个情况
                elif isinstance(data, dict):
                    data = data.get(key)
            else :
                print('__getDataByKeys error , keyPath:', keyPath)
                return None
        return data

    def __notifyChange(self) :
        # import json
        self.addBtns.setData(None)
        self.__checkEmpty()
        # print(json.dumps(self.data, indent=2))

        if self.callback :
            self.callback(self.data)

    def __checkEmpty(self) :
        self.data = self.data or {}
        if len(list(self.data.keys())) == 0 :
            # TODO:设置合适的位置
            self.addBtns.setData('', (10, 10, 100, 40))


class KeyOptionBar(ttk.Frame):
    """docstring for KeyOptionBar"""
    def __init__(self, *args, **dArgs):
        ttk.Frame.__init__(self, *args, **dArgs)
        self.row = None
        self.callback = None

        addBtn = ttk.Button(self, text='+', width=2, command=self.__onAddItem)
        delBtn = ttk.Button(self, text='-', width=2, command=self.__onDelItem)
        addSubBtn = ttk.Button(self, text=u'\u21AB', width=2, command=self.__onAddSubItem)

        addBtn.pack(side=tk.LEFT)
        delBtn.pack(side=tk.RIGHT)
        # addSubBtn.pack(side=tk.RIGHT)

        self.addBtn = addBtn
        self.delBtn = delBtn
        self.addSubBtn = addSubBtn

    def setCallback(self, callback) :
        self.callback = callback
        
    def setData(self, row, box=None, addsub=False) :
        if box :
            self.place(x=box[0]+box[2], y=box[1]+box[3]/2, anchor=tk.E)
        else :
            self.place(x=-100, y=-100)
        self.row = row
        if addsub :
            self.addSubBtn.pack(side=tk.RIGHT)
        else :
            self.addSubBtn.pack_forget()

    def getRow(self) :
        return self.row

    def __onAddItem(self) :
        if self.callback :
            self.callback('addItem', self.row)

    def __onDelItem(self) :
        if self.callback :
            self.callback('delItem', self.row)

    def __onAddSubItem(self):
        if self.callback :
            self.callback('addSubItem', self.row)

class ConfEditView(tk.Toplevel):
    """docstring for ConfEditView"""
    def __init__(self, *args, **dArgs):
        callback = dArgs.get('callback')
        if callback :
            dArgs.pop('callback')
        supportTypes = dArgs.get('types')
        if supportTypes :
            dArgs.pop('types')
            if not (isinstance(supportTypes, list) or isinstance(supportTypes, tuple)) :
                supportTypes = None
        supportTypes = supportTypes or ('int', 'float', 'bool', 'string', 'version', 'dict', 'list')
        tk.Toplevel.__init__(self, *args, **dArgs)
        
        self.configure(takefocus=True)
        self.data = []
        self.propagate(0)

        frame = ttk.Frame(self)
        frame.pack(expand=tk.YES, fill=tk.BOTH, padx=10, pady=6)

        fn = ttk.LabelFrame(frame, text='key:')
        fn.pack(expand=tk.YES, fill=tk.BOTH)

        ft = ttk.LabelFrame(frame, text='type:')
        ft.pack(expand=tk.YES, fill=tk.BOTH)

        fv = ttk.LabelFrame(frame, text='value:')
        fv.pack(expand=tk.YES, fill=tk.BOTH)

        nameV = tk.StringVar()
        entryName = ttk.Entry(fn, textvariable=nameV)
        entryName.pack(expand=tk.YES, fill=tk.BOTH)
        self.entryName = entryName
        self.nameV = nameV

        combobox = Combobox(ft, callbcak=self.changeType, values=supportTypes)
        combobox.pack(expand=tk.YES, fill=tk.BOTH)
        self.combobox = combobox

        valueV = tk.StringVar()
        entryValue = ttk.Entry(
            fv, 
            textvariable=valueV, 
            validate='all', 
            validatecommand=(frame.register(self.__validateValue), '%P', '%V', '%s'),
            invalidcommand=(frame.register(self.__onInvalid), '%P', '%V', '%s')
        )
        
        self.entryValue = entryValue
        self.valueV = valueV

        v = tk.IntVar()
        checkBtn = ttk.Checkbutton(fv, variable=v)
        self.checkBtn = checkBtn
        self.checkV = v

        version = VersionWidget(fv)
        version.setShowInfo(False)
        self.version = version
        version.pack(expand=tk.YES, fill=tk.BOTH)

        ttk.Button(frame, text=u'确定', command=lambda *a: self.__onKeyEnter()).pack(pady=10)

        self.curWeidget = version

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        self.callback = callback
        self.bind('<Return>', self.__onKeyEnter)
        self.bind('<Escape>', self.__onKeyEsc)

        self.lastValid = ''
        self.focusIdx = 0
        self.cancleEdit = True

        centerToplevel(frame)

    def setData(self, data, focusIdx=0, editName=True) :
        self.data = data
        self.focusIdx = focusIdx

        n, t, v = data[:3]
        self.changeType(t, False)
        self.fresh()
        state = (editName and tk.NORMAL or tk.DISABLED)
        self.entryName.configure(state=state)
        if not editName :
            focusIdx = min(1, focusIdx)

    def __getValue(self) :
        t = self.data[1]
        if t == 'int' or t == 'float' :
            v = self.entryValue.get().strip()
            if v == '' or v == '-' :
                return '0'
            else :
                return v
        elif t == 'string' :
            return str(self.valueV.get().replace('\\n', '\n'))
            # self.entryValue.configure(text=value)
        elif t == 'bool' :
            return str(bool(self.checkV.get()))
        elif t == 'version' :
            return self.version.getVersion()
        elif t == 'dict' :
            return {}
        elif t == 'list' :
            return []

    def changeType(self, t, nextFocus=True) :
        if self.curWeidget :
            self.curWeidget.pack_forget()
            self.curWeidget = None
        self.curWeidget = None
        if t in ('int', 'float', 'string') :
            self.curWeidget = self.entryValue
            # self.entryValue.configure(text=value)
        elif t == 'bool' :
            self.curWeidget = self.checkBtn
        elif t == 'version' :
            self.curWeidget = self.version

        if self.curWeidget :
            self.lastValid = ''
            self.curWeidget.pack(expand=tk.YES, fill=tk.BOTH)
        self.combobox.setValue(t)
        self.data[1] = t

        if nextFocus :
            self.focusIdx = 2

    def fresh(self) :
        n, t, v = self.data[:3]
        self.nameV.set(n)
        valid = True
        if not self.__validateValue(v) :
            valid = False

        if t in ('int', 'float', 'string') :
            self.valueV.set(valid and str(v) or '')
        elif t == 'bool' :
            v = bool(v) and 1 or 0
            self.checkV.set(valid and v or 0)
        else :
            self.version.setVertion(v)

        focusIdx = self.focusIdx
        
        if focusIdx == 0 :
            self.entryName.focus()
            self.entryName.select_range(0, tk.END)
        elif focusIdx == 1 :
            self.combobox.focus()
        elif focusIdx == 2 and self.curWeidget:
            self.curWeidget.focus()
            if t in ('int', 'float', 'string') :
                self.entryValue.select_range(0, tk.END)

    def setCallback(self, callback) :
        self.callback = callback

    def __validateValue(self, *content) :
        import re
        textBefore = content[0]
        if textBefore == '' :
            return True
        t = self.data[1]
        ret = False
        if len(self.data) >= 3:
            t = self.data[1]
            if t == 'int' :
                ret = re.match(r'^[-]?\d*$', textBefore) is not None
            elif t == 'float' :
                ret = re.match(r'^[-]?\d*(\.\d*)?$', textBefore) is not None
            elif t == 'bool' :
                ret = textBefore in ('0', '1')
            else :
                ret = True
        else :
            print(u'数据错误') 
            print(self.data)
        if ret :
            if len(content) == 3 :
                self.lastValid = content[2]
            else :
                self.lastValid = ''
        return ret

    def __onInvalid(self, *content) :
        self.valueV.set(self.lastValid)

    def destroy(self, *args, **dArgs) :
        import traceback

        data = (self.entryName.get(), self.data[1], self.__getValue())
        canDes = True
        if self.callback and not self.cancleEdit :
            try:
                canDes = self.callback(data, self.data[3], self.data[4])
            except Exception as e:
                ShowInfoDialog('%s\n%s'%(repr(e), traceback.format_exc()))
        if canDes :
            tk.Toplevel.destroy(self, *args, **dArgs)


    def __onKeyEnter(self, event=None) :
        self.cancleEdit = False
        self.destroy()

    def __onKeyEsc(self, event=None) :
        self.cancleEdit = True
        self.destroy()

def __main() :
    path = os.getcwd()
    testCall = True

    m = ConfigEditor()
    m.pack(expand=YES,fill=BOTH)



    data = {
        'test1':('string', 'test1str',),
        'testDic':('dict', {
            'a':('string', 'aStr'),
            'b':('string', 'bStr'),
            't':('dict', {
                'a':('string', 'aStr'),
                'b':('string', 'bStr'),
            }),
        }),
        'testList':('list', (('string', 'list1'), ('int', 1)))
    }
    m.setData(data)
    def printData(d) :
        import json
        print(json.dumps(d, indent=2))

    m.setCallback(lambda d:printData(d))
    centerToplevel(m)

    m.mainloop()

if __name__ == '__main__' :

    __main()
