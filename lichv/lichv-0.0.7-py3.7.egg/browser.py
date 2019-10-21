from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from subprocess import *

import time
import sys

class Browser(object):
    driver = None
    devicename = ''
    port = ''
    chromepath = ''
    driverpath = ''
    userdatapath = ''
    """docstring for Brower"""
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__()
        self.args = args
        self.kwargs = kwargs

        if 'device' in kwargs:
            self.setDeviceName(kwargs['device'])
        else:
            self.setDeviceName('*****')

        if 'port' in kwargs:
            self.setPort(kwargs['port'])
        else:
            self.setPort('9999')

        if 'chromePath' in kwargs:
            self.setChromePath(kwargs['chromePath'])
        else:
            self.setChromePath('"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"')

        if 'driverPath' in kwargs:
            self.setDriverPath(kwargs['driverPath'])
        else:
            self.setDriverPath("./chromedriver.exe")

        if 'userDataPath' in kwargs:
            self.setUserDataPath(kwargs['userDataPath'])
        else:
            self.setUserDataPath(".\\userdata"+self.port)

    def setDeviceName(self, name):
        self.devicename = name
        return self

    def setPort(self, port):
        self.port = port
        return self

    def setChromePath(self, chromepath):
        self.chromepath = chromepath
        return self

    def setDriverPath(self, driverpath):
        self.driverpath = driverpath
        return self

    def setUserDataPath(self, userdatapath):
        self.userdatapath = userdatapath
        return self

    def getDriver(self):
        return self.driver

    def existPort(self, port,needClear=False):
        console_length = 0
        browser_length = 0
        all_pids = []
        checked_console_pids = []
        checked_browser_pids = []
        cmd = 'netstat -aon | findstr "'+str(port)+'.*LISTENING"'
        check_cmd = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        for line in iter(check_cmd.stdout.readline, b''):
            print(line)
            strs = str(line).replace('    ',' ').replace('   ',' ').replace('  ',' ')
            strs = strs.strip("'").strip('\\n').strip('\\r').split(' ')
            target  = '127.0.0.1:'+str(port)
            if strs[2]==target:
                console_length += 1
                checked_console_pids.append(strs[-1])
            elif strs[3] == target:
                browser_length += 1
                checked_browser_pids.append(strs[-1])
            all_pids.append(strs[-1])
        if needClear:
            for pid in all_pids:
                Popen('taskkill -f -pid %s' %pid);
                print(self.devicename+'清除进程端口'+pid)
        check_cmd.stdout.close()
        check_cmd.wait()
        return console_length,browser_length,checked_console_pids,checked_browser_pids

    def openSelenium(self, show=False):
        chrome_options = Options()
        if show:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')        # 谷歌文档提到需要加上这个属性来规避bug

        chrome_options.add_argument('disable-infobars')     # 隐藏"Chrome正在受到自动软件的控制"
        chrome_options.add_argument('lang=zh_CN.UTF-8')     # 设置中文

        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:"+str(self.port))
        chrome_driver = self.driverpath
        self.driver = webdriver.Chrome(chrome_driver, options=chrome_options)
        self.driver.set_window_size(1440,880)

        return self.driver

    def openPage(self, url, times=5):
        print('打开网页：['+url+']')
        begin = times + 1
        result = False
        if not url:
            print('链接为空，检查一下了')
            return result

        while not result and times > 0:
            limit = begin - times
            try:
                self.driver.get(url)
                result = True
            except Exception as e:
                print(e)
                print('发生异常，'+str(limit)+'次重新连接: '+url)
                times -= 1
                time.sleep(limit * 5)
        return result

    def init(self):
        check_result = self.existPort(self.port)
        print(check_result)
        if int(check_result[0]) > 0:
            print(self.devicename+'端口'+self.port+'已经有浏览器在打开了')
        else:
            print(self.devicename+'端口'+self.port+'没有在浏览器打开，需要启动浏览器')
            cmd = self.driverpath + ' --remote-debugging-port=%(port)s --user-data-dir="%(name)s" '% dict(port=self.port,name=self.userdatapath)
            ps = Popen(cmd);
            print(self.devicename+'正在启动浏览器...')

        self.driver = self.openSelenium(self.port)

    def getCurrentUrl(self):
        return self.driver.current_url

    def refresh(self):
        return self.driver.refresh()

    def searchBySelectors(self, search):
        try:
            element = self.driver.find_elements_by_css_selector(search)
            return element
        except Exception as e:
            return None

    def searchBySelector(self, search):
        try:
            element = self.driver.find_element_by_css_selector(search)
            return element
        except Exception as e:
            return None

    def searchByClassName(self, search):
        try:
            element = self.driver.find_element_by_class_name(search)
            return element
        except Exception as e:
            return None

    def searchByID(self, search):
        try:
            element = self.driver.find_element_by_id(search)
            return element
        except Exception as e:
            return None

    def serachXpaths(self, search):
        try:
            element = self.driver.find_elements_by_xpath(search)
            return element
        except Exception as e:
            return None

    def serachXpath(self, search):
        try:
            element = self.driver.find_element_by_xpath(search)
            return element
        except Exception as e:
            return None

    def execute_script(self,script,element=None):
        return self.driver.execute_script(script,element)
        
    def close(self):
        if self.driver:
            self.driver.quit()

    def __del__(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print('退出selenium异常：'+str(e))
            

if __name__ == "__main__":
    browser = Browser().setDeviceName('Xinger567')
    browser.init('9221','"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"',".\\userdata" )
    print('ok')
