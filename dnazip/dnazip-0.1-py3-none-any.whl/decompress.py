import math # needed for rounding up amount of bases in bytes
import sys
import itertools

def makeListOfBaseOptions():
    bases = 'ACTG'
    products = list(itertools.product(bases, repeat=4)) # https://docs.python.org/3/library/itertools.html#itertools.product
    baseOptions = []
    for baseProduct in products:
        baseOptions.append(''.join(baseProduct)) # ['AAAA', 'AAAC' etc.
    return baseOptions

baseOptions = makeListOfBaseOptions()

def decompressDNA(dnaBytes, amountOfBases, outputFile, basesInLine = 80):
    dnaSeq = ''
    for byte in dnaBytes: # byte is actually 8-bit integer (0 - 255) in a for loop
        dnaSeq += baseOptions[byte]
    
    # Fix padding needed for full bytes
    lastChunkLen = amountOfBases % 4 # 0 if it's a full byte
    if lastChunkLen != 0: # Only remove padding if there is padding
        print(lastChunkLen)
        dnaSeq = dnaSeq[:(4 - lastChunkLen) * -1] # Remove padding

    # Write to file
    for i in range(0, len(dnaSeq), basesInLine): # every n char write \n
        line = dnaSeq[i:i+basesInLine]
        outputFile.write(line + '\n')
    

def decompress(inputFile, outputFile, lineLength = 60):
    header = inputFile.readline().decode('utf-8')
    if header != 'dnazip file; v0.1; https://github.com/Bartvelp/dnazip\n':
        raise ValueError('Invalid dnazip file provided') # Raise errors for non dnazip file

    for line in inputFile:
        # The random DNA byts are always fully read so the pointer in the filehandle is always moved forward to either
        # a new FASTA header or to another 'DNAZIP START', meaning the next bytes python reads are handled as a new line, even though
        # no newline character is present before them. That is why .startswith works
        if line.decode('utf-8').startswith('DNAZIP START'): # It's a start line, read the next x bytes
            amountOfBases = int(line[14:-1]) # Remove 'DNAZIP START: ' and trailing newline
            amountOfBytes = math.ceil(amountOfBases / 4) # end is padded (with zero's)
            dnaBytes = inputFile.read(amountOfBytes) # read the DNA bytes here, also moves forward the pointer
            decompressDNA(dnaBytes, amountOfBases, outputFile, lineLength) # parse the bits and write to output file
        else: # it's likely a header line, just copy it to the output file
            outputFile.write(line.decode('utf-8'))

if __name__ == "__main__": # execute if not included and is main script
    inputF = open('{}.dnazip'.format(sys.argv[1]), 'rb')
    outputF = open('{}.out.fa'.format(sys.argv[1]), 'w')

    decompress(inputF, outputF)
    print('Done decompressing')
    inputF.close()
    outputF.close()