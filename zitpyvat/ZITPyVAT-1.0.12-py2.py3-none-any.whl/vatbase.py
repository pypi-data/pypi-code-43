# -*- coding: utf-8 -*-
# @Time    : 2017/1/24 8:25
# @Author  : Liu Gang
# @Site    : 
# @File    : Vatbase.py
# @Software: PyCharm Community Edition

import csv
import time
import os
import ftplib
import struct
import logging
from socket import *
from threading import Thread, enumerate

try:
    import ConfigParser as configparser
    from ConfigParser import NoSectionError, NoOptionError
except ImportError:
    import configparser
    from configparser import NoSectionError, NoOptionError

# __all__ = ["Vatbase", "CfgSet", "LOGGER_PATH", "VAT_BASE_VER", "gettime", "NoSectionError", "NoOptionError"]

_CFG_FILE = "Config\\config.ini"
LOGGER_PATH = 'Config\\logging.ini'

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01, 19Jun2018, Liu Gang Add Config Set functions
V1.00.02, 03Aug2018, Liu Gang Vatbase.file_open, add model name.
V1.00.03, 21May2019, Liu Gang Add Python 3.
V1.00.04, 24May2019, Liu Gang Add Read file ,before set...
V1.00.05, 19Oct2019, Liu Gang revise getvalue
V1.00.06, 21Oct2019, Liu Gang Add ftpclient,tftp Server
--------------------
"""
VAT_BASE_VER = "V1.00.06"

logging.config.fileConfig(LOGGER_PATH)
logger = logging.getLogger("vatbase")

class StdReturn:
    def __init__(self):
        self.result = False
        self.data = list()
        self.ret_str = str()
        self.ret_str_gb = str()


def gettime(time_format=0):
    """
    get system current time
    :param time_format: the format for return value
    :return:
    """
    if time_format == 0:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    elif time_format == 1:
        return time.strftime("%Y%m%d", time.localtime(time.time()))
    elif time_format == 2:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


class Vatbase:
    def __init__(self):
        self.fn = None
        self.writer = None
        self.isopen = False
        self.headprinted = False
        if os.path.exists("Log") is False:
            logger.debug("No Dir Name 'Log'")
            os.mkdir("Log")

        # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # def __del__(self):
    #     # self.s.close()
    #     # if self.fn is not None:
    #     #     # tmplist = []
    #     #     # wstr = "---TestEnd---"
    #     #     # tmplist.append(wstr)
    #     #     # self.writer.writerow(tmplist)
    #     #     # tmplist.remove(wstr)
    #     #     # tmplist.append("")
    #     #     # self.writer.writerow(tmplist)
    #     #     self.fn.close()
    #     #     self.isopen = False

    def log_tail(self):
        tmplist = []
        wstr = "---TestEnd---"
        tmplist.append(wstr)
        self.writer.writerow(tmplist)
        tmplist.remove(wstr)
        tmplist.append("")
        self.writer.writerow(tmplist)
        self.fn.close()
        self.isopen = False

    def faillog_head(self):
        if self.headprinted is True:
            return True

        if self.isopen is False:
            try:
                self.fn = open('Log\\FailLog' + gettime(1) + '.csv', 'ab+')
            except IOError:
                logger.error("File Open Error")
                return False
            self.isopen = True

        self.writer = csv.writer(self.fn)
        tmplist = []

        wstr = '---TestStart---'
        tmplist.append(wstr)
        self.writer.writerow(tmplist)
        tmplist.remove(wstr)
        tmplist.append(gettime(2))
        self.writer.writerow(tmplist)
        del tmplist
        self.headprinted = True
        return True

    def file_open(self, sel=1, model_name=""):
        """
        file open and print the default head content for log
        :param sel:1 for test log, 0 for platform fail log
        :param model_name:model name ,in file name .
        :return:bool

        180803, add model name.  Liugang

        """
        # if os.getcwd()

        try:
            if sel == 1:
                self.fn = open('Log\\TestLog' + "_%s_" % model_name + gettime(1) + '.csv', 'ab+')
            else:
                self.fn = open('Log\\FailLog' + "_%s_" % model_name + gettime(1) + '.csv', 'ab+')

        except IOError:
            logger.error("File Open Error")
            return False
        self.isopen = True
        self.writer = csv.writer(self.fn)
        if sel == 1:
            tmplist = []
            wstr = '---TestStart---'
            tmplist.append(wstr)
            self.writer.writerow(tmplist)
            tmplist.remove(wstr)
            tmplist.append(gettime(2))
            self.writer.writerow(tmplist)
            tmplist = ["Item", "Low", "High", "Value", "Result", "Time"]
            self.writer.writerow(tmplist)
            self.headprinted = True
            del tmplist

        return True

    def faillog_close(self):
        if self.fn is not None:
            self.fn.close()
            self.isopen = False
        self.isopen = False

    def d_print(self, *str_data):
        """
        print to csv file
        :param str_data:data to print
        :return:
        """
        if self.isopen is False:
            self.file_open(0)

        if self.headprinted is False:
            self.faillog_head()

        str_list = list()
        for s in str_data:
            str_list.append(s)
        self.writer.writerow(str_list)
        # print str_list

        # def udpsend(self, txstr):
        #     """
        #     Udp send , communicate with QT VAT platform
        #     :param txstr:
        #     :return:
        #     """
        #     global _HOST_IP
        #     txstr = txstr.decode("utf-8")
        #     txstr = txstr.encode("gb2312")
        #     c = self.s.sendto(txstr, _HOST_IP)
        #     if c > 0:
        #         return True
        #     else:
        #         return False


class CfgSet:
    def __init__(self, fn=_CFG_FILE):
        self.conf = configparser.ConfigParser()
        self.fn = fn

    def readfile(self):
        if len(self.conf.read(self.fn)) == 0:
            return False
        else:
            return True

    def getsections(self):
        return self.conf.sections()

    def getoptions(self, sec):
        return self.conf.options(sec)

    def getvalue(self, sec, opt, dtype='s'):
        try:
            if dtype == 's':  # get for string
                return self.conf.get(sec, opt)
            elif dtype == 'f':  # get for float
                return self.conf.getfloat(sec, opt)
            elif dtype == 'i':  # get for int
                return self.conf.getint(sec, opt)
        except NoOptionError:
            self.setvalue(sec, opt, "0")
            ret = 0 if dtype == 's' else "0"
            return ret

    def getlist(self, sec, dtype='s'):
        optionlen = len(self.getoptions(sec))
        lists = [0] * optionlen
        for i in range(0, optionlen):
            lists[i] = self.getvalue(sec, self.getoptions(sec)[i], dtype)

        return lists

    def setvalue(self, sec, opt, set_value):
        # Add readfile before change. 190524 liugang
        self.readfile()
        try:
            self.conf.set(sec, opt, set_value)
        except NoSectionError:
            self.conf.add_section(sec)
            self.conf.set(sec, opt, set_value)
        finally:
            with open(self.fn, "w") as configfile:
                self.conf.write(configfile)
            self.readfile()
            return True


class ftp_client:

    def __init__(self, user, pwd, server_ip, server_port=21, debug_level=0):
        self.ftp = ftplib.FTP()
        self.ftp.set_debuglevel(debug_level)
        self.ip = server_ip
        self.port = server_port
        self.user = user
        self.pwd = pwd
        self.ret = StdReturn()

    def ftp_login(self):
        self.ret.result = True
        try:
            self.ftp.connect(self.ip, self.port)
        except Exception as e_exp:
            self.ret.ret_str = "FTP Connect Fail!{0}".format(e_exp)
            self.ret.ret_str_gb = "FTP 连接失败!{0}".format(e_exp)
            self.ret.resutl = False
        else:
            try:
                self.ftp.login(self.user, self.pwd)
            except ftplib.error_perm:
                self.ret.ret_str = "FTP Login Fail!"
                self.ret.ret_str_gb = "FTP 登陆失败!"
                self.ret.result = False
            else:
                self.ret.ret_str = "FTP Login Success!"
                self.ret.ret_str_gb = "FTP 登录成功!"

        return self.ret

    def file_transmit(self, src_file, rmt_file):
        self.ret.result = True
        self.ftp.voidcmd('TYPE I')
        file_remote = "{0}.temp".format(rmt_file)
        file_local = src_file
        buf_size = 1024  # 设置缓冲器大小

        with open(file_local, 'rb') as fp:
            try:
                self.ftp.storbinary('STOR ' + file_remote, fp, buf_size)
            except Exception as e_exp:
                self.ret.ret_str = "Download Fail!{0}".format(e_exp)
                self.ret.ret_str_gb = "下载失败!{0}".format(e_exp)
                self.ret.result = False
            else:
                self.ftp.rename(file_remote, rmt_file)
                self.ret.ret_str = "Download Complete!"
                self.ret.ret_str_gb = "下载完成!"

        self.ftp.quit()
        return self.ret


class tftp_srv:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.ret = StdReturn()
        self.run_flag = False
        self.opr_flag = False

    # 客户端下载线程
    def tftp_srv_dl_thr(self, file_name, client_info):
        file_num = 0  # 表示接收文件的序号
        try:
            f = open(file_name, 'rb')
        except Exception as e_exp:
            # 打包
            error_data = struct.pack('!HHHb', 5, 5, 5, file_num)
            # 发送错误信息
            self.s.sendto(error_data, client_info)  # 文件不存在时发送
            self.ret.ret_str = e_exp
            self.ret.ret_str_gb = e_exp
            self.ret.result = False
            self.run_flag = False
            exit()  # 退出下载线程
        else:
            while True:
                # 从本地服务器中读取文件内容512字节
                read_file_data = f.read(512)
                file_num += 1
                # 打包
                send_data = struct.pack('!HH', 3, file_num) + read_file_data
                # 向客户端发送文件数据
                self.s.sendto(send_data, client_info)  # 数据第一次发送
                if len(send_data) < 516:
                    logger.debug('User' + str(client_info) + ': Download ' + file_name + ' file complete!')
                    self.ret.ret_str = "File Download Success!"
                    self.ret.ret_str_gb = "文件传输完成!"
                    break
                # 第二次接收数据
                response_data = self.s.recvfrom(1024)
                # print(responseData)
                recv_data, client_info = response_data
                # print(recvData, client_info)
                # 解包
                packet_opt = struct.unpack("!H", recv_data[:2])  # 操作码
                packet_num = struct.unpack("!H", recv_data[2:4])  # 块编号
                # print(packetOpt, packetNum)
                if packet_opt[0] != 4 or packet_num[0] != file_num:
                    self.ret.ret_str_gb = "文件传输错误！"
                    self.ret.ret_str = "File Transmit Error!"
                    self.ret.result = False
                    self.run_flag = False
                    logger.error(self.ret.ret_str)
                    break

            # 关闭文件
            f.close()
            # 退出下载线程
            self.opr_flag = False
            exit()

    # 客户端上传线程
    def tftp_srv_up_thr(self, file_name, client_info):
        self.ret.result = True
        file_num = 0  # 表示接收文件的序号
        # 以二进制方式打开文件
        f = open(file_name, 'wb')
        # 打包
        send_data_first = struct.pack("!HH", 4, file_num)
        # 回复客户端上传请求
        self.s.sendto(send_data_first, client_info)  # 第一次用随机端口发送
        while True:
            file_num += 1
            response_data = self.s.recvfrom(1024)  # 第二次客户连接我随机端口
            recv_data, client_info = response_data
            packet_opt = struct.unpack("!H", recv_data[:2])  # 操作码
            packet_num = struct.unpack("!H", recv_data[2:4])  # 块编号
            # print(packet_opt[0], packet_num[0])
            # 客户端上传数据
            if packet_opt[0] == 3 and packet_num[0] == file_num:
                # 　保存数据到文件中
                f.write(recv_data[4:])
                # 　打包
                send_data = struct.pack("!HH", 4, file_num)
                # 回复客户端ACK信号
                self.s.sendto(send_data, client_info)  # 第二次用随机端口发
                if len(recv_data) < 516:
                    logger.debug('User' + str(client_info) + ' :upload ' + file_name + ' file complete!')
                    self.ret.ret_str = "File Upload Success!"
                    self.ret.ret_str_gb = "文件上传完成!"
                    logger.debug(self.ret.ret_str)
                    break
        # 关闭文件
        f.close()
        # 退出上传线程
        self.opr_flag = False
        exit()

    def exit_force(self):
        self.ret.ret_str = "Force Exit!"
        self.ret.ret_str_gb = "TFTP 退出!"
        self.ret.result = False
        self.run_flag = False
        exit_flag = False
        while not exit_flag:
            ret_list = enumerate()
            for ret in ret_list:
                if ret.getName() == "tftp_dl" or ret.getName == "tftp_up":
                    time.sleep(1)
                    logger.debug("Re find")
                    break

            exit_flag = True
        logger.debug("Exit Success!")

    def srv_run(self):
        self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self.s.bind(('', 69))
        except error as err:
            self.ret.ret_str = err
            self.ret.ret_str_gb = err
            self.ret.result = False
            return self.ret

        self.run_flag = True
        while self.run_flag:
            # 接收客户端发送的消息
            if not self.opr_flag:
                # print("Waiting for command!")
                self.s.settimeout(2)
                try:
                    recv_data, client_info = self.s.recvfrom(1024)  # 第一次客户连接69端口
                    # print(client_info, recv_data)
                except error:
                    # print(err)
                    continue
                else:
                    ret = recv_data.find("octet")
                    # 解包
                    if ret != -1:
                        self.s.settimeout(5)
                        op_code = struct.unpack('!H', recv_data[:2])  # 操作码
                        file_name = recv_data[2:ret - 1].decode('gb2312')  # 文件名
                        file_name = "{0}\\{1}".format(self.base_dir, file_name)
                        # print(op_code, file_name)
                        # 请求下载
                        self.opr_flag = True
                        if op_code[0] == 1:
                            t = Thread(target=self.tftp_srv_dl_thr, args=(file_name, client_info), name="tftp_dl")
                            t.start()  # 启动下载线程

                        # 请求上传
                        elif op_code[0] == 2:
                            t = Thread(target=self.tftp_srv_up_thr, args=(file_name, client_info), name="tftp_up")
                            t.start()  # 启动上传线程
                        else:
                            self.opr_flag = False
            time.sleep(0.5)

        self.s.close()
        logger.debug("srv_run tftp!")
        return self.ret


if __name__ == "__main__":
    # ftpclient = ftp_client("root", "zlits", "10.86.38.28", 2121)
    # ret = ftpclient.ftp_login()
    # print(ret.ret_str)
    # ret = ftpclient.file_transmit("ratb5.py", "ratb5.py")
    # print(ret.ret_str)
    tftp = tftp_srv()
    thr = Thread(target=tftp.srv_run)
    thr.setDaemon(False)
    thr.start()
    time.sleep(15)
    tftp.exit_force()
