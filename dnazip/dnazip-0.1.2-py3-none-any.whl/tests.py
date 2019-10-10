import compress # pylint: disable=import-error
import decompress # pylint: disable=import-error
import unittest
from io import StringIO # https://stackoverflow.com/a/3945057
from io import BytesIO
import itertools

def makeListOfBaseOptions():
    bases = 'ACTG'
    products = list(itertools.product(bases, repeat=4)) # https://docs.python.org/3/library/itertools.html#itertools.product
    baseOptions = []
    for baseProduct in products:
        baseOptions.append(''.join(baseProduct)) # ['AAAA', 'AAAC' etc.
    return baseOptions

baseOptions = makeListOfBaseOptions()

# First test all functions from compress
class TestCompress(unittest.TestCase): # https://realpython.com/python-testing/
    def test_bases2bits(self):
        bases = 'ACTG'
        output = compress.basesToBits(bases)
        self.assertEqual(output, '00011011', 'Should be 00011011')

    def test_compressDNA(self):
        dnaSeq = 'AACCTTGGAACCTTGGTTT'
        byteBuffer = BytesIO() # Init a byte buffer to write to
        compress.compressDNA(dnaSeq, byteBuffer) # write to it
        byteBuffer.seek(0) # Reset the pointer
        header = byteBuffer.readline()
        headerParts = header.decode().split(':')
        self.assertEqual(headerParts[0], 'DNAZIP START')
        body = byteBuffer.read() # Read the rest, with the bases data
        decompressedOutput = ''
        for byte in body:
            decompressedOutput += baseOptions[byte] # Same as in decompress.py
        self.assertEqual(decompressedOutput, 'AACCTTGGAACCTTGGTTTA', 'Should be padded with A')
        
    def test_compress(self):
        stringBuffer = StringIO()
        stringBuffer.write('>Test \nAACCTGACT\n>Test2 \nAACCTGAA') # Sample multifasta
        byteBuffer = BytesIO() # Init a byte buffer to write to
        compress.compress(stringBuffer, byteBuffer)
        byteBuffer.seek(0) # Reset the pointer
        header = byteBuffer.readline().decode()
        headerParts = header.split(';')
        self.assertEqual(headerParts[0], 'dnazip file', 'Should be dnazip file')
        self.assertEqual(headerParts[2].strip(), 'https://github.com/Bartvelp/dnazip', 'Should contain project link')
        # Only check header here

# Just check both the compression and decompression in 1 go
class TestBoth(unittest.TestCase):
    def test_compressAndDecompress(self):
        inputBuffer = StringIO()
        outputBuffer = StringIO()
        multiFastaData = '>Test \nAACCTGACT\n>Test2 \nAACCTGAA'
        inputBuffer.write(multiFastaData) # Sample multifasta
        inputBuffer.seek(0)
        byteBuffer = BytesIO() # Init a byte buffer to write to
        compress.compress(inputBuffer, byteBuffer) # Compress to bytebuffer
        byteBuffer.seek(0) # Reset the pointer
        decompress.decompress(byteBuffer, outputBuffer) # Decompress from bytebuffer
        outputBuffer.seek(0)
        body = outputBuffer.read()
        self.assertEqual(body.strip(), multiFastaData.strip(), 'Full cycle should be lossless') # Newlines can be added in decompression


if __name__ == '__main__':
    unittest.main()
