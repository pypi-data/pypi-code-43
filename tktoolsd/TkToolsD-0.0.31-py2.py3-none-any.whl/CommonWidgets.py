# -*- coding:utf-8 -*- 
# Date: 2018-03-07 16:41:50
# Author: dekiven

import os
from DKVTools.Funcs import *

if isPython3() :
    import tkinter as tk  
    from tkinter import ttk 
    from tkinter import *
    import tkinter.filedialog as fileDialog
    import tkinter.messagebox as messageBox
else:
    import Tkinter as tk  
    import  ttk
    from Tkinter import *
    import tkFileDialog as fileDialog
    import tkMessageBox as messageBox


Pathjoin = os.path.join
PathExists = os.path.exists
# curDir = os.getcwd()
curDir = os.path.split(sys.argv[0])[0]

def getTk() :
    '''return tk, ttk
    '''
    return tk, ttk

def GetEntry(root, default='', onKey=None) :
    et = StringVar()
    entry = ttk.Entry(root, textvariable=et)
    if isFunc(onKey) :
        entry.bind('<Key>', lambda event : onKey(event.char))

    def getValue() :
        return et.get()
    def setValue(value) :
        return et.set(str(value))
    entry.getValue = getValue
    entry.setValue = setValue
    setValue(default)

    return entry


def GetDirWidget(root, title='', titleUp='', pathSaved = None, callback = None, enableEmpty = False, showOpen = True):
    '''paramas:root, title='', titleUp='', pathSaved = None, callback = None, enableEmpty = False, showOpen = True
    root:           tk 父节点
    title:          显示在Entry左边的标题
    titleUp:        显示在Entry上面的文本
    pathSaved:      默认的路径，会显示都Entry
    callback:       选择好文件夹的回调
    enableEmpty:    没有选择文件夹时是否回调空串
    showOpen:       是否显示打开文件夹的按钮
    '''
    widget = Frame(root)
    widget.columnconfigure(1, weight=1)


    strTitle = StringVar()
    strTitle.set(title)
    Label(widget, textvariable = strTitle).grid(row = 1, column = 0, padx=5)

    strPathD = StringVar()
    strPathD.set(titleUp)
    Label(widget, textvariable = strPathD).grid(row = 0, column = 1, sticky=(N, S, W, E), pady=5)

    strTitle = StringVar()
    strTitle.set(title)
    et = StringVar()
    if pathSaved :
        et.set(pathSaved)

    Entry(widget, textvariable = et).grid(row = 1, column = 1, sticky=(N, S, W, E), pady=5)

    def btnCallback():
        def onChosen(path):
            if path is not None and path != '' or enableEmpty :
                setValue(path)
                if callback is not None :
                    callback(path)
        ShowChooseDirDialog(onChosen, initialdir=et.get())

    def openBtnCallback():
        path = et.get()
        if os.path.exists(path) :
            startFile(path)
        else :
            ShowInfoDialog('文件夹[%s]不存在！'%(str(path)))

    Button(widget, text = 'Search', command = btnCallback).grid(row = 1, column = 2, padx=5)
    if showOpen :
        Button(widget, text = 'Open', command = openBtnCallback).grid(row = 1, column = 3, padx=5)

    widget.strTitle = strTitle
    widget.strPathD = strPathD
    widget.et = et

    def setValue(value):
        et.set(value)
    widget.setValue = setValue

    def getValue() :
        return et.get()
    widget.getValue = getValue

    return widget

def ShowChooseDirDialog(callback=None, **options):  
    '''ShowChooseDirDialog(callback=None, **options)
    callback 回调，传入选中的文件夹名
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : initDir,
        'initialfile' : 'myfile.txt',
        'parent' : root,
        'title' : 'This is a title',
    }可部分或全部不设置  
    '''
    path = fileDialog.askdirectory(**options)
    if isFunc(callback):
        # if not isinstance(path, str):
        #   path = path
        callback(path)


def ShowChooseFileDialog(callback=None, MultiChoose=False, **options):  
    '''ShowChooseFileDialog(callback=None, MultiChoose=False, **options)
    callback 回调，传入选中的文件名Tuple
    MultiChoose 是否是多选模式
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : initDir,
        'initialfile' : 'myfile.txt',
        'parent' : root,
        'title' : 'This is a title',
    }可部分或全部不设置
    '''
    path = None
    if MultiChoose :
        path = fileDialog.askopenfilenames(**options)
    else :
        path = fileDialog.askopenfilename(**options)
    if isFunc(callback) :
        # if not isinstance(path, str):
        #   path = path
        callback(path)

def ShowSaveAsFileDialog(callback=None, **options):
    '''ShowSaveAsFileDialog(callback=None, **options)
    callback 回调，传入保存的文件名
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : initDir,
        'initialfile' : 'myfile.txt',
        'parent' : root,
        'title' : 'This is a title',
    }可部分或全部不设置  
    '''
    path = fileDialog.asksaveasfilename(**options)
    if isFunc(callback) :
        # if not isinstance(path, str):
        #   path = path
        callback(path)

def ShowInfoDialog(msg, title = 'Tips'):
    '''显示一个按钮的消息框。'''
    return messageBox.showinfo(title = title, message = msg)

def ShowAskDialog(msg, title = 'Asking'):
    '''显示有Yes，NO两个选项的提示框。'''
    return messageBox.askokcancel(title = title, message = msg)

def isTkWidget(widget) :
    '''返回widget是否是tk.Widget实例
    '''
    return isinstance(widget, Widget)

def isTK(widget) :
    '''返回widget是否是TK实例
    '''
    return isinstance(widget, Tk)

def getToplevel(widget) :
    '''获取tk(ttk) widget的Toplevel(根节点)
    '''
    if isTkWidget(widget) :
        return widget.winfo_toplevel()
    elif isTK(widget) or isinstance(widget, Toplevel) :
        return widget 

    return None

def centerToplevel(widget) :
    '''将给定widget的Toplevel移到屏幕中央
    最好是在UI布局完成后调用
    '''
    top = getToplevel(widget)
    if top :
        top.update()
        topH = max(top.winfo_reqheight(), top.winfo_height())
        topW = max(top.winfo_reqwidth(), top.winfo_width())
        screenW, screenH = top.maxsize()
        top.geometry('+%d+%d'%((screenW-topW)/2, (screenH-topH)/2))

def getScreenSize(widget) :
    '''通过widget获取屏幕大小（toplevel的最大大小）
    '''
    top = getToplevel(widget)
    if top :
        return top.maxsize()

__quitHandleFuncs = {}
def handleToplevelQuit(widget, callback) :
    '''弃用，直接复写 destroy 方法即可
    捕获给定widget的Toplevel的关闭事件。当Toplevel关闭时调用callback'''
    top = getToplevel(widget)

    funcs = __quitHandleFuncs.get(str(top))
    if funcs is None :
        funcs = []
    if not callback in funcs :
        funcs.append(callback)
    __quitHandleFuncs[str(top)] = funcs

    def quit(*args, **dArgs):
        for f in funcs :
            if isFunc(f) :
                f()
        if __quitHandleFuncs.get(str(top)) :
            del __quitHandleFuncs[str(top)]
        top.destroy()

    if top is not None and isFunc(callback) :
        top.protocol('WM_DELETE_WINDOW', quit)

def startTk(viewCotr, *args, **dArgs) :
    '''传入tk.View的子类构造函数（类名）和除parent之外的参数启动一个tk窗口
如:   startTk(GetDirWidget,  u'选择路径', 'test')
额外参数：
    size： 窗口大小, 以x分割的字符串, 如：500x500
    title: 窗口title,字符串
'''
    root = tk.Tk()

    # size = tryGetDictValue(dArgs, 'size', delete=True)
    size = tryGetDictValue(dArgs, 'size', delete=True)
    if size :
        root.geometry(size)
    title = tryGetDictValue(dArgs, 'title', delete=True)
    if title :
        root.title(title)

    app = viewCotr(root, *args, **dArgs)
    # app.loadConfigs('config/projConfig.json')
    app.pack(fill=tk.BOTH, expand=True)
    centerToplevel(app)
    app.focus_set()
    root.mainloop()

def getMenu( root, *conf ) :
    '''获取menu，如果有绑定热键mac上使用command键代替Ctrl
有子菜单的暂不支持热键设置
不建议在右键菜单中使用热键
示例：
    conf = (
        ('1', (
                ('1-1', __test1),
                ('1-2', __test2),
                'line',
                ('3', (
                        ('3-1', __test1),
                        ('3-2', __test2),
                    )
                ),
            ) 
        ),
        ('2', (
                ('2-1', __test1, 'Ce'),
                ('2-2', __test2),
            ) 
        ),
    )
    root = getToplevel(m)
    menu = getMenu(m, *conf)
    root.config(menu=menu) 

    m: Frame等Tk控件
    '''
    def isLoT(obj) :
        return isinstance(obj, list) or isinstance(obj, tuple)
    def __getMenu(root, menuRoot, *conf) :
        if menuRoot is None :
            menuRoot = tk.Menu(root)
        if isLoT(conf) :
            c1 = conf[0]
            if isStr(c1) :
                label = c1
                c2 = conf[1]
                l = len(conf)

                if isFunc(c2) :
                    accelerator = None
                    bindCom = None
                    if l == 3 :
                        bindCom, accelerator = getHotKeyCommandName(conf[2], True)
                    elif l == 4 :
                        bindCom = conf[2]
                        accelerator = conf[3]
                    menuRoot.add_command(label=label, command=c2, accelerator=accelerator)
                    if bindCom :
                        getToplevel(root).bind(bindCom, c2)

                elif isLoT(c2) :
                    subMenu = __getMenu(root, None, *(c2))
                    if subMenu :
                        menuRoot.add_cascade(label=label, menu=subMenu)
                else :
                    menuRoot.add_separator()
            elif isLoT(c1) :
                for c in conf :
                    __getMenu(root, menuRoot, *c)
        else :
            raise Exception('conf wrong exception')
        return menuRoot

    return __getMenu(root, None, *conf)


def getHotKeyCommandName(com, macUseCommand=False) :
    '''将简单的快捷键转换成bind函数的事件,
参数：
    com：传入的值
    macUseCommand：mac 上是否使用command键替换Ctrl键
返回值：bindCommand, accelerator 
    bindCommand: bind方法事件名
    accelerator: 各平台的按键提示
转换规则如下:
C:      Ctrl
A:      Alt
S:      Shift
*:      AnyKey
W:      鼠标滚轮
(B\\d):  鼠标1~3
(F\\d+):   F1~F12
([a-z]):    a-z
示例：
    win32平台：
    c, a = getHotKeyCommandName(CaF2) 
    c: '<Control-KeyRelease-F2-KeyRelease-a>'
    a: 'Ctrl+F2+A'

keysym文档：
http://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm
    '''
    import re
    patterns = None
    separator = '+'
    if isWindows() or isMac() :
        patterns = {
            'C' : ('Control', 'Ctrl'),
            'S' : ('Shift', 'Shift'),
            'A' : ('Alt', 'Alt'),
            'E' : ('KeyRelease-Escape', 'Escape'),
        }
    # # mac 会自动将 Ctrl、Alt、Shift、Escape、Command 等替换为⌃、⇧、⌥、⎋、⌘，不需要手动转换
    # elif isMac() :
    #     # separator = ''
    #     patterns = {
    #         'C' : ('Control', u'\u2303'),         # 符号 ⌃
    #         'S' : ('Shift', u'\u21e7'),           # 符号 ⇧
    #         'A' : ('Alt', 'Alt'),                 # 符号 ⌥
    #         'E' : ('Escape', u'\u238b'),     # 符号 ⎋
    #     }
    else :
        ShowInfoDialog('only support for win32 and Mac！！！')

    if isMac() and macUseCommand :
        # mac上⌘键使用 Mod1或者 M1 代替，
        # 见https://stackoverflow.com/questions/16379877/how-to-get-tkinter-mac-friendly-menu-shortcuts-cmdkey
        patterns['C'] = ('M1', 'Command') 

    upPatters = (
        (r'B(\d)', 'Button-', 'M_'),
        r'(F\d+)',
        r'([a-z]{1})'
    )
    
    command = []
    accelerator = []

    if patterns :
        patterns['*'] = ('Any-KeyRelease', '*')
        patterns['W'] = ('MouseWheel', 'Scroll')

        for k in list(patterns.keys()) :
            c, a = patterns.get(k)
            # m = re.search(k, com)
            if com.find(k) >= 0 : 
                command.append(c)
                accelerator.append(a)

        for k in upPatters :
            if isinstance(k, tuple) or isinstance(k, list) :
                mc = re.findall(k[0], com)
                for v in mc :
                    command.append(k[1]+v)
                    # print()
                    # v = v.upper()
                    accelerator.append(k[2]+v)
            else :
                mc = re.findall(k, com)
                for v in mc :
                    command.append('KeyRelease-'+v)
                    v = v.upper()
                    accelerator.append(v)

    return '<%s>'%'-'.join(command), separator.join(accelerator) # .encode('utf-8')

# ==================鼠标Enter提示Label  begin----------------
class __ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.x = self.y = 0

    def showtip(self, **labelConfig):
        "Display text in tooltip window"
        if self.tipwindow :
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx()
        y = y + cy + self.widget.winfo_rooty() - 50
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        keys = list(labelConfig.keys())

        if 'bg' not in keys and 'background' not in keys :
            labelConfig['bg'] = '#aaaaff'
        label = tk.Label(tw, **labelConfig)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def regEnterTip(widget, **labelConfig) :
    '''regEnterTip(widget, **labelConfig)
    给widget注册事件，当鼠标移到widget中时显示toolTip
    labelConfig 是tk.Label的构造参数，如：text='toolTip', bg = '#aaaaff'
    '''
    toolTip = __ToolTip(widget)
    def enter(event):
        toolTip.showtip(**labelConfig)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
# ----------------鼠标Enter提示Label  end==================


# ---------------------------------------------test begin --------------------------------------------------

def __testHandleToplevelQuit() :
    f = Frame()
    f.grid()

    l = Label(f, text='test')
    f.grid()

    def handleF() :
        print('f')

    def handleL() :
        print('l')

    handleToplevelQuit(f, handleF)
    handleToplevelQuit(l, handleL)

    f.mainloop()

def __testAskFile() :
    def func(*args, **dArgs) :
        print(args, dArgs)

    ShowChooseFileDialog(func)
    ShowChooseFileDialog(func, True)

def __testGetDirWid() :
    # root = Tk()
    # v = GetDirWidget(root, '选择路径', 'test')
    # v.pack(expand=YES, fill=BOTH)
    # centerToplevel(v)
    # v.mainloop()
    startTk(GetDirWidget,  u'选择路径', 'test')

def __testCenterTop() :
    app = tk.Tk()
    centerToplevel(app)
    app.mainloop()

def __testMenu() :
    '''测试程序菜单栏菜单和右键菜单'''
    def __test1(event=None) :
        print('test1')

    def __test2(event=None) :
        print('test2')

    conf = (
        ('1', (
                ('1-1', __test1),
                ('1-2', __test2),
                'line',
                ('3', (
                        ('3-1', __test1),
                        ('3-2', __test2),
                    )
                ),
            ) 
        ),
        ('2', (
                ('2-1', __test1, 'Ce'),
                ('2-2', __test2),
            ) 
        ),
    )

    m = tk.Frame()
    root = getToplevel(m)
    root.title(u'菜单测试')
    menu = getMenu(m, *conf)
    root.config(menu=menu)

    def onClickRight(event) :
        getMenu(root, *conf).post(event.x_root, event.y_root)
    root.bind('<Button-3>', onClickRight)

    menu.mainloop()

def __main():
    # __testAskFile()
    # __testHandleToplevelQuit()
    # __testGetDirWid()
    # __testCenterTop()
    __testMenu()

if __name__ == '__main__':
    __main()
# ============================================test end ===========================================
