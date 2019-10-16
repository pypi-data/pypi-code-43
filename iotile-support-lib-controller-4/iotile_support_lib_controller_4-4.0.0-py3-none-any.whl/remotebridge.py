import time
import struct
import os
import sys
import binascii
from tempfile import NamedTemporaryFile
import subprocess
import hashlib
from iotile.core.utilities.console import ProgressBar
from iotile.core.exceptions import *
from iotile.core.hw.exceptions import RPCNotFoundError
from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from iotile.core.utilities.typedargs.annotate import param, annotated, return_type, context
from iotile.core.utilities.typedargs import iprint, type_system
from iotile.core.utilities.intelhex import IntelHex
from .firmware_image_analyzer import FirmwareImageAnalyzer

@context("RemoteBridge")
class RemoteBridgePlugin(TileBusProxyPlugin):
    """A Python interface to the untrusted remote bridge component on an IOTile Controller

    The untrusted remote bridge can be used to send scripts down to a device that are
    executed once the entire script is received, stored in flash and authenticated.
    """

    SD_UPGRADE_CON_VERSION = 4
    SD_UPGRADE_EXEC_VERSION = 3

    def _batch(self, iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    def __init__(self, parent):
        super(RemoteBridgePlugin, self).__init__(parent)
        self.script = None

    def begin_script(self):
        """Indicate that we are going to start loading a script"""

        err, = self.rpc(0x21, 0x00, result_format="L", timeout=10.0)
        return err

    def end_script(self):
        """Indicate that we are going to start loading a script"""

        err, = self.rpc(0x21, 0x02, result_format="L")
        return err

    @return_type("integer")
    def trigger_script(self):
        """Indicate that we are going to start loading a script"""

        err, = self.rpc(0x21, 0x03, result_format="L")
        return err

    @return_type("list(integer)")
    def query_status(self):
        """Query the status of script loading or execution"""

        status, error = self.rpc(0x21, 0x04, result_format="LL")
        return status, error

    @param("target", "fw_tileselector", desc="Tile to reflash")
    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def reflash_tile(self, target, firmware):
        """Synchronously reflash the tile firmware in the given slot"""

        self.create_script()
        self.add_reflash_tile_action(target, firmware)
        self.send_script()

        self.wait_script()

    @annotated
    def wait_script(self):
        """Trigger a script and then synchronously wait for it to finish processing"""

        self.trigger_script()
        status, error = self.query_status()
        if error != 0:
            raise HardwareError("Error executing remote script", error_code=error)

        iprint("Waiting for script to validate")
        while status == 3:
            time.sleep(0.1)
            status, error = self.query_status()
            if error != 0:
                raise HardwareError("Error executing remote script", error_code=error)


        iprint("Waiting for script to finish executing")

        while status != 0:
            if type_system.interactive:
                sys.stdout.write('.')
                sys.stdout.flush()

            time.sleep(0.1)
            status, error = self.query_status()
            if error != 0:
                raise HardwareError("Error executing remote script", error_code=error)


        if type_system.interactive:
            sys.stdout.write('\n')

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    @param("auto_update", "bool", desc="Flag to auto update bootloader and softdevice if needed.")
    def reflash_controller(self, firmware, auto_update=False):
        """Reflash the controller with new firmware"""

        self.create_script()

        if self._check_required_updates(firmware, auto_update):
            self._update_softdevice_and_executive()

        enhanced = self._is_sd_upgraded_controller()

        if enhanced is True:
            self.add_enhanced_reflash_controller_action(firmware, 0)
        else:
            self.add_reflash_controller_action(firmware)

        self.send_script()
        self.trigger_script()

        iprint("Waiting 10 seconds for script to finish executing")
        time.sleep(10)
        iprint("NB, you must reconnect to the controller now until we support persistent connections across resets")

    @param("pingpong", "path", "readable", desc="Firmware file for the pingpong shim")
    @param("controller", "path", "readable", desc="Firmware file for the controller image")
    @param("vendor_stack", "path", "readable", desc="Vendor stack image")
    @param("out_path", "path", "writeable", desc="Path of output file")
    def build_OTA_script(self, pingpong, controller, vendor_stack, out_path):
        """Create .trub script for OTA SD upgrade"""

        self.create_script()

        self.add_reflash_controller_action(pingpong)
        self.add_enhanced_reflash_controller_action(controller, 1)
        self.add_enhanced_reflash_controller_action(vendor_stack, 0, arch_code=False)

        self.dump_script(out_path)

    def push_script(self, buffer, progress=None):
        """Push a byte array into the controller as a remote script"""

        progress_bar = progress

        def update_progress(current, total):
            if progress_bar is not None:
                progress.progress(current*100/total)

        self._proxy.stream.send_highspeed(buffer, update_progress)

    @annotated
    def reset_script(self):
        """Send a RPC to reset the trub script"""

        self.rpc(0x21, 0x05, result_format="L", timeout=15.0)

    @annotated
    def create_script(self):
        """Create a new empty script for downloading to a controller"""

        self.script = bytearray()

    @param("target", "fw_tileselector", desc="Tile to reflash")
    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def add_reflash_tile_action(self, target, firmware):
        """Add a record to our current script that reflashes a tile on the device"""

        #FIXME: This is hardcoded data from NXP LPC824 cortex m0+ 
        offset = 6*1024
        total_size = 32*1024

        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        bindata = self.load_binary_firmware(firmware, offset, total_size)

        #FIXME: Include hardware type here
        bootload_header = struct.pack("<LL8sBxxx", offset, len(bindata), target.raw_data, 0)
        self.add_record(1, bootload_header + bindata)

    def load_binary_firmware(self, firmware, offset=None, check_size=None):
        """Extracts/loads binary data from a firmware file"""

        if not firmware.endswith(".elf") and not firmware.endswith(".hex"):
            raise ArgumentError("You must pass an ARM firmware image in elf/hex format", path=firmware)

        #Get a temporary file to store the binary dump
        tmpf = NamedTemporaryFile(delete=False)
        tmpf.close()

        tmp = tmpf.name

        objcopy_args = ['arm-none-eabi-objcopy', '-O', 'binary']

        try:
            if firmware.endswith(".hex"):
                objcopy_args.append('--gap-fill')
                objcopy_args.append('0xFF')
                objcopy_args.append('-I')
                objcopy_args.append('ihex')
            objcopy_args.append(firmware)
            objcopy_args.append(tmp)

            err = subprocess.call(objcopy_args)
            if err != 0:
                raise ExternalError("Cannot convert elf to binary file", error_code=err)

            with open(tmp, "rb") as f:
                bindata = f.read()

        finally:
            os.remove(tmp)

        if check_size is not None and (offset + len(bindata) != check_size):
            raise ArgumentError("Firmware image is the wrong size", actual_size=len(bindata), desired_size=(check_size - offset))

        return bindata

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    @param("arch_code", "bool", desc="Specifying if file is an arch firmware image")
    def add_reflash_controller_action(self, firmware, arch_code=True):
        """Add reflash record to script"""

        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        fw_image = self.load_binary_firmware(firmware)

        #This is the firmware offset specific to the con_nrf52832 with softdevice 3.0
        firmware_info = FirmwareImageAnalyzer(firmware, arch_code=arch_code)

        bootload_header = struct.pack("<LL", firmware_info.min_addr, len(fw_image))
        self.add_record(2, bootload_header + fw_image)

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    @param("flags", "integer", desc="Flags for enhanced record header")
    @param("arch_code", "bool", desc="Specifying if file is an arch firmware image")
    def add_enhanced_reflash_controller_action(self, firmware, flags, arch_code=True):
        """Add enhanced reflash record to script"""

        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        fw_image = self.load_binary_firmware(firmware)

        firmware_info = FirmwareImageAnalyzer(firmware, arch_code=arch_code)

        # TODO add compression settings and preinstall checks
        compression_settings = bytearray(16)
        preinstall_checks = bytearray(64)

        bootload_header = struct.pack("<LLLBBBB16s64s", firmware_info.min_addr, len(fw_image), len(fw_image),
                                      1, flags, 0, 0, compression_settings, preinstall_checks)

        self.add_record(6, bootload_header + fw_image)

    def add_record(self, record_type, contents):
        """Add an action record to the current script with an appropriate header"""

        record_header = record_header = struct.pack("<LBBBB", len(contents)+8, record_type, 0, 0, 0)

        self.script += record_header + contents

    def add_rpc_action(self, address, cmd, payload, resp_size=0, variable_resp=False, check_errors=False):
        """Send an RPC as part of the script

        Args:
            address (int): The addres of the tile to send the RPC to
            cmd (int): The RPC id to call
            payload (bytearray): The payload buffer for the RPC
            resp_size (int): The expected response size if the rpc gives a fixed size
            variable_resp (bool): Whether the rpc returns a variably sized object
            check_errors (bool): Whether the rpc returns a uint32_t only that is an error code
                that we should check to ensure it's 0.

        Notes:
            Header record we are constructing is:
            typedef struct
            {
                uint16_t    command;
                uint8_t     address;
                uint8_t     variable_length_resp:1;
                uint8_t     response_length:7;
            } trub_execute_rpc_record_t;
        """

        if resp_size >= (1 << 7):
            raise ArgumentError("The expected response size is too big to fit in an RPC", resp_size=resp_size)

        if variable_resp:
            resp_length = 1
        elif check_errors:
            resp_length = (4 << 1)
        else:
            resp_length = (resp_size << 1)

        rpc_header = struct.pack("<HBB", cmd, address, resp_length)

        if check_errors:
            record_type = 4
        else:
            record_type = 3

        self.add_record(record_type, rpc_header + payload)

    @annotated
    def add_reset_action(self):
        """Reset the device"""

        self.add_record(5, bytearray())

    @param("device_id", "integer", desc='The new UUID to set')
    def add_setuuid_action(self, device_id):
        """Set the uuid of the device to the given value"""

        payload = struct.pack("<L", device_id)
        self.add_rpc_action(8, 0x2006, bytearray(payload), check_errors=True)

    @param("name", "string", desc="app or os")
    @param("tag", "integer", "nonnegative", desc="OS or app version to program")
    @param("version", "string", desc="X.Y version number to program.  X and Y must each be < 64")
    def add_setversion_action(self, name, tag, version="0.0"):
        """Update the controller's internal app or os tags and versions.

        The controller stores a 20 bit tag value that should uniquely identify
        the kind of OS or APP that it is running.  Each of those are asociated
        with a 6.6 bit X.Y major and minor version number.
        """

        if name not in ['app', 'os']:
            raise ArgumentError("You must specify either app or os to set_version", name=name)

        update_app = int(name == 'app')
        update_os = int(name == 'os')

        try:
            major, _, minor = version.partition('.')
            major = int(major)
            minor = int(minor)
        except ValueError:
            raise ArgumentError("Could not parse version as X.Y", version=version)

        if major < 0 or major >= 64:
            raise ArgumentError("Major version not in [0, 64)", version=version, parsed_major=major)

        if minor < 0 or minor >= 64:
            raise ArgumentError("Minor version not in [0, 64)", version=version, parsed_minor=minor)

        if tag >= (1 << 20):
            raise ArgumentError("Invalid tag that is too large, it must be < (1 << 20)", tag=tag)

        packed_version = tag | (major << 26) | (minor << 20)

        args = struct.pack("<LLBB", packed_version, packed_version, update_os, update_app)
        self.add_rpc_action(8, 0x100B, bytearray(args), check_errors=True)

    @param("user_key", "string", desc='The device key to set as 64 hex digits')
    def add_setuserkey_action(self, user_key):
        """Set the user key of a device
        """

        binkey = bytearray(binascii.unhexlify(user_key))
        if len(binkey) != 32:
            raise ArgumentError("You must pass 64 hex digits that convert into a 32 byte key", keylength=len(binkey))

        lowpayload = struct.pack("<HH16s", 0, 0, bytes(binkey[:16]))
        highpayload = struct.pack("<HH16s", 1, 0, bytes(binkey[16:]))
        self.add_rpc_action(8, 0x1007, bytearray(lowpayload), check_errors=True)
        self.add_rpc_action(8, 0x1007, bytearray(highpayload), check_errors=True)

    @param("graph_file", "path", "readable", desc="The binary sensorgraph file to load")
    def add_loadsensorgraph_action(self, graph_file):
        """Load the sensorgraph specified by the binary file graph_file

        Note that this action turns into a sequence of RPCs executed as part of the script.
        If the graph_file does not specify a reset as the first RPC, it will not erase the
        current sensor graph.  Similarly, if it does not specify persist, it will not save
        the sensor graph to flash.
        """

        with open(graph_file, "r") as f:
            lines = f.readlines()

        if len(lines) < 3:
            raise DataError("Invalid sensorgraph file that did not have a header")

        header = lines[0].rstrip()
        version = lines[1].rstrip()
        filetype = lines[2].rstrip()

        if header != "Sensor Graph":
            raise DataError("Invalid sensorgraph file that had an unknown header", expected="Sensor Graph", read=header)

        if version != "Format: 1.0":
            raise DataError("Unknown sensorgraph file version", expected="Format: 1.0", read=version)

        if filetype != "Type: BINARY":
            raise DataError("Sensorgraph file is not in ascii format", excepted="Type: BINARY", read=filetype)

        cmds = [x.strip() for x in lines[3:] if not x.startswith('#') and not x.strip() == ""]

        for cmd in cmds:
            rpc_id, _, arg = cmd.partition(":")

            arg = arg.strip()
            rpc_id = rpc_id.strip()

            if arg == "":
                arg = bytearray()
            else:
                arg = bytearray(binascii.unhexlify(arg))

            rpc_id = int(rpc_id, 16)
            self.add_rpc_action(8, rpc_id, arg, check_errors=True)

    def add_header(self, script):
        """Add a hashed header to the script for verification"""

        #Script header is 2 uint32_t variables and a 16 byte hash code
        length = len(script) + 4 + 4 + 16
        header = struct.pack("<LL", 0x1F2E3D4C, length)

        script = bytearray(header) + script

        sha = hashlib.sha256()
        sha.update(script)

        hashval = bytearray(sha.digest())[:16]
        return hashval + script

    @param("outfile", "path", "writeable", desc="Path of output file")
    def dump_script(self, outfile):
        """Dump the current script to a file"""

        if self.script is None:
            raise HardwareError("You must first load a script before you can dump it")

        #Add a header to our script
        script = self.add_header(self.script)

        with open(outfile, "wb") as file:
            file.write(script)

    @param("script", "path", desc="Optional file to load script from")
    def send_script(self, script=None):
        """Send the currently loaded script to the attached controller

        If a script file is instead supplied as an argument, use that instead
        of the currently loaded one.

        """

        if script is not None:
            with open(script, "rb") as sfile:
                script = sfile.read()
        else:
            if self.script is None:
                raise HardwareError("You must first load a script before you can send it to a device")

            #Add a header to our script
            script = self.add_header(self.script)

        err = self.begin_script()
        if err:
            raise HardwareError("Error beginning script", error_code=err)

        progress = ProgressBar("Downloading script", 100)

        progress.start()
        self.push_script(script, progress)
        progress.end()

        err = self.end_script()

        if err:
            raise HardwareError("Error beginning script", error_code=err)

    def _get_controller_info(self):
        """Retrieves controller firmware"""

        _hw_type, name, major, minor, patch, _status = self.rpc(0x00, 0x04, result_format="H6sBBBB")
        controller_info = {
            'name': name.decode("utf-8"),
            'major_version': major,
            'minor_version': minor,
            'patch_version': patch
            }

        return controller_info

    def _get_exec_info(self):
        """Return information about the executive
        
        Gets information about the executive image. The information received
        is of CDBRegistrationPacket type. The only information reported are
        the API version, executive version, and name of the module.

        Returns:
            str: Executive image information.
        """
        _, api_major, api_minor, name, _, _, _, \
        executive_major, executive_minor, executive_patch, _, _ \
        = self.rpc(0xCC, 0xCE, result_format="BBB6sBBBBBBBL")

        exec_info = {
            'api_version': (api_major, api_minor),
            'name': name.decode('utf-8'),
            'major_version': executive_major,
            'minor_version': executive_minor,
            'patch_version': executive_patch
        }

        return exec_info

    def _is_sd_upgraded_controller(self):
        """Checks if the running device is a controller >= 4.0.0"""

        controller_info = self._get_controller_info()

        if controller_info['name'] != 'NRF52 ':
            return False

        try:
            exec_info = self._get_exec_info()
            if exec_info['major_version'] >= RemoteBridgePlugin.SD_UPGRADE_EXEC_VERSION \
            and controller_info['major_version'] >= RemoteBridgePlugin.SD_UPGRADE_CON_VERSION:
                return True
        except RPCNotFoundError:
            return False

    def _check_required_updates(self, firmware, auto_update):
        """Checks if user's firmware requires device's bootloader/softdevice to be upgraded first"""

        controller_info = self._get_controller_info()

        if controller_info['name'] != 'NRF52 ':
            return False

        firmware_info = FirmwareImageAnalyzer(firmware)

        if controller_info['major_version'] < RemoteBridgePlugin.SD_UPGRADE_CON_VERSION \
            and firmware_info.get_firmware_version()[0] >= RemoteBridgePlugin.SD_UPGRADE_CON_VERSION:
            if auto_update is False:
                use_update = input("The current executive/softdevice on the device is out of\n"
                                   "date and incompatible with the firmware you want to load.\n"
                                   "Do you wish to update?\n(y/n)")
                if use_update.lower() == 'y':
                    return True
                else:
                    raise ArgumentError("Firmware downgrading not allowed")
            else:
                return True
        elif controller_info['major_version'] >= RemoteBridgePlugin.SD_UPGRADE_CON_VERSION \
            and firmware_info.get_firmware_version()[0] < RemoteBridgePlugin.SD_UPGRADE_CON_VERSION:
            raise ArgumentError("Firmware downgrading not allowed")

        return False

    def _update_softdevice_and_executive(self):
        """Adds the bundled pingpong and softdevice images to the trub script"""

        script_path = os.path.realpath(__file__)
        script_dirname = os.path.dirname(script_path)

        self.add_reflash_controller_action(os.path.join(script_dirname, 'data', 'pingpong_exec_bundle.hex'))
        self.add_enhanced_reflash_controller_action(os.path.join(script_dirname, 'data', 's112_nrf52_6.1.1_softdevice.hex'), 1, arch_code=False)
        