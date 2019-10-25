# -*- coding: utf-8 -*-
# @CreateTime : 2018/11/26 18:18
# @Author     : Liu Gang
# @File       : py_na_opr.py
# @Software   : PyCharm

# import visa
import pyvisa.highlevel as visa
from pyvisa.errors import VisaIOError
from time import sleep, mktime, strptime
import logging.config
from pyvat.vatbase import LOGGER_PATH
from pyvisa.constants import StatusCode

"""
modification history
--------------------
V1.00.00, 26Nov2018, Liu Gang written
V1.00.01, 23Oct2019, Liu Gang Add Calibration
--------------------
"""
NA_DRV_VER = "V1.00.01"

_ZVB8 = 0
_N9912 = 1


class NA:
    def __init__(self):
        self.is_open = False
        logging.config.fileConfig(LOGGER_PATH)
        self.logger = logging.getLogger("pynaopr")
        self.inst = None
        self.inst_model = int()

    def __del__(self):
        if self.is_open:
            self.close_na()

    def write(self, str_cmd):
        if self.is_open is False:
            self.logger.error("Inst not open")
            return False
        else:
            ret = self.inst.write(str_cmd)
            if ret == StatusCode.success:
                self.logger.error('Command "%s" Execute Fail: %d' % (str_cmd, ret))
                return False
            else:
                self.logger.info('Command "%s" Execute Success!' % str_cmd)
                return True

    def set_timeout(self, f_timeout):
        """
        config time out
        :param f_timeout:ms
        :return:
        """
        self.inst.timeout = f_timeout
        self.logger.info("Set Inst timeout:{0}ms".format(f_timeout))
        return True

    def open_na(self, str_addr="TCPIP0::10.86.20.224::inst0::INSTR"):
        """
        Open NA.
        :param str_addr: inst IP addr
        :return:BOOL
        """
        if self.is_open:
            pass
        else:
            try:
                rm = visa.ResourceManager()
                self.inst = rm.open_resource(str_addr)
            except VisaIOError:
                self.is_open = False
                self.logger.error("NA Open Error")
                return False
            else:
                self.is_open = True
                self.logger.debug("NA Open Success")

        if self.get_na_model() == -1:
            return False

        self.set_timeout(5000)

        return self.is_open

    def get_na_info(self):
        """
        Get inst infomation
        :return:
        """
        return self.inst.query("*IDN?")

    def get_error_info(self, err_str=None):
        str_cmd = "SYST:ERR:ALL?"
        ret = self.inst.query(str_cmd).replace("\n", "").replace("\r", "")
        self.logger.debug("Err Msg:{0}".format(ret))
        if err_str is None:
            return True
        else:
            if ret.count(err_str) != 0:
                return False
            else:
                return True

    def get_na_model(self):
        ret_str = self.get_na_info()
        if ret_str.count("ZVB") != 0:
            self.inst_model = _ZVB8
            self.logger.debug("Inst Model:ZVB8")
        elif ret_str.count("N9912") != 0:
            self.inst_model = _N9912
            self.logger.debug("Inst Model:N9912")
        else:
            self.inst_model = -1
            self.logger.debug("Inst Model:Not Support")

    def close_na(self):
        """
        close inst.
        if is Open ,set auto cal back on .
        :return:
        """
        if self.is_open:
            self.is_open = False
            self.inst.close()
            self.logger.debug("NA Closed!")

        return True

    def init(self):
        """

        :return:
        """
        self.write("*RST;*CLS;")
        sleep(0.5)
        self.write("INIT:CONT 1")
        sleep(0.5)
        if self.inst_model == _N9912:
            if self.write("CALC:PAR:DEF VSWR") is False:
                return False

        elif self.inst_model == _ZVB8:
            if self.write("CALC:PAR:DEF 'Trc1',S11") is False:
                return False

            if self.write("DISP:WIND:STAT ON") is False:
                return False

            if self.write("DISP:WIND:TRAC1:FEED 'Trc1'") is False:
                return False

            if self.write("CALC:FORM SWR") is False:
                return False

        self.logger.info("NA Init Success!")
        return True

    def set_span(self, f_span):
        """
        Set Span
        :param f_span: MHz
        :return:
        """

        if self.write("SENS:FREQ:SPAN %fMHz" % f_span) is False:
            self.logger.error("Set Span Fail")
            return False
        else:
            self.logger.info("Set Span to %.2fMhz" % f_span)
            return True

    def set_cent_freq(self, f_freq):
        """
        Set center Freq
        :param f_freq:MHz
        :return:
        """
        if self.write("SENS:FREQ:CENT %fMHz" % f_freq) is False:
            self.logger.error("Set Center Freq Fail")
            return False
        else:
            self.logger.info("Set Center Freq to %.2fMhz" % f_freq)
            return True

    def set_start_freq(self, f_freq):
        """
        Set start Freq
        :param f_freq:MHz
        :return:
        """
        if self.write("SENS:FREQ:STAR %fMHz" % f_freq) is False:
            self.logger.error("Set Start Freq Fail")
            return False
        else:
            self.logger.info("Set Start Freq to %.2fMhz" % f_freq)
            return True

    def set_stop_freq(self, f_freq):
        """
        Set stop Freq
        :param f_freq:MHz
        :return:
        """
        if self.write("SENS:FREQ:STOP %fMHz" % f_freq) is False:
            self.logger.error("Set Stop Freq Fail")
            return False
        else:
            self.logger.info("Set Stop Freq to %.2fMhz" % f_freq)
            return True

    def set_marker_x(self, x_val, i_no=1):
        """
        Set Marker x Value in MHz
        :param i_no: the Marker No.
        :param x_val: the Value MHz
        :return:
        """
        str_cmd = ""
        if self.inst_model == _N9912:
            str_cmd = "CALC:MARK%d NORM" % i_no
        elif self.inst_model == _ZVB8:
            str_cmd = "CALC:MARK%d ON;:CALC:MARK%d:TYPE NORM" % (i_no, i_no)

        ret = self.write(str_cmd)
        if ret is False:
            self.logger.error("Set Mark No. Fail")
            return False

        ret = self.write("CALC:MARK%d:X %fMHz" % (i_no, x_val))
        if ret is False:
            self.logger.error("Set Marker:%d Freq:%.2fMhz Fail" % (i_no, x_val))
            return False

        self.logger.info("Set Marker:%d Freq:%.2fMhz Success" % (i_no, x_val))
        return True

    def get_marker_y_val(self, i_no=1):
        """
        get marker y value
        :param i_no:
        :return: db Value
        """
        ret = float(self.inst.query(":CALC:MARK{0}:Y?".format(i_no)))
        return ret

    def set_cont_mode(self, i_mode=1):
        """
        Set Continue or Single mode
        :param i_mode: 0,Single, 1, Con
        :return:
        """
        str_cmd = ":INIT:CONT"
        if i_mode == 0:
            str_type = "OFF"
        elif i_mode == 1:
            str_type = "ON"
        else:
            self.logger.warning("no such mode")
            return False

        ret = self.write(str_cmd + " {0}".format(str_type))
        if ret is False:
            self.logger.error("Set Cont Mode {0} Fail".format(str_type))
            return False
        else:
            self.logger.debug("Set Cont Mode {0} Success".format(str_type))
            return True

    def cal_init(self, port_no=1):
        str_cmd = "SENS:CORR:COLL:RSAV:DEF ON"
        if self.write(str_cmd) is False:
            self.logger.error("Start Cal Measure ON Fail")
            return False
        else:
            self.logger.info("Start Cal Measure ON")

        str_cmd = "SENS:CORR:COLL:METH:DEF 'ZITAntTest',FOP,{0}".format(port_no)
        if self.write(str_cmd) is False:
            self.logger.error("Start Cal with Full One Port Mode Fail")
            return False
        else:
            self.logger.info("Start Cal with Full One Port Mode")
            return True

    def cal_meas_open(self, port_no=1):
        str_cmd = "SENS:CORR:COLL:SEL OPEN,{0}".format(port_no)
        if self.write(str_cmd) is False:
            self.logger.error("Cal Open Measure Fail!")
            return False
        else:
            self.logger.info("Cal Open Measure Success!")
            return True

    def cal_meas_short(self, port_no=1):
        str_cmd = "SENS:CORR:COLL:SEL SHOR,{0}".format(port_no)
        if self.write(str_cmd) is False:
            self.logger.error("Cal Short Measure Fail!")
            return False
        else:
            self.logger.info("Cal Short Measure Success!")
            return True

    def cal_meas_match(self, port_no=1):
        str_cmd = "SENS:CORR:COLL:SEL MATC,{0}".format(port_no)
        if self.write(str_cmd) is False:
            self.logger.error("Cal Match Measure Fail!")
            return False
        else:
            self.logger.info("Cal Match Measure Success!")
            return True

    def cal_save(self):
        str_cmd = "SENS:CORR:COLL:RSAV:DEF OFF"
        if self.write(str_cmd) is False:
            self.logger.error("Cal Measure OFF Fail")
            return False
        else:
            self.logger.info("Cal Measure OFF")

        str_cmd = "SENS:CORR:COLL:SAVE:SEL"
        if self.write(str_cmd) is False:
            self.logger.error("Cal Data Save Fail!")
            return False
        else:
            if self.get_error_info(str_cmd) is False:
                self.logger.error("Cal Data Save Fail!")
                return False

            str_cmd = "MMEM:STOR:CORR 1,'ZITAntTest'"
            if self.write(str_cmd) is False:
                self.logger.error("Cal Data Save Fail!")
                return False
            self.logger.info("Cal Data Save Success!")
            return True

    def cal_load(self):
        str_cmd = "CONF:CHAN1:STAT ON; :MMEM:LOAD:CORR 1,'ZITAntTest'"
        if self.write(str_cmd) is False:
            self.logger.error("Cal Data Load Fail!")
            return False
        ret = self.get_error_info("ZITAntTest")
        if ret is False:
            self.logger.error("Cal Data Load Fail!")
        else:
            self.logger.info("Cal Data Load Success!")
        return ret

    def cal_date(self):
        str_cmd = "SENS:CORR:DATE?"
        ret = self.inst.query(str_cmd).replace("\r", "").replace("\n", "").replace("'", "")
        if ret == "":
            self.logger.error("Can't get cal date!")
            return False
        else:
            self.logger.debug("Cal Data:{0}".format(ret))
            date_str = ret[:6] + "20" + ret[6:]
            try:
                time_array = strptime(date_str, "%m/%d/%Y,%H:%M:%S")
                time_sec = mktime(time_array)
            except Exception as exp:
                self.logger.error(exp)
                return False
            else:
                return time_sec


if __name__ == '__main__':
    na_Inst = NA()
    na_Inst.open_na()
    na_Inst.init()
    na_Inst.set_start_freq(917.5)
    na_Inst.set_stop_freq(927.5)
    na_Inst.set_marker_x(920, 1)
    na_Inst.set_marker_x(922.5, 2)
    na_Inst.set_marker_x(925, 3)
    sleep(3)
    print(na_Inst.get_marker_y_val(1))
    print(na_Inst.get_marker_y_val(2))
    print(na_Inst.get_marker_y_val(3))
    na_Inst.cal_load()
    na_Inst.cal_date()

    na_Inst.cal_init()
    raw_input("Connect Short")
    na_Inst.cal_meas_short()
    raw_input("Connect Open")
    na_Inst.cal_meas_open()
    raw_input("Connect Load")
    na_Inst.cal_meas_match()
    na_Inst.cal_save()
    # sleep(1)
    na_Inst.close_na()
