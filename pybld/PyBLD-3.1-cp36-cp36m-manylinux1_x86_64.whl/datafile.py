# $Id: datafile.py,v 9050d96e5f31 2016/09/11 03:30:50 watabe $

# Written by Michael Haggerty <mhagger@blizzard.harvard.edu>

# Read text data files (of columnar data) into an array.

import re
import numpy
import sys


class DataFormat(Exception):
    pass


class datafile:
    mantissa_re = re.compile(r"[\+\-]?(?:\d+\.\d*|\d+|\.\d+)")
    float_re = re.compile(mantissa_re.pattern + r"(?:[eE][\+\-]?\d+)?")
    columns_re = re.compile(r"^Columns\:\s*(.*)$")
    parmline_re = re.compile(r"^(\w+)\s*=\s*(" +
                             float_re.pattern +
                             r")(\s+(.*))?$")
    dataline_re = re.compile(r"^" +
                             float_re.pattern +
                             r"(\s+" +
                             float_re.pattern +
                             r")*$")
    binstart_re = re.compile(r"^binary_start\("
                             r"\s*(\w)\s*\,"
                             r"\s*(\d+)\s*\,"
                             r"\s*(\d+)\s*\,"
                             r"\s*(\d+)\s*\)$")
    binend_re = re.compile(r"^binary_end\(\)$")

    # f can be a filename (string) or a file-like object.
    def __init__(self, f=None):
        self.colnames = [] # column names, in order, as strings
        self.colnums = {} # numbered starting with 0
        self.data = None # array to store data
        self.comments = [] # full-line comment lines, saved literally
        self.parms = {} # parameters from the header of the file
        self.gaps = [] # data row numbers that are preceded by blank lines
        self.filename = None # the filename associated with the data

        if f is not None:
            self.read(f)

    # Add comment c for file (initial '#' and whitespace should
    # already be deleted).  If c is a column line, set up
    # self.colnames and self.colnums.  If c is a parm line, adjust
    # self.parms.  Otherwise, append the comment to self.comments.
    def add_comment(self, c):
        m = self.columns_re.match(c)
        if m:
            newcolnames = (m.group(1)).split()
            if self.colnames:
                assert newcolnames == self.colnames
            else:
                self.colnames = newcolnames
                for i in range(len(self.colnames)):
                    self.colnums[self.colnames[i]] = i
                if self.data is not None:
                    assert len(self.colnames) == self.data.shape[1]
            return
        m = self.parmline_re.match(c)
        if m:
            if self.parms.has_key(m.group(1)):
                assert self.parms[m.group(1)] == float(m.group(2))
            else:
                self.parms[m.group(1)] = float(m.group(2))
            return
        # If it's not a columns or parm line, just store it:
        self.comments.append(c)

    # f can be a filename (string) or a file-like object.
    def read(self, f):
        numrows = self.numrows() # numer of rows currently stored

        if type(f) is type(''):
            if not self.filename: self.filename = f
            f = open(f, 'rt') # treat as a filename

        while 1:
            l = f.readline()
            if not l: break

            # Strip whitespace:
            l = l.strip()
            pos_sharp = l.find("#")

            # look for full-line comment:
            if l and l[0] == '#':
                self.add_comment(l[1:].lstrip())
                continue

            # strip end-of-line comments:
            if l.find('#') != -1:
                l = (l.rstrip[:l.find('#')])

            # Look for text data lines:
            m = self.dataline_re.match(l)
            if m:
                row = numpy.array(list(map(float, l.split())))
                if self.data is None:
                    # allocate initial space for data:
                    self.data = numpy.zeros((128, row.shape[0]),
                                              numpy.float)
                    if self.colnames:
                        assert len(self.colnames) == row.shape[0]
                else:
                    # line length agreement is tested implicitly by assignment
                    if self.data.shape[0] == numrows:
                        # allocate some more space (double size):
                        newsize = (self.data.shape[0] +
                                   max(128, self.data.shape[0]))
                        self.data = numpy.resize(self.data,
                                                   (newsize,
                                                    self.data.shape[1]))
                self.data[numrows, :] = row
                numrows = numrows + 1
                continue

            if l == '':
                if numrows:
                    self.gaps.append(numrows)
                continue

            m = self.binstart_re.match(l)
            if m:
                # binary data
                typecode = m.group(1)
                itemsize = int(m.group(2))
                newnumrows = int(m.group(3))
                newnumcols = int(m.group(4))
                assert typecode == 'd' # Don't worry about other formats yet
                if self.colnames:
                    assert newnumcols == len(self.colnames)
                size = itemsize*newnumrows*newnumcols
                s = f.read(size)
                if len(s) != size:
                    raise DataFormat("Binary data of insufficient length")
                newdata = numpy.fromstring(s, typecode)
                newdata = numpy.reshape(newdata, (newnumrows, newnumcols))
                assert newdata.itemsize() == itemsize # sanity check
                if self.data:
                    assert typecode == self.data.typecode()
                    assert newdata.shape[1] == self.data.shape[1]
                    self.data = numpy.concatenate((self.data[:numrows],
                                                     newdata))
                else:
                    assert newdata.shape[1] == len(self.colnames)
                    self.data = newdata
                numrows = self.data.shape[0]
                assert f.read(1) == '\n'
                assert self.binend_re.match(f.readline())
                continue
            raise DataFormat("%d" % l)
        if self.data.any():
            # truncate extra allocated data space:
            self.data = self.data[:numrows, :]

    # Allow the special notation d[<index>,"colname"] for a second
    # argument which is a string.
    def __getitem__(self, i):
        if type(i) is type(()) and len(i) == 2 and type(i[1]) is type(""):
            return self.data[i[0], self.colnums[i[1]]]
        else:
            return self.data[i]

    def __setitem__(self, i, x):
        if type(i) is type(()) and len(i) == 2 and type(i[1]) is type(""):
            self.data[i[0], self.colnums[i[1]]] = x
        else:
            self.data[i] = x

    def numrows(self):
        if self.data is None: return 0
        else: return self.data.shape[0]

    def numcols(self):
        if self.data is None: return 0
        else: return self.data.shape[1]

    def appendcolumn(self, name):
        """Append a column of zeros to the right of the existing data.

        Use the column name specified."""
        if self.colnums.has_key(name):
            raise KeyError(name)
        newpart = numpy.zeros((self.data.shape[0], 1), numpy.float)
        self.data = numpy.concatenate((self.data, newpart), 1)
        self.colnums[name] = self.data.shape[1]
        self.colnames.append(name)

    def deletecolumn(self, j):
        """Delete the specified column from the dataset."""
        if type(j) is type(""):
            name = j
            j = self.colnums[name]
        else:
            name = self.colnames[j]
        self.data = numpy.concatenate((self.data[:,:j],
                                         self.data[:,j+1:]), 1)
        self.colnames[j:j+1] = []
        self.colnums = {}
        for i in range(len(self.colnames)):
            self.colnums[self.colnames[i]] = i

    def write(self, f=None, binary=None):
        """Write the data to a file or the stored filename.

        f can be a file-type object or a filename.  If it is omitted,
        then the file is saved to self.filename, from which the data
        were originally read.  Also attempts to copy the comment lines,
        parm lines, and column lines to output file though their order
        may be changed."""

        if f is None:
            assert self.filename
            f = self.filename
        if type(f) is type(""):
            # treat as a filename
            if binary: f = open(f, 'wb')
            else: f = open(f, 'w')
        for l in self.comments:
            f.write("# " + l + "\n")
        for p in self.parms.keys():
            f.write("# %s = %g\n" % (p, self.parms[p]))
        f.write("# Columns: " + string.join(self.colnames, "\t") + "\n")
        if binary:
            if self.gaps:
                sys.stderr.write("datafile: Warning--"
                                 "gaps not preserved in binary files.\n")
            f.write("binary_start(%s,%d,%d,%d)\n" %
                    (self.data.typecode(), self.data.itemsize(),
                     self.data.shape[0], self.data.shape[1]))
            f.write(self.data.tostring())
            f.write("\nbinary_end()\n")
        else:
            fmt = string.join(["%.15g"]*self.data.shape[1], '\t') + '\n'
            gaps = self.gaps[:]
            for i in range(self.data.shape[0]):
                while gaps and gaps[0]==i:
                    f.write('\n')
                    gaps = gaps[1:]
                f.write(fmt % tuple(self.data[i]))


# Demo code
if __name__ == '__main__':
    import getopt
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'b')
    except getopt.error:
        sys.stderr.write("Usage: %s [-b] [filename...]\n" % sys.argv[0])
        sys.exit(1)
    binary = 0
    for (opt,val) in opts:
        if opt == '-b': binary = 1
        else:
            # This should never happen:
            raise OptionError(opt)
    if args:
        d = datafile()
        for f in args:
            d.read(f)
    else:
        d = datafile(sys.stdin)
    d.write(sys.stdout, binary=binary)

