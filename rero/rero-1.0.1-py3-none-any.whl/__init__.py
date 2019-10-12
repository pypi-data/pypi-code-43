"""Rero is a communication protocol intended for transmissions of byte frames over e.g. a serial interface or
buses. It builds upon [COBS](https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing) which allows for a
minimum encoding overhead. It is perfectly suited for MCUs with DMA support.

Example usage:

```Python
import rero
import logging

# Setup logging
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# Setup rero
reroPacker = rero.Packer(1, 10, logHandler=ch)

# Dummy payload
payload = bytes([1, 2, 3, 4])

msgToSend = b''     # dummy init to prevent pycharm from complaining
try:
    msgToSend = reroPacker.pack(payload, 20) # Packing with dedicated address
    # msgToSend = reroPacker.pack(payload)   # Sending with default address
    print(msgToSend)
except rero.PayloadOverlengthReroError as e:
    print(e)
except rero.NoDestinationAddressReroError as e:
    print(e)

# Unpack received message - it is assumed a complete frame was received including EOF delimiter (0x00)
for payloadRcd in reroPacker.unpack(msgToSend):
    print(payloadRcd)
```

For further information read the docs.

"""

from rero.packer import *
