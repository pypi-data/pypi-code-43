
import os,time
class MyFrame(wx.Frame):
    
    #设置默认delay时间值
    delayDefault = "2"
    #设置默认种子数
    seedDefault = "5000000"
    #设置默认执行次数
    executionFrequencyDefault = "60000000"
    logDir = "./"
    def __init__(self):
        #执行方式定义
            excuteMode = ["忽略程序崩溃",
                        "忽略程序无响应",
                        "忽略安全异常",
                        "出错中断程序",
                        "本地代码导致的崩溃",
                        "默认"
                        ]
            #日志输出等级区分
            logMode = ["简单","普通","详细"]
            executionModeDefault = excuteMode[0]
            #初始化菜单按钮
            menuBar = wx.MenuBar()
            menu1 = wx.Menu("")
            menuBar.Append(menu1, "File")
            self.SetMenuBar(menuBar)
            #初始化标签栏
            wx.StaticText(panel, -1, "种子数:", pos=(xPos, yPos))
            self.seedCtrl = wx.TextCtrl(panel, -1, "", pos=(xPos1, yPos))
            #绑定点击事件
            self.seedCtrl.Bind(wx.EVT_KILL_FOCUS, self.OnAction)
            self.seedCtrl.SetFocus()
            #初始化标签栏
            wx.StaticText(panel, -1, "执行次数:", pos=(xPos, yPos+yDelta))
            #设置窗口位置
            self.excuteNumCtrl = wx.TextCtrl(panel, -1, "", pos=(xPos1, yPos+yDelta))
            #初始化标签栏
            wx.StaticText(panel, -1, "延时:", pos=(xPos, yPos+2*yDelta))
            self.delayNumCtrl = wx.TextCtrl(panel, -1, "", pos=(xPos1, yPos+2*yDelta))
            #初始化标签栏       
            wx.StaticText(panel, -1, "执行方式:", pos=(xPos, yPos+3*yDelta))
            #设置窗口位置
            self.excuteModeCtrl = wx.ComboBox(panel, -1, "", (xPos1,yPos+3*yDelta), choices=excuteMode,style=wx.CB_DROPDOWN)
    #设置初始化checklistbox，下拉菜单
            self.checkListBox = wx.CheckListBox(panel, -1, (xPos, yPos+4*yDelta ), (400, 350), [])
            wx.StaticText(panel, -1, "日志输出等级:", pos=(xPos, yPoslayout-yDelta))
            self.logModeCtrl = wx.ComboBox(panel, -1, "", (xPos1,yPoslayout-yDelta), choices=logMode,style=wx.CB_DROPDOWN)
    
            #初始化按钮，读取程序包按钮绑定readButton事件
            self.readButton = wx.Button(panel, -1, "读取程序包", pos=(xPos, yPoslayout))
            self.Bind(wx.EVT_BUTTON, self.OnReadClick, self.readButton)
            self.readButton.SetDefault()
            #初始化默认参数按钮，绑定defaultButton事件
            self.defaultButton = wx.Button(panel, -1, "默认参数", pos=(xPos, yPoslayout+yDelta))
            self.Bind(wx.EVT_BUTTON, self.OnResetClick, self.defaultButton)
            self.defaultButton.SetDefault()
            #初始化一键monkey按钮，按钮绑定quick事件
            self.quickButton = wx.Button(panel, -1, "一键Monkey", pos=(xPos+120, yPoslayout+yDelta))
            self.Bind(wx.EVT_BUTTON, self.OnQuickStartClick, self.quickButton)
            self.quickButton.SetDefault()
#生成log函数

    def OnBuildLog(self,event):
        os.chdir(self.logDir)  
        #通过日期创建唯一标识文件名称
        date = time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))
        dir_m = "Monkey_Log_"+date.replace("-","")
        dir0 = "sdcard0_log"
        创建目标文件目录
        if (os.path.exists(dir_m+"/"+dir0)):
            print ("already exists")
        else:
            os.system("mkdir -p "+dir_m+"/"+dir0)
        os.chdir(dir_m)
        #通过adb命令导出log文件到目标文件夹中
        os.system("adb pull /storage/sdcard0/log/ "+dir0)
        #查找异常log文件
        self.BuildFatalLog(os.getcwd())

    #遍历所有的log文件函数
def ListFiles(self,path):
    #遍历文件件
        for root,dirs,files in os.walk(path):
            log_f = ""
            for f in files:
                if(f.find("main") == 0):
                    log_f = f.strip()
                    #切换到目标目录
                    os.chdir(root)
                    #通过grep 命令查找所有的异常文件
                    if (log_f != ""):
                        grep_cmd = "grep-Eni-B2-A20'FATAL|error|exception|system.err|androidruntime' " + log_f + " > " + log_f + "_fatal.log"
                        os.system(grep_cmd)

    #查找异常文件函数
def BuildFatalLog(self,path):
    self.ListFiles(path)

#读取程序包函数声明
def OnReadClick(self, event):
    #清空控件内容
        self.checkListBox.Clear()
        #通过读取手机data/data目录来确认所有的包名
        os.system("adb shell ls data/data > ~/log.log")
        #解析log.log文件
        home = os.path.expanduser('~')
        f = open(home+"/log.log", 'r')
        line = f.readline()
        while line:
            line = f.readline()
            if (line != ""):
                print ("===="+line)
                #将解析的包名，添加包名checkbox中显示
                self.checkListBox.Append(line)
        f.close()


if __name__ == '__main__':
    pass
    

