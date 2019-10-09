# -*- coding: utf-8 -*-
"""
Created on Tuesday 11-June-2019 at 14:55

@author: Rastko Pajković

---------------------
This driver requires:
---------------------

1. the instalation of ActiveDSO:
  https://teledynelecroy.com/support/softwaredownload/activedso.aspx?capid=106
2.Communication protocol LXI (VXI11) - to be set on the oscilloscope
  under Utilities->Remote

--------
Example:
--------

with Oscilloscope(address='169.254.101.187') as o:
    o.save_trace(trace='C4', save_to='E:', filename='test')

-----
Tips:
-----

1. Use XStreamBrowser on the oscilloscope the inspect
   all of the available commands and properties
"""
import win32com.client


class Oscilloscope():
    """Driver for LeCroy HDO 4104A Oscilloscope"""

    def __init__(self, address='169.254.101.187'):
        """One-line docString"""
        self._address = address
        self._scope = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")

    def __enter__(self):
        self._scope.MakeConnection(f"VXI11:{self._address}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._scope.Disconnect()

    def query(self, command="app.SaveRecall.WaveForm.SaveSource", byte_len=80):
        """Read and return a parameter as a string"""
        self._scope.WriteString(f"VBS? 'return = {command}' ")
        return self._scope.ReadString(byte_len)

    def write(self, command='app.SaveRecall.WaveForm.SaveSource', value="C4"):
        if value is not None:
            comstr = f"""VBS? '{command} = "{value}"'"""
        else:
            comstr = f"""VBS? '{command}'"""
        self._scope.WriteString(comstr, True)

    def save_trace(self, trace='AllDisplayed', save_to='E:', filename='test'):
        self.write(command='app.SaveRecall.WaveForm.SaveSource',  value=trace)
        self.write(command='app.SaveRecall.WaveForm.TraceTitle',  value=filename)
        self.write(command='app.SaveRecall.WaveForm.WaveFormDir', value=save_to)
        self.write(command='app.SaveRecall.WaveForm.SaveFile',    value=None)
        # see if it finished
        self.WaitForOPC()

    def transfer_file(self, source, destination):
        """TODO: implement and test"""
        self._scope.TransferFileToPc("HDD", "D: \dso\src.txt", "C: \pc\dest.txt")

