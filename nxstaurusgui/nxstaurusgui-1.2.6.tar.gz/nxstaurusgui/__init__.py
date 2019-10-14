#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

""" --- NXS MacroGUI --
GUI for taurusgui
"""

from . import serverinfo
from . import config
from xml.dom import minidom
import tempfile
import PyTango

#: version of the application
__version__ = "1.2.6"


def replaceText(node, text):
    """
    replace text in the minidom node

    :param node: minidom node
    :type node: :class:`xml.dom.mindom.Node`
    :param text: new text
    :type text: new :obj:`str`
    """
    if node.firstChild.nodeType == node.TEXT_NODE:
        node.firstChild.replaceWholeText(text)


def findDevices():
    """
    find NXS and Sardana devices and store them in
    :class:`nxstaurusgui.serverinfo`
    """
    db = PyTango.Database()
    if not serverinfo.SELECTORSERVER_NAME:
        dvs = db.get_device_exported_for_class("NXSRecSelector")

        for dv in dvs:
            try:
                dp = PyTango.DeviceProxy(dv)
                dp.ping()
                if not serverinfo.DOOR_NAME:
                    serverinfo.DOOR_NAME = dp.Door
                serverinfo.SELECTORSERVER_NAME = dv
                break
            except Exception:
                pass
    elif not serverinfo.DOOR_NAME:
        try:
            dp = PyTango.DeviceProxy(serverinfo.SELECTORSERVER_NAME)
            dp.ping()
            serverinfo.DOOR_NAME = dp.Door
        except Exception:
            pass

    if not serverinfo.SELECTORSERVER_NAME:
        serverinfo.SELECTORSERVER_NAME = 'module'
    if not serverinfo.DOOR_NAME:
        dvs = db.get_device_exported_for_class("Door")

        for dv in dvs:
            try:
                dp = PyTango.DeviceProxy(dv)
                dp.ping()
                serverinfo.DOOR_NAME = dv
                break
            except Exception:
                pass

    if not serverinfo.MACROSERVER_NAME:
        dvs = db.get_device_exported_for_class("MacroServer")
        for dv in dvs:
            try:
                dp = PyTango.DeviceProxy(dv)
                dp.ping()
                dl = dp.DoorList
                if serverinfo.DOOR_NAME in dl:
                    serverinfo.MACROSERVER_NAME = dv
                    break
            except Exception:
                pass


def changeXML(ifile):
    """
    replace device names from serverinfo in `ifile`

    :param ifile: file name
    :type ifile: :obj:`str`
    """
    with open(ifile, 'r') as content_file:
        xmlstring = content_file.read()
    indom = None
    findDevices()
    if serverinfo.SELECTORSERVER_NAME:
        if not indom:
            indom = minidom.parseString(xmlstring)
        modelnode = indom.getElementsByTagName("model")
        if modelnode:
            replaceText(modelnode[0], serverinfo.SELECTORSERVER_NAME)
    if serverinfo.DOOR_NAME:
        if not indom:
            indom = minidom.parseString(xmlstring)
        doornode = indom.getElementsByTagName("DOOR_NAME")
        if doornode:
            replaceText(doornode[0], serverinfo.DOOR_NAME)
    if serverinfo.MACROSERVER_NAME:
        if not indom:
            indom = minidom.parseString(xmlstring)
        macronode = indom.getElementsByTagName("MACROSERVER_NAME")
        if macronode:
            replaceText(macronode[0], serverinfo.MACROSERVER_NAME)
    try:
        __import__("nxsselector")
    except ImportError:
        try:
            __import__("nxselector")
            modulename = indom.getElementsByTagName("modulename")
            if modulename:
                replaceText(modulename[0], "nxselector.Selector")
        except ImportError:
            __import__("nxsselector")

    if indom:
        clxml = indom.toxml()
        if serverinfo.TMPFILE:
            f = open(serverinfo.TMPFILE, 'w')
        else:
            f = tempfile.NamedTemporaryFile(delete=False)
        if hasattr(clxml, "encode"):
            clxml = clxml.encode('utf-8')
        f.write(clxml)
        f.close()
        serverinfo.TMPFILE = f.name
        return f.name


if serverinfo.FIND:
    newfile = changeXML('%s/data/config.xml' % __path__[0])
    if newfile:
        config.XML_CONFIG = newfile

XML_CONFIG_DIR, XML_CONFIG = config.XML_CONFIG_DIR, config.XML_CONFIG

__all__ = ['XML_CONFIG_DIR', 'XML_CONFIG']
