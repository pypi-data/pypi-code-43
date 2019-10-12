# Setup error classes of Packer
class ReroError(Exception):
    """Base class for exceptions in this module.

    """
    pass


class PayloadOverlengthReroError(ReroError):
    """Exception raised by pack() method if length of payload is bigger than maximum payload length.

    """

    def __init__(self, payloadLen, payloadLenMax):
        """

        Parameters
        ----------
        payloadLen : int
            Length of given payload.
        payloadLenMax : int
            Maximum possible payload length.
        """
        self.payloadLen = payloadLen
        self.payloadLenMax = payloadLenMax
        super().__init__("Payload length too long: {:d} > {:d}".format(self.payloadLen, self.payloadLenMax))


class OutOfSyncReroError(ReroError):
    """Exception raised by unpack() method if delimiter byte 0x00 was not at position defined by length field. In
    this case resynchronize by scanning for a 0x00 delimiter byte is necessary. After finding one we are
    resynchronized.

    """

    def __init__(self):
        super().__init__("Out of synchronisation")


class CRCReroError(ReroError):
    """Exception raised by unpack() method if CRC check failed.

    """

    def __init__(self, crcFrame: bytes, crcRcd: bytes, msg: str):
        """

        Parameters
        ----------
        crcFrame : bytes
            The received frame to be CRC tested.
        crcRcd : bytes
            The received CRC code.
        msg : str
            The message string.
        """
        super().__init__(
            "CRC check failed! CRC of frame: 0x{:x}, CRC received: 0x{:x}".format(int.from_bytes(crcFrame, 'big'),
                                                                                  int.from_bytes(crcRcd, 'big')))
        self.crcFrame = crcFrame
        self.crcRcd = crcRcd
        self.msg = msg


class NoDestinationAddressReroError(ReroError):
    """Exception raised by pack() method if no destination address and no default destination address is given."""

    def __init__(self):
        super().__init__("No destination or default destination address defined")


class OtherRecipientReroNotification(ReroError):
    """Exception raised by unpack() method if address of received frame differs from source address."""

    def __init__(self, addrFrame: int, addrSrc: int):
        """

        Parameters
        ----------
        addrFrame : int
            Address to which frame was sent to.
        addrSrc : int
            Address of this node.
        """
        self.addrFrame = addrFrame
        self.addrSrc = addrSrc
        super().__init__("Received frame sent to node: {:d} (this node: {:d})".format(self.addrFrame, self.addrSrc))


class TimeoutReroError(ReroError, TimeoutError):
    """Exception raised by unpack() method if partly received frame was not received in time."""

    def __init__(self):
        super().__init__("Timeout: Partly received frame not received frame not received in time!")
