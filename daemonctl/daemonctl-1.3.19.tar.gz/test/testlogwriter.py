#!/usr/bin/env python
# coding: utf8

import common
import sys

from src import logwriter

def doTest(gzip):
	log = logwriter.LogWriter("testlog.log",maxSize=1024*1024,numFiles=4,gzip=gzip)
	for x in range(100):
		log.write("hejsanåäö\n")
		if sys.version_info[0] < 3:
			log.write(u"hejsanåäö\n")
		else:
			log.write(b"hejsan\n")

for _ in range(300):
	doTest(True)

