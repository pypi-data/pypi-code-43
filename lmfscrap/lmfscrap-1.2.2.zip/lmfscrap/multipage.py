import datetime
from dateutil.relativedelta import relativedelta
from lmf.dbv2 import db_write, db_query, db_command
from selenium import webdriver
import pandas as pd
import sys
import time, math
from sqlalchemy import create_engine, types
import re
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from threading import Semaphore

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lmfscrap.fake_useragent import UserAgent


def singleton(cls, *args, **kwargs):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


# @singleton
class web:
    def __init__(self, add_ip_flag=False):
        self.add_ip_flag = add_ip_flag
        self.image_show_gg = 1
        self.ua = UserAgent()
        self.add_ip()
        self.headless = True
        self.pageloadstrategy = 'normal'
        self.pageloadtimeout = 40
        self.url = "http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"
        self.get_ip_url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        self.result_q = Queue()
        self.tmp_q = Queue()
        self.ip_q = Queue()
        self.long_ip_q = Queue()
        self.__init_tmp_q(10)
        self.sema = Semaphore(1)
        # 本地ip数量设置
        self.__init_localhost_q(localNum=0)
        self.long_ip_url = ""
        self.long_ip_num = 20

    def get_driver(self, ip=None):

        chrome_option = webdriver.ChromeOptions()
        if ip is not None: chrome_option.add_argument("--proxy-server=http://%s" % (ip))
        if self.headless:
            chrome_option.add_argument("--headless")
            chrome_option.add_argument("--no-sandbox")
            chrome_option.add_argument('--disable-gpu')

        prefs = {
            'profile.default_content_setting_values': {'images': self.image_show_gg, }
        }

        chrome_option.add_experimental_option("prefs", prefs)

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = self.pageloadstrategy
        # complete#caps["pageLoadStrategy"] = "eager" # interactive#caps["pageLoadStrategy"] = "none"
        args = {"desired_capabilities": caps, "chrome_options": chrome_option}

        driver = webdriver.Chrome(**args)
        driver.maximize_window()
        driver.set_page_load_timeout(self.pageloadtimeout)
        return driver

    def add_ip(self):
        # 获取本机ip，是否在白名单中
        if not self.add_ip_flag:
            print('[Do_Not]:不执行添加本地ip到白名单的操作.')
        else:
            try:
                try:
                    r = requests.get("http://www.trackip.net/", timeout=10, headers={'User-Agent': self.ua.random}).text

                except:
                    r = requests.get("http://200019.ip138.com/", timeout=10,
                                     headers={'User-Agent': self.ua.random}).text
                ip = r[r.find('title') + 6:r.find('/title') - 1]
                ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                i = 3
                while ip == []:
                    try:
                        r = requests.get("http://www.trackip.net/", timeout=10,
                                         headers={'User-Agent': self.ua.random}).text
                    except:
                        r = requests.get("http://200019.ip138.com/", timeout=10,
                                         headers={'User-Agent': self.ua.random}).text
                    ip = r[r.find('title') + 6:r.find('/title') - 1]
                    ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                    i -= 1
                    if i < 0: break
                ip = ip[0]
                i = 3
                ips = None
                while i > 0:
                    x = """http://http.zhiliandaili.cn/Users-whiteIpListNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc"""
                    r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()

                    if "data" in r.keys():
                        ips = r["data"]
                        print('ips', ips)
                        break
                    else:
                        time.sleep(1)
                        i -= 1
                if ips == None:
                    return False
                if ip in ips:
                    print("%s 已经在白名单中" % ip)
                    return True
                i = 3

                while i > 0:
                    x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s""" % ip
                    r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()
                    if "存在" in r["msg"]:
                        print("[Already_in_white_list]:IP:[ %s ] 已经在白名单中." % ip)
                        break
                    if "最多数量" in r["msg"]:
                        time.sleep(1)
                        x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s&index=5""" % ip
                        r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()

                    if "成功" in r["msg"]:
                        print("[Add_Succeed]:添加 IP %s ," % ip)
                        break
                    i -= 1
                    time.sleep(1)
                self.add_ip_flag = False
            except:
                traceback.print_exc()

    def get_ip(self, get_ip_url=False):
        if get_ip_url is False: get_ip_url = self.get_ip_url
        # print(self.get_ip_url)
        self.sema.acquire()
        i = 3
        try:
            url = get_ip_url
            r = requests.get(url, timeout=40, headers={'User-Agent': self.ua.random})
            time.sleep(1)
            ip = r.text
            while re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None and i > 0:
                time.sleep(3 - i)
                i -= 1
                url = get_ip_url
                r = requests.get(url, timeout=40, headers={'User-Agent': self.ua.random})
                time.sleep(1)
                ip = r.text
            self.ip_q.put(r.text)
        except:
            ip = False
        finally:
            self.sema.release()
            if ip:
                if '登录IP不是白名单IP，请在用户中心添加该白名单. Please add ip to white list' in ip:
                    self.add_ip_flag = True
                    self.add_ip()
                    self.get_ip()
        return ip

    ###################################--- 获取长效ip ---##########################################

    def select_long_ip(self, long_ip_conp):
        sql1 = """
        select ip,ExpireTime from %s.long_ip_cfg;
        """ % (long_ip_conp[4])
        df = db_query(sql1, dbtype="postgresql", conp=long_ip_conp)
        if df.values.tolist():
            data = df.sample(frac=1).values.tolist()
        else:data = df.values.tolist()
        return data


    # 入口
    def get_long_ips(self):
        long_ip_conp = self.long_ip_conp
        # 获取数据库中的IP
        data = self.select_long_ip(long_ip_conp)
        if data:
            len_data = int(len(data))
        else:
            len_data = 0
        print("数据库中有 {} 条长效IP,long_ip Num".format(len_data))

        if len_data != 0:
            for d in data:
                d_ip, d_ExpireTime = d[0], d[1]
                # 获取当前时间
                end_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
                d1 = datetime.datetime.strptime('{}'.format(d_ExpireTime), '%Y-%m-%d %H:%M:%S')
                d2 = datetime.datetime.strptime('{}'.format(end_time), '%Y-%m-%d %H:%M:%S')
                # # 比较时间差值
                delta = d1 - d2
                if delta.days >= 0:
                    self.long_ip_q.put(d_ip)



    ###########################################################################

    def __init_localhost_q(self, localNum=2):
        self.localhost_q = Queue()
        for i in range(localNum): self.localhost_q.put(i)

    def __init_total(self, f2, ipNum=3, retry=5):
        num = retry - ipNum
        if num < 0:
            num = 0
            ipNum = retry
        # self.long_ip_num = retry - ipNum
        if self.long_ip:
            print("""[Get_page]:总共 %s 次尝试爬取页面总量，代理ip爬 %s 次，剩余 %s 长效 ip 爬取.""" % (retry, ipNum, num))
        else:
            print("""[Get_page]:总共 %s 次尝试爬取页面总量，代理ip爬 %s 次，剩余 %s 本地 ip 爬取.""" % (retry, ipNum, num))
        m = ipNum

        while num > 0:
            # 本地 IP or 长效 IP
            if self.long_ip:
                try:
                    if self.long_ip_q.empty():
                        self.get_long_ips()
                    ip = self.long_ip_q.get(block=False)
                    # ip="1.28.0.90:20455"
                    print("本次长效 IP %s" % ip)
                    if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                        print("ip不合法")
                        return False
                    try:
                        print("使用长效IP")
                        driver = self.get_driver(ip)
                        driver.get(self.url)
                        self.total = f2(driver)
                    except Exception as e:
                        driver.quit()
                        traceback.print_exc()
                        raise ValueError('[Get_Page_Error]:url 地址错误 或 f2获取总页数错误.')
                    print("[Get_page]:用长效IP获取总量,全局 %d 页面." % self.total)
                    return "sccess"
                except Exception as e:
                    traceback.print_exc()
                    num -= 1
                    print("[Get_Page_Error]:用长效IP获取总量,第 %d 次失败." % (retry - ipNum - num))
            else:
                try:
                    try:
                        driver = self.get_driver()
                        driver.get(self.url)
                        self.total = f2(driver)
                    except Exception as e:
                        driver.quit()
                        traceback.print_exc()
                        raise ValueError('[Get_Page_Error]:url 地址错误 或 f2获取总页数错误.')
                    print("[Get_page]:用本地IP获取总量,全局 %d 页面." % self.total)
                    return "sccess"
                except Exception as e:
                    traceback.print_exc()
                    num -= 1
                    print("[Get_Page_Error]:用本地ip获取总量,第 %d 次失败." % (retry - ipNum - num))
        while m > 0:
            # 短期代理 IP
            try:
                ip = self.get_ip()
                # ip="1.28.0.90:20455"
                print("代理 IP %s" % ip)
                try:
                    driver = self.get_driver(ip)
                    driver.get(self.url)
                    self.total = f2(driver)
                except Exception as e:
                    driver.quit()
                    traceback.print_exc()
                    raise ValueError('[Get_Page_Error]:url 地址错误 或 f2获取总页数错误.')
                print("[Get_page]:用代理IP获取总量,全局 %d 页面." % self.total)
                return "sccess"
            except Exception as e:
                traceback.print_exc()
                m -= 1
                print("[Get_Page_Error]:用代理 IP 获取总量,第 %d 次失败" % (ipNum - m))

        return "failed"

    def __init_tmp_q(self, total):
        self.tmp_q.queue.clear()
        for i in range(total):
            self.tmp_q.put(i + 1)

    def __read_thread(self, f):
        url = self.url
        if self.localhost_q.empty():
            ip = self.get_ip()
            # ip="1.28.0.90:20455"
            print("本次 IP %s" % ip)

            if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                print("ip不合法")
                return False
            try:
                driver = self.get_driver(ip)
                driver.get(url)
            except:
                traceback.print_exc()
                driver.quit()
                return False

        else:
            if self.long_ip:
                if self.long_ip_q.empty():
                    self.get_long_ips()
                ip = self.long_ip_q.get(block=False)
                # ip="1.28.0.90:20455"
                print("长效IP %s" % ip)
                if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                    print("ip不合法")
                    return False
                try:
                    print("使用长效IP %s"%ip)
                    self.localhost_q.get(block=False)
                    driver = self.get_driver(ip)
                    driver.get(url)
                except:
                    traceback.print_exc()
                    driver.quit()
                    return False
            else:
                try:
                    print("使用本地IP")
                    self.localhost_q.get(block=False)
                    driver = self.get_driver()
                    driver.get(url)
                except Exception as e:
                    traceback.print_exc()

                    driver.quit()
                    return False

        while not self.tmp_q.empty():
            try:
                x = self.tmp_q.get(block=False)
            except:
                traceback.print_exc()
                continue
            if x is None: continue
            try:
                df = f(driver, x)
                self.result_q.put(df)

            except Exception as e:
                traceback.print_exc()
                msg = traceback.format_exc()
                print("[Page_Error]:第 %d 页面异常" % x)
                if "违反" not in msg:
                    self.tmp_q.put(x)
                driver.quit()
                return False
        driver.quit()
        print("[Thread_Done]:线程正常退出")
        return True

    def read_thread(self, f, thread_retry=5):

        num = thread_retry
        flag = self.__read_thread(f)
        while not flag and num > 0:
            num -= 1

            ##设置线程最后启动时必须为 本机 ip
            if num < 3:
                self.localhost_q.put(1)

            print("[Switch_Ip]:切换 IP ,本线程第 %d 次,已经消耗 IP %d 个" % (thread_retry - num, self.ip_q.qsize()))
            flag = self.__read_thread(f)

    def read_threads(self, f, num=10, total=100, ipNum=3, thread_retry=5):
        bg = time.time()
        ths = []
        dfs = []
        if total == 0:
            print("[Info] : 总共 0 页,线程不启动，任务结束")
            return False
        if total < 2: num = 1
        if num / total > 1: num = int(total / 5) + 1 if int(total / 5) + 1 < 4 else num
        if total / num < 10: num = int(total / 10) + 1
        localNum = num - ipNum
        if localNum < 0: localNum = 0
        if ipNum > num: ipNum = num
        if not self.long_ip:
            print("[Thread_Start]:开始爬[%s],本次共 %d 个页面,共 %d 个线程，代理IP %s 个，本地IP %s 个." % (self.url, total, num, ipNum, localNum))
        else:
            print("[Thread_Start]:开始爬[%s],本次共 %d 个页面,共 %d 个线程，代理IP %s 个，长效IP %s 个." % (self.url, total, num, ipNum, localNum))

        self.result_q.queue.clear()
        self.__init_tmp_q(total)
        self.__init_localhost_q(localNum=localNum)

        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f, thread_retry))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q(localNum=localNum)
        left_page = self.tmp_q.qsize()
        print("[Remaining_Num]:剩余 %d 页." % (left_page))
        if left_page > 0:
            self.read_thread(f, thread_retry)
            left_page = self.tmp_q.qsize()
            print("[Remaining_Num]:剩余 %d 页." % (left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("[Spend_Time]:耗时 %d --秒" % cost)
        else:
            print("[Spend_Time]:耗时 %.4f 分" % (cost / 60))
        print("[Work_Over]:read_threads 结束")

    def getdf_from_result(self):
        if self.result_q.empty():
            return pd.DataFrame(data=[])
        dfs = list(self.result_q.queue)
        df = pd.concat(dfs, ignore_index=False)
        return df

    def getdf(self, url, f1, f2, total, num, ipNum, retry=10, thread_retry=5):
        if ipNum > 10: ipNum = 10
        if ipNum < 0: ipNum = 0
        if retry < 0: retry = 0

        self.url = url
        self.__init_total(f2, ipNum=ipNum, retry=retry)
        self.__init_tmp_q(self.total)
        if total is None:
            total = self.total
        elif total > self.total:
            total = self.total
        if num is None: num = 10
        if total == 0: return pd.DataFrame()
        self.read_threads(f=f1, num=num, total=total, ipNum=ipNum, thread_retry=thread_retry)
        df = self.getdf_from_result()
        return df

    def write(self, **krg):
        """
        :param krg:

        ipNum: 使用ip数量，默认值是3
        thread_retry : f1 线程重试的次数   默认值为5
        retry  :  f2  获取总页数 重试次数  默认值为10
        get_ip_url  : 获取代理ip的 url
        add_ip_flag : 是否添加本地ip到白名单      默认值 False
        page_retry : page页面爬取的重复次数    默认值为 10
        image_show_gg : 爬取gg页面是否展示图片   1 为展示,2 为不展示 默认为 1
        image_show_html : 爬取html页面是否展示图片   1 为展示,2 为不展示 默认为 1
        long_ip_conp: 存放长效IP的数据库,分阿里云以及昆明环境，  默认为["postgres", "since2015", "192.168.3.171", "postgres", "public"]
        long_ip: 是否使用长效IP，   默认值 True,使用长效IP
        # long_ip_url: 获取长效IP的链接
        # long_ip_num: 获取长效IP的个数   默认值 20
        :return:
        """
        url = krg["url"]
        f1 = krg["f1"]
        f2 = krg["f2"]
        tb = krg["tb"]
        col = krg["col"]
        # headless=krg["headless"]
        if "total" not in krg.keys():
            total = None
        else:
            total = krg["total"]

        if "num" not in krg.keys():
            num = None
        else:
            num = krg["num"]

        if "ipNum" not in krg.keys():
            ipNum = 3
        else:
            ipNum = krg["ipNum"]

        if "thread_retry" not in krg.keys():
            thread_retry = 6
        else:
            thread_retry = krg["thread_retry"]

        if "retry" not in krg.keys():
            retry = 5
        else:
            retry = krg["retry"]

        if "dbtype" not in krg.keys():
            dbtype = "postgresql"
        else:
            dbtype = krg["dbtype"]
        if "conp" not in krg.keys():
            conp = ["postgres", "since2015", "127.0.0.1", "postgres", "public"]
        else:
            conp = krg["conp"]

        if "image_show_gg" not in krg.keys():
            self.image_show_gg = 1
        else:
            self.image_show_gg = krg["image_show_gg"]

        if "add_ip_flag" not in krg.keys():
            self.add_ip_flag = False
        else:
            self.add_ip_flag = krg["add_ip_flag"]

        if "get_ip_url" not in krg.keys():
            self.get_ip_url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        else:
            self.get_ip_url = krg["get_ip_url"]

        if "headless" not in krg.keys():
            self.headless = True
        else:
            self.headless = krg["headless"]

        if "pageloadstrategy" not in krg.keys():
            self.pageloadstrategy = 'normal'
        else:
            self.pageloadstrategy = krg["pageloadstrategy"]

        if "pageloadtimeout" not in krg.keys():
            self.pageloadtimeout = 40
        else:
            self.pageloadtimeout = krg["pageloadtimeout"]

        if krg.get("loc")=="aliyun":
            self.long_ip_conp = ["postgres", "since2015", "192.168.4.201", "postgres", "public"]
        elif krg.get("loc") == "kunming":
            self.long_ip_conp = ["postgres", "since2015", "192.168.169.89", "postgres", "public"]
        else:
            self.long_ip_conp = ["postgres", "since2015", "192.168.3.171", "postgres", "public"]

        if "long_ip_url" not in krg.keys():
            self.long_ip_url = ""
        else:
            self.long_ip_url = krg["long_ip_url"]

        if "long_ip_num" not in krg.keys():
            self.long_ip_num = 20
        else:
            self.long_ip_num = krg["long_ip_num"]

        if "long_ip" not in krg.keys():
            self.long_ip = True
        else:
            self.long_ip = krg["long_ip"]

        print("[SS]%s 开始,爬取[%s]" % (tb, url))
        if total == 0: return False
        df = self.getdf(url, f1, f2, total, num, ipNum=ipNum, retry=retry, thread_retry=thread_retry)

        if len(df) > 1:
            print("已爬取完成：[%s]" % url)
            # print(df)
            df.columns = col
        else:
            df = pd.DataFrame(columns=col)
            print("暂无数据")
        print("将数据df 写入 %s" % tb)
        db_write(df, tb, dbtype=dbtype, conp=conp, datadict='postgresql-text')
        print("df写入%s完毕" % tb)

    ###页数过多时
    def write_large(self, **krg):
        """
        :param krg:
        ipNum: 使用ip数量，默认值是3
        thread_retry : f1 线程重试的次数   默认值为5
        retry  :  f2  获取总页数 重试次数  默认值为10
        get_ip_url  : 获取代理ip的 url
        add_ip_flag : 是否添加本地ip到白名单      默认值 False
        page_retry : page页面爬取的重复次数    默认值为 10
        image_show_gg : 爬取gg页面是否展示图片   1 为展示,2 为不展示 默认为 1
        image_show_html : 爬取html页面是否展示图片   1 为展示,2 为不展示 默认为 1
        long_ip_conp: 存放长效IP的数据库,分阿里云以及昆明环境，  默认为["postgres", "since2015", "192.168.3.171", "postgres", "public"]
        long_ip: 是否使用长效IP，   默认值 True,使用长效IP
        # long_ip_url: 获取长效IP的链接
        # long_ip_num: 获取长效IP的个数   默认值 20
        :return:
        """

        url = krg["url"]
        f1 = krg["f1"]
        f2 = krg["f2"]
        tb = krg["tb"]
        col = krg["col"]

        # headless=krg["headless"]
        if "total" not in krg.keys():
            total = None
        else:
            total = krg["total"]

        if "num" not in krg.keys():
            num = None
        else:
            num = krg["num"]

        if "dbtype" not in krg.keys():
            dbtype = "postgresql"
        else:
            dbtype = krg["dbtype"]

        if "conp" not in krg.keys():
            conp = ["postgres", "since2015", "127.0.0.1", "postgres", "public"]
        else:
            conp = krg["conp"]

        if "ipNum" not in krg.keys():
            ipNum = 3
        else:
            ipNum = krg["ipNum"]

        if "image_show_gg" not in krg.keys():
            self.image_show_gg = 1
        else:
            self.image_show_gg = krg["image_show_gg"]

        if "get_ip_url" not in krg.keys():
            self.get_ip_url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        else:
            self.get_ip_url = krg["get_ip_url"]

        if "thread_retry" not in krg.keys():
            thread_retry = 6
        else:
            thread_retry = krg["thread_retry"]

        if "retry" not in krg.keys():
            retry = 10
        else:
            retry = krg["retry"]

        if "add_ip_flag" not in krg.keys():
            self.add_ip_flag = False
        else:
            self.add_ip_flag = krg["add_ip_flag"]

        if "headless" not in krg.keys():
            self.headless = True
        else:
            self.headless = krg["headless"]

        if "pageloadstrategy" not in krg.keys():
            self.pageloadstrategy = 'normal'
        else:
            self.pageloadstrategy = krg["pageloadstrategy"]

        if "pageloadtimeout" not in krg.keys():
            self.pageloadtimeout = 40
        else:
            self.pageloadtimeout = krg["pageloadtimeout"]


        if krg.get("loc")=="aliyun":
            self.long_ip_conp = ["postgres", "since2015", "192.168.4.201", "postgres", "public"]
        elif krg.get("loc") == "kunming":
            self.long_ip_conp = ["postgres", "since2015", "192.168.169.89", "postgres", "public"]
        else:
            self.long_ip_conp = ["postgres", "since2015", "192.168.3.171", "postgres", "public"]

        if "long_ip_url" not in krg.keys():
            self.long_ip_url = ""
        else:
            self.long_ip_url = krg["long_ip_url"]

        if "long_ip_num" not in krg.keys():
            self.long_ip_num = 20
        else:
            self.long_ip_num = krg["long_ip_num"]

        if "long_ip" not in krg.keys():
            self.long_ip = True
        else:
            self.long_ip = krg["long_ip"]

        print("[SS]:%s 开始,爬取[%s]" % (tb, url))
        if not total: return False
        df = self.getdf_large(url, f1, f2, total, num, ipNum=ipNum, retry=retry, thread_retry=thread_retry)

        if len(df) > 1:
            print(url)
            # print(df)
            df.columns = col
        else:
            df = pd.DataFrame(columns=col)
            print("暂无数据")
        print("将数据df 写入 %s" % tb)
        db_write(df, tb, dbtype=dbtype, conp=conp, datadict='postgresql-text', if_exists='append')
        print("df写入%s完毕" % tb)

    def read_threads_large(self, f, num=10, total=list(range(100)), ipNum=3, retry=10, thread_retry=5):
        bg = time.time()
        ths = []
        dfs = []
        total_count = len(total)
        localNum = num - ipNum
        self.__init_localhost_q(localNum=localNum)
        if total_count == 0:
            print("0页,线程不启动，任务结束")
            return False
        if total_count < 2: num = 1
        if num / total_count > 1: num = int(total_count / 5) + 1 if int(total_count / 5) + 1 < 4 else num
        if ipNum > num: ipNum = math.ceil(num / 3)
        if not self.long_ip:
            print("[Thread_Start]:开始爬[%s],本次共 %d 个页面,共 %d 个线程，代理ip %s 个，本地 IP %s 个." % (self.url, total_count, num, ipNum, localNum))
        else:
            print("[Thread_Start]:开始爬[%s],本次共 %d 个页面,共 %d 个线程，代理ip %s 个，长效 IP %s 个." % (self.url, total_count, num, ipNum, localNum))
        self.result_q.queue.clear()

        # 生成页码queue
        self.tmp_q.queue.clear()
        for i in total:
            self.tmp_q.put(i + 1)

        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f, thread_retry))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q(localNum=3)
        left_page = self.tmp_q.qsize()
        print("[Remaining_Num]:剩余 %d 页." % (left_page))
        if left_page > 0:
            self.read_thread(f, thread_retry)
            left_page = self.tmp_q.qsize()
            print("[Remaining_Num]:剩余 %d 页." % (left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("耗时 %d --秒" % cost)
        else:
            print("耗时 %.4f 分" % (cost / 60))
        print("[Read_Threads_Done]:结束")

    def getdf_large(self, url, f1, f2, total, num, ipNum, retry=10, thread_retry=5):
        if ipNum > 10: ipNum = 10
        if ipNum < 0: ipNum = 0
        self.url = url

        ##生成页码queue
        self.tmp_q.queue.clear()
        for i in total:
            self.tmp_q.put(i + 1)

        if not total:
            total = list(range(self.total))
        elif len(total) > self.total:
            total = list(range(self.total))

        if num is None: num = 10
        if total == 0: return pd.DataFrame()
        self.read_threads_large(f=f1, num=num, total=total, ipNum=ipNum, retry=retry, thread_retry=thread_retry)
        df = self.getdf_from_result()
        return df

    def get_total(self, f2, url, ipNum=3, retry=10):

        if retry < 0: retry = 5
        if ipNum > retry: ipNum = retry
        num = retry - ipNum
        if num < 0:
            num = 0
            ipNum = retry
        print("""获取需要爬取的页面总量，先用代理ip爬 %s 次，若失败本地ip爬 %s 次""" % (ipNum, num))

        m = ipNum
        while m > 0:
            try:
                ip = self.get_ip()
                print("使用代理IP %s" % ip)
                driver = self.get_driver(ip)

                driver.get(url)

                self.total = f2(driver)
                driver.quit()
                print("[Get_Page]:用代理ip获取总量,全局共 %d 页面." % self.total)
                return self.total
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                m -= 1
                print("[Get_Page_Error]:用代理ip获取总量,第 %d 次失败." % (ipNum - m))
        while num > 0:
            try:
                driver = self.get_driver()
                driver.get(url)
                self.total = f2(driver)
                driver.quit()
                print("[Get_Page]:用本地ip获取总量,全局共 %d 页面." % self.total)
                return self.total
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                num -= 1
                print("[Get_Page_Error]:用本地ip获取总量,第 %d 次失败." % (retry - ipNum - num))

        return "failed"
