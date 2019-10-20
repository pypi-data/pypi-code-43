"""
Copyright 2019 Julian Metzler

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import serial


class KroneFBKController:
    """
    Controls a FBK (Fallblatt-Buskopfkarte)
    (split-flap bus head module) board.
    """
    
    CTRL_READ = 0x81
    CTRL_WRITE_SINGLE_ACK = 0x82
    CTRL_WRITE_SINGLE_NOACK = 0x02
    CTRL_WRITE_BLOCK_ACK = 0x84
    CTRL_WRITE_BLOCK_NOACK = 0x04

    def __init__(self, port, debug = False):
        self.debug = debug
        self.port = serial.Serial(port, baudrate=19200, timeout=1.0)
        
    def send_command(self, address, control, command, block = 0x01, parameters = None, num_response_bytes = 0):
        data = [command]
        
        if parameters is not None:
            if type(parameters) not in (list, tuple):
                parameters = [parameters]
            data += parameters
        
        payload = [0xB2, address, 0x00, control, block] + data + [0x00]
        length = len(payload)
        payload[2] = length
        
        checksum = 0x00
        for byte in payload:
            checksum ^= byte
        
        cmd_bytes = [0xFF, 0xFF] + payload + [checksum]
        
        if self.debug:
            print(" ".join((format(x, "02X") for x in cmd_bytes)))
        
        # Send it
        self.port.write(bytearray(cmd_bytes))

        # Read response
        if num_response_bytes > 0:
            return self.port.read(num_response_bytes)
        else:
            return None
    
    def send_heartbeat(self, address):
        cmd_bytes = [0xFF, 0xFF, 0xB2, address, 0x00]
        if self.debug:
            print(" ".join((format(x, "02X") for x in cmd_bytes)))
        self.port.write(bytearray(cmd_bytes))
