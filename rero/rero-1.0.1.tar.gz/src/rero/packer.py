"""Packer is a communication protocol intended for transmissions of byte frames over e.g. a serial interface or
buses. It builds upon [COBS](https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing) which allows for a
minimum encoding overhead. It is perfectly suited for MCUs with DMA support.

A Packer frame is simplified packed the following way:

| length field k | checksum length field c | address field l | payload p | CRC m | EOF |
|----------------|-------------------------|-----------------|-----------|-------|-----|

The maximum number of overhead bytes
                                                t = k + c + l + m
is limited to <= 13! The maximum payload length pMax in bytes is determined by the number of length field bytes k
and the total number of overhead bytes as
                                        pMax = 2 ** (8 * (k + 1) - n) - 1
                                        n = ceil(log2(t + 2)),
where n is the number of bits needed to represent the first COBS code (look into the docs for more information).
The table below lists all possible combinations.

| k |  t |         pMax        |
|:-:|:--:|:-------------------:|
| 0 |  0 |          63         |
| 0 |  1 |          63         |
| 1 |  1 |        16383        |
| 0 |  2 |          31         |
| 1 |  2 |         8191        |
| 2 |  2 |       2097151       |
| 0 |  3 |          31         |
| 1 |  3 |         8191        |
| 2 |  3 |       2097151       |
| 3 |  3 |      536870911      |
| 0 |  4 |          31         |
| 1 |  4 |         8191        |
| 2 |  4 |       2097151       |
| 3 |  4 |      536870911      |
| 0 |  5 |          31         |
| 1 |  5 |         8191        |
| 2 |  5 |       2097151       |
| 3 |  5 |      536870911      |
| 0 |  6 |          15         |
| 1 |  6 |         4095        |
| 2 |  6 |       1048575       |
| 3 |  6 |      268435455      |
| 0 |  7 |          15         |
| 1 |  7 |         4095        |
| 2 |  7 |       1048575       |
| 3 |  7 |      268435455      |
| 0 |  8 |          15         |
| 1 |  8 |         4095        |
| 2 |  8 |       1048575       |
| 3 |  8 |      268435455      |
| 0 |  9 |          15         |
| 1 |  9 |         4095        |
| 2 |  9 |       1048575       |
| 3 |  9 |      268435455      |
| 0 | 10 |          15         |
| 1 | 10 |         4095        |
| 2 | 10 |       1048575       |
| 3 | 10 |      268435455      |
| 0 | 11 |          15         |
| 1 | 11 |         4095        |
| 2 | 11 |       1048575       |
| 3 | 11 |      268435455      |
| 0 | 12 |          15         |
| 1 | 12 |         4095        |
| 2 | 12 |       1048575       |
| 3 | 12 |      268435455      |
| 0 | 13 |          15         |
| 1 | 13 |         4095        |
| 2 | 13 |       1048575       |
| 3 | 13 |      268435455      |

Logging messages and levels:

|            Event               |  Level  |
|:------------------------------:|:-------:|
|   PayloadOverlengthReroError   |  ERROR  |
|  NoDestinationAddressReroError |  ERROR  |
|       OutOfSyncReroError       | WARNING |
|          CRCReroError          |   INFO  |
| OtherRecipientReroNotification |   INFO  |
|        Frame packed            |  DEBUG  |
|       Frame unpacked           |  DEBUG  |

For further information read the docs.

"""

# MIT License

# Copyright (c) 2019 Reinhard Panhuber

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from cobs import cobs, cobsr
import crcmod
import logging
from math import log2, floor, ceil
from typing import Dict, Union
from time import monotonic

# To make it work both in PyCharm and for building
try:
    from src.rero.exceptions import *
except ImportError:
    from rero.exceptions import *


# Setup Packer class
class Packer:
    # Static exceptions
    __outOfSyncError = OutOfSyncReroError()
    __destAddrError = NoDestinationAddressReroError()

    def __init__(self, addrSrc: int = None,
                 addrDstDefault: int = None,
                 crc: Union[crcmod.Crc, None] = crcmod.predefined.Crc('crc-32-mpeg'),
                 addrFieldLen: int = 1,
                 addFrameFieldLen: int = 1,
                 enableFrameLenCheck: bool = False,
                 yieldCRCError: bool = False,
                 yieldOutOfSyncError: bool = False,
                 yieldOtherRecipientNotification: bool = False,
                 yieldTimeoutError: bool = False,
                 timeoutPeriod: float = 0.0,
                 logHandler: logging.Handler = logging.NullHandler()):

        """
        Parameters
        ----------
        addrSrc : int
            Source address used to determine if received frame is intended for this node. Default = None.
        addrDstDefault : int
            Default destination address. Default = None.
        crc : crcmod.Crc
            CRC object of crcmod package used for CRC calculation. If None is given no CRC checks are conducted.
            Default = crcmod.predefined.Crc('crc-32-mpeg').
        addrFieldLen : int
            Number of address bytes - valid range is [0-4]. If 0 no address checks are conducted. Default = 1.
        addFrameFieldLen : int
            Number of extra frame length bytes - valid range is [0-3]. Default = 1.
        enableFrameLenCheck : bool
            If true an additional checksum for the length field is used. Default = False.
        yieldCRCError : bool
            If true an exception is yielded in case CRC check fails. Default = False.
        yieldOutOfSyncError : bool
            If true an exception is yielded in case we are out of synchronization. Default = False.
        yieldOtherRecipientNotification : bool
            If true an exception is yielded in case a frame intended for a different node is received.  Default = False.
        yieldTimeoutError : bool
            If true an exception is yielded in case timeoutPeriod happens. Default = False.
        timeoutPeriod : float
            Timeout duration in seconds. If timeoutPeriod = 0, timeoutPeriod is disabled.  Default = 0.0.
        logHandler : logging.Handler
            Handler object of logging package. Default = logging.NullHandler().

        Raises
        ------
        ValueError
            If limits described above are violated.

        """

        # Conduct assertions
        assert addrDstDefault is None or isinstance(addrDstDefault, int)
        assert crc is None or isinstance(crc, crcmod.Crc)
        assert isinstance(addrFieldLen, int)
        assert isinstance(addFrameFieldLen, int)
        assert isinstance(enableFrameLenCheck, bool)
        assert isinstance(timeoutPeriod, float)
        assert isinstance(yieldCRCError, bool)
        assert isinstance(yieldOutOfSyncError, bool)
        assert isinstance(yieldOtherRecipientNotification, bool)
        assert isinstance(yieldTimeoutError, bool)
        assert isinstance(logHandler, logging.Handler)

        # Sanity checks
        if not 0 <= addrFieldLen <= 4:
            raise ValueError('0 <= addrFieldLen <= 4 out of bounds!')

        if not 0 <= addFrameFieldLen <= 3:
            raise ValueError('0 <= addFrameFieldLen <= 3 out of bounds!')

        if crc:
            if not crc.digest_size <= 8:
                raise ValueError('crc.digest_size <= 8 out of bounds!')
            if enableFrameLenCheck:
                if not crc.digest_size + addrFieldLen + addFrameFieldLen + 1 <= 13:
                    raise ValueError('Number of overhead + CRC bytes <= 13 out of bounds!')
            else:
                if not crc.digest_size + addrFieldLen + addFrameFieldLen <= 13:
                    raise ValueError('Number of overhead + CRC bytes <= 13 out of bounds!')

        if addrSrc is None and addrFieldLen > 0:
            raise ValueError('Address field defined but no source address!')

        if isinstance(addrSrc, int) and addrFieldLen == 0:
            raise ValueError('Source address defined but no address field!')

        self.addrSrc = addrSrc
        self.addrDestDefault = addrDstDefault
        self._addrFieldLen = addrFieldLen
        self._frameFieldLen = addFrameFieldLen
        self.yieldCRCError = yieldCRCError
        self.yieldOutOfSyncError = yieldOutOfSyncError
        self.yieldOtherRecipientNotification = yieldOtherRecipientNotification
        self.yieldTimeoutError = yieldTimeoutError
        self.timeoutPeriod = timeoutPeriod
        self.logger = logging.getLogger('rero')

        # For better index calculation use some numbers here
        if enableFrameLenCheck:
            self._lenFieldChecksum = 1
        else:
            self._lenFieldChecksum = 0

        if crc:
            self._crcLen = crc.digest_size
        else:
            self._crcLen = 0

        # Setup CRC module

        # Default is crc-32-mpeg mode which is: poly = 0x4C11DB7, initVal = 0xFFFFFFFF, no input- and
        # output reflection, and no XOR out
        self.crc = crc

        # Determine # bits needed for COBS code 0 and maximum possible frame length Since we require
        # self.crc.digest_size + _frameFieldLen + _addrFieldLen <= 13 it is guaranteed that # bits needed is <= 4
        nManBytes = addFrameFieldLen + 1 + addrFieldLen + 1 + self._lenFieldChecksum + self._crcLen

        self.__nBitsCobsCode0 = ceil(log2(nManBytes + 1))

        # Determine maximum payload length
        self.payloadLenMax = 2 ** (8 * (addFrameFieldLen + 1) - self.__nBitsCobsCode0) - 1

        # Check if we need to consider stuffing bytes
        if self.payloadLenMax > 254:
            self.payloadLenMax = floor(self.payloadLenMax / (1 + 1 / 254))

        # Setup message buffer
        self.msgBuffer = bytearray()

        # Setup synchronization status
        self.__statOutOfSyncError = False

        # Setup time passed variable for timeoutPeriod
        self.__startTimerFlag = False
        self.__timeStamp = 0

        # Setup logging
        self.logger.addHandler(logHandler)
        self.logger.setLevel(logging.DEBUG)

    def pack(self, payload: bytes, addrDst: int = None) -> bytes:

        """
        Packs a frame.

        Parameters
        ----------
        payload : bytes
            Payload to be packed.
        addrDst : int
            Address of destination node, if not given addrDstDefault is used.

        Returns
        -------
        msgToSend : bytes
            Packed frame.

        Raises
        ------
        NoDestinationAddressReroError
            No destination address or default destination address set.
        PayloadOverlengthReroError
            Payload too long.

        """

        # Conduct assertions
        assert isinstance(payload, bytes)
        assert addrDst is None or isinstance(addrDst, int)

        # Check if destination address exists if address fields are setup
        if self._addrFieldLen > 0 and not (addrDst or self.addrDestDefault):
            self.logger.error(self.__destAddrError.__str__())
            raise self.__destAddrError

        # Check length of payload
        if len(payload) > self.payloadLenMax:
            err = PayloadOverlengthReroError(len(payload), self.payloadLenMax)
            self.logger.error(err.__str__())
            raise err

        # If no address is defined use default value
        addrDst = addrDst or self.addrDestDefault

        # Encode payload
        msgEnc = cobsr.encode(payload)

        # Setup address field if required
        if self._addrFieldLen > 0:
            addrField = addrDst.to_bytes(self._addrFieldLen, byteorder='big')

        # Calculate CRC of payload and address field if required
        if self.crc:
            crcGen = self.crc.new()
            if self._addrFieldLen > 0:
                crcGen.update(addrField + msgEnc)
            else:
                crcGen.update(msgEnc)
            crcField = crcGen.digest()

        # Determine encoded message length
        lenField = len(msgEnc).to_bytes(self._frameFieldLen + 1, byteorder='big')

        # Encode length field, lenFieldChecksum, address field, and CRC field using plain COBS - this takes care the
        # total length is exactly one byte more
        managementBytesEnc = lenField

        if self._lenFieldChecksum > 0:
            # Conduct ones complement on one byte
            managementBytesEnc = managementBytesEnc + self._ones_comp_checksum(lenField)

        if self._addrFieldLen > 0:
            managementBytesEnc = managementBytesEnc + addrField

        if self.crc:
            managementBytesEnc = managementBytesEnc + crcField

        managementBytesEnc = cobs.encode(managementBytesEnc)

        # Combine first two bytes - these exist for sure
        msgToSend = bytes([((managementBytesEnc[0] << (8 - self.__nBitsCobsCode0)) | managementBytesEnc[1])])

        # Build frame to send
        idxStart = 2
        if self._frameFieldLen > 0:
            msgToSend = msgToSend + managementBytesEnc[idxStart:(idxStart + self._frameFieldLen)]
            idxStart = idxStart + self._frameFieldLen

        if self._lenFieldChecksum > 0:
            msgToSend = msgToSend + managementBytesEnc[idxStart:(idxStart + self._lenFieldChecksum)]
            idxStart = idxStart + self._lenFieldChecksum

        if self._addrFieldLen > 0:
            msgToSend = msgToSend + managementBytesEnc[idxStart:(idxStart + self._addrFieldLen)]
            idxStart = idxStart + self._addrFieldLen

        msgToSend = msgToSend + msgEnc

        if self.crc:
            msgToSend = msgToSend + managementBytesEnc[idxStart:]

        msgToSend = msgToSend + bytes([0x00])

        # Done return
        self.logger.debug(
            "Frame packed - payload length: {:d} bytes - frame length: {:d} bytes".format(len(payload), len(msgToSend)))
        return msgToSend

    def unpack(self, msgRcd: bytes = b'') -> Union[bytes, ReroError]:
        """
        This method buffers received bytes, checks if sufficient bytes are received and if so it decodes them and
        yields the decoded frame. This is done until no more complete frames are available. In case no sufficient
        bytes were received (or remain) it starts a timeout counter if defined in _init_. In case of a CRC error it
        discards the frame and yields a CRC exception if defined in _init_. In case of a synchronization error it
        tries to resynchronize on its own by looking for an EOF delimiter in the received bytes. All bytes received
        before the found EOF delimiter get discarded. If defined in _init_ it yields a synchronization error.

        Parameters
        ----------
        msgRcd : bytes
            Received or partly received frame.

        Yields
        ------
        Union[bytes, ReroError]
            Decoded frame or rero exceptions if defined so in _init_. Yielded exceptions may be:

            OutOfSyncReroError
                Out of synchronization, function tries to resynchronize on its own by searching an EOF delimiter (0x00)
                in the subsequent bytes.
            OtherRecipientNotification
                Frame was not addressed to this node.
            CRCReroError
                CRC error was detected.
            TimeoutError
                Partly received frame was not received in time.

        """

        # Conduct assertions
        assert isinstance(msgRcd, bytes)

        while True:
            # Check if timeout happened
            if self.timeoutPeriod > 0 and self.__startTimerFlag:
                # Reset Flag
                self.__startTimerFlag = False

                # Determine elapsed time
                timeElapsed = monotonic() - self.__timeStamp
                if timeElapsed > self.timeoutPeriod:
                    # Timeout happened - flush buffer
                    self.msgBuffer = bytearray()

                    # Report error if required
                    if self.yieldTimeoutError:
                        yield TimeoutReroError()

            # Save message in buffer
            self.msgBuffer = self.msgBuffer + msgRcd

            # Clear input message since otherwise msgRcd would be appended every iteration
            msgRcd = b''

            # Check for out of sync status
            if self.__statOutOfSyncError:
                # Try to synchronize again
                # Find first occurrence of EOF delimiter
                idx = self.msgBuffer.find(bytes([0]))

                # If there is any
                if idx >= 0:
                    # Get rid of all bytes before EOF delimiter (including EOF delimiter)
                    self.msgBuffer = self.msgBuffer[idx + 1:]
                    # Get rid of all additional present EOF delimiters which may occur here
                    self.msgBuffer = self.msgBuffer.lstrip(bytes([0]))
                    # We are synchronized again - reset status
                    self.__statOutOfSyncError = False
                else:
                    # If nothing found get rid of all and hope for the next time
                    self.msgBuffer = bytearray()

                    # Nothing left in buffer so break
                    break

            # Check if enough bytes were received for header
            if len(self.msgBuffer) < self._frameFieldLen + 1 + self._addrFieldLen + self._lenFieldChecksum:

                # Something is left in buffer - start timeout if required
                if self.timeoutPeriod > 0:
                    self.__startTimerFlag = True
                    self.__timeStamp = monotonic()

                # Nothing can be done any more so break
                break

            # Check the header if an EOF delimiter (0x00) is contained within for robustness
            if bytes([0]) in self.msgBuffer[:(self._frameFieldLen + 1 + self._addrFieldLen + self._lenFieldChecksum)]:
                # Header is not valid - we are not synchronized
                # Set flag to start resynchronization next cycle
                self.__statOutOfSyncError = True

                # Flush all until (including) EOF delimiter
                self.msgBuffer = self.msgBuffer[self.msgBuffer.find(bytes([0])) + 1:]

                # Print message
                self.logger.warning(self.__outOfSyncError.__str__())

                # Yield exception and return if needed
                if self.yieldOutOfSyncError:
                    yield self.__outOfSyncError

                # Start again
                continue

            # Decode header
            header = self._decode_header(self.msgBuffer)

            frameLen = header['frameLen']

            # Check the length field if required
            if self._lenFieldChecksum > 0:
                if header['frameLenCheckSum'] != int.from_bytes(
                        self._ones_comp_checksum(frameLen.to_bytes(1 + self._frameFieldLen, 'big')), 'big'):
                    # The check was not successful hence we are not synchronized
                    # Set flag to start resynchronization next time
                    self.__statOutOfSyncError = True

                    # Flush buffer
                    self.msgBuffer = self.msgBuffer[self._frameFieldLen + 1:]

                    # Print message
                    self.logger.warning(self.__outOfSyncError.__str__())

                    # Yield exception and return if needed
                    if self.yieldOutOfSyncError:
                        yield self.__outOfSyncError

                    # Start again
                    continue

            # Check if enough bytes were received for the whole frame
            totFrameLen = self._frameFieldLen + 1 + self._addrFieldLen + frameLen + 1 + self._crcLen + self._lenFieldChecksum

            if len(self.msgBuffer) < totFrameLen:

                # Something is left in buffer - start timeout if required
                if self.timeoutPeriod > 0:
                    self.__startTimerFlag = True
                    self.__timeStamp = monotonic()

                # Definitely nothing in buffer to process any more - so break
                break

            # Check if EOF delimiter is at designated position
            if self.msgBuffer[totFrameLen - 1] != 0:
                # Set flag to start resynchronization next time
                self.__statOutOfSyncError = True

                # Flush buffer
                self.msgBuffer = self.msgBuffer[totFrameLen:]

                # Print message
                self.logger.warning(self.__outOfSyncError.__str__())

                # Yield exception if needed
                if self.yieldOutOfSyncError:
                    yield self.__outOfSyncError

                continue

            # Check address if required
            if self._addrFieldLen > 0:
                addr = header['addr']
                if addr != self.addrSrc:
                    # Frame is not meant for this node so flush it
                    self.msgBuffer = self.msgBuffer[totFrameLen:]

                    # Yield exception
                    err = OtherRecipientReroNotification(addr, self.addrSrc)
                    self.logger.info(err.__str__())
                    if self.yieldOtherRecipientNotification:
                        yield err

                    # Start again
                    continue

            # Check CRC if required
            if self.crc:
                cobsCode = header['cobsCode']

                idxStart = self._frameFieldLen + 1 + self._addrFieldLen + frameLen + self._lenFieldChecksum

                crcValRcd, _ = self._decode_COBS_tiny(self.msgBuffer[idxStart:(idxStart + self.crc.digest_size)],
                                                      cobsCode)

                # Address field is also CRC covered
                idxStart = self._frameFieldLen + 1 + self._lenFieldChecksum + self._addrFieldLen

                msgEncRcd = self.msgBuffer[(idxStart):(idxStart + frameLen)]

                if self._addrFieldLen > 0:
                    msgEncRcd = header['addr'].to_bytes(self._addrFieldLen, byteorder='big') + msgEncRcd

                crcGen = self.crc.new()
                crcGen.update(msgEncRcd)
                crcValCheck = crcGen.digest()

                if crcValCheck != crcValRcd:

                    crcErr = CRCReroError(crcValCheck, crcValRcd,
                                          self.msgBuffer[idxStart + self._addrFieldLen + frameLen +
                                                         self.crc.digest_size + 1:])
                    # Flush buffer
                    self.msgBuffer = self.msgBuffer[totFrameLen:]

                    # Yield exception if required
                    self.logger.info(crcErr.__str__())
                    if self.yieldCRCError:
                        yield crcErr
                    continue

            # Decode message
            idxStart = self._frameFieldLen + 1 + self._addrFieldLen + self._lenFieldChecksum

            payloadEnc = self.msgBuffer[idxStart:(idxStart + frameLen)]
            payloadRcd = cobsr.decode(payloadEnc)

            # Cleanup buffer
            self.msgBuffer = self.msgBuffer[totFrameLen:]

            self.logger.debug(
                "Frame unpacked - payload length: {:d} bytes - frame length: {:d} bytes".format(len(payloadRcd),
                                                                                                totFrameLen))

            yield payloadRcd

    def _decode_header(self, msgRcd: bytes) -> Dict:

        """
        This is a tiny version of COBS meant to be used to decode the frame header of a received or partly received
        frame. It decodes the frame length field and the address field if defined and if enough bytes are received.
        Since the length of the header is <254 the decoding process is easier since no stuffing bytes must be handled.
        In case a CRC was defined also the COBS code required to decode the CRC is returned.

        Parameters
        ----------
        msgRcd : bytes
            Received frame or part of frame.

        Returns
        -------
        Dict
            Dictionary holding (frameLen, addr, cobsCode) if enough bytes are received. In case no address
            field was defined, only frameLen is returned. If not sufficient bytes are received an empty
            dictionary is returned.

        """

        # Check if sufficient bytes are received
        nBytesHeader = self._addrFieldLen + self._frameFieldLen + 1

        if self._lenFieldChecksum:
            nBytesHeader = nBytesHeader + 1

        # Rebuild first COBS code
        firstCobsCode = ((msgRcd[0] & (0xff << (8 - self.__nBitsCobsCode0))) >> (8 - self.__nBitsCobsCode0))

        # Rebuild first management byte
        firstFrameLenByte = bytes([msgRcd[0] & (0xff >> self.__nBitsCobsCode0)])

        # Decode
        msg, cobsCode = self._decode_COBS_tiny(firstFrameLenByte + msgRcd[1:nBytesHeader], firstCobsCode)

        # Setup a dictionary for return
        ret = {'cobsCode': cobsCode}

        # Rebuild length field
        frameLen = 0
        for cnt in range(self._frameFieldLen + 1):
            frameLen = frameLen + (msg[cnt] << 8 * (self._frameFieldLen - cnt))

        ret['frameLen'] = frameLen

        # Get length field checksum if required
        if self._lenFieldChecksum > 0:
            ret['frameLenCheckSum'] = msg[self._frameFieldLen + 1]

        # Rebuild address if required
        if self._addrFieldLen > 0:
            addr = 0
            off = self._frameFieldLen + 1 + self._lenFieldChecksum

            for cnt in range(self._addrFieldLen):
                addr = addr + (msg[cnt + off] << 8 * (self._addrFieldLen - cnt - 1))

            ret['addr'] = addr

        return ret

    def _decode_COBS_tiny(self, msg: bytes, firstCobsCode: int) -> (bytes, int):

        """
        This is a tiny version of COBS meant to be used to decode messages shorter than 254. It is intended to be used
        to decode the frame header and the frame CRC.

        Parameters
        ----------
        msg : bytes
            Received frame or part of frame, where the first COBS code (first byte) of the original encoded message is
            not contained. Also the delimiter byte 0x00 is not contained.
        firstCobsCode : int
            First COBS code of msg.

        Returns
        -------
        (msgDecoded, lastCobsCode) : (bytes, int)
            Decoded frame (bytes) and last COBS code (int) for later use.

        """

        if firstCobsCode > len(msg):
            return msg, firstCobsCode - len(msg)
        else:
            msg = bytearray(msg)

            idx = firstCobsCode - 1

            while idx < len(msg):
                cobsCode = msg[idx]
                idxLast = idx
                msg[idx] = 0
                idx = idx + cobsCode

            return bytes(msg), cobsCode - (len(msg) - idxLast - 1)

    def _carry_around_add(self, a: int, b: int) -> int:
        """
        Add with carry around.

        Parameters
        ----------
        a : int
            First number.
        b : int
            Second number.

        Returns
        -------
        int
            (c & 0xff) + (c >> 8)

        """
        c = a + b
        return (c & 0xff) + (c >> 8)

    def _ones_comp_checksum(self, msg: bytes) -> bytes:
        """
        Computes a 8 bit long ones complement.

        Parameters
        ----------
        msg : bytes
            Bytes from which ones complement checksum should be computed.

        Returns
        -------
        bytes
            Ones complement of msg.

        """
        s = 0
        for w in msg:
            s = self._carry_around_add(s, w)
        return (~s & 0xff).to_bytes(1, 'big')

    def add_logger_handler(self, logHandler: logging.Handler):

        """
        Add logging handler to logger.

        Parameters
        ----------
        logHandler : logging.Handler
            Logging handler. See logging package for more information.

        """
        # Conduct assertions
        assert isinstance(logHandler, logging.Handler)

        # Remove NullHandler if present
        for h in self.logger.handlers:
            if isinstance(h, logging.NullHandler):
                self.logger.removeHandler(h)

        self.logger.addHandler(logHandler)

    def remove_logger_handler(self, logHandler: logging.Handler):

        """
        Remove logging handler from logger. If no handlers remain, a NullHandler is added.

        Parameters
        ----------
        logHandler : logging.Handler
            Logging handler. See logging package for more information.

        """
        # Conduct assertions
        assert isinstance(logHandler, logging.Handler)

        self.logger.removeHandler(logHandler)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.NullHandler())
