# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.wrappers.py

This file contains wrappers for TSP01B DLL functions.

Author: Dima Pustakhod
Copyright: TU/e
"""
from ctypes import c_double
from ctypes import byref
from typing import Tuple


from .constants import VI_NULL, TLTSP_BUFFER_SIZE, TLTSP_ERR_DESCR_BUFFER_SIZE
from .dll_routines import _call_dll_fcn
from .typedef import ViSession, ViRsrc, ViStatus
from .typedef import ViUInt32, ViInt32, ViInt16, ViUInt16
from .typedef import ViReal64
from .typedef import ViBoolean
from .typedef import ViChar_arr


MSG_ENCODING = 'ascii'


def _calibrationMessage(instrument_handle: int) -> Tuple[int, str]:
    """Return a human readable calibration message.

    This function returns a human readable calibration message.
    NOT IMPLEMENTED.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    message : str
        The calibration message. NOT IMPLEMENTED.
    """
    instrumentHandle = ViSession(instrument_handle)

    message = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, message)

    return status, message.value.decode(MSG_ENCODING)


def _close(instrument_handle: int) -> int:
    """Close the instrument driver session.

    The instrument must be reinitialized to use it again.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)

    status = _call_dll_fcn(instrumentHandle)

    return status


def _errorMessage(
    instrument_handle: int, status_code: int = 0
) -> Tuple[int, str]:
    """Return error code as a user readable string.

    This function takes the error code returned by the instrument driver
    functions, interprets it and returns it as an user readable string.

    Status/error codes and description:
    --- Instrument Driver Errors and Warnings ---
    Status      Description
    -------------------------------------------------
    0  No error (the call was successful).
    0x3FFF0085  Unknown Status Code     - VI_WARN_UNKNOWN_STATUS
    0x3FFC0901  WARNING: Value overflow - VI_INSTR_WARN_OVERFLOW
    0x3FFC0902  WARNING: Value underrun - VI_INSTR_WARN_UNDERRUN
    0x3FFC0903  WARNING: Value is NaN   - VI_INSTR_WARN_NAN
    0xBFFC0001  Parameter 1 out of range.
    0xBFFC0002  Parameter 2 out of range.
    0xBFFC0003  Parameter 3 out of range.
    0xBFFC0004  Parameter 4 out of range.
    0xBFFC0005  Parameter 5 out of range.
    0xBFFC0006  Parameter 6 out of range.
    0xBFFC0007  Parameter 7 out of range.
    0xBFFC0008  Parameter 8 out of range.
    0xBFFC0012  Error Interpreting instrument response.

    --- Instrument Errors ---
    Range: 0xBFFC0700 .. 0xBFFC0CFF.
    Calculation: Device error code + 0xBFFC0900.
    Please see your device documentation for details.

    --- VISA Errors ---
    Please see your VISA documentation for details.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    status_code : int
        This parameter accepts the error codes returned from the
        instrument driver functions. Default Value: 0 - VI_SUCCESS.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    description : str
        This parameter returns the interpreted code as an user readable
        message string.
    """
    instrumentHandle = ViSession(instrument_handle)
    statusCode = ViStatus(status_code)

    description = ViChar_arr(b'\0' * TLTSP_ERR_DESCR_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, statusCode, description)

    return status, description.value.decode(MSG_ENCODING)


def _errorQuery(instrument_handle: int) -> Tuple[int, int, str]:
    """Query the instrument's error queue manually.

    This function queries the instrument's error queue manually.
    Use this function to query the instrument's error queue if the
    driver's error query mode is set to manual query.

    Note:
    The returned values are stored in the drivers error store. You may
    use <Error Message> to get a descriptive text at a later point of
    time.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    errorNumber : int
        This parameter returns the instrument error number.
    errorMessage : str
        This parameter returns the instrument error message.
    """
    instrumentHandle = ViSession(instrument_handle)

    errorNumber = ViInt32()
    errorMessage = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, byref(errorNumber), errorMessage)

    return status, errorNumber.value, errorMessage.value.decode(MSG_ENCODING)


def _findRsrc() -> Tuple[int, int]:
    """Get the number of connected devices.

    Gets the number of connected devices available in your system that can be
    controlled with this driver.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    deviceCount : int
        The number of connected devices you can control with this driver.
    """
    # This parameter is only needed for IVI compliant. Set to VI_NULL.
    instrumentHandle = VI_NULL

    deviceCount = ViUInt32()

    status = _call_dll_fcn(instrumentHandle, byref(deviceCount))

    return status, deviceCount.value


def _getExtRefVoltage(instrument_handle: int) -> Tuple[int, float]:
    """Return the reference voltage of the external thermistor.  TODO: exclude from test

    This function returns the reference voltage of the external
    thermistor hw frontend if service mode has been enabled. Do not use
    in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    referenceVoltage : float
        Reference voltage of the external thermistor hardware frontend
        in Volt.
    """
    instrumentHandle = ViSession(instrument_handle)

    referenceVoltage = c_double()

    status = _call_dll_fcn(instrumentHandle, byref(referenceVoltage))

    return status, referenceVoltage.value


def _getExtSerResist(instrument_handle: int) -> Tuple[int, float]:
    """Return the serial resistance of the external thermistor.  TODO: exclude from test

    This function returns the serial resistance of the external
    thermistor hw frontend if service mode has been enabled. Do not use
    in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    serialResistance : float
        Serial resistance value for the external thermistor hardware
        frontend in Ohm.
    """
    instrumentHandle = ViSession(instrument_handle)

    serialResistance = c_double()

    status = _call_dll_fcn(instrumentHandle, byref(serialResistance))

    return status, serialResistance.value


def _getHumidityData(
    instrument_handle: int, attribute: int
) -> Tuple[int, float]:
    """Return the relative humidity value of the last humidity measurement.

    This function returns the relative humidity value of the last
    humidity measurement in % r.H.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    humidityValue : float
        This parameter returns the last measured humidity value in % r.H.
    """
    instrumentHandle = ViSession(instrument_handle)
    attribute_ = ViInt16(attribute)

    humidityValue = ViReal64()

    status = _call_dll_fcn(instrumentHandle, attribute_, byref(humidityValue))

    return status, humidityValue.value


def _getHumSensOffset(
    instrument_handle: int, attribute: int
) -> Tuple[int, float]:
    """Return the sensor's absolute humidity offset in % r.H.

    This function returns the sensor's absolute humidity offset in % r.H.
    Hint: The offset will be added to the humidity value.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    attribute : int
        This parameter specifies the value to be queried.
        Acceptable values:
            TLTSP_ATTR_SET_VAL (0): Set value
            TLTSP_ATTR_MIN_VAL (1): Minimum value
            TLTSP_ATTR_MAX_VAL (2): Maximum value

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    humidityOffset : float
        This parameter returns the humidity offset in % r.H.
    """
    instrumentHandle = ViSession(instrument_handle)
    attribute_ = ViInt16(attribute)

    humidityOffset = ViReal64()

    status = _call_dll_fcn(instrumentHandle, attribute_, byref(humidityOffset))

    return status, humidityOffset.value


def _getProductionDate(instrument_handle: int) -> Tuple[int, str]:
    """Return the date of production.

    This function returns the date of production.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    productionDate : str
        This parameter returns the date of production.
    """
    instrumentHandle = ViSession(instrument_handle)

    productionDate = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, productionDate)

    return status, productionDate.value.decode(MSG_ENCODING)


def _getRsrcInfo(device_index: int) -> Tuple[int, str, str, str, bool]:
    """Get more information about the connected instruments.

    With this function, the user gets more information about the
    connected instruments that are found in the function _findRsrc().

    TODO: check why instrumentHandle is not used

    Parameters
    ----------
    device_index : int
        Index of the connected device you want to get the resource name
        from (0 to number of connected devices - 1). See _getDeviceCount().

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    modelName : str
        The model name of the connected device at the given index.
    serialNumber : str
        The serial number of the connected device at the given index.
    manufacturerName : str
        The manufacturer name of the connected device at the given index.
    resourceInUse : bool
        Boolean flag indicating if the device at given index is already
        in use by another instance.
    """
    instrumentHandle = VI_NULL
    deviceIndex = ViUInt32(device_index)

    modelName = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    serialNumber = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    manufacturerName = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    resourceInUse = ViBoolean(False)

    status = _call_dll_fcn(
        instrumentHandle,
        deviceIndex,
        modelName,
        serialNumber,
        manufacturerName,
        byref(resourceInUse),
    )

    return (
        status,
        modelName.value.decode(MSG_ENCODING),
        serialNumber.value.decode(MSG_ENCODING),
        manufacturerName.value.decode(MSG_ENCODING),
        resourceInUse.value,
    )


def _getRsrcName(device_index: int) -> Tuple[int, str]:
    """Get resource string of a connected device.

    Gets resource string of a connected device you can control with
    this driver. You don't have to open a session with the device with
    _init() before you can use this function. It returns the resource
    name of a desired device.

    Parameters
    ----------
    device_index : int
        Index of the connected device you want to get the resource name
        from (0 to number of connected devices - 1). See _getDeviceCount().

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    resourceName : str
        The resource identification string. Use this string in function
        _init().
    """
    # This parameter is only needed for IVI compliance. Set to VI_NULL.
    instrumentHandle = VI_NULL
    deviceIndex = ViUInt32(device_index)

    resourceName = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, deviceIndex, resourceName)

    return status, resourceName.value.decode(MSG_ENCODING)


def _getTemperatureData(
    instrument_handle: int, channel: int, attribute: int
) -> Tuple[int, float]:
    """Return the temperature value of the last temperature measurement in degC.

    This function returns the temperature value of the last temperature
    measurement in degC. Note: This function is valid for all temperature
    sensors only.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    attribute : int
        This parameter specifies the value to be queried.
        Acceptable values:
            TLTSP_ATTR_SET_VAL  (0): Set value
            TLTSP_ATTR_MIN_VAL  (1): Minimum value
            TLTSP_ATTR_MAX_VAL  (2): Maximum value
            TLTSP_ATTR_DFLT_VAL (3): Default value

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    temperatureValue : float
        This parameter returns the last measured temperature value in degC.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    attribute_ = ViInt16(attribute)

    temperatureValue = ViReal64()

    status = _call_dll_fcn(
        instrumentHandle, channel_, attribute_, byref(temperatureValue)
    )

    return status, temperatureValue.value


def _getTempSensOffset(
    instrument_handle: int, channel: int, attribute: int
) -> Tuple[int, float]:
    """Return the sensor's absolute temperature offset in K.

    This function returns the sensor's absolute temperature offset in K.
    Note: This function is valid for all temperature sensors only
    Hint: The offset will be added to the temperature value.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    attribute : int
        This parameter specifies the value to be queried.
        Acceptable values:
            TLTSP_ATTR_SET_VAL  (0): Set value
            TLTSP_ATTR_MIN_VAL  (1): Minimum value
            TLTSP_ATTR_MAX_VAL  (2): Maximum value

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    temperatureOffset : float
        This parameter returns the temperature offset in K.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    attribute_ = ViInt16(attribute)

    temperatureOffset = ViReal64()

    status = _call_dll_fcn(
        instrumentHandle, channel_, attribute_, byref(temperatureOffset)
    )

    return status, temperatureOffset.value


def _getThermistorExpParams(
    instrument_handle: int, channel: int, attribute: int
) -> Tuple[int, float, float, float]:
    """Return the thermistor exponential method parameters.

    This function returns the thermistor exponential method parameters.
    Note: This function is valid for external temperature sensors only.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    attribute : int
        This parameter specifies the value to be queried.
        Acceptable values:
            TLTSP_ATTR_SET_VAL  (0): Set value
            TLTSP_ATTR_MIN_VAL  (1): Minimum value
            TLTSP_ATTR_MAX_VAL  (2): Maximum value
            TLTSP_ATTR_DFLT_VAL (3): Default value

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    r0Value : float
        This parameter returns the R0 value.
    t0Value : float
        This parameter returns the T0 value.
    betaValue : float
        This parameter returns the beta value.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    attribute_ = ViInt16(attribute)

    r0Value = ViReal64()
    t0Value = ViReal64()
    betaValue = ViReal64()

    status = _call_dll_fcn(
        instrumentHandle,
        channel_,
        attribute_,
        byref(r0Value),
        byref(t0Value),
        byref(betaValue),
    )

    return status, r0Value.value, t0Value.value, betaValue.value


def _getThermRes(
    instrument_handle: int, channel: int, attribute: int
) -> Tuple[int, float]:
    """Return the resistance value of the external thermistor.

    This function returns the resistance value of the external
    temperature sensor (thermistor).
    Note: This function is valid for the external temperature sensors only.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    attribute : int
        This parameter specifies the value to be queried.
        Acceptable values:
            TLTSP_ATTR_SET_VAL  (0): Set value
            TLTSP_ATTR_MIN_VAL  (1): Minimum value
            TLTSP_ATTR_MAX_VAL  (2): Maximum value
            TLTSP_ATTR_DFLT_VAL (3): Default value

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    resistanceInOhm : float
        This parameter returns the resistance value in Ohm.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    attribute_ = ViInt16(attribute)

    resistanceInOhm = ViReal64()

    status = _call_dll_fcn(
        instrumentHandle, channel_, attribute_, byref(resistanceInOhm)
    )

    return status, resistanceInOhm.value


def _identificationQuery(
    instrument_handle: int
) -> Tuple[int, str, str, str, str]:
    """Return the device identification information.

    This function returns the device identification information.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    manufacturerName : str
        This parameter returns the manufacturer name.
    deviceName : str
        This parameter returns the device name.
    serialNumber : str
        This parameter returns the device serial number.
    firmwareRevision : str
        This parameter returns the device firmware revision.
    """
    instrumentHandle = ViSession(instrument_handle)

    manufacturerName = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    deviceName = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    serialNumber = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    firmwareRevision = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(
        instrumentHandle,
        manufacturerName,
        deviceName,
        serialNumber,
        firmwareRevision,
    )

    return (
        status,
        manufacturerName.value.decode(MSG_ENCODING),
        deviceName.value.decode(MSG_ENCODING),
        serialNumber.value.decode(MSG_ENCODING),
        firmwareRevision.value.decode(MSG_ENCODING),
    )


def _init(
    resource_name: str, id_query: bool = False, reset_device: bool = False
) -> Tuple[int, int]:
    """Initialize the instrument driver session.

    This function initializes the instrument driver session and performs
    the following initialization actions:
        (1) Opens a session to the Default Resource Manager resource and
            a session to the specified device using the Resource Name
            specified.
        (2) Performs an identification query on the instrument.
        (3) Resets the instrument to a known state.
        (4) Sends initialization commands to the instrument.
        (5) Returns an instrument handle which is used to distinguish
            between different sessions of this instrument driver.
    Note: Each time this function is invoked a unique session is opened.

    Parameters
    ----------
    resourceName : str
        This parameter specifies the device (resource) with which to
        establish a communication session. The syntax for the Instrument
        Descriptor is shown below. Optional segments are shown in square
        brackets ([]). Required segments that must be filled in are
        denoted by angle brackets (<>).

            USB[board]::0x1313::product id
            ::serial number[::interface number][::INSTR]
            Remote Access   visa://hostname[:port]/resource

        The default values for optional parameters are shown below.

        Optional Segment          Default Value
        ---------------------------------------
        board                     0
        USB interface number      0

        The product id codes for supported instruments are shown below.

        Product ID   Instrument Type
        -------------------------------------------------
        0x80F0       TSP01 with DFU interface enabled
        0x80F8       TSP01 without DFU interface enabled

        Example Resource Strings:
        --------------------------------------------------------------
        USB::0x1313::0x80F8::M12345678::INSTR
        TSP01 with a serial number of M12345678.

        visa://1.2.3.4/USB::0x1313::0x80F8::M23456789::INSTR
        Remote access to the TSP01 with a serial number of M23456789 at
        the specified IP address.

        visa://hostname/USB::0x1313::0x80F8::M34567890::INSTR
        Remote access to the TSP01 with a serial number of M23456789 on
        the specified host.

        Note: You should use _getDeviceResourceString() to get the
        Resource Name for your device.

        But you may use VISA <Find Resources> with an appropriate search
        pattern to get the Resource Name for your device too.
        For TSPxx devices use: "USB?*::0x1313::0x80F?::?*::INSTR"
    IDQuery : bool
        This parameter specifies whether an identification query is
        performed during the initialization process.
        False: Skip query.
        True: Do query (default).
    resetDevice : bool
        This parameter specifies whether the instrument is reset during
        the initialization process.
        Do only use this option if the previous parameter values are
        unknown or invalid. Never reset a device to set the equal
        parameter values after initialization again. Every device reset
        will write to the TSP01B internal EEPROM. The lifetime of this
        EEPROM is limited.
        False - no reset (default)
        True  - instrument is reset

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    instrumentHandle : int
        This parameter returns an instrument handle that is used in all
        subsequent calls to distinguish between different sessions of
        this instrument driver.
    """
    resourceName = ViRsrc(resource_name.encode(MSG_ENCODING))
    IDQuery = ViBoolean(id_query)
    resetDevice = ViBoolean(reset_device)

    instrumentHandle = ViSession()

    status = _call_dll_fcn(
        resourceName, IDQuery, resetDevice, byref(instrumentHandle)
    )

    return status, instrumentHandle.value


def _isServiceMode(instrument_handle: int) -> Tuple[int, bool]:
    """Check if the service mode is active.

    This function checks if the service mode is active.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    serviceModeActive : bool
        True if service mode on, False otherwise.
    """
    instrumentHandle = ViSession(instrument_handle)

    serviceModeActive = ViBoolean(False)

    status = _call_dll_fcn(instrumentHandle, byref(serviceModeActive))

    return status, serviceModeActive.value


def _measHumidity(instrument_handle: int) -> Tuple[int, float]:
    """Obtain relative humidity readings from the internal sensor.

    This function is used to obtain relative humidity readings from the
    internal sensor. Same as _getHumidityData().

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    humidity : float
        This parameter returns the relative humidity in % r.H.
    """
    instrumentHandle = ViSession(instrument_handle)

    humidity = ViReal64()

    status = _call_dll_fcn(instrumentHandle, byref(humidity))

    return status, humidity.value


def _measTemperature(instrument_handle: int, channel: int) -> Tuple[int, float]:
    """Obtain temperature readings from the instrument.

    This function is used to obtain temperature readings from the
    instrument. Same as _getTemperatureData().
    Note: This function is valid for all temperature sensors only.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    temperature : float
        This parameter returns the temperature in degC.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13

    temperature = ViReal64()

    status = _call_dll_fcn(instrumentHandle, channel_, byref(temperature))

    return status, temperature.value


def _reset(instrument_handle: int) -> int:
    """Reset the device to a known state.

    This function resets the device to a known state.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)

    status = _call_dll_fcn(instrumentHandle)

    return status


def _revisionQuery(instrument_handle: int) -> Tuple[int, str, str]:
    """Return the revision numbers of the driver and the firmware.

    This function returns the revision numbers of the instrument driver
    and the device firmware.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    instrumentDriverRevision : str
        This parameter returns the Instrument Driver revision.
    firmwareRevision : str
        This parameter returns the device firmware revision.
    """
    instrumentHandle = ViSession(instrument_handle)

    instrumentDriverRevision = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)
    firmwareRevision = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(
        instrumentHandle, instrumentDriverRevision, firmwareRevision
    )

    return (
        status,
        instrumentDriverRevision.value.decode(MSG_ENCODING),
        firmwareRevision.value.decode(MSG_ENCODING),
    )


def _selfTest(instrument_handle: int) -> Tuple[int, int, str]:
    """Run the device self test routine and return the test result.

    This function runs the device self test routine and returns the test result.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    selfTestResult : int
        This parameter contains the value returned from the device self
        test routine. A returned zero value indicates a successful run,
        a value other than zero indicates failure.
    description : str
        This parameter returns the interpreted code as a user readable
        message string.
    """
    instrumentHandle = ViSession(instrument_handle)

    selfTestResult = ViInt16(-1)  # default result !=0 to avoid false positive
    description = ViChar_arr(b'\0' * TLTSP_BUFFER_SIZE)

    status = _call_dll_fcn(instrumentHandle, byref(selfTestResult), description)

    return status, selfTestResult.value, description.value.decode(MSG_ENCODING)


def _setDeviceName(instrument_handle: int, device_name: str) -> int:
    """Set the device name if service mode has been enabled. NOT TESTED.

    This function sets the device name if service mode has been enabled.
    Do not use in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    deviceName : str
        Name of the device

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    deviceName = ViChar_arr(device_name.encode(MSG_ENCODING))

    status = _call_dll_fcn(instrumentHandle, deviceName)

    return status


def _setExtRefVoltage(instrument_handle: int, reference_voltage: float) -> int:
    """Set the reference voltage of the external thermistor. NOT TESTED.

    This function sets the reference voltage of the external thermistor
    hw frontend if service mode has been enabled. Do not use in user
    applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    reference_voltage : float
        Reference voltage of the external thermistor hardware frontend
        in Volt.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    referenceVoltage = c_double(reference_voltage)

    status = _call_dll_fcn(instrumentHandle, referenceVoltage)

    return status


def _setExtSerResist(instrument_handle: int, serial_resistance: float) -> int:
    """Set the serial resistance of the external thermistor. NOT TESTED.

    This function sets the serial resistance of the external thermistor
    hw frontend if service mode has been enabled. Do not use in user
    applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    serial_resistance : float
        Serial resistance value for the external thermistor hardware
        frontend in Ohm.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    serialResistance = c_double(serial_resistance)

    status = _call_dll_fcn(instrumentHandle, serialResistance)

    return status


def _setHumSensOffset(instrument_handle: int, humidity_offset: float) -> int:
    """Set the sensor's absolute humidity offset. NOT TESTED.

    This function sets the sensor's absolute humidity offset.
    Hint: The offset will be added to the humidity value.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    humidity_offset : float
        This parameter specifies the humidity offset in % r.H.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    humidityOffset = ViReal64(humidity_offset)

    status = _call_dll_fcn(instrumentHandle, humidityOffset)

    return status


def _setProductionDate(instrument_handle: int, production_date: str) -> int:
    """Set the production date of the device. NOT TESTED.

    This function sets the production date of the device if service mode
    has been enabled. Do not use in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    production_date : str
        Production date of the device.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    productionDate = ViChar_arr(production_date.encode(MSG_ENCODING))

    status = _call_dll_fcn(instrumentHandle, productionDate)

    return status


def _setSerialNr(instrument_handle: int, serial_no: str) -> int:
    """Set the serial number of the device. NOT TESTED.

    This function sets the serial number of the device if service mode
    has been enabled. Do not use in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    serial_no : str
        Production date of the device.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    serialNr = ViChar_arr(serial_no.encode(MSG_ENCODING))

    status = _call_dll_fcn(instrumentHandle, serialNr)

    return status


def _setServiceMode(instrument_handle: int, password: str) -> int:
    """Enable the service mode of the device during manufacturing. NOT TESTED.

    This function enables the service mode of the device during
    manufacturing. Do not use in user applications.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    password : str
        Enter password to enter service mode.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    password_ = ViChar_arr(password.encode(MSG_ENCODING))

    status = _call_dll_fcn(instrumentHandle, password_)

    return status


def _setTempSensOffset(
    instrument_handle: int, channel: int, temperature_offset: float
) -> int:
    """Set the sensor's absolute temperature offset in K. NOT TESTED.

    This function sets the sensor's absolute temperature offset in K.
    Note: This function is valid for all temperature sensors only.
    Hint: The offset will be added to the temperature value.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    temperature_offset : float
        This parameter specifies the temperature offset in K.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    temperatureOffset = ViReal64(temperature_offset)

    status = _call_dll_fcn(instrumentHandle, channel_, temperatureOffset)

    return status


def _setThermistorExpParams(
    instrument_handle: int,
    channel: int,
    r0_value: float,
    t0_value: float,
    beta_value: float,
) -> int:
    """Set the thermistor exponential method parameters. NOT TESTED.

    This function sets the thermistor exponential method parameters.
    Note: This function is valid for external temperature sensors only.

    Parameters
    ----------
    instrument_handle : int
        This parameter accepts the instrument handle returned by
        <Initialize> to select the desired instrument driver session.
    channel : int
        This parameter specifies the temperature channel.
        Note: This function is valid for all temperature sensors only
        (channels 1, 2 and 3).
    r0_value : float
        This parameter specifies the R0 value.
    t0_value : float
        This parameter specifies the T0 value.
    beta_value : float
        This parameter specifies the beta value.

    Returns
    -------
    status : int
        This is the error code returned by the function call. For error
        codes and descriptions see <Error Message>.
    """
    instrumentHandle = ViSession(instrument_handle)
    channel_ = ViUInt16(channel + 10)  # channels are numbered 11, 12, 13
    r0Value = ViReal64(r0_value)
    t0Value = ViReal64(t0_value)
    betaValue = ViReal64(beta_value)

    status = _call_dll_fcn(
        instrumentHandle, channel_, r0Value, t0Value, betaValue
    )

    return status



