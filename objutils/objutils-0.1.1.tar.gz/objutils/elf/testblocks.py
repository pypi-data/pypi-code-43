
import unittest

from construct import Struct
from objutils.dwarf.encoding import Block1, Block2l, Block2b, Block4l, Block4b, BlockUleb, Address


ap = Address(4, 0)
print(ap.build(0x4711))


class TestBlocks(unittest.TestCase):

  def testBlock1Parse(self):
    self.assertEqual(Block1.parse(b'\x05hello'), b"hello")
    
  def testBlock2lParse(self):  
    self.assertEqual(Block2l.parse(b'\x05\x00world'), b"world")
    
  def testBlock2bParse(self):
    self.assertEqual(Block2b.parse(b'\x00\x05world'), b"world")
    
  def testBlock4lParse(self):  
    self.assertEqual(Block4l.parse(b'\x05\x00\x00\x00world'), b"world")
    
  def testBlock4bParse(self):
    self.assertEqual(Block4b.parse(b'\x00\x00\x00\x05world'), b"world")    


if __name__ == "__main__":
  unittest.main()