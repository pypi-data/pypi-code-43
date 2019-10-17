"""An IOTileApp Plugin that operates a POD-1M as a shock/environmental tracker."""

from __future__ import print_function
import sys
import os
import shutil
import json
import logging
import glob
import msgpack
from datetime import datetime

from typedargs.annotate import context, docannotate
from typedargs import type_system, iprint
from iotile.core.hw import IOTileApp
from iotile.core.hw.exceptions import RPCNotFoundError
from iotile.core.dev.config import ConfigManager
from iotile.core.hw.reports import IndividualReadingReport, SignedListReport, FlexibleDictionaryReport, UTCAssigner
from iotile.core.hw.reports.report import IOTileEvent
from iotile.core.dev.semver import SemanticVersionRange
from iotile.core.exceptions import HardwareError, ArgumentError
from iotile.core.utilities.console import ProgressBar
from iotile.cloud import IOTileCloud
from iotile.sg import DataStream


# Physical Constants
M_S__TO_IN_S = 39.3700787
G_CONST = 9.80665

#Logistics tracker Streamer Constants
START_STREAM = 'system buffered 1536'
START_STREAM_ENCODED = DataStream.FromString(START_STREAM).encode()
END_STREAM = 'system buffered 1537'
END_STREAM_ENCODED = DataStream.FromString(END_STREAM).encode()
PAUSERESUME_STREAM = 'system buffered 1538'

START_INPUT_STREAM = 'system input 1536'
END_INPUT_STREAM = 'system input 1537'
PAUSERESUME_INPUT_STREAM = 'system input 1538'

ACCEL_STREAM = "output 32"
PRESS_STREAM = "output 33"
HUM_STREAM = "output 34"
TEMP_STREAM = "output 35"

HUM_RT_STREAM = "unbuffered 15"
TEMP_RT_STREAM = "unbuffered 25"
PRESS_RT_STREAM = "unbuffered 22"
SHOCKS_RT_STREAM = "unbuffered 18"

ISRUNNING_VSTREAM = "constant 1"

USER_STREAMER = 0
SYSTEM_STREAMER = 1
TRIP_STREAMER = 2

WAVEFORM_STREAMER = 0x100
ACCEL_ADDRESS = 12


@context("LogisticsTracker")
class LogisticsTracker(IOTileApp):
    """A shipment tracker with support for shock, vibe and environmental logging.

    This app requires a POD-1M device with a properly configured shipment
    tracker sensorgraph for all functionality to work as intended.  This app
    provides equivalent functionality to the IOTile Companion device page for
    the shipment tracker.
    """

    APP_TAG = [2049, 2055]
    APP_VERSION = "^1.0.0"

    logger = logging.getLogger(__name__)

    @classmethod
    def MatchInfo(cls):
        """Return the list of app types that we automatch."""

        out = []
        for tag in cls.APP_TAG:
            out.append((tag, SemanticVersionRange.FromString(cls.APP_VERSION), 50))

        return out

    @classmethod
    def AppName(cls):
        """Return our name to allow users to explicitly specify us."""

        return "logistics_tracker"

    def suppress_output(self):
        """Context manager that will not show interactive output."""

        class _Suppressor(object):  #pylint:disable=too-few-public-methods; This is an internal class
            old_interactive = False
            def __enter__(self):
                self.old_interactive = type_system.interactive
                type_system.interactive = False

            def __exit__(self, *args):
                type_system.interactive = self.old_interactive

        return _Suppressor()

    @docannotate
    def trip_info(self):
        """Get information on the current trip, if there is one.

        This function will determine if there is a trip currently in progress
        and if so, when it started.  If there is a finished trip stored in the
        tracker, this function will also determine the stop date.

        There are 4 potential trip statuses that you can find with
        this function:
            'not started': The device is waiting for a trip to start
            'in progress': The device is currently in the middle of
                a trip
            'finished': The device has recorded one complete trip
                with a start and end date.
            'corrupted': The device is in a corrupted state where there
                is an end trip event but no corresponding start trip
                event.
            'multiple trips': The device is in an unsupported state
                where data from more than one trip is stored.

        The device's current internal UTC time and time since last reboot are
        also included for verification purposes.

        Returns:
            basic_dict: Information about the trip.
        """

        con = self._hw.controller()
        hwversion = con.hardware_version()

        test_iface = con.test_interface()
        sgraph = con.sensor_graph()

        with self.suppress_output():
            trip_starts = sgraph.download_stream(START_STREAM)
            trip_ends = sgraph.download_stream(END_STREAM)
            _pause_resumes = sgraph.download_stream(PAUSERESUME_STREAM)

            is_running = sgraph.inspect_virtualstream(ISRUNNING_VSTREAM)

        info = _determine_trip_status(trip_starts, trip_ends)
        info['recording_data'] = bool(is_running)

        current_time = test_iface.current_time()

        # On older firmware get_uptime() doesn't exist, but those firmware versions
        # also don't support returning a UTC value for current_time so in those
        # cases current_time is just the uptime.
        if current_time & (1 << 31):
            uptime = test_iface.get_uptime()
        else:
            uptime = current_time

        if current_time & (1 << 31):
            info['utc_synchronized'] = True
            info['current_time'] = UTCAssigner.convert_rtc(current_time)
        else:
            info['utc_synchronized'] = False
            info['current_time'] = None

        info['device_uptime'] = uptime
        info['hardware_version'] = hwversion

        return info

    @docannotate
    def admin(self):
        """Access the protected administrative interface of the device.

        The admin interface should not be necessary in normal usage.  It
        exists for debugging purposes and other engineering needs.  If you
        find yourself using it repeatedly and you are not an Arch developer,
        you should probably report a bug and describe what you are trying to
        accomplish.
        """

        return TrackerAdmin(self)

    @docannotate
    def start_trip(self, synchronize=True):
        """Start a trip.

        This routine will mark the start of the trip and begin recording data.
        You can stop a trip by calling stop_trip().  You can pause and resume
        data recording during a trip by calling pause_trip() or resume_trip().

        Args:
            synchronize (bool): Synchronize the RTC on the POD-1M to the current
                UTC time of the computer that is running this application.  If
                this is set to False, no synchronization will be performed and
                if the POD-1M does not have a synchronized RPT, it will produce
                timestamps in uptime rather than UTC time, which will require
                reconstruction to convert to UTC when the trip is uploaded.
        """

        info = self.trip_info()
        if info['trip_status'] != 'not started':
            raise HardwareError("You may only start a trip once without resetting the tracker", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input(START_INPUT_STREAM, _current_timestamp())
        self.resume_trip()

        if synchronize:
            self.synchronize_clock()

    @docannotate
    def end_trip(self):
        """End a trip that is currently in progress.

        This routine will stop data recording and mark the end of the trip.
        You can only call it when a trip is in progress.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress':
            raise HardwareError("You must start a trip before you can stop a trip", **info)

        if info['recording_data']:
            self.pause_trip()

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input(END_INPUT_STREAM, _current_timestamp())

    @docannotate
    def resume_trip(self):
        """Resume recording data during a trip.

        You may only call resume trip after a trip has started and recording
        has been paused.  Calling resume trip when recording has already been
        resumed will throw an exception.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress' or info['recording_data'] is not False:
            raise HardwareError("You may only resume a trip when there is a trip to resume", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input(PAUSERESUME_INPUT_STREAM, 1)

    @docannotate
    def pause_trip(self):
        """Resume recording data during a trip.

        You may only call resume trip after a trip has started and recording
        has been paused.  Calling resume trip when recording has already been
        resumed will throw an exception.
        """

        info = self.trip_info()
        if info['trip_status'] != 'in progress' or info['recording_data'] is not True:
            raise HardwareError("You may only pause a trip when it is currently recording data", **info)

        sgraph = self._hw.controller().sensor_graph()
        sgraph.input(PAUSERESUME_INPUT_STREAM, 0)


    @docannotate
    def overview(self):
        """Get an overview of the current status of the tracker.

        This function will query all relevant high level information about the
        tracker and present it as a single dictionary.  It determines:

        - whether the tracker is currently in a trip
        - how many shocks it has seen
        - information on the largest shocks seen since the trip began

        Returns:
            basic_dict: A dictionary of information about the current status of
                the tracker.
        """

        accel = self._hw.get(ACCEL_ADDRESS)
        status = accel.setup_manager().get_status()

        trip_info = self.trip_info()

        overview = {}
        overview['trip_status'] = trip_info['trip_status']
        overview['shocks_seen'] = status['shock_counter']
        overview['recording_data'] = trip_info['recording_data']

        if overview['shocks_seen'] > 0:
            overview['shocks_peakg'] = _format_shock(accel.get_shock('max_g'))
            overview['shocks_peakdv'] = _format_shock(accel.get_shock('max_dv'))
            overview['shocks_last'] = _format_shock(accel.get_shock('last'))
        else:
            overview['shocks_peakg'] = None
            overview['shocks_peakdv'] = None
            overview['shocks_last'] = None

        return overview

    @docannotate
    def watch_realtime(self):
        """Print out realtime information as it comes from the device.

        This will continually update the displayed realtime information once
        per second until you stop it with Ctrl-C.
        """

        temp_tag = DataStream.FromString(TEMP_RT_STREAM).encode()
        hum_tag = DataStream.FromString(HUM_RT_STREAM).encode()
        press_tag = DataStream.FromString(PRESS_RT_STREAM).encode()
        shocks_tag = DataStream.FromString(SHOCKS_RT_STREAM).encode()

        try:
            self._hw.enable_streaming()
            press = 0.0
            temp = 0.0
            shock_count = 0
            hum = 0.0
            last_shock = ""

            for report in self._hw.iter_reports(blocking=True):
                if not isinstance(report, IndividualReadingReport):
                    continue

                reading = report.visible_readings[0]
                if reading.stream == temp_tag:
                    temp = reading.value / 100.0
                elif reading.stream == hum_tag:
                    hum = reading.value / 1024.
                elif reading.stream == press_tag:
                    press = reading.value / 100.
                elif reading.stream == shocks_tag:
                    if reading.value != shock_count:
                        last_shock = _format_shock(self._hw.get(ACCEL_ADDRESS).last_shock())

                    shock_count = reading.value

                sys.stdout.write("\r| Shocks: %04d | Last Shock: %21s | Temp: % 02.1f C | Pressure: %04.0f mbar | H: %02.1f %%RH |"
                                 % (shock_count, last_shock, temp, press, hum))
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("")

    @docannotate
    def upload_trip(self, save=None, clean=False, dryrun=False, acknowledge=True, waveform_ack=None):
        """Upload a finished trip to the cloud.

        This function will download all data from the device and upload it to
        IOTile.cloud.  If you pass dryrun=True, no data will actually be
        uploaded.  If you pass a path to a folder in the save parameter, all
        files that would be uploaded to the cloud will be saved to that
        folder.  This can be combined with dryrun only download data and not
        upload it to the cloud.

        Args:
            save (str): The path to a folder where all data should be saved
                before uploading.  This is optional, if you don't specify it
                no data will be saved.
            dryrun (bool): Download the data from the device but do not upload
                it to the cloud.  This is useful for testing and for
                downloading data only when combined with the save parameter.
            clean (bool): When combined with save, this will clear all old files
                from the directory specified in save.  Otherwise it has no effect.
            acknowledge (bool): Acknowledge received readings from iotile.cloud
                before downloading new data.
            waveform_ack (int): Optional argument to forcibly tell the POD the explicit
                highest id of the most recent successful waveform upload.  This is a
                dangerous operation that should not be used without understanding what
                it does.
        """

        info = self.trip_info()
        if info['trip_status'] != 'finished':
            raise HardwareError("You must finish a trip first before calling upload_trip", trip_status=info['trip_status'])

        if save is not None:
            if os.path.exists(save) and not os.path.isdir(save):
                raise ArgumentError("You passed a save directory that exists but is not a directory", directory=save)

            if os.path.exists(save) and clean:
                iprint("Cleaning folder at: %s" % save)
                shutil.rmtree(save)

            if not os.path.exists(save):
                os.makedirs(save)

        # Make sure to sort the waveforms we got by time so they are in cronological order.
        waves = self._download_waveforms(acknowledge=acknowledge, force_ack=waveform_ack)
        waves = sorted(waves, key=lambda x: x['unique_id'])

        force_acks = None
        if not self._check_wavesforms_utc(waves):
            iprint("We received waveforms with uptime rather than utc timestamps, rolling back streamer 0")
            iprint("This will ensure we have all of the data we need to assign utc timestamps.")
            force_acks = {0: (1, True)}

        reports = self._download_trip_reports(acknowledge, force_acks=force_acks)

        waves = self._ensure_waveforms_utc(waves, reports=reports)

        if save:
            for i, report in enumerate(reports):
                out_path = os.path.join(save, "report_%d_%s.bin" % (i, report.received_time.isoformat().replace(':', '-')))
                with open(out_path, "wb") as outfile:
                    outfile.write(report.encode())

            for wave in waves:
                out_path = os.path.join(save, "waveform_%08X.json" % wave['unique_id'])
                with open(out_path, "w") as out_file:
                    json.dump(wave, out_file, indent=4)

        events = [_create_waveform_event(x) for x in waves]
        iprint("Found %d reports and %d waveforms." % (len(reports), len(events)))
        wave_report = FlexibleDictionaryReport.FromReadings(self._device_id, [], events,
                                                            sent_timestamp=0xFFFFFFFF,
                                                            streamer=WAVEFORM_STREAMER,
                                                            received_time=datetime.utcnow())

        if save:
            out_path = os.path.join(save, "waveform_report.mp")
            with open(out_path, "wb") as outfile:
                outfile.write(wave_report.encode())

            out_path = os.path.join(save, "waveform_report.json")
            with open(out_path, "w") as outfile:
                data = msgpack.unpackb(wave_report.encode(), raw=False)
                json.dump(data, outfile, indent=4)

        if dryrun:
            iprint("End of dry-run.")
            return

        self._cloud_upload_reports(reports, wave_report)

    def synchronize_clock(self, force_timestamp=None):
        """Synchronize the clock on the device with UTC time.

        If force_timestamp is passed, this timestamp will be used.  If not,
        the current utc time of this computer will be used.

        If you pass in force_timestamp it should be a normal unix timestamp as
        a float in seconds since the unix epoch.

        If the firmware does not support clock synchronization because it is
        too old, a False value will be returned.   This is not necessarily
        an error, it just means that UTC time is not supported.

        Args:
            force_timestamp (float): Optional timestamp to force the clock
                    to a specific time for testing purposes.

        Returns:
            bool: False if the firmware is too old to support synchronization.

        Raises:
            HardwareError: If there is a problem synchronizing on firmware that
                does support synchronization.
            ArgumentError: If you pass a fixed timestamp that is older than
                1/1 2000.
        """


        zero = datetime(1970, 1, 1)
        y2k = datetime(2000, 1, 1)

        epoch2000 = int((y2k - zero).total_seconds())

        if force_timestamp is not None:
            force_timestamp = int(force_timestamp)
            if force_timestamp < epoch2000:
                raise ArgumentError("force_timestamp must be greater than the epoch Jan 1 2000 0:0:0 = {0} (0x{0:X})".format(epoch2000),
                                    force_timestamp=force_timestamp)

            now = datetime.utcfromtimestamp(force_timestamp)
        else:
            now = datetime.utcnow()

        seconds_since_2000 = int((now - y2k).total_seconds())

        con = self._hw.controller()

        try:
            err, = con.rpc(0x10, 0x10, seconds_since_2000, arg_format="L", result_format="L")
            if err:
                raise HardwareError("Error synchronizing clock", error_code=err)
        except RPCNotFoundError:
            self.logger.info("Could not synchronize clock because firmware did not support the RPC")
            return False

        return True

    # Private function to upload data (*.bin) reports and waveforms to the cloud
    def _cloud_upload_reports(self, reports, wave_report):
        cloud = IOTileCloud()

        # Important for correct cloud processing, waveforms must be uploaded first before reports
        _, events = wave_report.decode()
        iprint("Uploading %d reports and %d waveforms to %s" % (len(reports), len(events), ConfigManager().get('cloud:server')))
        if len(events) > 0:
            iprint(" - uploading waveform events")
            cloud.upload_report(wave_report)
        else:
            iprint(" - no new waveforms to upload")

        for i, report in enumerate(reports):
            iprint(" - uploading data report %d" % (i+1,))
            cloud.upload_report(report)

        iprint(" - finished")
        return

    # Reads trip files
    def _get_trip_datafile_reports(self, path):
        """ Decodes saved trip data *.bin files and returns report objects.

        Args:
            path (str): The path to the bin file or folder where data was saved.
        Returns:
            list: A list of SignedListReport objects.
        """

        if not os.path.exists(path):
            raise ArgumentError("Path does not exist.", directory=path)

        binfiles = []
        if os.path.exists(path) and os.path.isdir(path):
            files = os.listdir(path)
            for file in files:
                _, ext = os.path.splitext(file)
                if ext == ".bin":
                    binfiles.append(os.path.join(path, file))
        elif os.path.exists(path) and os.path.isfile(path):
            binfiles.append(os.path.join(".", path))
        else:
            raise ArgumentError("Parameter is not a directory or file", directory=path)

        reports = []
        for bin_file in sorted(binfiles):
            with open(bin_file, "rb") as infile:
                iprint(".... checking {0}".format(bin_file))

                data = infile.read()
                reports.append(SignedListReport(data))

        return reports

    def _download_trip_reports(self, acknowledge, force_acks=None):
        downloader = self._hw.app(name='cloud_uploader')

        iprint("Downloading trip reports from device...")
        reports = downloader.download(trigger=0, acknowledge=acknowledge, force=force_acks)

        for report in reports:
            iprint(" - received report from streamer %d with %d readings" % (report.origin_streamer, len(report.visible_readings)))

        iprint(" - finished.")

        return reports

    def _get_waveform_ack(self):
        cloud = IOTileCloud()

        uuid = self._device_id
        streamer = WAVEFORM_STREAMER

        try:
            iprint("Checking iotile.cloud for UUID:{0:4X}, Streamer:{1:X}".format(uuid, streamer))
            last_uploaded = cloud.highest_acknowledged(uuid, streamer)
            iprint("Highest ack in iotile.cloud for UUID:{0:X}, Streamer:{1:X} is {2}".format(uuid, streamer, last_uploaded))
        except ArgumentError:
            iprint("Did not find ACKs in iotile.cloud for UUID:{0:X}, Streamer:{1:X}".format(uuid, streamer))
            last_uploaded = 0

        return last_uploaded

    @classmethod
    def _check_wavesforms_utc(cls, waves):
        for wave in waves:
            timestamp = wave['timestamp']

            if timestamp == 0xFFFFFFFF or not timestamp & (1 << 31):
                return False

        return True

    def _build_utc_assigner(self, reports):
        assigner = UTCAssigner()

        assigner.anchor_stream(START_STREAM_ENCODED, converter='epoch')
        assigner.anchor_stream(END_STREAM_ENCODED, converter='epoch')

        for report in reports:
            assigner.add_report(report)

        sgraph = self._hw.controller().sensor_graph()

        with self.suppress_output():
            trip_starts = sgraph.download_stream(START_STREAM)
            trip_ends = sgraph.download_stream(END_STREAM)

        for reading in trip_starts:
            assigner.add_reading(reading)

        for reading in trip_ends:
            assigner.add_reading(reading)

        return assigner

    @classmethod
    def _get_user_report(cls, reports):
        user_report = None
        for report in reports:
            if report.origin_streamer == USER_STREAMER:
                user_report = report
                break

        if user_report is None:
            raise HardwareError("Could not assign utc timestamps to waveforms because we did not receive a user data report", received_reports=reports)

        return user_report

    def _ensure_waveforms_utc(self, waves, reports=None):
        """Ensure that all received waveforms have UTC timestamps."""
        uptime_count = 0
        for wave in waves:
            timestamp = wave['timestamp']

            if timestamp & (1 << 31) and timestamp != 0xFFFFFFFF:
                wave['utc_timestamp'] = timestamp
            else:
                uptime_count += 1

        if uptime_count == 0:
            return waves

        iprint("Found %d waveforms with uptime not utc timestamps, preparing to fix." % uptime_count)

        user_report = self._get_user_report(reports)
        wave_map = {x.value: x.reading_id for x in user_report.visible_readings if x.stream == 0x5020}

        utc_assigner = self._build_utc_assigner(reports)

        to_drop = []
        for i, wave in enumerate(waves):
            timestamp = wave['timestamp']
            unique_id = wave['unique_id']
            utc_assignment = None

            if timestamp & (1 << 31) and timestamp != 0xFFFFFFFF:
                continue

            # Support old firmware that did not store timestamps with waveforms but
            # just included a blank 0xFFFFFFFF token.
            if timestamp == 0xFFFFFFFF:
                timestamp = None

            reading_id = wave_map.get(unique_id)
            if reading_id is not None:
                utc_assignment = utc_assigner.assign_utc(reading_id, timestamp)
            else:
                self.logger.debug("Dropping waveform %08X because it was not in user report", unique_id)

            if utc_assignment is None:
                self.logger.debug("Dropping waveform %08X because utc could not be assigned (controller_id=%s)", unique_id, reading_id)
                to_drop.append(i)
            else:
                self.logger.debug("Waveform %08X utc assignment: %s", reading_id, utc_assignment)
                wave['utc_timestamp'] = utc_assignment.rtc_value

        if len(to_drop) > 0:
            iprint("WARNING: Dropping %d waveforms of %d total whose utc timestamps could not be determined" % (len(to_drop), len(waves)))

            for i in reversed(to_drop):
                del waves[i]

        return waves

    def _download_all_waveforms_simple(self, path=None, prefix="_wavetmp_"):
        # Restore state (if error occured)
        # Read any existing waveforms into memory
        waves = []
        if path and prefix:
            temppath = os.path.join(path,"{}*.json".format(prefix))
            self.logger.debug("temppath:{}".format(path))
            if not os.path.exists(path):
                self.logger.debug("makedirs:{}".format(path))
                os.makedirs(path)

            tempfiles = glob.glob(temppath)
            self.logger.debug("tempfiles:{}".format(tempfiles))
            for tfile in tempfiles:
                self.logger.debug("opening:{}".format(tfile))
                with open(tfile, 'r') as tf:
                    w = json.load(tf)
                    uid = w.get('unique_id')
                    crc = w.get('crc32_value')
                    crcv = w.get('crc_verification')
                    ts = w.get('timestamp')
                    d = w.get('data')
                    if uid and crc and crcv and ts and d:
                        waves.append(w)
                        iprint("Reading waveform from tempfile: {}".format(tfile))
                    else:
                        iprint("ERROR, JSON DATA NOT OK")
                        return None

        accel = self._hw.get(ACCEL_ADDRESS)
        waveman = accel.waveform_manager()
        waveman.enter_streaming_mode()
        try:
            cnt = waveman.count()
            if len(waves) < cnt:
                for idx in range(len(waves),cnt):
                    self.logger.info("UUID {2} (0x{2:X}): Downloading: {0}/{1} = {3:.1f}%".format(
                        idx,cnt, self._device_id, float(idx*100.0/cnt)))
                    wave = waveman.stream_waveform(idx)

                    out_path = os.path.join(path, "{}_{:08X}.json".format(prefix,wave['unique_id']))
                    with open(out_path, "w") as out_file:
                        json.dump(wave, out_file, indent=4)

                    waves.append(wave)
        finally:
            waveman.leave_streaming_mode()

        return waves

    def _download_waveforms(self, acknowledge=True, force_ack=None):
        """Download the top 100 stored waveforms in the POD1-M."""

        accel = self._hw.get(ACCEL_ADDRESS)
        waveman = accel.waveform_manager()
        waveman.enter_streaming_mode()
        try:
            highest_id = 0

            if acknowledge:
                if force_ack is not None:
                    highest_id = force_ack
                else:
                    highest_id = self._get_waveform_ack()

            if highest_id > 0:
                iprint("Skipping all waveforms up to 0x{0:X} because they have been acknowledged by the cloud".format(highest_id))

            waveman.sort_waveforms(skip_id=highest_id)
            waves = waveman.stream_sorted_waveforms()
        finally:
            waveman.leave_streaming_mode()

        return waves


@context("TrackerAdmin")
class TrackerAdmin(object):
    """Advanced administrative interface to POD-1M.

    The methods in this interface are not for general use but only for
    advanced support use cases.

    **Using them can cause you to lose data on your POD-1M.**
    """

    def __init__(self, app):
        self.app = app

    @docannotate
    def clear_trip(self):
        """Clear all data on the POD and prepare for another trip.

        This routine will delete all information stored on the POD and return
        it to 'not started' status so that you can begin another trip.  If you
        call this function before uploading data you will lose all data on the
        device.
        """

        status = self.app.trip_info()
        if status['trip_status'] == 'in progress':
            raise HardwareError("You cannot reset a POD while it is in a trip, please end the trip first.")

        setup = self.app._hw.get(ACCEL_ADDRESS).setup_manager()
        sgraph = self.app._hw.controller().sensor_graph()

        setup.admin_reset()
        sgraph.clear()

    @docannotate
    def set_environmental_timer(self, time_in_seconds):
        """Changes the interval for the environmental timer.

        This sets the config variable inside the config database to reflect the
        user's desired interval rate. Afterwards, it sets user tick so that the
        change takes effect immediately without needing a reset.

        Args:
            time_in_seconds (int): The time in seconds to set the environmental
                    timer's interval to.

        """

        status = self.app.trip_info()
        if status['trip_status'] != 'not started':
            raise HardwareError("You can only change the environmental timer before a trip has started.")

        con = self.app._hw.controller()
        sgraph = con.sensor_graph()
        conf_db = con.config_database()

        conf_db.set_variable('controller', 0x2002, 'uint32_t', time_in_seconds)
        sgraph.set_user_tick(1, time_in_seconds)
        sgraph.user_tick(1)

    @docannotate
    def reboot(self):
        """Forcibly reboot the device.

        This reboots the device and causes it to reinitialize itself. This will
        not delete any data from the device and should not be generally necessary
        to do ever.  It exists only to provide a quick way to fix any weirdness
        that you observe while using the device.

        If you need to use this function you should also probably also report
        a bug and describe what behavior you were seeing from the device.
        """

        print("Rebooting, this will take about 5 seconds...")

        with self.app.suppress_output():
            self.app._hw.controller().reset()

    @docannotate
    def synchronize_clock(self, force_timestamp=None):
        """Synchronize the clock on the device with UTC time.

        If force_timestamp is passed, this timestamp will be used.  If not, the
        current utc time of this computer will be used.

        If you pass in force_timestamp it should be a normal unix timestamp
        as a float in seconds since the unix epoch.

        Args:
            force_timestamp (float): Optional timestamp to force the clock
                    to a specific time for testing purposes.
        """

        self.app.synchronize_clock(force_timestamp)

    @docannotate
    def save_trip_locally(self, path=".", clean=False):
        """Save all waveforms locally
        This function will download all data from the device and save it
        locally on the computer harddrive.

        Args:
            path (str): The path to a folder where all data should be saved.
            clean (bool): This will clear all old files from the directory specified in path.
        """
        info = self.app.trip_info()
        if info['trip_status'] != 'finished':
            raise HardwareError("You must finish a trip first before calling save_trip_locally", trip_status=info['trip_status'])

        if path is not None:
            if os.path.exists(path) and not os.path.isdir(path):
                raise ArgumentError("You passed a path directory that exists but is not a directory", directory=path)

            if os.path.exists(path) and clean:
                iprint("Cleaning folder at: %s" % path)
                shutil.rmtree(path)

            if not os.path.exists(path):
                os.makedirs(path)

        # Make sure to sort the waveforms we got by time so they are in cronological order.
        waves = self.app._download_all_waveforms_simple(path=path+"/.tracker_app_temp")
        waves = sorted(waves, key=lambda x: x['unique_id'])

        force_acks = None
        if not self.app._check_wavesforms_utc(waves):
            iprint("We received waveforms with uptime rather than utc timestamps, rolling back streamer 0")
            iprint("This will ensure we have all of the data we need to assign utc timestamps.")
            force_acks = {0: (1, True)}
        reports = self.app._download_trip_reports(acknowledge=False, force_acks=force_acks)

        waves = self.app._ensure_waveforms_utc(waves, reports=reports)

        if path:
            for i, report in enumerate(reports):
                out_path = os.path.join(path, "report_%d_%s.bin" % (i, report.received_time.isoformat().replace(':', '-')))
                with open(out_path, "wb") as outfile:
                    outfile.write(report.encode())

            for wave in waves:
                out_path = os.path.join(path, "waveform_%08X.json" % wave['unique_id'])
                with open(out_path, "w") as out_file:
                    json.dump(wave, out_file, indent=4)

        events = [_create_waveform_event(x) for x in waves]
        iprint("Found %d reports and %d waveforms." % (len(reports), len(events)))
        wave_report = FlexibleDictionaryReport.FromReadings(self.app._device_id, [], events,
                                                            sent_timestamp=0xFFFFFFFF,
                                                            streamer=WAVEFORM_STREAMER,
                                                            received_time=datetime.utcnow())

        if path:
            out_path = os.path.join(path, "waveform_report.mp")
            with open(out_path, "wb") as outfile:
                outfile.write(wave_report.encode())

            out_path = os.path.join(path, "waveform_report.json")
            with open(out_path, "w") as outfile:
                data = msgpack.unpackb(wave_report.encode(),raw=False)
                json.dump(data, outfile, indent=4)

        return

    @docannotate
    def save_bin_locally(self, save=".", clean=False, acknowledge=False):
        """Save just the streamer reports locally

        Args:
            save (str): The path to a folder where all data should be saved
                before uploading.  This is optional, if you don't specify it
                no data will be saved.
            clean (bool): When combined with save, this will clear all old files
                from the directory specified in save.  Otherwise it has no effect.
            acknowledge (bool): Acknowledge received readings from iotile.cloud
                before downloading new data.
        """

        info = self.app.trip_info()
        if info['trip_status'] != 'finished':
            raise HardwareError("You must finish a trip first before calling upload_trip", trip_status=info['trip_status'])

        if save is not None:
            if os.path.exists(save) and not os.path.isdir(save):
                raise ArgumentError("You passed a save directory that exists but is not a directory", directory=save)

            if os.path.exists(save) and clean:
                iprint("Cleaning folder at: %s" % save)
                shutil.rmtree(save)

            if not os.path.exists(save):
                os.makedirs(save)

        reports = self.app._download_trip_reports(acknowledge)

        if save:
            for i, report in enumerate(reports):
                out_path = os.path.join(save, "report_%d_%s.bin" % (i, report.received_time.isoformat().replace(':', '-')))
                with open(out_path, "wb") as outfile:
                    outfile.write(report.encode())


# Private Functions
def _format_shock(shock):
    """Format a shock into X G, Y in/s."""

    peak = shock['peak']
    peak_axis = shock['peak_axis']
    max_dv = max(abs(shock['deltav_x']), max(abs(shock['deltav_y']), abs(shock['deltav_z'])))

    max_dv *= M_S__TO_IN_S

    return "%.1f G, %.2f in/s on %s" %(peak, max_dv, peak_axis)

def _current_timestamp():
    """Return the number of seconds since the unix epoch."""

    now = datetime.utcnow()
    return int((now - datetime(1970, 1, 1)).total_seconds())


def _parse_timestamp(seconds):
    """Turn the number of seconds since the epoch into a datetime."""

    return datetime.utcfromtimestamp(float(seconds))


def _determine_trip_status(start_events, end_events):
    """Determine a trip status given a list of start and end events."""

    if len(start_events) == 0 and len(end_events) == 0:
        return {
            'trip_status': 'not started',
            'trip_start': None,
            'trip_end': None
        }
    elif len(start_events) == 0 and len(end_events) > 0:
        return {
            'trip_status': 'corrupted',
            'trip_start': None,
            'trip_end': _parse_timestamp(end_events[-1].value)
        }
    elif len(start_events) > 1 or len(end_events) > 1:
        return {
            'trip_status': 'multiple trips',
            'trip_start': None,
            'trip_end': None
        }
    elif len(start_events) == 1 and len(end_events) == 0:
        return {
            'trip_status': 'in progress',
            'trip_start': _parse_timestamp(start_events[0].value),
            'trip_end': None
        }

    return {
        'trip_status': 'finished',
        'trip_start': _parse_timestamp(start_events[0].value),
        'trip_end': _parse_timestamp(end_events[0].value)
    }


def _time_above_threshold(data, thresh, sampling_rate):
    """Return the number of ms that a given time series is above a threshold."""

    max_count = 0
    curr_count = 0
    above = False
    last_sample = 0.0

    for sample in data:
        if above is False and abs(sample) >= thresh:
            above = True
            curr_count = 0
        elif above:
            curr_count += 1
            if abs(sample) < thresh or last_sample*sample < 0.0:
                above = False
                if curr_count > max_count:
                    max_count = curr_count

        last_sample = sample

    if above and curr_count > max_count:
        max_count = curr_count

    return max_count / sampling_rate * 1000.0


def _delta_v(data, thresh, sampling_rate):
    """Calculate the largest delta_v for the timeseries."""

    max_dv = 0
    curr_dv = 0
    above = False
    last_sample = 0.0

    for sample in data:
        if above is False and abs(sample) >= thresh:
            above = True
            curr_dv = sample
        elif above:
            curr_dv += sample
            if abs(sample) < thresh or last_sample*sample < 0.0:
                above = False
                if abs(curr_dv) > abs(max_dv):
                    max_dv = curr_dv

        last_sample = sample

    if above and abs(curr_dv) > abs(max_dv):
        max_dv = curr_dv

    return max_dv*G_CONST / sampling_rate


def _abslist(indata):
    return [abs(x) for x in indata]


def _summarize_waveform(wave, thresh, sampling_rate):
    """Create summary data for a waveform."""

    x_data = wave['data']['x']
    y_data = wave['data']['y']
    z_data = wave['data']['z']

    max_x = max(_abslist(x_data))
    max_y = max(_abslist(y_data))
    max_z = max(_abslist(z_data))

    max_g = max(max_x, max(max_y, max_z))

    if max_g == max_x:
        axis = 'x'
    elif max_g == max_y:
        axis = 'y'
    else:
        axis = 'z'

    dur_x = _time_above_threshold(x_data, thresh, sampling_rate)
    dur_y = _time_above_threshold(y_data, thresh, sampling_rate)
    dur_z = _time_above_threshold(z_data, thresh, sampling_rate)

    dur = max(dur_x, max(dur_y, dur_z))

    return {
        'peak': max_g,
        'axis': axis,
        'duration': dur,
        'delta_v_x': _delta_v(x_data, thresh, sampling_rate),
        'delta_v_y': _delta_v(y_data, thresh, sampling_rate),
        'delta_v_z': _delta_v(z_data, thresh, sampling_rate)
    }


def _create_waveform_event(wave, sampling_rate=3200 / 3., threshold=1.0):
    """Create an IOTileEvent object for a waveform."""

    stream = DataStream.FromString(ACCEL_STREAM).encode()

    data = {
        'acceleration_data': {
            'x': wave['data']['x'],
            'y': wave['data']['y'],
            'z': wave['data']['z']
        },

        'sampling_rate': sampling_rate,  # We sample at 1066 Hz (3200 hz with 3x decimation)
        'crc_code': wave['crc32_value']
    }

    reading_time = UTCAssigner.convert_rtc(wave['utc_timestamp'])

    summary = _summarize_waveform(wave, threshold, sampling_rate)

    return IOTileEvent(wave['timestamp'], stream, summary, data, reading_id=wave['unique_id'], reading_time=reading_time)
