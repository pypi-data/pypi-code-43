#nrf52832_controller.py
#Proxy object for controller module based on

from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.proxy.external_proxy import find_proxy_plugin
from typedargs.annotate import param, annotated, return_type, context, docannotate
from typedargs import iprint
from iotile.core.hw.exceptions import *
from iotile.core.exceptions import *
from iotile.core.utilities import typedargs
from iotile.core.dev.semver import SemanticVersionRange
from iotile_support_lib_controller_4.reference_controller_proxy import ReferenceControllerProxy
import datetime
import calendar
import struct

def _bcd2int(bcd):
    decimal = int('%x' % bcd)
    return decimal

def _int2bcd(decimal):
    bcd = int(str(decimal), 16)
    return bcd

@context("NRF52832Controller")
class NRF52832Controller (ReferenceControllerProxy):
    def __init__(self, stream, addr):
        super(NRF52832Controller, self).__init__(stream, addr)
        self.name = 'NRF52832Controller'
        self._rtcman = RTCManagerPlugin(self)

    @classmethod
    def ModuleName(cls):
        return 'NRF52 '

    @classmethod
    def ModuleVersion(cls):
        return SemanticVersionRange.FromString('^4.0.0')

    @annotated
    def rtc_manager(self):
        """Real Time Clock Control Manager"""
        return self._rtcman

    @return_type("list(integer)")
    def get_bootstrap_info(self):
        bid = self.rpc(0xAC,0x02, result_format="LLLLL")
        print("{0:X}, {1:X}, {2:X}, {3:X}, {4:X}".format(bid[0], bid[1], bid[2], bid[3], bid[4]))
        return bid

    @return_type("integer", "hex")
    def get_board_id(self):
        boardid, = self.rpc(0x00,0x05, result_format="L")
        return boardid

    @return_type("integer")
    def inc_atecc(self):
        """Test incrementing a counter inside the ATECC508A chip."""

        err, value = self.rpc(0xAB, 0x01, result_format="LL")
        if err:
            raise HardwareError("Error talking to ATECC508A chip", code=err)

        return value

    @return_type("basic_dict")
    def query_streaming(self):
        """Query the current parameters used for streaming data over bluetooth.

        This function returns information like:
        - The maximum size of a report that the device will emit
        - The supported and selected compression types to be used when transmitting
          data.
        """

        max_packet, supported_comp, chosen_comp = self.rpc(0x0A, 0x06, result_format="LBB")

        return {
            'max_report_size': max_packet,
            'supported_compression': supported_comp,
            'selected_compression': chosen_comp
        }

    @param("max_packet", "integer", "positive", desc="The maximum report size that the device should send")
    def config_streaming(self, max_packet):
        """Configure the curent parameters to use for streaming until we disconnect."""

        # Currently hardcode a lack of support for compression

        err, = self.rpc(0x0A, 0x05, max_packet, 0, arg_format="LB", result_format="L")
        if err:
            raise HardwareError("Error configuring streaming", code=err)

    @docannotate
    def query_bleparams(self):
        """Query the current BLE connection parameters.

        The connection interval and timeout information is returned
        as well as the device's preferred information as a dictionary.

        This function can be used to determine whether you should
        request the device change its connection parameters.

        Returns:
            basic_dict: A dictionary of connection information.
        """

        err, interval, timeout, pref_min, pref_max, pref_timeout = self.rpc(0x80, 0x00, result_format="LHHHHH2x")
        if err != 0:
            raise HardwareError("Could not query ble parameters", error_code=err)

        return {
            'conn_interval_ms': interval * 1.25,
            'preferred_min_ms': pref_min * 1.25,
            'preferred_max_ms': pref_max * 1.25,
            'timeout_ms': timeout * 10,
            'pref_timeout_ms': pref_timeout * 10
        }

    @docannotate
    def update_bleparams(self, min_conn, max_conn, timeout):
        """Update the current BLE connection parameters.

        These parameters determine the maximum throughput of the BLE connection
        by setting the interval with which the two parties communicate.  With
        most devices either 4 or 6 packets may be sent in each direction during
        each connection interval. With standard 20-byte packets this means that
        the maximum throughput is:
              4*20*1000
            -------------
            conn_interval

        with conn_interval in units of milliseconds, this will result in a
        throughput in bytes per second.  Note that this throughput will only
        be reached if you are able to queue at least 4 packets in advance of
        each connection interval, which will only be possible if you don't need
        an explicit acknowledgement from the other side for each packet before
        generating the next packet.

        This function will trigger the device to request a connection parameter
        update with its central and then return.  You can check if the parameters
        changed by calling query_bleparams afterward.

        There are certain requirements that must be followed for the parameters
        or if will be rejected by the partner device.  It may always be rejected
        if the partner feels like it.

        In particular:
        - min_conn in [7.5 ms, 4 s]
        - max_conn >= min_conn and giving a range is better than forcing a single
          value although you can set min_conn to max_conn to force a single value.
        - timeout in [100 ms, 32 s]

        Args:
            min_conn (float): The minimum connection interval in ms.  The minimum
                acceptable value is 7.5 ms.
            max_conn (float): The maximum connection interval in ms.  The minimum
                acceptable value is 7.5 ms.
            timeout (float): The supervisory timeout in seconds.  If
                no successful communication happens in this timeout, the
                connection is terminated.  This minimum acceptable value is 100 ms.
        """

        min_conn = int(min_conn / 1.25)
        max_conn = int(max_conn / 1.25)
        timeout = int(timeout / 0.01)

        err, = self.rpc(0x80, 0x01, min_conn, max_conn, timeout, 0, arg_format="HHHH", result_format="L")
        if err:
            raise HardwareError("Could not trigger update to ble connection parameters", error_code=err)

    @annotated
    def reset(self):
        """Reset this controller tile."""

        #NB, the wait time here must be longer than the supervisory timeout on the BLE
        #connection, otherwise the ble connection will not be seen to be disconnected
        #on the client side.
        iprint("Resetting, takes at least 2 seconds")
        TileBusProxyObject.reset(self, wait=2.0)

    @return_type("string")
    def hardware_version(self):
        """Return the embedded hardware version string for this tile
        """
        res = self.rpc(0x00, 0x02, result_type=(0, True))

        #Result is a string but with zero appended to the end to make it a fixed 10 byte
        #size
        binary_version = res['buffer']

        ver = ""

        for x in binary_version:
            if x != 0:
                ver += chr(x)

        return ver

    @return_type("basic_dict")
    def exec_info(self):
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
            'executive_version': (executive_major, executive_minor, executive_patch)
        }

        return exec_info

    @param("expected", "string", desc="The hardware string we expect to find")
    @return_type("bool")
    def check_hardware(self, expected):
        """Make sure the hardware version is what we expect

        Returns true if the hardware is the expected version, false otherwise
        """

        if len(expected) < 10:
            expected += '\0'*(10 - len(expected))
        err, = self.rpc(0x00, 0x03, expected, result_format="L")
        if err == 0:
            return True

        return False



@context("RTCManager")
class   RTCManagerPlugin(TileBusProxyPlugin):
    """ Manager to manipulate the RTC.
        These functions do not set the controller time. They only directly access the RTC
        for debug/testing functionality. See the lib_controller::test_interface for the
        official interface to synchronize the clocks on the controller
    """

    @param('year', 'integer',   desc='Year to set:   (2000 - 2099)')
    @param('month', 'integer',  desc='Month to set:  (1 - 12)')
    @param('day', 'integer',    desc='Day to set:    (1 - 28|29|30|31, depending on month and year')
    @param('hour', 'integer',   desc='Hour to set:   (0 - 23)')
    @param('minute', 'integer', desc='Minute to set: (0 - 59)')
    @param('second', 'integer', desc='Second to set: (0 - 59)')
    def rtc_set_datetime(self, year, month, day, hour, minute, second):
        """Sets time in the RTC"""
        t = datetime.datetime(year,month,day,hour,minute,second)
        self._set_datetime(t)
        return

    @return_type("list(integer)")
    def rtc_get_datetime(self):
        """Gets the RTC time as a list of integers"""
        hund, second, minute, hour, day, wday, month, year = self.rpc(0xAB,0x02, result_format="BBBBBBBB")
        dttuple = (year+2000,month,day,hour,minute,second)
        return dttuple

    @return_type("integer", "hex")
    @param("seconds", "integer", desc="Number of seconds since 1/1/2000 0:0:0")
    def rtc_set_secs(self, seconds):
        """Setting the RTC time in seconds since the epoch 1/1/2000 0:0:0 from the controller"""
        err, = self.rpc(0xAB,0x04, seconds, arg_format="L", result_format="L")
        if err:
            raise HardwareError("Error setting RTC seconds", code=err, seconds=seconds)
        return seconds

    @return_type("integer","hex")
    def rtc_get_secs(self):
        """Getting the RTC time in seconds since the epoch 1/1/2000 0:0:0 from the controller"""
        err, seconds = self.rpc(0xAB,0x05, result_format="LL")
        if err:
            raise HardwareError("Error getting seconds from RTC", code=err, seconds=seconds)
        return seconds

    @param("addr", "integer", desc="Register Address to be written")
    @param("data", "integer", desc="Data byte to be written")
    def rtc_set_byte(self, addr, data):
        """ Sets a data byte in the RTC """
        err, = self.rpc(0xAB, 0x06, addr, data, arg_format="BB", result_format="L")
        if err:
            raise HardwareError("Error setting byte in RTC", code=err, addr=addr, data=data)
        return

    @return_type("integer", "hex")
    @param("addr", "integer", desc="Register Address to be read")
    def rtc_get_byte(self, addr):
        """ Reads a data byte from the RTC """
        err, data = self.rpc(0xAB,0x07, addr, arg_format="B", result_format="LL")
        if err:
            raise HardwareError("Error getting byte from RTC", code=err, addr=addr, data=data)
        return data

    @param("timestamp", "integer", desc="POSIX Timestamp in seconds since 1970")
    def rtc_set_linux_timestamp(self, timestamp):
        """Sets time in RTC using a POSIX timestamp"""
        t = datetime.datetime.utcfromtimestamp(timestamp)
        self._set_datetime(t)
        return

    @return_type("integer")
    def rtc_get_linux_timestamp(self):
        """Gets the RTC time as a POSIX timestamp"""
        t = self._get_datetime()
        ts = calendar.timegm(t.timetuple())
        return ts

    @return_type("string")
    def rtc_set_time_to_now(self):
        """Sets time to current computer time in UTC"""
        t = datetime.datetime.utcnow()
        self._set_datetime(t)
        timestr = self._gen_timestr(t)
        return timestr

    @return_type("string")
    def rtc_get_timestr(self):
        """Gets the RTC time string"""
        t = self._get_datetime()
        timestr = self._gen_timestr(t)
        return timestr


    # Support function to set time from a datetime object
    def _set_datetime(self, dt):
        if (dt.year < 2000):
            raise ArgumentError("Invalid Year `{0}`. Year must be >= 2000.".format(dt.year))
        hund    = int(dt.microsecond / 10000)
        second  = int(dt.second)
        minute  = int(dt.minute)
        hour    = int(dt.hour)
        day     = int(dt.day)
        month   = int(dt.month)
        year    = int(dt.year - 2000)
        weekday = (int(dt.strftime("%w")))

        timenow = struct.pack("<BBBBBBBB", hund, second, minute, hour, day, weekday, month, year)
        err, = self.rpc(0xAB,0x03, timenow, arg_format="%ds" % len(timenow), result_format="L")
        if err:
            raise HardwareError("Error Syncing time to RTC", code=err)
        return

    # Support function to fetch time from the RTC and return a datetime object
    def _get_datetime(self):
        hund, second, minute, hour, day, wday, month, year = self.rpc(0xAB,0x02, result_format="BBBBBBBB")
        t = datetime.datetime(2000+year,month,day,hour,minute,second)
        return t

    # Common time string generation
    def _gen_timestr(self, dt):
        timestr = dt.strftime("%x %X %Z")
        return timestr



