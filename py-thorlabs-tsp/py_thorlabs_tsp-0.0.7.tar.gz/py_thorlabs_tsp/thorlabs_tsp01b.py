# -*- coding: utf-8 -*-
"""py_thorlabs_tsp.thorlabs_tsp01b.py

This file implements a class to control Thorlabs TSP01B sensor.

It wraps limited set of low-level functions in a single class and
provides error processing.

Author: Dima Pustakhod
Copyright: TU/e
"""
from typing import Optional

from . import _findRsrc, _getRsrcInfo, _getRsrcName
from . import _init, _close
from . import _measTemperature, _measHumidity
from .errors import _process_error, ThorlabsTsp01BException


def _check_connected_device(manufacturer: str, model: str):
    if manufacturer == 'Thorlabs' and model == 'TSP01B':
        return True
    else:
        return False


class ThorlabsTsp01B(object):
    CH_MAPPING = {'TH0': 1, 'TH1': 2, 'TH2': 3, 'H0': None}

    def __init__(self, serial_no: Optional[str] = None):
        self._serial_no = None
        self._instr_handle = None
        self._res_name = None

        e, n_connected_devices = _findRsrc()
        self._process_error(e, '_findRsrc')

        print('No connected devices: {}'.format(n_connected_devices))
        if n_connected_devices < 1:
            print('No connected devices compatible with TSP01B found.')

        # Search for the proper device
        device_found = False
        for dev_id in range(0, n_connected_devices):
            e, model, sn, manufacturer, is_in_use = _getRsrcInfo(dev_id)
            self._process_error(e, '_getRsrcInfo')

            if _check_connected_device(manufacturer, model):
                # proper manufacturer and model, check SN if given
                if serial_no:
                    if sn == serial_no:
                        device_found = True
                        self._serial_no = sn
                        break
                else:
                    device_found = True
                    self._serial_no = sn
                    break
            else:
                # go to the next device
                pass

        if not device_found:
            raise ThorlabsTsp01BException(
                'Thorlabs TSP01B with SN {} not found.'.format(serial_no)
            )
        else:
            e, self._res_name = _getRsrcName(0)
            self._process_error(e, '_getRsrcName')

            e, self._instr_handle = _init(self._res_name, False, False)
            self._process_error(e, '_init')

            print(
                'Thorlabs TSP01B with SN {} (resource {}) is connected.'.format(
                    self._serial_no, self._res_name
                )
            )

    def release(self):
        e = _close(self._instr_handle)
        self._process_error(e, '_close')
        print(
            'Thorlabs TSP01B with SN {} (resource {}) is released.'.format(
                self._serial_no, self._res_name
            )
        )

    def measure_temperature(self, ch_id: str = 'TH0'):
        if ch_id.upper() not in ('TH0', 'TH1', 'TH2'):
            raise ValueError(
                'Thorlabs TSP01B has temperature channels "TH0" '
                '(internal), "TH1", "TH2" only. "{}" is given.'.format(ch_id)
            )

        e, t = _measTemperature(
            self._instr_handle, self.CH_MAPPING[ch_id.upper()]
        )
        self._process_error(e, '_measTemperature')

        return t

    def measure_humidity(self, ch_id: str = 'H0'):
        if ch_id.upper() not in ('H0',):
            raise ValueError(
                'Thorlabs TSP01B has humidity channel "H0" only. '
                '{} is given.'.format(ch_id)
            )
        e, h = _measHumidity(self._instr_handle)
        self._process_error(e, '_measHumidity')

        return h

    def _process_error(self, error_code, fcn: Optional[str] = ''):
        _process_error(self._instr_handle, error_code, fcn)
