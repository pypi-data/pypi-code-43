from __future__ import print_function
import click
import glob
import os
import logging
from os.path import join

from mcutk.debugger import getdebugger
from mcutk.managers.conf_mgr import ConfMgr




class Debughelper(object):

    supported_debuggers = ['jlink', 'pyocd']


    @staticmethod
    def list_debuggers():
        """List installed debuggers from system."""

        debs = list()
        for name in Debughelper.supported_debuggers:
            debugger = getdebugger(name).get_latest()
            if debugger and debugger.is_ready:
                debs.append(debugger)
            else:
                click.secho('warning: cannot found %s installation, please check if it is installed!'%name, fg="yellow")

        return debs



    @staticmethod
    def list_devices():
        """List connected devices."""

        debuggers = Debughelper.list_debuggers()
        devices = list()
        for deb in debuggers:
            for item in deb.list_connected_devices():
                item['debugger'] = deb
                devices.append(item)

        return devices


    @staticmethod
    def choose_device(device):
        """Promt user to select device."""

        if device == None:
            device = dict()

        debugger = None

        debugger_type = device.get('debugger_type')
        usbid = device.get('usbid')

        devices = Debughelper.list_devices()

        if len(devices) == 0:
            click.secho('no devices found!', fg='red')
            return None, None


        selected_device = None
        # use usb id to find debugger type
        if usbid:
            for d in devices:
                if d['usbid'] == str(usbid):
                    selected_device = d
                    break
            else:
                logging.warning('not found usbid in system, is it right?', fg='red')
                return None, None

        else:
            # prompt user to select
            if devices and len(devices) == 1:
                selected_device = devices[0]
            else:
                for index, item in enumerate(devices):
                    print('{:2} - {:10} - {} - {}'.format(index, item['type'], item.get('name'), item['usbid']))

                while True:
                    try:
                        index = raw_input('Please input the index to select device > ')
                        index = int(index)
                        selected_device = devices[index]
                        break
                    except (ValueError, IndexError) as e:
                        pass

        device['usbid'] = selected_device['usbid']
        device['debugger_type'] = selected_device['type']



        if device.get('debugger_type') == 'jlink':
            if not device.get('devicename'):
                device['devicename'] = raw_input('Please input device name > ')

            if not device.get('interface'):
                interface = raw_input('SWD or JTAG > ')
                device['interface'] = "SWD" if not interface else interface

        debugger = selected_device.pop('debugger')
        return debugger, device



