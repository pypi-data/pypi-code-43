"""
Shared protocol tokens
"""

from __future__ import annotations


class AsciiToken:
    STX = '\x02'  # Start of text
    ETX = '\x03'  # End of text
    EOT = '\x04'  # End of transmission
    ENQ = '\x05'  # Enquiry
    ACK = '\x06'  # Acknowledge
    LF = '\x0A'  # Line feed
    CR = '\x0D'  # Carriage return
    NAK = '\x15'  # Negative acknowledge
    ETB = '\x17'  # End of transmission block
    CAN = '\x18'  # Cancel
    CRLF = '\r\n'  # <CR><LF>
