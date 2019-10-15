# -*- coding: utf-8 -*-

# Resource object code
#
# Created: 周二 9月 10 17:42:43 2019
#      by: The Resource Compiler for PySide2 (Qt v5.13.0)
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore

qt_resource_data = b"\
\x00\x00\x00\x10\
<\
\xb8d\x18\xca\xef\x9c\x95\xcd!\x1c\xbf`\xa1\xbd\xdd\
"

qt_resource_name = b"\
\x00\x03\
\x00\x00x\x83\
\x00q\
\x00r\x00c\
\x00\x02\
\x00\x00\x07\xb2\
\x00t\
\x00r\
\x00\x08\
\x0e8\x05}\
\x00z\
\x00h\x00_\x00C\x00N\x00.\x00q\x00m\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x0c\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
