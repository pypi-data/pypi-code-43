from selenium import webdriver
import pandas as pd
import sys
import time
from sqlalchemy import create_engine, types
import psycopg2
import re
import pymssql
import cx_Oracle
import MySQLdb
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from threading import Semaphore
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from lmfscrap.fake_useragent import UserAgent


class page:
    def __init__(self,add_ip_flag=False):
        self.add_ip_flag = add_ip_flag
        self.image_show_html=1
        self.ua = UserAgent()
        self.add_ip()
        self.headless = True
        self.pageloadstrategy = 'normal'
        self.pageloadtimeout = 40
        self.get_ip_url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        self.tmp_q = Queue()
        self.ip_q = Queue()

        self.sema = Semaphore(1)
        self.__init_localhost_q(num=0)

    def get_driver(self, ip=None):

        chrome_option = webdriver.ChromeOptions()
        if ip is not None: chrome_option.add_argument("--proxy-server=http://%s" % (ip))
        if self.headless:
            chrome_option.add_argument("--headless")
            chrome_option.add_argument("--no-sandbox")
            chrome_option.add_argument('--disable-gpu')

        prefs = {
            'profile.default_content_setting_values': {'images': self.image_show_html, }
        }

        chrome_option.add_experimental_option("prefs", prefs)

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = self.pageloadstrategy  # complete#caps["pageLoadStrategy"] = "eager" # interactive#caps["pageLoadStrategy"] = "none"
        args = {"desired_capabilities": caps, "chrome_options": chrome_option}

        driver = webdriver.Chrome(**args)
        driver.maximize_window()

        driver.set_page_load_timeout(self.pageloadtimeout)
        return driver

    def add_ip(self):
        if self.add_ip_flag:
            # 获取本机ip，是否在白名单中
            try:
                try:
                    r = requests.get("http://www.trackip.net/", timeout=10, headers={'User-Agent': self.ua.random, 'Cookie': '__cfduid=d5cc00aa0983286bb09108ccaef017a2e1563845122; _ga=GA1.2.200115857.1563845158; _gid=GA1.2.766328626.1563845158'}, ).text

                except:
                    r = requests.get("http://200019.ip138.com/", timeout=10, headers={'User-Agent': self.ua.random}).text
                ip = r[r.find('title') + 6:r.find('/title') - 1]
                ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                i = 3
                while ip == []:
                    try:
                        r = requests.get("http://www.trackip.net/", timeout=10, headers={'User-Agent': self.ua.random}).text
                    except:
                        r = requests.get("http://200019.ip138.com/", timeout=10, headers={'User-Agent': self.ua.random}).text
                    ip = r[r.find('title') + 6:r.find('/title') - 1]
                    ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                    i -= 1
                    if i < 0: break
                ip = ip[0]
                i = 3
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
                        print("ip : [ %s ] 已经在白名单中" % ip)
                        break
                    if "最多数量" in r["msg"]:
                        time.sleep(1)
                        x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s&index=5""" % ip
                        r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()

                    if "成功" in r["msg"]:
                        print("添加ip%s" % ip)
                        break
                    i -= 1
                    time.sleep(1)

            except:
                traceback.print_exc()
        else:
            print('[Do_Not]:不执行添加本地ip到白名单的操作。')

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
        except Exception as e:
            traceback.print_exc()
            ip = False
        finally:
            self.sema.release()
        return ip

    def __init_localhost_q(self, num=2):
        self.localhost_q = Queue()
        for i in range(num): self.localhost_q.put(i)

    def __init_tmp_q(self, arr):
        self.tmp_q.queue.clear()
        for i in arr:
            self.tmp_q.put(i)

    def __read_thread(self, f):
        conp = self.conp
        if self.localhost_q.empty():

            ip = self.get_ip()
            # ip="1.28.0.90:20455"
            print("本次ip %s" % ip)
            if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                print("ip不合法")
                return False

            try:
                driver = self.get_driver(ip)
 
            except Exception as e:
                traceback.print_exc()

                driver.quit()
                return False
        else:
            try:
                print("使用本机ip")
                self.localhost_q.get(block=False)
                driver = self.get_driver()
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
                self.db_write(conp, x, df)
                time.sleep(0.1)
                size = self.tmp_q.qsize()
                if size % 100 == 0: print("还剩 %d 页" % size)

            except Exception as e:
                traceback.print_exc()
                msg = traceback.format_exc()
                print("[Page_Error]:第 %s 页面异常" % x)
                if "违反" in msg: continue
                if "invalid URL" in msg: continue
                self.tmp_q.put(x)
                driver.quit()
                return False
        driver.quit()
        print("[Thread_Done]:线程正常退出")
        return True

    def read_thread(self, f, page_retry=10):
        num = page_retry
        flag = self.__read_thread(f)
        while not flag and num > 0:
            num -= 1

            ##设置线程最后启动时必须为 本机 ip
            if num < 3:
                self.localhost_q.put(1)

            print("切换ip,本线程第 %d 次，已经消耗ip %d 个" % (page_retry - num,self.ip_q.qsize()))
            flag = self.__read_thread(f)

    def read_threads(self, f, arr, num=10,page_retry=10):
        bg = time.time()
        ths = []
        dfs = []
        print(arr[:3])
        total = len(arr)
        if total <= 5: num = 1
        if total != 0:
            if num / total > 1:
                num = int(total / 5) + 1 if int(total / 5) + 1 < 4 else num

        print("本次共 %d 个页面,共 %d 个线程, 重复尝试次数 %s 次。" % (total, num, page_retry))

        self.__init_tmp_q(arr)
        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f,page_retry))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q(num=2)
        left_page = self.tmp_q.qsize()
        print("[Remaining_Num]:剩余 %d 页" % (left_page))
        if left_page > 0:
            self.read_thread(f, page_retry)
            left_page = self.tmp_q.qsize()
            print("[Remaining_Num]:剩余 %d 页" % (left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("耗时 %d 秒" % cost)
        else:
            print("耗时 %.4f 分" % (cost / 60))
        print("[Read_Threads_Done]:read_threads_page结束")

    def db_write(self, conp, href, page):

        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        sql = """insert into %s.%s values($lmf$%s$lmf$,$lmf$%s$lmf$)""" % (conp[4], conp[5], href, page)
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

    def db_write_many(self, conp, data):

        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        sql = """insert into %s.%s values(href,page)""" % (conp[4], conp[5])
        cur = con.cursor()
        cur.executemany(sql, data)
        con.commit()
        cur.close()
        con.close()

    def db_command(self, sql, conp):

        """db_command 仅仅到数据库"""
        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

    def write(self, **arg):

        """
        :param krg:

        ipNum: 使用ip数量，默认值是3
        thread_retry : f1 线程重试的次数   默认值为7
        retry  :  f2  获取总页数 重试次数  默认值为10
        get_ip_url  : 获取代理ip的 url
        add_ip_flag : 是否添加本地ip到白名单      默认值 False
        page_retry : page页面爬取的重复次数    默认值为 7
        image_show_gg : 爬取gg页面是否展示图片   1 为展示,2 为不展示 默认为 1
        image_show_html : 爬取html页面是否展示图片   1 为展示,2 为不展示 默认为 1

        :return:

        """

        tb = arg['tb']
        conp = arg["conp"]

        f = arg["f"]
        num = arg["num"]
        arr = arg["arr"]
        if "headless" not in arg.keys():
            self.headless = True
        else:
            self.headless = arg["headless"]

        if "image_show_html" not in arg.keys():
            self.image_show_gg=1
        else:
            self.image_show_gg=arg["image_show_html"]

        if "pageloadstrategy" not in arg.keys():
            self.pageloadstrategy = "normal"
        else:
            self.pageloadstrategy = arg["pageloadstrategy"]

        if "pageloadtimeout" not in arg.keys():
            self.pageloadtimeout = 40
        else:
            self.pageloadtimeout = arg["pageloadtimeout"]
        if "page_retry" not in arg.keys():
            page_retry = 6
        else:
            page_retry = arg["page_retry"]

        sql = "create table if not exists %s.%s(href text,page text,primary key(href))" % (conp[4], tb)
        self.db_command(sql, conp)
        print("创建表if不存在")
        conp.append(tb)
        print(conp)
        self.conp = conp
        self.read_threads(f=f, num=num, arr=arr,page_retry=page_retry)
        return self.tmp_q.qsize()
