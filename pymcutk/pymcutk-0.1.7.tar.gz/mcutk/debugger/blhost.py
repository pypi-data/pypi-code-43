
import os
import sys
import re
import platform
import subprocess
import logging
import threading
import time
import tempfile
import json



from mcutk.debugger.base import DebuggerBase
from mcutk.util import run_command


PY = sys.version_info[0]

DEFAULT_TIMEOUT = 600000


def find_hid_devices():
    """Use pywinusb as the backend to discovery HID devices, windows only."""

    from pywinusb import hid as hid

    devices = list()
    hid_devices = hid.find_all_hid_devices()

    for dev in hid_devices:
        # filter vid is: 0x15a2
        if hex(dev.vendor_id) == "0x15a2":
            print(dev.device_path)
            print('---------------------------')
            devices.append(dev)

    return devices





class Response(object):
    """Represent a blhost response."""

    @classmethod
    def parse(cls, raw):
        response = cls()
        response.output = raw

        match = re.search(r"{[\s\S]+}", raw)
        if match:
            raw_data = json.loads(match.group(0))
            response.content = raw_data.get('response') #raw.replace(match.group(0), '').strip()
            response.command = raw_data.get('command')
            response.status_value = raw_data.get('status').get('value')
            response.description = raw_data.get('status').get('description')
        else:
            response.content = raw
            if "Response status = 0 (0x0) Success" in raw:
                response.status_value = 0
            else:
                response.status_value = -1
        return response


    def __init__(self, **kwargs):
        self.status_value = kwargs.get("status_value")
        self.description = kwargs.get("status_description")
        self.command = kwargs.get("command")
        self.output = kwargs.get("output")
        self.value = kwargs.get("value")

    def __str__(self):
        return "<CMD: {}, {}>".format(self.command, self.description)


    @property
    def status(self):
        return self.status_value




class Blhost(DebuggerBase):
    """Blhost is application running on host PC and used to issue commands to MCU bootloader.
        Guides online: https://www.nxp.com/docs/en/user-guide/MCUBLHOSTUG.pdf.

    This class wrapped blhost tool, it always set "--json" to get formatted JSON string,
    and when command is run successful, a Response object will be returned.

    Example, initial blhost debugger
        >>> bl = Blhost('C:/user/blhost.exe')
        >>> bl.set_connection("-p COM3,56700")                  # set connection
        >>> bl.set_connection("-u")                             # set connection
        >>> resp = bl.run_command("get-property 1")             # send command get-property 1
        >>> resp = bl.run_command("get-property 1", json=False) # send command get-property 1, none json output
        >>> bl.reset()                                          # reset chip
        >>> bl.erase()                                          # erase flash


    Response object:
        >>> resp = bl.run_command("get-property 2")
        >>> print resp.status_code
        0

        >>> print resp.value
        [ 23 ]

        >>> print resp.command
        get-property 2

        >>> print resp.status
        True

        >>> print resp.output
        {
        "command" : "get-property",
        "response" : [ 23 ],
        "status" : {
            "description" : "0 (0x0) Success.",
            "value" : 0
            }
        }


    Run commands without constructor
        >>> resp = Blhost.run("blhost -p COM3 -- get-property 1")
        >>> print resp.status
        True
        >>> print resp.output
        Inject command 'get-property'
        Response status = 0 (0x0) Success.
        Response word 1 = 1258424064 (0x4b020700)
        Current Version = K2.7.0

    """

    @staticmethod
    def run(cmd, **kwargs):
        """Run blhost command directly"""

        if '-t' in cmd:
            timeout = 1200
        else:
            timeout = 30

        rc, output = run_command(cmd, stdout=True, timeout=timeout)
 
        # print Response.parse(output)       
        if rc != 0:
            raise RuntimeError("blhost command error: %s"%rc)

        response = Response.parse(output)

        logging.info(output)

        return response




    def __init__(self, *args, **kwargs):
        """Blhost debugger constructor."""

        super(Blhost, self).__init__("blhost", *args, **kwargs)
        if self.path:
            self._blhost_exe = self.path
        else:
            self._blhost_exe = 'blhost'
        self._connect_opt = "-u"



    @property
    def is_ready(self):
        return os.path.exists(self._blhost_exe)



    def set_connection(self, type=None, value=None):
        """Set blhost connection. Default automaticlly select usb to connect.

        Manual to set connection options by value:
            - port: -p/--port <name>[,<speed>]
            - usb: -u/--usb [[[<vid>,]<pid>] | [<path>]]

            Example:
            - set connection with port:
                blhost.set_connection(value="--port COM3,57600")
            - set connection with usb hid:
                blhost.set_connection(value="--usb 0x15a2,0x0073")

        Arguments:
            type {str} -- usb or port.
            value {str} -- port,baudrate | vid,pid
        """

        if value:
            self._connect_opt = value

        elif type == 'port':
            if self._board.main_serial and self._board.main_serial.port:
                self._connect_opt = "--port {}".format(self._board.main_serial.port)
            else:
                logging.warning("port is not configured")

        elif type == 'usb':
            devices = find_hid_devices()
            if not devices:
                logging.warning("Not found hid devices with VID: %s!", "0x15a2")

            elif len(devices) > 1:
                logging.warning("Multiple devices found!")
                self._connect_opt = "--usb \"{}\"".format(devices[0].device_path)

        if not self._connect_opt:
            logging.warning("connect options is not set, forget to set board?")



    def _build_command(self, cmd, json, memid, timeout):
        assert self._connect_opt

        command = [
            "{exe}",
            "{connect_opt}",
            "-t {0}".format(timeout) if timeout else '',
            "--json" if json else "",
            "--",
            "{cmd}",
            "{memid}".format(memid=memid) if memid != None else ""
        ]

        return " ".join(command).format(exe=self._blhost_exe, connect_opt=self._connect_opt, cmd=cmd)

    def eval_timeout(self, byte_count):
        '''
        Evalute the timeout for fill-memory/ write-memory/ read-memory
        '''
        try:
            byte_count = eval(byte_count)
        except TypeError:
            pass

        if byte_count in range(0, 0x172000):
            timeout = DEFAULT_TIMEOUT / 2
        elif byte_count in range(0x172000, 0x2E4000):
            timeout = DEFAULT_TIMEOUT
        else:
            timeout = DEFAULT_TIMEOUT * 2
        return timeout

    def run_command(self, cmd, json=True, memid=None, timeout=None):
        """Run a single blhost command, and return a blhost response object.

        Arguments:
            cmd -- {str} blhost command
            json -- {boolean} json formmatted output
            memid -- {str/int} memory ID

        Returns:
            Response object

        blhost-commands:
            reset
            get-property
            set-property
            flash-erase-region
            flash-erase-all
            flash-erase-all-unsecure
            read-memory
            write-memory
            fill-memory
            receive-sb-file
            execute
            call
            flash-security-disable
            flash-program-once
            flash-read-once
            flash-read-resource
            configure-memory
            reliable-update
            key-provisioning
            flash-image
            list-memory
            efuse-program-once
            efuse-read-once
            program-aeskey
            generate-key-blob
        """

        blhost_cmd = self._build_command(cmd, json, memid, timeout)
        logging.info(blhost_cmd)
        return Blhost.run(blhost_cmd)



    def run_commands(self, commands, **kwargs):
        """Run a list of commands. RuntimeError will be raised when one of command failed."""

        for cmd in commands:
            resp = self.run_command(cmd, **kwargs)
            if not resp.status:
                raise RuntimeError("command run failed, %s"%str(resp))



    def test_conn(self):
        """Test debugger connection."""
        resp = self.run_command("get-property 1")
        return resp



    def erase(self, memid=None):
        """rase all flash according to [memory_id],
            excluding protected regions.

        blhot: flash-erase-all
        """
        self.run_command('flash-erase-all', memid=memid)



    def reset(self):
        """Use blhost to reset chip."""

        return self.run_command("reset")



    def read_mem(self, addr, length, file=None, memid=None):
        """Read memory from a given address.
        If file is set, read memory will to file.

        blhost: read-memory <addr> <byte_count> [<file>] [memory_id]
        """
        timeout = self.eval_timeout(length)
        cmd = "read-memory {addr} {length}".format(addr=addr, length=length)

        if file:
            cmd += " %s "%file

        return self.run_command(cmd, memid=memid, timeout=timeout)


    def write_mem(self, addr, value=None, file=None, memid=None):
        """Write memory.

        blhost: write-memory <addr> [<file>[,byte_count]| {{<hex-data>}}] [memory_id]
        """
        
        cmd = "write-memory {addr}".format(addr=addr)

        if value:
            cmd += " %s "%value
            timeout = None

        elif file:
            cmd += " %s "%file
            file_size = os.path.getsize(file)
            timeout = self.eval_timeout(file_size)

        return self.run_command(cmd, memid=memid, timeout=timeout)

    def fill_memory(self, addr, length, pattern ,pattern_mode = "word"):
        """Fill memory with pattern; size is word (default), short or byte
        blhost: <addr> <byte_count> <pattern> [word | short | byte]
        """
        timeout = self.eval_timeout(length)
        cmd = "fill-memory {addr} {length} {pattern} {pattern_mode}".format(addr=addr, length=length, pattern=pattern, pattern_mode=pattern_mode)

        return self.run_command(cmd, timeout=timeout)


    def flash(self, filepath, erase='erase', memid=None):
        """Flash a formated image <file> to memory with ID <memory_id>.
        Supported file types: SRecord(.srec and .s19) and HEX (.hex). Flash is erased
        before writing if [erase]=erase. The erase unit size depends on the target and
         the minimum erase unit size is 1K.

        Arguments:
            filepath {str} -- image file path
            erase {int} -- erase flash or not before flashing. 
            memid {int} --

        """

        cmd = "flash-image {file}".format(file=filepath)

        if erase:
            cmd += ' %s'%erase
        else:
            pass

        return self.run_command(cmd, memid=memid)

    def get_property(self, tag, memid_index = None, json=True):
        """
        Return bootloader specific property.
        blhost: get-property <tag> [<memid>]
        """

        cmd = "get-property {tag}".format(tag=tag)

        return self.run_command(cmd, memid=memid_index, json=json)

    def set_property(self, tag, value):
        """
        Set the specified property.file
        blhost: set-priperty <tag> <value>
        """

        cmd = "set-property {tag} {value}".format(tag=tag, value=value)
        return self.run_command(cmd)

    def flash_erase_region(self, addr, byte_count, memid=None):
        """
        Erase a region of flash according to [memory_id]
        blhost: flash-erase-region <addr> <byte_count> [memory_id]
        """
        timeout = self.eval_timeout(byte_count)

        cmd = "flash-erase-region {addr} {byte_count}".format(addr=addr, byte_count=byte_count)
        return self.run_command(cmd, memid=memid, timeout=timeout)

    def flash_erase_all_unsecure(self):
        """
        Erase all internal flash, including protected regions
        blhost: flash-erase-all-unsecure
        """
        return self.run_command("flash-erase-all-unsecure", timeout=DEFAULT_TIMEOUT)

    def flash_erase_all(self, memid=0):
        '''
        Erase all flash according to [memid], excluding protected regions
        blhost: flash-erase-all <memid>

        '''
        return self.run_command('flash-erase-all', memid=memid, timeout=DEFAULT_TIMEOUT)

    def receive_sb_file(self, file):
        """Receive SB file
        blhost: receive-sb-file <file>
        """

        cmd = "receive-sb-file {file}".format(file=file)
        return self.run_command(cmd, timeout=DEFAULT_TIMEOUT)

    def execute(self, addr, arg, stackpointer):
        """
        Execute at address with arg and stack pointer
        blhost: execute <addr> <arg> <stackpointer>
        """
        cmd = "execute {addr} {arg} {stackpointer}".format(addr=addr, arg=arg, stackpointer=stackpointer)
        return self.run_command(cmd)

    def call(self, addr, arg):
        """
        Call address with arg
        blhost: call <addr> <arg>
        """

        cmd = "call {addr} {arg}".format(addr=addr, arg=arg)
        return self.run_command(cmd)

    def flash_program_once(self, index, byte_count, value, mode= "LSB"):
        """
        Program Flash Program Once Field
        blhost: flash-program-once <index> <byte_count> <data> [LSB | MSB]
        """

        cmd = "flash-program-once {index} {byte_count} {value} {mode}".format(index=index, byte_count=byte_count, value=value, mode=mode)
        return self.run_command(cmd)

    def flash_read_once(self, index, byte_count):
        """
        Read Flash Program Once Field
        blhost: flash-read-once <index> <byte_count>
        """

        cmd = "flash-read-once {index} {byte_count}".format(index=index, byte_count=byte_count)
        return self.run_command(cmd)

    def flash_read_resource(self, addr, byte_count, option, file = None):
        """
        Read Resource from special-purpose, non-volatile memory and write to file, or stdout if no file specified
        """

        cmd = "flash-read-resource {addr} {byte_count} {option}".format(addr=addr, byte_count=byte_count, option=option)

        if file:
            cmd += " %s "%file
        else:
            pass

        return self.run_command(cmd)

    def configure_memory(self, memid, internal_addr):
        """
        Apply configuration block at internal memory address <internal_addr> to memory with ID <memory_id>
        blhost: configure-memory <memory_id> <internal_addr>
        """
        cmd = "configure-memory {memid} {internal_addr}".format(memid=memid, internal_addr=internal_addr)

        return self.run_command(cmd)

    def generate_key_blob(self, dek_file, blob_file):
        """
        Generate the Blob for given Dek Key
        <dek_file> - input, a binary Dek Key (128 Bits) generated by CST tool.
        <blob_file> - output, a generated blob (72 Bytes) in binary format.
        blhost: generate-key-blob <dek_file> <blob_file>
        """

        cmd = "generate-key-blob {dek_file} {blob_file}".format(dek_file=dek_file, blob_file=blob_file)

        return self.run_command(cmd)

    def reliable_update(self, addr):
        """
        Copy backup app from address to main app region or swap flash using indicator address
        blhost: reliable-update <addr>
        """

        cmd = "reliable-update {addr}".format(addr=addr)

        return self.run_command(cmd)

    def key_provisioninig_enroll(self):
        """
        Key provisioning enroll. No argument for this operation.
        blhost: key-provisioning enroll
        """

        cmd = "key-provisioning enroll"

        return self.run_command(cmd)

    def key_provisioning_set_user_key(self, typeid, file, size=None):
        """
        Send the user key specified by <type> to bootloader. 
        <file> is the binary file containing user key plaintext. If <size> is not specified, the entire <file> will be sent. 
        Otherwise, only send the first <size> bytes.
        blhost: key-provisioning set_user_key <type> <file> [,<size>]
        """

        cmd = "key-provisioning set_user_key {type} {file}".format(type=typeid, file=file)

        if size:
            cmd += ",%s "%size
        else:
            pass

        return self.run_command(cmd)

    def key_provisioning_set_key(self, typeid, size):
        """
        Generate <size> bytes of the key specified by <type>.
        blhost: key-provisioning set_key <type> <size>
        """

        cmd = "key-provisioning set_key {type} {size}".format(type=typeid, size=size)

        return self.run_command(cmd)

    def key_provisioning_write_key_nonvolatile(self, memid):
        """
        Write the key to a nonvolatile memory to bootloader.
        blhost: key-provisioning write_key_nonvolatile <memid>
        """

        cmd = "key-provisioning write_key_nonvolatile {memid}".format(memid=memid)

        return self.run_command(cmd)

    def key_provisioning_read_key_nonvolatile(self, memid):
        """
        Load the key from a nonvolatile memory to bootloader.
        blhost: key-provisioning read_key_nonvolatile <memid>
        """

        cmd = "key-provisioning read_key_nonvolatile {memid}".format(memid=memid)

        return self.run_command(cmd)

    def key_provisioning_write_key_store(self, file, size=None):
        """
        Send the key store to bootloader. 
        <file>is the binary file containing key store. 
        If <size> is not specified, the entire <file> will be sent. 
        Otherwise, only send the first <size> bytes.

        blhost: key-provisioning write_key_store <file>[,<size>]
        """

        cmd = "key-provisioning write_key_store {file}".format(file=file)

        if size:
            cmd += ",%s "%size
        else:
            pass

        return self.run_command(cmd)

    def key_provisioning_read_key_store(self, file):
        """
        Read the key store from bootloader to host(PC). <file> is the binary file to store the key store.
        blhost: key-provisioning read_key_store <file>
        """

        cmd = "key-provisioning read_key_store {file}".format(file=file)

        return self.run_command(cmd)

    def list_memory(self):
        """
        List all on-chip Flash and RAM regions, and off-chip memories, supported by current device.
        Only the configured off-chip memory will be list.
        blhost: list-memory
        """
        return self.run_command("list-memory", json=False)

    def efuse_program_once(self, addr, data, iflock=None):
        """
        Program one word of OCOTP Filed.
        <addr> is ADDR of OTP word, not the shadowed memory address.
        <data> is hex digits without prefix '0x'
        """
        cmd = "efuse-program-once {addr} {data}".format(addr=addr, data=data)

        if iflock:
            cmd += " %s "%iflock
        else:
            pass

        return self.run_command(cmd)

    def efuse_read_once(self, addr):
        """
        Read one word of OCOTP Field.
        <addr> is ADDR of OTP word, not the shadowed memory address.
        blhost: efuse-read-once <addr>
        """

        cmd = "efuse-read-once {addr}".format(addr=addr)

        return self.run_command(cmd)
