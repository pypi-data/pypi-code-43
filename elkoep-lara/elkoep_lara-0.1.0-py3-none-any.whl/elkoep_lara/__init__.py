#!/usr/bin/python

from random import randrange
import socket
import struct
import logging

#_LOGGER = logging.getLogger(__name__)

name = "elkoep_lara"

class LARA_ERRORS:
  OK = 0
  OPERATION_FAILED = 1
  INVALID_USERPASS = 2
  UNSUPPORTED_VERSION = 3

class LARA_COMMANDS:
  WAKE_UP = 1
  SLEEP = 2
  PLAY = 3
  STOP = 4
  VOLUME = 5
  VOLUME_UP = 6
  VOLUME_DOWN = 7
  MUTE = 9
  NEXT = 10
  PREVIOUS = 11
  SOURCE = 12
  SELECT_STATION = 14
  #DISPLAY_ON_OFF = 14
  BELL = 16

class LARA_SOURCES:
  RADIO = 0
  AUX_IN = 2
  DLNA = 5

class LARA_SELECT_SOURCE:
  RADIO = 1
  AUX_IN = 3
  DLNA = 4

XOR_mask = bytearray([47, 216, 111, 158, 83, 102, 230, 17, 127, 118, 199, 204, 16, 122, 65, 132, 108, 202, 202, 60,
    118, 187, 254, 10, 247, 50, 57, 170, 64, 3, 130, 64, 181, 79, 48, 196, 45, 250, 117, 158, 246,
    107, 62, 244, 197, 55, 221, 98, 243, 10, 12, 15, 202, 74, 55, 114, 216, 101, 165, 32, 44, 60,
    208, 124, 243, 135, 23, 191, 74, 124, 87, 113, 85, 43, 69, 11, 125, 10, 67, 191, 83, 213, 182,
    53, 246, 114, 116, 106, 24, 188, 234, 198, 84, 84, 114, 186, 153, 193, 0, 62, 32, 29, 24, 119,
    178, 153, 185, 158, 5, 43, 244, 205, 34, 228, 203, 85, 133, 154, 133, 128, 18, 171, 166, 140,
    145, 143, 28, 0, 183, 137, 112, 187, 10, 4, 159, 53, 189, 62, 129, 92, 184, 212, 100, 236, 198,
    28, 163, 110, 135, 29, 53, 254, 60, 127, 44, 115, 117, 139, 229, 34, 125, 184, 230, 123, 185,
    57, 195, 30, 69, 150, 151, 70, 24, 40, 199, 60, 70, 185, 196, 116, 234, 172, 120, 154, 84, 113,
    126, 137, 215, 43, 191, 50, 88, 95, 221, 0, 237, 232, 50, 141, 87, 133, 41, 240, 133, 238, 229,
    19, 183, 238, 45, 187, 197, 112, 54, 207, 63, 75, 38, 71, 185, 58, 70, 25, 213, 101, 236, 184,
    74, 198, 77, 93, 134, 55, 28, 101, 131, 134, 21, 101, 139, 107, 209, 231, 253, 3, 107, 231, 40,
    14, 191, 162, 194, 234, 210, 29, 63, 16, 26, 32, 1, 44, 200, 239, 160, 206, 52, 141, 83, 208,
    76, 183, 54, 191, 187, 77, 103, 93, 26, 210, 248, 5, 144, 59, 7, 170, 153, 155, 99, 254, 37,
    115, 108, 243, 99, 94, 162, 225, 70, 46, 206, 221, 147, 86, 193, 7, 107, 2, 47, 132, 181, 224,
    244, 71, 39, 251, 155, 140, 232, 245, 52, 152, 41, 84, 170, 216, 75, 65, 91, 92, 170, 133, 23,
    234, 3, 26, 112, 57, 121, 254, 63, 151, 108, 222, 73, 68, 125, 36, 204, 103, 194, 21, 247, 80,
    248, 54, 179, 63, 171, 232, 186, 41, 165, 209, 217, 47, 201, 9, 67, 12, 139, 97, 19, 232, 182,
    156, 43, 74, 10, 102, 90, 39, 115, 243, 153, 149, 140, 198, 240, 204, 101, 48, 141, 143, 67,
    21, 241, 153, 4, 25, 122, 116, 223, 192, 218, 96, 2, 15, 152, 92, 10, 105, 52, 68, 141, 147,
    180, 176, 56, 67, 162, 2, 23, 118, 165, 90, 211, 130, 165, 160, 170, 145, 69, 240, 235, 229,
    70, 178, 25, 56, 146, 125, 45, 148, 194, 251, 251, 72, 2, 174, 95, 64, 97, 191, 117, 119, 92,
    105, 26, 128, 140, 126, 104, 247, 177, 119, 35, 67, 88, 167, 77, 2, 151, 0, 176, 37, 212, 130,
    178, 169, 94, 139, 128, 245, 65, 105, 47, 132, 122, 116, 137, 219, 151, 151, 171, 20, 20, 53,
    226, 74, 215, 184, 238, 89, 97, 93, 168, 97, 15, 80, 161, 217, 182, 112, 34, 1, 253, 113, 181,
    71, 71, 158, 199, 227, 30, 112, 105, 254, 84, 155, 16, 159, 158, 103, 208, 164, 155, 38, 148,
    227, 192, 205, 116, 42, 209, 174, 37, 39, 117, 169, 21, 161, 126, 154, 2, 56, 239, 11, 58, 240,
    242, 168, 12, 115, 63, 2, 58, 78, 158, 124, 100, 214, 220, 209, 133, 121, 41, 156, 18, 110, 75,
    66, 137, 169, 133, 110, 32, 3, 100, 151, 180, 144, 235, 162, 239, 24, 193, 1, 234, 206, 116,
    213, 135, 248, 68, 62, 195, 171, 21, 136, 15, 83, 247, 203, 165, 175, 30, 98, 236, 208, 224,
    54, 233, 6, 199, 211, 234, 58, 225, 109, 183, 40, 177, 66, 248, 116, 186, 144, 100, 71, 169,
    116, 237, 219, 136, 96, 151, 31, 252, 64, 249, 94, 20, 26, 237, 62, 235, 128, 48, 112, 83, 137,
    201, 167, 208, 229, 160, 181, 209, 48, 244, 141, 253, 164, 38, 108, 71, 14, 124, 102, 60, 202,
    60, 161, 114, 88, 19, 151, 84, 186, 136, 57, 95, 243, 243, 31, 169, 70, 10, 161, 191, 224, 77,
    204, 74, 107, 96, 110, 242, 128, 246, 221, 4, 201, 51, 135, 77, 40, 52, 120, 210, 9, 97, 23,
    167, 187, 45, 10, 176, 6, 193, 0, 3, 217, 166, 90, 125, 111, 86, 7, 247, 164, 163, 210, 195,
    169, 52, 149, 191, 107, 209, 129, 18, 145, 206, 181, 126, 54, 36, 142, 62, 86, 189, 235, 189,
    245, 217, 41, 35, 216, 10, 221, 208, 45, 127, 45, 101, 142, 83, 252, 134, 151, 74, 68, 52, 64,
    237, 113, 11, 239, 219, 70, 74, 199, 199, 161, 229, 182, 21, 204, 207, 11, 114, 229, 97, 243,
    176, 227, 17, 161, 80, 239, 226, 39, 8, 165, 11, 121, 183, 125, 7, 104, 30, 50, 251, 194, 146,
    9, 100, 221, 70, 173, 121, 133, 45, 122, 37, 99, 226, 64, 143, 9, 95, 105, 159, 234, 99, 35,
    191, 33, 149, 108, 254, 150, 197, 103, 236, 64, 233, 157, 96, 166, 127, 51, 90, 161, 118, 92,
    249, 140, 128, 167, 150, 118, 236, 252, 8, 180, 145, 17, 95, 111, 73, 66, 71, 217, 174, 225,
    191, 196, 140, 228, 121, 68, 222, 231, 137, 44, 14, 253, 116, 6, 41, 50, 160, 236, 213, 136,
    169, 199, 94, 56, 173, 215, 62, 240, 93, 60, 234, 128, 242, 148, 156, 52, 254, 155, 46, 81,
    150, 5, 115, 218, 165, 146, 155, 88, 69, 22, 161, 89, 3, 37, 56, 246, 102, 84, 54, 160, 6,
    237, 137, 76, 64, 141, 11, 223, 105, 243, 50, 4, 190, 132, 240, 163, 84, 130, 146, 27, 59,
    228, 170, 71, 154, 144, 124, 204, 92, 165, 205, 170, 101, 141, 75, 168, 122, 38, 154, 23, 135,
    187, 238, 80, 226, 156, 154, 126, 52, 147, 161, 226, 193, 26, 100, 32, 66, 66, 177, 174, 17,
    61, 130, 194, 38, 135, 158, 49, 56, 72, 41, 46, 231, 122, 146, 127])


class LaraClient:
  def __init__(self, host, name=None, user=None, password=None):
    if (user == None) or (len(user) == 0):
        user = "admin"
    self._user = user
    if (password == None) or (len(password) == 0):
        password = "elkoep"
    self._password = password
    if (host == None) or (len(host) == 0):
        host = '192.168.1.1'
    self._host = host
    self._stations_count = 0
    self._stations = ['']*40
    self._current_station = 0
    self._current_source = 0
    self._volume = 0
    self._playing = False
    self._name = name
    self._FWver = 0
    self._initialized = False

  @property
  def FWver(self):
    if not self._initialized:
        return 0
    return self._FWver

  @property
  def stations(self):
    if not self._initialized:
        return ['']
    return self._stations[:self._stations_count]

  @property
  def volume_level(self):
    if not self._initialized:
        return 0
    return self._volume / 100.0

  @property
  def playing(self):
    if not self._initialized:
        return False
    return self._playing

  @property
  def station(self):
    if not self._initialized:
        return ''
    return self._stations[self._current_station]

  @property
  def initialized(self):
    return self._initialized


  def volume_mute(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.MUTE)

  def volume_up(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.VOLUME_UP)

  def volume_down(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.VOLUME_DOWN)

  def volume_set(self, volume):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    if int(volume) > 100:
        volume = 100
    elif int(volume) < 0:
        volume = 0
    return self.SendRemoteControllPacket(LARA_COMMANDS.VOLUME, int(volume))

  def play(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.PLAY)

  def pause(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.STOP)

  def next(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    if (self._current_station + 1) < self._stations_count:
      self._current_station += 1
      return self.SendRemoteControllPacket(LARA_COMMANDS.NEXT)
    return LARA_ERRORS.OK

  def previous(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    if self._current_station > 0:
      self._current_station -= 1
      return self.SendRemoteControllPacket(LARA_COMMANDS.PREVIOUS)
    return LARA_ERRORS.OK

  def select_source(self, source):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    return self.SendRemoteControllPacket(LARA_COMMANDS.SOURCE, source)

  def select_station(self, station):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    if station >= self._stations_count:
        station = self._stations_count-1
    self._current_station = station
    return self.SendRemoteControllPacket(LARA_COMMANDS.SELECT_STATION, station)


  def code(self, data, datalen):
    num = randrange(700)
    num2 = num
    for i in range(datalen):
      if num2 >= 1024:
        num2 = 0
      data[i] ^= XOR_mask[num2]
      num2 += 1
    data[datalen] = num >> 8
    data[datalen+1] = (num & 0xff)
    return data

  def decode(self, data, datalen):
    num = struct.unpack('>1h', data[datalen-2: ])[0]
    for i in range(datalen-2):
      if num >= 1024:
        num = 0
      data[i] ^= XOR_mask[num]
      num += 1
    return data

  def init(self):
    self._initialized = False
    if (self.SendTestPacket() != LARA_ERRORS.OK):
      return LARA_ERRORS.OPERATION_FAILED
    if (self._FWver != 36003):
      return LARA_ERRORS.UNSUPPORTED_VERSION
    self._initialized = True
    self.select_source(LARA_SELECT_SOURCE.RADIO)
    if (self.SendLoadStatusPacket() != LARA_ERRORS.OK):
      self._FWver = 0
      self._initialized = False
      return LARA_ERRORS.OPERATION_FAILED
    if (self.SendLoadStationsPacket(0) != LARA_ERRORS.OK):
      self._FWver = 0
      self._initialized = False
      return LARA_ERRORS.OPERATION_FAILED
    if (self.SendLoadStationsPacket(1) != LARA_ERRORS.OK):
      self._FWver = 0
      self._initialized = False
      return LARA_ERRORS.OPERATION_FAILED
    if (self.SendLoadStationsPacket(2) != LARA_ERRORS.OK):
      self._FWver = 0
      self._initialized = False
      return LARA_ERRORS.OPERATION_FAILED
    if (self.SendLoadStationsPacket(3) != LARA_ERRORS.OK):
      self._FWver = 0
      self._initialized = False
      return LARA_ERRORS.OPERATION_FAILED
    return LARA_ERRORS.OK

  def SendRemoteControllPacket(self, command, attribute=0):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    array = bytearray(51)
    array[0] = 255
    array[1] = 250
    array[2] = 250
    array[3] = 255
    array[4] = randrange(255)
    array[5] = 1
    array[6] = 47
    array[7] = 129
    array[8] = 192
    array[9] = 0
    array[10] = 17
    b_user = bytearray(self._user, 'utf8')
    b_password = bytearray(self._password, 'utf8')
    pos = 0
    for b in b_user:
      array[11 + pos] = b
      pos += 1
    pos = 0
    for b in b_password:
      array[28 + pos] = b
      pos += 1
    array[45] = command
    array[46] = attribute
    c_array = self.code( array, len(array)-2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
      s.connect((self._host, 61695))
      s.settimeout(2)
      s.sendall(c_array)
      s.settimeout(2)
      data = s.recv(30)
    except socket.timeout:
      return LARA_ERRORS.OPERATION_FAILED
    finally:
      s.close()
    data = bytearray(data)
    data = self.decode( data, len(data))

    if data[0] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[1] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[2] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[3] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[7] != 0:
      return LARA_ERRORS.OPERATION_FAILED
    if data[8] != 193:
      return LARA_ERRORS.OPERATION_FAILED

    if data[9] == 1 and data[10] == 0:
      # Ok
      if command == 16:
        return LARA_ERRORS.OK
      if data[11] == 3:
        return LARA_ERRORS.OK
      #print("Station: %s" % (data[12]))
      return LARA_ERRORS.OK
    elif data[9] == 1 and data[10] == 1:
      # Incorrect username/password
      return LARA_ERRORS.INVALID_USERPASS
    else:
      # Somwthing went wrong
      return LARA_ERRORS.OPERATION_FAILED
    return LARA_ERRORS.OK

  def SendLoadStationsPacket(self, page):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    pagemap = {
      0: 6,
      1: 12,
      2: 13,
      3: 14
    }
    array = bytearray(47)
    array[0] = 255
    array[1] = 250
    array[2] = 250
    array[3] = 255
    array[4] = randrange(255)
    array[5] = 1
    array[6] = 45
    array[7] = 129
    array[8] = 192
    array[9] = pagemap.get(page, 0)
    array[10] = 17
    b_user = bytearray(self._user, 'utf8')
    b_password = bytearray(self._password, 'utf8')
    pos = 0
    for b in b_user:
      array[11 + pos] = b
      pos += 1
    pos = 0
    for b in b_password:
      array[28 + pos] = b
      pos += 1
    c_array = self.code( array, len(array)-2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
      s.connect((self._host, 61695))
      s.settimeout(2)
      s.sendall(c_array)
      s.settimeout(2)
      data = s.recv(2100)
    except socket.timeout:
      return LARA_ERRORS.OPERATION_FAILED
    finally:
      s.close()
    data = bytearray(data)
    data = self.decode( data, len(data))

    if data[0] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[1] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[2] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[3] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[7] != 0:
      return LARA_ERRORS.OPERATION_FAILED
    if data[8] != 193:
      return LARA_ERRORS.OPERATION_FAILED
    if data[9] != 7:
      return LARA_ERRORS.OPERATION_FAILED
    if data[10] != 0:
      return LARA_ERRORS.INVALID_USERPASS
    num = 139
    page = data[11]
    self._stations_count = data[12]
    for station in range(10):
      StatName = data[13+(station*num):26+(station*num)]
      self._stations[page*10 + station] = StatName.split(b'\0',1)[0].decode("utf-8")
    return LARA_ERRORS.OK

  def SendTestPacket(self):
    array = bytearray(11)
    array[0] = 255
    array[1] = 250
    array[2] = 250
    array[3] = 255
    array[4] = randrange(255)
    array[5] = 7
    array[6] = 9
    array[7] = 128
    array[8] = 0
    c_array = self.code( array, len(array)-2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
      s.connect((self._host, 61695))
      s.settimeout(2)
      s.sendall(c_array)
      s.settimeout(2)
      data = s.recv(30)
    except socket.timeout:
      return LARA_ERRORS.OPERATION_FAILED
    finally:
      s.close()
    data = bytearray(data)
    data = self.decode( data, len(data))

    if data[0] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[1] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[2] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[3] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[8] != 1:
      return LARA_ERRORS.OPERATION_FAILED
    if data[9] != 0:
      return LARA_ERRORS.OPERATION_FAILED
    if data[10] != 3:
      return LARA_ERRORS.OPERATION_FAILED

    self._FWver = data[11] * 65536 + data[12] * 256 + data[13]
    self._HWver = data[14]
    return LARA_ERRORS.OK

  def SendLoadStatusPacket(self):
    if not self._initialized:
      return LARA_ERRORS.UNSUPPORTED_VERSION
    array = bytearray(49)
    array[0] = 255
    array[1] = 250
    array[2] = 250
    array[3] = 255
    array[4] = randrange(255)
    array[5] = 7
    array[6] = 49
    array[7] = 129
    array[8] = 192
    array[9] = 0
    array[10] = 17
    b_user = bytearray(self._user, 'utf8')
    b_password = bytearray(self._password, 'utf8')
    pos = 0
    for b in b_user:
      array[11 + pos] = b
      pos += 1
    pos = 0
    for b in b_password:
      array[28 + pos] = b
      pos += 1
    c_array = self.code( array, len(array)-2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
      s.connect((self._host, 61695))
      s.settimeout(2)
      s.sendall(c_array)
      s.settimeout(2)
      data = s.recv(19)
    except socket.timeout:
      return LARA_ERRORS.OPERATION_FAILED
    finally:
      s.close()
    data = bytearray(data)
    if len(data) < 19:
      return LARA_ERRORS.OPERATION_FAILED
    data = self.decode( data, len(data))

    if data[0] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[1] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[2] != 250:
      return LARA_ERRORS.OPERATION_FAILED
    if data[3] != 255:
      return LARA_ERRORS.OPERATION_FAILED
    if data[7] != 0:
      return LARA_ERRORS.OPERATION_FAILED
    if data[8] != 193:
      return LARA_ERRORS.OPERATION_FAILED
    if data[9] != 1:
      return LARA_ERRORS.OPERATION_FAILED
    if data[10] != 0:
      return LARA_ERRORS.INVALID_USERPASS

    self._current_source = data[11]
    self._current_station = data[12]
    self._volume = data[13]
    if data[15] == 0:
      self._playing = False
    else:
      self._playing = True
#    print(''.join(format(x, '02x') for x in data))
    return LARA_ERRORS.OK

#if __name__ == '__main__':
#  data = "\xf4\xc0\x0a\x0d\x98\x29\x42\xbe\xc2\x3a\x5f\xff\x18\x09\xbf\xb2" \
#"\xd1\x85\x79\x29\x9c\x12\x6e\x4b\x42\x89\xa9\x85\x0b\x4c\x68\x0b" \
#"\xf2\xc4\x90\xeb\xa2\xef\x18\xc1\x01\xea\xce\x74\xd5\x82\xf2\x44" \
#"\x02\x2d"





#  data = bytearray(data)
#  client_1 = LaraClient('192.168.88.202')
#  data = client_1.decode(data, len(data))
#  print(data)
#  print(''.join(format(x, '02x') for x in data))

#  client_1.init()

#  print("Before")
#  print(client_1.SendLoadStatusPacket())
#  client_1.select_station(3)
#  client_1.SendLoadStatusPacket()
#  print(client_1.stations)

  #print(SendLoadConfigPacket())



# Lara off:
# fffafaff3c7ab100c10300b68d61646d696e000000000000000000000000656c6b6f657000000000000000000000007573657200000000000000000000000000656c6b6f65700000000000000000000000c0a858cbffffff00c0a85804f0ff0200c0a802504d61696e00000000000000000000000000c37190c904c0a858040001321e0300000000000000000000000000000000000000000000000000000000000000000000684d6564696153657276650218
# fffafaff3d7cb100c10300b68d61646d696e000000000000000000000000656c6b6f657000000000000000000000007573657200000000000000000000000000656c6b6f65700000000000000000000000c0a858cbffffff00c0a85804f0ff0200c0a802504d61696e00000000000000000000000000c37190c904c0a858040001321e0300000000000000000000000000000000000000000000000000000000000000000000684d6564696153657276650041
# Lara on:
# Lara volume upped
# fffafaff3e7eb100c10300b68d61646d696e000000000000000000000000656c6b6f657000000000000000000000007573657200000000000000000000000000656c6b6f65700000000000000000000000c0a858cbffffff00c0a85804f0ff0200c0a802504d61696e00000000000000000000000000c37190c904c0a858040001321e0300000000000000000000000000000000000000000000000000000000000000000000684d656469615365727665006f
# Volume 0
# fffafaff3f80b100c10300b68d61646d696e000000000000000000000000656c6b6f657000000000000000000000007573657200000000000000000000000000656c6b6f65700000000000000000000000c0a858cbffffff00c0a85804f0ff0200c0a802504d61696e00000000000000000000000000c37190c904c0a858040001321e0300000000000000000000000000000000000000000000000000000000000000000000684d656469615365727665014f
# Another station
# fffafaff4082b100c10300b68d61646d696e000000000000000000000000656c6b6f657000000000000000000000007573657200000000000000000000000000656c6b6f65700000000000000000000000c0a858cbffffff00c0a85804f0ff0200c0a802504d61696e00000000000000000000000000c37190c904c0a858040001321e0300000000000000000000000000000000000000000000000000000000000000000000684d6564696153657276650145
