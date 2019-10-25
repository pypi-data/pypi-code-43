from typing import List, Tuple, Union, Optional
import logging
from ftdi_serial import Serial, SerialReadTimeoutException

logger = logging.getLogger(__name__)


class ScientechZeta:
    GRAMS = 'GRAMS'
    KG = 'KG'
    MG = 'MG'

    @staticmethod
    def parse_weight_response(response: bytes) -> float:
        stripped = response.strip(b'\r\n ')
        split = stripped.split(b' ')
        return float(split[0])

    def __init__(self, serial: Serial, timeout: float=0.5, retry_timeout: float=0.1, units: str=GRAMS):
        self.logger = logger.getChild(self.__class__.__name__)
        self.serial = serial
        self.timeout = timeout
        self.retry_timeout = retry_timeout
        self.set_units(units)
        self.clear()

    def request(self, request: bytes, retries: int=1) -> bytes:
        try:
            self.logger.debug(f'Request: {request}')
            response_raw = self.serial.request(request + b'\r', line_ending=b'\r\n', timeout=self.timeout)
            response = response_raw.rstrip(b'\r\n')
            self.logger.debug(f'Response: {response}')

            if response.startswith(b'?'):
                self.logger.debug(f'Error response: {response}')
                if retries <= 0:
                    raise ScientechZetaResponseError(f'Error response for request: {request}')

                return self.request(request, retries=retries-1)

            return response

        except SerialReadTimeoutException:
            self.logger.debug(f'Timeout')
            if retries <= 0:
                raise ScientechZetaRequestTimeout(f'Request timeout: {request}')

            return self.request(request, retries=retries-1)

    def set_units(self, units: str):
        if units not in (self.GRAMS, self.KG, self.MG):
            raise ScientechZetaInvalidUnitsError(f'Invalid units: {units}')

        self.request(units.encode())

    def clear(self):
        self.logger.info('Clear')
        self.request(b'CLEAR')

    def tare(self):
        self.logger.info('Tare')
        self.request(b'TARE')

    def weigh(self):
        return self.parse_weight_response(self.request(b'SEND'))


class ScientechZetaError(Exception):
    pass


class ScientechZetaRequestTimeout(ScientechZetaError):
    pass


class ScientechZetaInvalidUnitsError(ScientechZetaError):
    pass


class ScientechZetaResponseError(ScientechZetaError):
    pass