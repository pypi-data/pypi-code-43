# coding=utf-8
import os
import re
import sys
import zipfile
import shutil
import time
import subprocess
import tempfile
import getopt
import sys
import platform
import datetime


class Shell:
    def __init__(self, bins):
        self.bins = bins

    def call(self):
        exbin = " ".join(self.bins)
        if platform.system() == "Darwin":
            p = subprocess.Popen(exbin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            p = subprocess.Popen(exbin, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        lines = []
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            line = line.replace("\\", "/").replace("\n", "").replace("\r", "").replace(" ", "")
            if len(line) > 0:
                lines.append(line)
        return p.returncode, lines
