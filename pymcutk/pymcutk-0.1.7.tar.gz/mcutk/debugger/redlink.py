from __future__ import print_function
import os
import sys
import re
import platform
import subprocess
import logging
import threading
import time
import tempfile
import shlex
import glob
import pexpect
# import psutil
import socket
import telnetlib

from xml.etree import ElementTree as ET
from threading import Thread, Timer
from pexpect.popen_spawn import PopenSpawn
from mcutk.debugger.base import DebuggerBase
from mcutk.util import run_command
from mcutk.gdb_session import GDBSession
from mcutk.debugger.base import _validate_port_is_ready

class RedLinkServerIssue(Exception):
    pass

class RedLink(DebuggerBase):
    """
    Redlink (also known as Link Server) is the mechanism used by LPCXpresso to provide a debug
    connection down to a target MCU. It provides the means to connect to single MCUs or to multiple
    CPUs within the same MCU via a single debug probe.

    Command line flash programming reference:
        https://community.nxp.com/thread/389139


    Notes from MCUXpresso IDE User's Guide:
        The MCUXpresso IDE Flash programming utility is located at:
        - crt_emu_cm_redlink.exe is the name of the Flash utility, it is located at <mcuxpressod_root>/ide/bin/.
        - target is the target chip name. For example LPC1343, LPC1114/301, LPC1768 etc. (see
        'Finding Correct Parameters...' below)
        - --flash-load can actually be one of a few different options. Use:
        - --flash-load to write the file to Flash,
        - --flash-load-exec to write it to Flash and then cause it to start running,
        - --flash-mass-load to erase the Flash and then write the file to the Flash, and
        - --flash-mass-load-exec to erase the Flash, write the file to Flash and then cause it to start running.
        - filename is the file to Flash program. It may be an executable (axf) or a binary (bin) file. If using
        a binary file, the base_address also must be specified. Using enclosing quotes is optional
        unless the name includes unusual characters or spaces.
        - base_address is the address where the binary file will be written. It can be specified as a hex
            value with a leading 0x.

        If you are using Flash memory that is external to the main chip you will need to specify an
        appropriate Flash driver that supports the device. This usually takes the name of a .cfx file held
        in a default location. In unusual circumstances it is possible to specify an absolute file system
        name of a file. Using enclosing quotes is optional unless.
    """
    def __init__(self, *args, **kwargs):
        super(RedLink, self).__init__("redlink", *args, **kwargs)

        # MCUXpressoIDE 10.2 & 10.1
        mcux_tool_bin = os.path.join(self.path, "bin")
        self._is_old_version = True

        # For MCUXpressoIDE 10.3 & later
        if not os.path.exists(mcux_tool_bin):
            plugins_dir = os.path.join(self.path, "plugins")
            try:
                tools_bin = glob.glob(plugins_dir+"/com.nxp.mcuxpresso.tools.bin.*")[0]
                mcux_tool_bin = os.path.join(tools_bin, "binaries")
                self._is_old_version = False
            except IndexError:
                logging.warning('cannot found redlinkserv.exe, %s', plugins_dir)

        self._crt_emu_redlink = os.path.join(mcux_tool_bin, "crt_emu_cm_redlink.exe").replace("\\", "/")
        self._redlinkserver = os.path.join(mcux_tool_bin, "redlinkserv.exe").replace("\\", "/")
        self.template_root = None
        self.tn = None
        self._redlinkserverpro = None


    @property
    def is_ready(self):
        return os.path.exists(self._crt_emu_redlink)


    def set_board(self, board):
        # workaround to clear the prefix of usbid
        if ":" in board.usbid:
            board.usbid = board.usbid.split(":")[-1]
        self._board = board


    def erase(self):
        """
        Erase flash by: -flash-erase
        """
        logging.info("erase flash")
        crt_redlink_cmd = self.gen_crt_cmd(self._board) + " -flash-erase "
        return run_command(crt_redlink_cmd, timeout=120)




    def reset(self):
        """
        reset board by: pyocd-tool.exe reset -b <id>
        """
        logging.warning("cannot reset board by redlink")
        return False




    def _start_linkserver(self, connectscript=None):
        # start linkserver in background
        args = [
            self._redlinkserver,
            "--telnetport=%s"%self._board.gdbport,
            "--port=%s"%(int(self._board.gdbport) + 30)
        ]

        if connectscript:
            args.append("--connectscript %s"%connectscript.replace('\\', '/'))

        self._redlinkserverpro = subprocess.Popen(args)





    def _get_probe_index(self, usbid, retry=3):
        pattern = re.compile("serial number = .*\n", re.I)
        usbid_list = []

        for _ in xrange(retry):
            try:
                if not(self._redlinkserverpro and self._redlinkserverpro.poll() is None):
                    raise RedLinkServerIssue('Server is not running')

                self.tn = telnetlib.Telnet('localhost', self._board.gdbport, timeout=10)
                logging.info('connected redlinkserver: %s', self._board.gdbport)
                time.sleep(0.5)
                self.tn.write('PROBELIST\n')
                output = self.tn.read_until('redlink>PROBELIST', timeout=3)
                usbid_list = pattern.findall(output)
                usbid_list = [uid.split(" = ")[-1].replace("\n", "") for uid in usbid_list]
                if usbid_list:
                    break
                else:
                    logging.error('usbid list is empty')

            except Exception as e:
                logging.exception('failed to get probeindex, retry again.')
                time.sleep(0.5)
        else:
            raise RedLinkServerIssue('server is not ready')


        try:
            index = usbid_list.index(usbid)
        except ValueError:
            logging.error(usbid_list)
            raise RedLinkServerIssue("Usb SN '{0}' is not connect!".format(usbid))

        index += 1
        print("UsbID: %s, Probe Index: %s"%(usbid, index))

        return index







    def gen_crt_cmd(self, board, connectscript=None, resetscript=None, device_parts_dir=None, flash_driver_dir="default", coreindex=0):
        """Generate crt_emu_redlink command line string."""
        conf = _parse_conf_from_template(self.template_root)
        conf['connectscript'] = None

        # There is a bug in crt_emu_redlink.exe, when the connscript is set, the client will always use the probeindex 1
        # if connectscript and os.path.exists(connectscript):
        #     conf['connectscript'] = connectscript

        if conf['devicename']:
            board.devicename = conf['devicename']

        _params = [
            self._crt_emu_redlink,
            "-p {}".format(board.devicename),
            "-g",
            # "--cache disable",
            # "--no-info-roms",
            # "--no-packed",
            # "--reset system,soft",
            # "--flash-driver= ",
            "-COREINDEX=%s"%coreindex
            # "--telnet 3333",
        ]

        # workaround for MIMXRT1052xxxxB, https://jira.sw.nxp.com/browse/RE-1830
        if board.devicename in ['MIMXRT1052xxxxB', 'MIMXRT1021xxxxx']:
            _params.append('--reset VECTRESET')

        # self._start_linkserver(connectscript)

        # For 10.2 version, we need to get the probeindex at first.
        # New in MCUXpresso IDE Version 10.3 eb2 is the option to reference a debug probe via its serial number from the
        # command line. This feature allows multiple debug probes to be connected (over USB) at the same time and referenced
        #  individually. Currently this feature is not used directly by the IDE but this may change before we release
        # version 10.3.
        if self._is_old_version:
            probe_index = self._get_probe_index(board.usbid)
            _params.append("-PROBEHANDLE=%s"%probe_index)
        else:
            _params.append("--probeserial=%s"%board.usbid)


        if conf['connectscript']:
            _params.append("--connectscript %s"%conf['connectscript'].replace('\\', '/'))

        if conf['device_parts_dir']:
            _params.append("-x {}".format(conf['device_parts_dir'].replace('\\', '/')))

        # don't use flash driver for RAM and SDRAM
        if flash_driver_dir is None:
            _params.append("--no-flash-dir-default")
        else:
            # add falsh_dir
            if flash_driver_dir not in ('default', ''):
                _params.append("--flash-dir {}".format(flash_driver_dir.replace('\\', '/')))
            # add falsh_dir from configuration
            if conf['flash_driver_dir']:
                _params.append("--flash-dir {}".format(conf['flash_driver_dir'].replace('\\', '/')))

        if resetscript:
            _params.append("--resetscript {}".format(resetscript.replace('\\', '/')))

        return " ".join(_params)




    def gdb_init_template(self):
        """Default gdb commands for crt_emu_redlink.
        Reference from https://community.nxp.com/inbox.
        mon ondisconnect <type>
            type: Must be one of: nochange, stop, cont, run_cont.
        """
        commands = \
'''set non-stop on
set remotetimeout 100000
target extended-remote | {}
set mem inaccessible-by-default off
mon semihosting dis
mon ondisconnect cont
set arm force-mode thumb
load
q
'''
        return commands





    def _crt_debugging(self, filepath, crt_redlink_cmd, timeout):
        # add flash operation
        crt_redlink_cmd += ' -flash-load-exec "{}"'.format(filepath.replace("\\", "/"))
        # add start address
        if filepath.endswith('.bin'):
            if self._board.start_address:
                crt_redlink_cmd += " --load-base=%s"%self._board.start_address
            # else:
            #     # default value
            #     crt_redlink_cmd += " --load-base=0x0"

        # call registerd callback function
        self._call_registered_callback("before-load")

        logging.info(crt_redlink_cmd)

        ret, console = run_command(crt_redlink_cmd, timeout=timeout)

        logging.info('linkserver exit code: %s', ret)

        # workaround: force kill alive redlinkserv process
        if ret != 0:
            os.system('''TASKKILL /F /T /FI "IMAGENAME eq redlinkserv*"''')

        return ret, console




    def _gdb_debugging(self, filename, gdbinit, timeout):
        if not self.gdbpath or not os.path.exists(self.gdbpath):
            raise IOError('gdb executable is not exists!')

        def _check_gdb_cmd_run_error(text):
            return 'failed on connect' in text or 'load failed' in text \
                or "error finishing flash operation" in text \
                or 'redlink interface error' in text

        gdb_cmd = "{} --exec {} --silent".format(self.gdbpath, filename)
        session = GDBSession.start(gdb_cmd)
        errorcode = 0

        # convert string commands to a list
        _gdb_actions = [line.strip() for line in gdbinit.split("\n") if line.strip()]

        for act in _gdb_actions:
            # call registerd callback function before-load command
            if act == 'load':
                self._call_registered_callback("before-load")
            try:
                c = session.run_cmd(act).lower()
                if _check_gdb_cmd_run_error(c):
                    errorcode = 1
                    break
            except:
                logging.exception('gdb cmd run exception, CMD: %s', act)

        session.close()

        return errorcode, session.console_output



    def flash(self, filepath, connectscript=None, resetscript=None, device_parts_dir=None, flash_driver_dir="default", **kwargs):
        """MCUXPresso IDE crt_emu_cm_redlink utility interface.

        This will program image by crt_emu_cm_redlink tool.

        Arguments:
            filepath {str} -- path to image file

        Keyword Arguments:
            base_addr {int} -- the base address to programming(default: 0)
            usbid {str}  -- link2/cmsis-dap usb serial number.
            connectscript {str} -- connect script (default: None)
            resetscript {str} -- reset script (default: None)
            device_parts_dir {str} -- directory include devices details(default: {None})
            flash_driver_dir {str} -- directory include flash drivers(default: {None})

        Raises:
            ValueError -- [description]

        Returns:
            Tuple -- (returncode, output)
        """
        crt_redlink_cmd = self.gen_crt_cmd(
            self._board,
            connectscript,
            resetscript,
            device_parts_dir,
            flash_driver_dir,
            0)

        timeout = 300
        # ret = self._crt_debugging(filepath, crt_redlink_cmd, timeout)
        if filepath.endswith('.bin'):
            ret = self._crt_debugging(filepath, crt_redlink_cmd, timeout)
        else:
            gdb_init = self.gdb_init_template().format(crt_redlink_cmd)
            ret = self._gdb_debugging(filepath, gdbinit=gdb_init, timeout=timeout)

        if self.tn:
            self.tn.close()

        return ret




def _parse_conf_from_template(path):
    ret = {
        "connectscript": None,
        "devicename": None,
        "device_parts_dir": None,
        "flash_driver_dir": None,
    }

    if not path:
        return ret

    if not os.path.exists(path):
        return ret

    ret['device_parts_dir'] = path
    ret['flash_driver_dir'] = path
    flash_dir = os.path.join(path, 'Flash')
    if os.path.exists(flash_dir):
        ret['flash_driver_dir'] = flash_dir


    try:
        project_conf_xml = glob.glob(os.path.join(path, "com.crt.advproject.config.exe.*.xml"))[0]
        root = ET.parse(project_conf_xml).getroot()
        node = root.find("parameters/initvalue[@var='internal.connect.script']")
        if node is not None:
            ret['connectscript'] = node.attrib['value']
    except IndexError:
        pass
    except Exception as e:
        raise e

    try:
        device_part_xml = glob.glob(os.path.join(path, "*_dir_part.xml"))[0]
        root = ET.parse(device_part_xml).getroot()
        node = root.find("chip")
        if node is not None:
            devicename = node.attrib['name']
            ret['devicename'] = devicename
            logging.info("Found Device Name: %s", devicename)
    except IndexError:
        pass

    return ret



