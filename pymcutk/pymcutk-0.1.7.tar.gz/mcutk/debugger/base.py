import abc
import os
import signal
import sys
import time
import logging
import subprocess
import tempfile
import threading
import socket
import errno
import shlex

import mbed_lstools
import pexpect
from pexpect.popen_spawn import PopenSpawn
from mcutk.appbase import APPBase
from mcutk.gdb_session import GDBSession


class DebuggerBase(APPBase):
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(DebuggerBase, self).__init__(*args, **kwargs)
        self.gdbpath = kwargs.get("gdbpath", "")
        self.version = kwargs.get("version", "unknown")
        self._board = None
        self._callback_map = {
            "before-load": None
        }


    def set_board(self, board):
        self._board = board





    def gdb_init_template():
        """Return a string about gdb init template.
        """
        return ""




    @abc.abstractmethod
    def reset(self):
        """Used to reset target CPU.
        """
        pass


    @abc.abstractmethod
    def erase(self):
        """Used to erase flash.
        """
        pass


    @abc.abstractmethod
    def flash(self):
        """Binary image programming.
            .bin
            .hex
        """
        pass



    def get_gdbserver(self, board=None):
        """Return a string about the command line of gdbserver
        """
        pass



    def start_gdbserver(self, **kwargs):
        gdbserver_cmd = self.get_gdbserver(**kwargs)
        print (gdbserver_cmd)
        # start gdb server
        retcode = subprocess.call(gdbserver_cmd, shell=True)



    def list_connected_devices(self):
        mbeds = mbed_lstools.create()
        devices = mbeds.list_mbeds()
        for device in devices:
            device['usbid'] = device.pop('target_id_usb_id')
            device['type'] = device.pop('device_type')
            device['name'] = device.pop('platform_name')
            if device['type'] == 'daplink':
                device['debugger'] = 'pyocd'

        return devices


    def gdb_program(self,
                    filename,
                    gdbserver_cmdline=None,
                    gdbinit_commands=None,
                    board=None,
                    timeout=200,
                    **kwargs):
        """Using gdb & gdbserver to programming image.
        Steps:
            1> Start gdbserver at port: board.gdbport
            2> Render gdbinit_template
            3> Start gdb.exe:
                gdb.exe -x <gdb.init> -se <binary.file>

        Arguments:
            filename - {str}: path to image file.
            gdbserver_cmdline - {str}: gdb server command line, used for starting gdb server.
            gdbinit_commands - {str}: gdb init commands to control gdb behaviour.
            timeout - {int}: set timeout for gdb & gdb server process. default 200 seconds.

        Returns:
            tuple --- (returncode, console-output)
        """
        if board is None:
            board = self._board

        if board is None:
            raise ValueError('no board is associated with debugger!')

        # load gdb init template
        gdb_init_template = board.gdb_init_commands
        if gdb_init_template is None:
            gdb_init_template = self.gdb_init_template()

        gdbcommands = gdbinit_commands if gdbinit_commands else \
                      render_gdbinit(gdb_init_template, board)

        gdbserver_cmdline = gdbserver_cmdline if gdbserver_cmdline else self.get_gdbserver(**kwargs)

        return self._gdb_program(board.gdbport,
                                 filename.replace("\\", "/"),
                                 gdbserver_cmdline,
                                 gdbcommands,
                                 timeout)


    def _gdb_program(self, gdbport, filename, gdbserver_cmd,
                    gdbinit, timeout):
        """use gdb to load program to target device"""

        def _kill_popen_process(process):
            # process.kill() just killed the parent process, and cannot kill the child process
            # that caused the popen process in running state.
            # force to use windows command to kill that the process!
            if not isinstance(process, subprocess.Popen):
                raise TypeError("argument is not a instance of subprocess.Popen")

            if os.name == "nt":
                os.system("TASKKILL /F /PID {pid} /T".format(pid=process.pid))
            else:
                process.kill()


        def timeout_exceeded(ps):
            """subprocess tiemout exceeded handler."""
            for p in ps:
                if isinstance(p, PopenSpawn):
                    p.kill(None)
                else:
                    _kill_popen_process(p)
                logging.warning('pid: %s exceeded timeout!', p.pid)



        logging.info("> starting gdb server.")
        logging.info(gdbserver_cmd)
        if os.name != "nt":
            gdbserver_cmd = shlex.split(gdbserver_cmd)

        # start gdb server
        gdbserverPro = subprocess.Popen(
            gdbserver_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            )

        if not _validate_port_is_ready(gdbserverPro, gdbport):
            logging.error("gdb server start failure")
            if gdbserverPro.poll() is None:
                _kill_popen_process(gdbserverPro)
            output, _ = gdbserverPro.communicate()
            logging.error(">>>> gdb server console output: \n\n%s", output)
            return 1, output

        logging.info("> gdb server is ready, pid: {0}, port: {1}".format(gdbserverPro.pid, gdbport))
        gdb_output = list()

        def stdout_reader(process):
            for line in iter(process.stdout.readline, b''):
                gdb_output.append(line)

        # To resolve large output from subprocess PIPE, use a background thread to continues read
        # data from stdout.
        reader_thread = threading.Thread(target=stdout_reader, args=(gdbserverPro, ))
        reader_thread.start()

        # start gdb client
        output = ""
        gdb_errorcode = 0

        logging.info("> start gdb client to connect to server: localhost, port: %s", gdbport)

        gdb_cmd = "{} --exec {} --silent".format(self.gdbpath, filename)
        session = GDBSession.start(gdb_cmd)

        # set timeout
        # Use a timer to stop the subprocess if the timeout is exceeded.
        if timeout is not None:
            ps_list = [gdbserverPro, session]
            process_timer = threading.Timer(timeout, timeout_exceeded, (ps_list, ))
            process_timer.start()

        # convert string commands to a list
        _gdb_actions = [line.strip() for line in gdbinit.split("\n") if line.strip()]

        for act in _gdb_actions:
            # call registerd callback function before-load command
            if act.startswith("load"):
                self._call_registered_callback("before-load")

            try:
                c = session.run_cmd(act).lower()
                if "No connection could be made" in c:
                    gdb_errorcode = 1
                    logging.error(c)
                    break
                elif '"monitor" command not supported by this target' in c:
                    gdb_errorcode = 1
                    logging.error('gdb command execute error!')
                    break
            except:
                logging.exception('gdb command run error, CMD: %s', act)

        # gdb client disconnect the connection,
        # and gdbsever will automaticlly close
        session.close()
        gdbserverPro.wait()
        reader_thread.join()

        # Stop timeout timer when communicate call returns.
        if timeout is not None:
            process_timer.cancel()

        logging.info("> gdb server exit! exit code: %s", gdbserverPro.returncode)

        # get gdb console output
        output = ''.join(gdb_output)
        output += session.console_output

        if gdb_errorcode == 0:
            retcode = gdbserverPro.returncode
        else:
            retcode = gdb_errorcode

        return retcode, output




    def register(self, name):
        """Declare a decorator to register callback to debugger instance.

        Arguments:
            name {str} -- before-load
        """
        def func_wrapper(func, *args, **kwagrs):
            self._callback_map[name] = (func, args, kwagrs)
            return func
        return func_wrapper


    def _call_registered_callback(self, name=None):
        value = self._callback_map.get(name)
        if type(value) is tuple:
            func, args, kwargs = value
            if func:
                return func(*args, **kwargs)

        return None



def render_gdbinit(template, board):
    """
    Render gdbinit template with board object.

    Render used '.foramt()' syntax:
        'target remote localhost: {gdbport}'

    Example:
        1. jlink

    """
    dicta = board.__dict__
    # dicta["file"] = executable
    return template.format(**dicta)





def _validate_port_is_ready(server_process, port, tiemout=30):
    """Validate the port is open on localhost"""

    is_ready = False
    port = int(port)
    s = None

    assert server_process != None

    # delay 1 seconds wait server up
    time.sleep(1)
    for _ in range(tiemout):
        print(" Wait for gdb server ready.")
        time.sleep(0.5)

        if server_process.poll() is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("127.0.0.1", port))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    is_ready = True
                    break
                else:
                    print(e)
        else:
            break

        if s is not None:
            s.close()

    return is_ready

