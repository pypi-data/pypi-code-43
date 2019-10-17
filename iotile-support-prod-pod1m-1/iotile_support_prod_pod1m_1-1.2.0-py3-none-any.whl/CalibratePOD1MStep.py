
"""
This is a CalibrationPOD1MStep object that will be used by the calibration recipes located in
the recipes folder.

This step can only be performed through bluetooth.

    If scanning needed
        Scan the Controller QR Code
        Scan the QR Code on the top board

    If using golden devices
        scripts will automatically collect humidity and temperature from golden devices

    if calibrating humidity
        If no golden devices used, enter current humidity value
        Otherwise use mean humidity from all golden devices
    if calibrating temperature
        If no golden devices used, enter current temperature value
        Otherwise use mean temperature from all golden devices

    if calibrating accel
        If doing one point calibration, the POD-1M should be laying flat on the floor
        If doing two point calibration, put POD-1M into configuration one when prompted,
            and then into configurtion two when prompted.
            Configuration 1 is with the POD lid facing up with Arch on the lower left
            cornner
            Configuration 2 is taking the top corner, flipping the POD 180 directly
            in front of you
        Measure standard deviation of the noise
    
    If needed, post the calibration information to iotile cloud

    If needed, post the calibration information to ArchFlow

    Make you run the test on a flat surface.
"""
from __future__ import (unicode_literals, print_function, absolute_import)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

import json
import logging
import datetime
import requests
from iotile.cloud.cloud import IOTileCloud
from iotile.core.exceptions import ArgumentError, IOTileException
from iotile.core.hw.hwmanager import HardwareManager
from iotile_cloud.api.exceptions import RestHttpBaseException

G_TO_LSB_SCALE_FACTOR = 0.049
HUMIDITY_SCALE_FACTOR = 1024
TEMPERATURE_SCALE_FACTOR = 100
# ADXL375 Typical Offset is +/-400mg, Max Offset +/-6000mg
ACCEPTABLE_G_ERROR = 1.0
# ADXL375 Typical Noise is 5 mg/sqrt(Hz)
ACCEPTABLE_G_NOISE = 1.0

class CalibratePOD1MStep():
    """ A Recipe Step Object used to callibrate the POD-1M

    Args:
        uuid (str): uuid of target device
        scan_qr_codes(bool): Optional. Default True, flag to determine whether
            calibrator should scan the QR codes on the top and bottom boards
        cal_humidity (bool): Optional. Default False, flag to determine whether
            humidity should be calibrated
        cal_temperature (bool): Optional. Default False, flag to determine whether
            temperature should be calibrated
        cal_accel (bool): Optional. Default False, flag to determine whether
            accelerometer should be calibrated
        cal_one_point_accel (bool): Optional. Default False, flag to determine whether
            accelerometer should be calibrated
        sample_count (int): Optional. Number of samples to take to determine
            static offset of accelerometer. Defaults to 128 samples
        golden_devices (str): Optional. List-like string of uuids that the process
            will connect to automatically to acquire environmental data as golden data
            to calibrate the target POD-1M to. Should look something like "[0xadc,0xbea]"
        post_note (bool): Optional. Defaults False, flag to determine whether to
            post a note onto iotile.cloud of the calibration data.
        post_archflow (bool): Optional. Defaults False, flag to determine whether to
            post a record onto Archflow of the calibration data.
        archflow_token (str): If post_archflow is True, necessary token to have permission
            to post to Archflow
        archflow_build_id (str): If post_archflow is True, necessary string to identify the
            build order number
        archflow_data_type (str): If post_archflow is True, necessary string to identify the
            data type of the payload send tto Archflow

    """
    REQUIRED_RESOURCES = [('connection', 'hardware_manager')]

    def __init__(self, args):
        if args.get('uuid') is None:
            raise ArgumentError("CalibratePOD1MStep Parameter Missing", parameter_name='uuid')

        self._uuid = args['uuid']
        self._scan_qr_codes = args.get('scan_qr_codes', True)

        # Calibration-related Arguments
        self._cal_humidity = args.get('cal_humidity', False)
        self._cal_temperature = args.get('cal_temperature', False)
        self._cal_accel = args.get('cal_accel', False)
        self._cal_one_point_accel = args.get('cal_one_point_accel', False)
        self._sample_count = args.get('sample_count', 128)
        self._golden_devices = args.get('golden_devices')
        self._golden_devices_sample_count = args.get('golden_devices_sample_count', 25)
        if self._golden_devices is not None:
            self._parse_golden_devices_list()

        # Posting to IOTile Cloud
        self._post_note = args.get('post_note', False)

        # Archflow related Arguments
        self._post_archflow = args.get('post_archflow', False)
        self._archflow_token = args.get('archflow_token', None)
        self._archflow_build_id = args.get('archflow_build_id', None)
        self._archflow_data_type = args.get('archflow_data_type', None)
        self._archflow_data_version = args.get('archflow_data_version', None)

        if self._post_archflow:
            self._check_all_archflow_fields()

        # Logging Information
        self._calibration_log_filename = args.get('calibration_log_filename', None)
        self._setup_logger()
        self._calib_payload = {}
        self._hw = None

        if not HAS_NUMPY:
            raise ArgumentError("You must install numpy to use this ship step", \
                suggestion="pip install numpy")

    def run(self, resources):
        """
        Needed function from iotile-ship to run the step.

        """
        self._hw = resources['connection'].hwman

        # Scan QR codes if needed
        if self._scan_qr_codes:
            self._calib_payload['bot_serial_code'] = input("Scan QR code on BMD module: ")
            self._calib_payload['top_serial_code'] = input("Scan QR code on top board: ")

        golden_data = {}
        # Get Data from Golden Devices is needed,, otherwise use the old way
        if self._golden_devices is not None:
            golden_data = self._get_golden_data()
        else:
            golden_data = self._get_golden_data_old_way()

        # Get proxies needed
        accel_tile = self._hw.get(12)
        env_tile = self._hw.get(14)

        # Calibrate Environemntal and Accel Tile
        if self._cal_humidity or self._cal_temperature:
            self._calibrate_env_tile(env_tile, golden_data)

        if self._cal_accel:
            self._calibrate_accel_tile(accel_tile)

        self._verify_accel_noise(accel_tile)

        self._log(self._calib_payload)
        # If needed, post to the cloud
        if self._post_note:
            self._post_calibration_note_iotile_cloud()

        # If needed, post to archflow
        if self._post_archflow:
            self._post_calibration_note_archflow()

    def _check_all_archflow_fields(self):
        """ This function checks if all variables needed to post to ArchFlow are passed in
        """
        if self._archflow_token is None or self._archflow_build_id is None or \
            self._archflow_data_type is None or self._archflow_data_version is None:
            raise ArgumentError("Missing Parameters in order to post to Archflow", \
                parameter_name=['archflow_token, archflow_build_id, archflow_data_type, \
                or archflow_data_version'])

    def _parse_golden_devices_list(self):
        """ Takes a string representation of the list of golden devices neeeded,
        returns a list of uuids
        """
        if self._golden_devices[0] != '[' or self._golden_devices[-1] != ']':
            raise ArgumentError("Make sure your golden_devices is a list that looks something \
                like [0x1, 0x2, 0x3]", golden_devices=self._golden_devices)
        self._golden_devices = self._golden_devices[1:-1].replace(" ", "").split(",")

    def _post_calibration_note_iotile_cloud(self):
        """Old Method of posting calibration note into iotile cloud.
        """
        cloud = IOTileCloud()
        device = cloud.device_info(self._uuid)

        # Post :device:calibration configuration attribute
        payload = {
            'target': device['slug'],
            'name': ':device:calibration',
            'data': self._calib_payload,
            'log_as_note': True
        }
        try:
            resp = cloud.api.config.attr.post(payload)
            self._log("Posting to IOTile Cloud Response: %s" % resp)
        except RestHttpBaseException as error:
            self._log('Write to IOTile Cloud Failed.\nError: %s' % (error))

    def _post_calibration_note_archflow(self):
        """Posting calibration event onto archflow
        """
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self._archflow_token
        }
        # Post :device:calibration configuration attribute

        payload = {
            'build_id': self._archflow_build_id,
            'data_type': self._archflow_data_type,
            'data_version': self._archflow_data_version,
            'device': self._get_device_slug(),
            'timestamp': datetime.datetime.now().isoformat(),
            'data': self._calib_payload
        }
        encoded_data = json.dumps(payload).encode('utf-8')
        resp = requests.post(
            'https://archflow.archsys.io/record',
            data=encoded_data,
            headers=headers
        )
        self._log('Posting to Arch Flow Status Code: %s\nContent: %s' % \
            (resp.status_code, resp.content))
        if not resp.ok:
            self._log('Write to ArchFlow Failed.\nPayload: %s\nResponse: %s' % \
                (payload, resp))
            raise IOTileException("Write to ArchFlow Cloud Failed.", \
                suggestion="Ensure ethernet cable is connected or correct token is passed.")

    def _setup_logger(self, filename="CalibrationShipScript.log"):
        """ Create logger to document calibration process.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d: \
            [%(levelname).4s] %(name)s: %(message)s', '%y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _log(self, msg):
        """Prints to shell and save output into logginer file
        """
        print(msg)
        self.logger.info(msg)

    def _get_golden_data(self):
        """ Using the list of uuids in self._golden_devices, conenct to each one, collect
        temperature and humidity, and then get their mean values. Save mean and stddev of values
        """
        golden_data = {}
        golden_data['pod_raw_data'] = {}
        golden_data['pod_raw_data']['temperature'] = {}
        golden_data['pod_raw_data']['humidity'] = {}

        self._hw.disconnect()
        for golden_device in self._golden_devices:
            print("Getting Golden Environmental Data from POD %s" % (golden_device))

            self._hw.connect(golden_device)
            golden_env_tile = self._hw.get(14)

            golden_data['pod_raw_data']['temperature'][golden_device] = []
            golden_data['pod_raw_data']['humidity'][golden_device] = []

            for i in range(self._golden_devices_sample_count):
                golden_env_tile.poll_data()

                golden_humidity = golden_env_tile.get_humidity()
                golden_temp = golden_env_tile.get_temperature()

                golden_data['pod_raw_data']['humidity'][golden_device].append(golden_humidity)
                golden_data['pod_raw_data']['temperature'][golden_device].append(golden_temp)

                self._log("Golden POD %s Run %d: Humidity: %.2fRH Temp: %.2fC" % \
                    (golden_device, i, golden_humidity, golden_temp))
            self._hw.disconnect()
        all_temperatures = np.array(sum(golden_data['pod_raw_data']['temperature'].values(), []))
        all_humidity = np.array(sum(golden_data['pod_raw_data']['humidity'].values(), []))
        golden_data['temperature'] = np.mean(all_temperatures)
        golden_data['humidity'] = np.mean(all_humidity)
        golden_data['temperature_stddev'] = np.std(all_temperatures)
        golden_data['humidity_stddev'] = np.std(all_humidity)
        self._log("Golden Data Values: %s" % golden_data)
        self._hw.connect(self._uuid)

        self._calib_payload['golden_data'] = golden_data
        return golden_data

    def _get_golden_data_old_way(self):
        """ Ask for golden data from user inputs
        """
        golden_data = {}
        if self._cal_humidity:
            golden_data['humidity'] = float(input("Enter humidity from golden sensor: "))

        if self._cal_temperature:
            golden_data['temperature'] = float(input("Enter temperature from golden sensor: "))
        return golden_data

    def _calibrate_env_tile(self, env_tile, golden_data):
        """Cabilbrate the environmental tile, currently only temperature and humidity
        """
        calib_vals = env_tile.get_calibration()
        env_tile.set_calibration(0, 0, 0)
        env_tile.poll_data()

        #Calibrate humidity if needed
        if self._cal_humidity:
            meas_humidity = env_tile.get_humidity()
            calib_vals['humidity_offset'] = int((meas_humidity-golden_data['humidity']) * \
                HUMIDITY_SCALE_FACTOR)

        #Calibrate temperature if needed
        if self._cal_temperature:
            meas_temperature = env_tile.get_temperature()
            calib_vals['temp_offset'] = int((meas_temperature-golden_data['temperature']) * \
                TEMPERATURE_SCALE_FACTOR)

        # Apply calibration and get info
        env_tile.set_calibration(calib_vals['temp_offset'], calib_vals['humidity_offset'], \
            calib_vals['pressure_offset'])
        env_tile.persist_calibration()
        env_tile_calib_info = env_tile.calibration_info()

        # Fill out information inside payload
        self._calib_payload['env_humidity_offset'] = calib_vals['humidity_offset']
        self._calib_payload['env_temperature_offset'] = calib_vals['temp_offset']
        self._calib_payload['env_guid'] = str(env_tile_calib_info['serial_number'])
        self._calib_payload['env_timestamp'] = str(env_tile_calib_info['calibration_time'])

        # Quickly verify the values look correct
        env_final_msg = "Env Tile Meas Values: %s %s %s" % \
            (env_tile.sample_humidity(), env_tile.sample_pressure(), env_tile.sample_temperature())
        self._log(env_final_msg)

    def _calibrate_accel_tile(self, accel_tile):
        """Cabilbrate the accelerometer tile
        """
        calib_manager = accel_tile.calibration_manager()
        setup_manager = accel_tile.setup_manager()

        calib_manager.set_calibration(1, 1, 1, 0, 0, 0)
        if self._cal_one_point_accel:
            self._calibrate_one_point_accel(calib_manager, setup_manager)
        else:
            self._calibrate_two_point_accel(calib_manager, setup_manager)
        acc_tile_calib_info = calib_manager.calibration_info()

        #Fill out data into payload
        self._calib_payload['acc_sample_count'] = self._sample_count
        self._calib_payload['acc_guid'] = str(acc_tile_calib_info['serial_number'])
        self._calib_payload['acc_timestamp'] = str(acc_tile_calib_info['calibration_time'])

        # Quickly verify the values look correct
        setup_manager.start_recording()
        accel_final_msg = "Acc Tile Meas Values: %s" % \
            str(np.array(calib_manager.static_offset(self._sample_count))*G_TO_LSB_SCALE_FACTOR)
        self._log(accel_final_msg)
        setup_manager.stop_recording()

    def _calibrate_one_point_accel(self, calib_manager, setup_manager):
        """Calibrate by putting the POD on a flat surface, only gravity acts on the z-axis
        """
        #Get current static values
        setup_manager.start_recording()
        meas_accel_config = np.array(calib_manager.static_offset(self._sample_count)) *\
            G_TO_LSB_SCALE_FACTOR
        setup_manager.stop_recording()

        actual_accel_config = np.array([0.0, 0.0, 1.0])
        offsets = meas_accel_config - actual_accel_config

        # Check for execssive offsets to prevent when a POD may be incorrectly placed
        if any(x > ACCEPTABLE_G_ERROR for x in np.abs(offsets)):
            self._log("Excessive Offset in Accelerometer during one point calibration, \
                \nMeasured: %s\nExpected: %s" %  (meas_accel_config, actual_accel_config))
            user_input = input("Excessive Offset, are you sure the POD-1M is flat on the table?\
                \ntype [c] if you are sure: ")
            if user_input != 'c':
                self._log("CALIBRATION CANCELLED")
                raise ArgumentError("Not on jig properly", values=meas_accel_config)
            self._calib_payload['accel_calib_override'] = "One-point configuration. Measured: %s" %\
                meas_accel_config

        # Fill out data into Payload
        self._calib_payload['acc_x_offset_set'] = offsets[0]
        self._calib_payload['acc_y_offset_set'] = offsets[1]
        self._calib_payload['acc_z_offset_set'] = offsets[2]

        calib_manager.set_calibration(1, 1, 1, offsets[0], offsets[1], offsets[2])
        calib_manager.persist_calibration()

    def _calibrate_two_point_accel(self, calib_manager, setup_manager):
        """ Two point calibration.
        Configuration 1 is with the POD lid facing up with Arch on the lower left cornner
        Configuration 2 is taking the top corner, flipping the POD 180 directly in front of you
        Takes the average of the offsets, and applies the offset.
        Ideally in two point calibration, a scale value is used as well but the
            perturbation of the +/-200G accel tile is currently not possible
        """
        input("Set POD in configuration 1 and then Enter: ")
        actual_accel_config1 = np.array([0.5, 0.5, np.sqrt(2)/2])
        setup_manager.start_recording()
        meas_accel_config1 = np.array(calib_manager.static_offset(self._sample_count)) *\
            G_TO_LSB_SCALE_FACTOR
        setup_manager.stop_recording()

        if any(x > ACCEPTABLE_G_ERROR for x in np.abs(meas_accel_config1-actual_accel_config1)):
            self._log("Excessive Offset in Accelerometer in Configuration 1 during\
                two point calibration, \nMeasured: %s\nExpected: %s" %\
                (meas_accel_config1, actual_accel_config1))
            user_input = input("Sum of vectors is less than 0 when they should all be positive,\
                \ntype [c] if you are sure the POD is correctly on the jig: ")
            if user_input != 'c':
                self._log("CALIBRATION CANCELLED")
                raise ArgumentError("Not on jig properly", values=meas_accel_config1)
            self._calib_payload['accel_calib_override'] = "Two-point configuration 1"

        input("Set POD in configuration 2 and then Enter: ")
        actual_accel_config2 = np.array([-0.5, -0.5, -np.sqrt(2)/2])
        setup_manager.start_recording()
        meas_accel_config2 = np.array(calib_manager.static_offset(self._sample_count)) *\
            G_TO_LSB_SCALE_FACTOR
        setup_manager.stop_recording()

        if any(x > ACCEPTABLE_G_ERROR for x in np.abs(meas_accel_config2-actual_accel_config2)):
            self._log("Excessive Offset in Accelerometer in Configuration 2 during\
                two point calibration, \nMeasured: %s\nExpected: %s" %\
                (meas_accel_config2, actual_accel_config2))
            user_input = input("Sum of vectors is greater than 0 when they should be all negative,\
                \ntype [c] if you are sure the POD is correctly on the jig: ")
            if user_input != 'c':
                self._log("CALIBRATION CANCELLED")
                raise ArgumentError("Not on jig properly", values=meas_accel_config2)
            self._calib_payload['accel_calib_override'] = "Two-point configuration 1"

        # We will calculate gain and offsets, but not actually use those numbers.
        # Will be saved into cloud
        gains = (actual_accel_config1-actual_accel_config2)/(meas_accel_config1-meas_accel_config2)
        offsets = meas_accel_config1-gains*actual_accel_config1

        # This is the offset that will actually be used. Will average the two opposing perturbations
        offsets_only = (meas_accel_config1+meas_accel_config2)/2

        self._calib_payload['acc_x_gain_method_1'] = gains[0]
        self._calib_payload['acc_x_offset_method_1'] = offsets[0]
        self._calib_payload['acc_y_gain_method_1'] = gains[1]
        self._calib_payload['acc_y_offset_method_1'] = offsets[1]
        self._calib_payload['acc_z_gain_method_1'] = gains[2]
        self._calib_payload['acc_z_offset_method_1'] = offsets[2]

        self._calib_payload['acc_x_offset_set'] = offsets_only[0]
        self._calib_payload['acc_y_offset_set'] = offsets_only[1]
        self._calib_payload['acc_z_offset_set'] = offsets_only[2]

        calib_manager.set_calibration(1, 1, 1, offsets_only[0], offsets_only[1], offsets_only[2])
        calib_manager.persist_calibration()

    def _verify_accel_noise(self, accel_tile):
        setup_manager = accel_tile.setup_manager()
        calib_manager = accel_tile.calibration_manager()
        # Get noise of all axis in accelerometer
        setup_manager.start_recording()
        x_noise = calib_manager.measure_noise('x', sample_count=128)*G_TO_LSB_SCALE_FACTOR
        y_noise = calib_manager.measure_noise('y', sample_count=128)*G_TO_LSB_SCALE_FACTOR
        z_noise = calib_manager.measure_noise('z', sample_count=128)*G_TO_LSB_SCALE_FACTOR
        noise = [x_noise, y_noise, z_noise]
        setup_manager.stop_recording()

        self._calib_payload['accel_noise_stddev'] = noise

        # Check if any excessive noise exists. If so, log, prompt user if process should continue
        self._log("Accelerometer Noise std dev: %s" % noise)
        if any(x > ACCEPTABLE_G_NOISE for x in noise):
            self._log("Excessive Noise in Accelerometer, \nMeasured: %s" % (noise))
            user_input = input("Excessive Noise in Accelerometer,\
                \ntype [c] if you wish to continue anyways : ")
            if user_input != 'c':
                self._log("CALIBRATION CANCELLED: EXCESSIVE NOISE")
                raise ArgumentError("Excessive Accelerometer Noise", values=noise)
            self._calib_payload['accel_calib_override'] = "Noise"


    def _get_device_slug(self):
        # TODO: this will only work if the number in hex is less than four digits
        # I anticipate moving to ArchMFG which contains the better parse_uuid function
        if self._uuid[0:2] == '0x':
            uuid_integer = int(self._uuid, 16)
        else:
            uuid_integer = int(self._uuid)
        return "d--0000-0000-0000-{0:04X}".format(uuid_integer)
