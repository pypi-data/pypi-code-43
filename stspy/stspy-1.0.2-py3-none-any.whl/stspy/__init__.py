import numpy as np
import re, struct, zlib
from scipy.optimize import leastsq
from scipy.ndimage import convolve

# hyst as a float
# always put positive voltages first

# for specific params:
PARAMS_VERT = ["ZPiezoconst", "LockinRC", "Vertmandelay", "VertSpecBack", "LockinAmpl", "Current[A]", "SetPoint", "DSP_Clock",
               "DAC-Type", "Gainpreamp", "Length x[A]", "Length y[A]"]
PARAMS_DAT = ["Num.X", "Num.Y", "Xpiezoconst", "YPiezoconst", "ZPiezoconst", "Channels", "GainZ", "DAC-Type", "Length x[A]", "Length y[A]", "SetPoint", "BiasVolt.[mV]"]
def make_param_re(params):
    re_string = f"({'|'.join(params)})=(.+)\\r\\n"
    re_string = re_string.replace('[', r'\[').replace(']', r'\]')
    return re.compile(re_string)
PARAMS_VERT_RE = make_param_re(PARAMS_VERT)
PARAMS_DAT_RE = make_param_re(PARAMS_DAT)

# for all params
PARAM_FINDER = re.compile(r'(.*)=(.*)\r\n')

class STM:
    def __init__(self, DAC_Voltage_Range = 20000.0):
        self.DAC_Voltage_Range = DAC_Voltage_Range #in mV
    def __str__(self):
        ret = 'DAC_Voltage_Range: %.1f mV' %self.DAC_Voltage_Range
        return ret

def shift(arr, n):
    # shifts a 1D array n positions to the right. Repeats starting/ending values for positions outside original array bounds.
    # ex:  [1, 2, 3, 4, 5, 6, 7] shifted n=2
    # out: [1, 1, 1, 2, 3, 4, 5]
    n = int(n)
    start, end = arr[0], arr[-1]
    out = np.zeros(arr.shape)
    if n > 0:
        out[n:] = arr[:-n]
        out[:n] = start
    elif n < 0:
        out[:n] = arr[-n:]
        out[n:] = end
    else:
        out = arr
    return out

class Spectra:
    def __init__(self, V, I, dIdV):
        self.label = None
        self.V, self.I, self.dIdV = V, I, dIdV
        self.N = len(V)
        self.z = np.empty(self.N)
        self.d2IdV2 = None

        self.ZPiezoconst = 1.0
        self.LockinRC = 0.0
        self.Speclength = 0
        self.VertSpecBack = 0
        self.LockinAmpl = 0
        self.Current = 1
        self.hyst = 0
        self.x = 0
        self.y = 0
        self.Length_x = 0
        self.Length_y = 0

    #use command print(spectra_object) to print out all relevant parameters
    def __str__(self):
        ret = f'Spectra object at label: {self.label}\n'
        for key in self.__dict__.keys():
            if key.startswith('__'):
                continue
            x = getattr(self, key)
            if isinstance(x, int) or isinstance(x, float) or isinstance(x, str) or x is None:
                ret += f'{key}: {x}\n'
        return ret

    def average(self, hyst_cor=True):
        # this function averages trace and retraces together, editing the attributes 'V', 'I', 'dIdV', and 'z' to reflect this.
        VSB = self.VertSpecBack
        HYST = self.hyst

        # Ensure at least 1 retrace exists.
        if VSB + 1 <= 1:
            raise Exception('VertSpecBack is %d, which means no averaging or hystersis correction is possible.' %n)
        n = self.N // (VSB + 1)
        self.V = self.V[0:n]

        # Ensure # data points is a multiple of # of trace/retraces. Removes points from the end accordingly.
        dif = self.N % (VSB + 1)
        if dif != 0:
             self.I = self.I[:-dif]
             self.dIdV = self.dIdV[:-dif]
             self.z = self.z[:-dif]
             self.N = len(self.V)
             if self.d2IdV2 is not None:
                self.d2IdV2 = self.d2IdV2[:-dif]

        # corrects for hysteresis (constant shift)
        if hyst_cor:
            if HYST % 2 != 0:
                HYST += 1
            self.I = shift(self.I, -HYST/2)
            self.dIdV = shift(self.dIdV, -HYST/2)
            self.z = shift(self.z, -HYST/2)
            if self.d2IdV2 is not None:
                self.d2IdV2 = shift(self.d2IdV2, -HYST/2)

        # Reshape single-row data arrays into a matrix of multiple rows, with single row containing exactly one trace.
        self.I = self.I.reshape((VSB + 1, n))
        self.dIdV = self.dIdV.reshape((VSB + 1, n))
        self.z = self.z.reshape((VSB + 1, n))
        if self.d2IdV2 is not None:
            self.d2IdV2 = self.d2IdV2.reshape((VSB + 1, n))

        # Reverse "back-traces", which are odd-numbered rows. (Forward/backward scans always alternate)
        for i in range(1, VSB + 1, 2): # i.e. odd numbers only
            self.I[i, :] = self.I[i, :][::-1]
            self.dIdV[i, :] = self.dIdV[i, :][::-1]
            self.z[i, :] = self.z[i, :][::-1]
            if self.d2IdV2 is not None:
                self.d2IdV2 = self.d2IdV2[i, :][::-1]

        # sum down column, divide by number of rows.
        self.I = (1 / (VSB + 1)) * np.sum(self.I, axis=0)
        self.dIdV = (1 / (VSB + 1)) * np.sum(self.dIdV, axis=0)
        self.z = (1 / (VSB + 1)) * np.sum(self.z, axis=0)
        if self.d2IdV2 is not None:
            self.d2IdV2 = (1 / (VSB + 1)) * np.sum(self.d2IdV2, axis=0)

        if self.V[0] < 0:
            self.V = self.V[::-1]
            self.I = self.I[::-1]
            self.dIdv = self.dIdV[::-1]
            self.z = self.z[::-1]
            if self.d2IdV2 is not None:
                self.d2IdV2 = self.d2IdV2[::-1]


    def normalize(self, kappa):
        #normalize the spectra using an input value of kappa in Ang^-1
        self.I = self.I * np.exp(-2 * kappa * self.z)
        self.dIdV = self.dIdV * np.exp(-2* kappa * self.z)

def load_VERT_file(filename, stm = STM()):
    # Now uses regex to search for parameters of interest. Regex object is defined above

    # find all the relevant parameters
    f = open(filename, 'rb')

    header = f.read(128 * 128)
    f.readline()  # random \r\n in data
    dline = f.readline()
    data = f.read()
    f.close()

    params = header.decode('ascii', errors='ignore')
    dline = dline.decode('ascii', errors='ignore')
    version = params[:11]  # Should read [ParVERT32]

    if "ParVERT32" in version:
        Version = '3.2' #STMAFM Software version
        LockinRC_factor = 7.989578/0.00251 #mutliplicative factor to get LockinRC param in Hz
        Current_index = 4 #column indexes for extracting current and dIdV
        dIdV_index = 5
        d2IdV2_index = 6
    if "ParVERT30" in version:
        Version = '3.0'
        LockinRC_factor = 7960.
        Current_index = 3
        dIdV_index = 4

    params = PARAMS_VERT_RE.findall(params)
    p_dict = dict()
    for p, v in params:
        try:
            p_dict[p] = float(v)
        except ValueError:
            if p == 'DAC-Type':
                p_dict[p] = float(v[:-3])  # removing 'bit' from end of string
            else:
                raise Exception(f'Parameter {p} gives an improper value {v}')

    dline = dline.split()
    N, x, y = int(dline[0]), int(dline[1]), int(dline[2])
    
    ncols = len(data[:data.find(b'\t\r\n')].split(b'\t'))
    data = np.fromstring(data, sep='\t')  # turns out this is MUCH faster than np.loadtxt.  Unsure how well it handles comments at the end though
    data = data.reshape((N, ncols))

    z = data[:, 2] * p_dict["ZPiezoconst"] / 1000.0 # Angstroms
    V = data[:, 1] / 1000.0 # Volts
    I = data[:, Current_index] / 2**p_dict["DAC-Type"] * stm.DAC_Voltage_Range / 10**p_dict["Gainpreamp"] / 1e6 # current in amps
    dIdV = data[:, dIdV_index] / 2**p_dict["DAC-Type"] * stm.DAC_Voltage_Range # conductance in meV
    if ncols == 7:
        d2IdV2 = data[:, d2IdV2_index] / 2**p_dict["DAC-Type"] * stm.DAC_Voltage_Range # 2nd deriv conductance in meV
    else:
        d2IdV2 = None

    ret = Spectra(V, I, dIdV)
    ret.z = z
    ret.d2IdV2 = d2IdV2

    label = filename[-19:-5]
    if 'L' in label or 'R' in label:
        label = filename[-25:-5]
    ret.label = label

    ret.ZPiezoconst = p_dict["ZPiezoconst"]
    ret.LockinRC = p_dict["LockinRC"] * LockinRC_factor # in Hz
    ret.Speclength = p_dict["Vertmandelay"] * N / p_dict["DSP_Clock"]
    ret.VertSpecBack = int(p_dict["VertSpecBack"])
    ret.LockinAmpl = p_dict["LockinAmpl"]
    try:
        ret.Current = p_dict["Current[A]"]
    except KeyError:
        ret.Current = p_dict["SetPoint"]
    ret.N = int(N)
    ret.x = x * 10./2.**(20-1) * 40 * 10 # value in DAC units * Voltage range / 2^(bit count - 1 (account for positive vs negative)) * piezo constant * high voltage gain (hard coded for now)
    ret.y = y * 10./2.**(20-1) * 40 * 10
    ret.Length_x = p_dict["Length x[A]"]
    ret.Length_y = p_dict["Length y[A]"]

    #hysteresis correction factor
    hyst = int(N / (ret.Speclength * p_dict["LockinRC"] * LockinRC_factor * np.pi))
    ret.hyst = hyst

    return ret

class Scan:

    def __init__(self, params, channels):
        self.channels = channels
        self.params = params

        # grab relevant params, add to class namespace
        self.xres, self.yres = self.params['Num.X'], self.params['Num.Y']
        self.XPiezoconst = self.params['Xpiezoconst']  # lol @ lowercase p
        self.YPiezoconst = self.params['YPiezoconst']
        self.ZPiezoconst = self.params['ZPiezoconst']
        self.length_x, self.length_y = self.params['Length x[A]'], self.params['Length y[A]']
        self.setpoint = self.params['SetPoint']
        self.biasvolt = self.params["BiasVolt.[mV]"]
        self.dacbits = int(self.params['DAC-Type'].replace('bit', ''))

        # create x & y grids
        self.x, self.y = np.meshgrid(np.linspace(0, self.length_x, self.xres),
                                     np.linspace(0, self.length_y, self.yres))

    def set_minimum_to_zero(self, channel=None):
        if channel is None:
            for i in range(len(self.channels)):
                self.set_minimum_to_zero(channel=i)
        else:
            self.channels[channel] -= self.channels[channel].min()

    def plane_sub(self, channel=None):
        if channel is None:
            for i in range(len(self.channels)):
                self.plane_sub(channel=i)
        else:
            c = self.channels[channel]
            def plane(p, x, y):
                mx, my, offset = p
                return mx * x + my * y + offset
            errfunc = lambda p, x, y, z: plane(p, x, y) - z

            offset_guess = c.mean()
            mx_guess = c[0, -1] - c[0, 0] / (self.x[0, -1] - self.x[0, 0])
            my_guess = c[-1, 0] - c[0, 0] / (self.y[-1, 0] - self.y[0, 0])

            p0 = [mx_guess, my_guess, offset_guess]

            (mx, my, offset), success = leastsq(errfunc, p0, args=(self.x.ravel(), self.y.ravel(), self.channels[channel].ravel()))
            if success not in (1, 2, 3, 4):
                print(f"Plane subtraction on channel {channel} has failed")
            else:
                self.channels[channel] = self.channels[channel] - plane((mx, my, 0), self.x, self.y)

    def boxcar(self, channel=None, neighbors=1):
        if channel is None:
            for i in range(len(self.channels)):
                self.boxcar(channel=i, neighbors=neighbors)
        else:
            size = 2 * neighbors + 1
            k = (1 / size**2) * np.ones((size, size))
            self.channels[channel] = convolve(self.channels[channel], k)

    def align_rows(self, channel=None, method='median'):
        # align rows using various methods
        if channel is None:
            for i in range(len(self.channels)):
                self.align_rows(channel=i, method=method)
        else:
            if method == 'median':
                full_median = np.median(self.channels[channel])
                row_medians = np.median(self.channels[channel], axis=1)
                row_subtrahend = (row_medians - full_median)[np.newaxis, :].T # some formatting for proper row-by-row subtraction
                self.channels[channel] = self.channels[channel] - row_subtrahend
            elif 'poly' in method:
                deg = int(method[-1])
                def polynomial(p, x):
                    # highest order coeff at p[0]
                    out = 0
                    for coeff in p:
                        out = out * x + coeff
                    return out
                errfunc = lambda p, x, y: polynomial(p, x) - y
                mean_offset = np.mean(self.channels[channel])

                for i in range(len(self.channels[channel])):
                    xrow, scanrow = self.x[i], self.channels[channel][i]
                    p0 = [0,] * deg + [np.mean(scanrow),]
                    p1, success = leastsq(errfunc, p0, args=(xrow, scanrow))
                    if success not in (1, 2, 3, 4):
                        print(f"Polynomial subtraction on channel {channel}, row {i} has failed")
                    self.channels[channel][i] = self.channels[channel][i] - polynomial(p1, xrow) + mean_offset
            else:
                print(f'Method {method} is not yet supported')


def import_DAT_file(fn, load_all_params=False):
    # requires struct, zlib, numpy, re
    # load_all_params = True will load every param in the *.dat file, at the expense of runtime
    # load_all_params = False will load only those params in PARAMS_DAT (at the this of the file)

    # open file in bytes mode ('rb'), read all bytes
    with open(fn, 'rb') as f:
        file = f.read()

    # header is first 128 * 128. Grab these, decode as ascii
    # data is remaining bytes, decompress using zlib
    header_len = 128 * 128
    header = file[:header_len]
    data = file[header_len:]

    header = header.decode('ascii', errors='ignore')
    data = zlib.decompress(data)

    # use regex, grab all parameters
    if not load_all_params:
        p = PARAMS_DAT_RE.findall(header)
        params = dict()
        for key, val in p:
            if '.' in val:  # i.e. is a float, or rarely a str
                try:
                    val = float(val)
                except ValueError:
                    pass
            else:  # i.e. is an int, or str
                try:
                    val = int(val)
                except ValueError:
                    pass
            params[key] = val
    else:
        # many redundant entries: keys of the form "key1 / key2" are entered in dict under "key1", "key2", and "key1 / key2"
        p = PARAM_FINDER.findall(header)
        params = dict()
        for key, val in p:
            if key in (' ', '  /  '):
                continue
            keys = key.split(' / ')
            if '.' in val:  # i.e. is a float, or rarely a str
                try:
                    val = float(val)
                except ValueError:
                    pass
            else:  # i.e. is an int, or str
                try:
                    val = int(val)
                except ValueError:
                    pass
            for k in keys:
                params[k] = val
            params[key] = val

    # Get image size, channels, and parameters for correct unit conversion
    xres, yres, nchans = params['Num.X'], params['Num.Y'], params['Channels']
    zgain, zpiezo, dacbits = params['GainZ'], params['ZPiezoconst'], int(params['DAC-Type'].replace('bit', ''))
    offset, bpp = 4, 4
    image_size = xres * yres * bpp
    conversion_factor = 20 / (2 ** dacbits) * zgain * (zpiezo * 10**-10) # Zpiezo is in Ang/V, convert to m/V

    channel_inds = [(i * image_size + offset, (i + 1) * image_size + offset) for i in range(nchans)]

    # import channels as numpy arrays, unpacking each 4-byte floating point number using struct.unpack('f', [num])
    channels = []
    for start, end in channel_inds:
        c = [struct.unpack('f', data[i:i + bpp])[0] * conversion_factor for i in range(start, end, bpp)]
        c = np.array(c).reshape(yres, xres)
        channels.append(c)

    # return params and all channels, or an object containing these
    return Scan(params, channels)

# UNCHANGED BELOW

class specgrid:
    def __init__(self, V, I, dIdV):
        self.label = None

        #data should include V, z, I, and dIdV in that order

        #Assign values to spectra object
        self.ZPiezoconst = 1.0
        self.LockinRC = 0.0
        self.Speclength = 0
        self.VertSpecBack = 0
        self.LockinAmpl = 0
        self.Current = 1

        self.hyst = 0

        self.z = np.ones(len(V))
        self.V = V

        self.I = I
        self.dIdV = dIdV

        #Number of data points, needed for averaging and hysteresis correction
        N = len(V)
        self.N = N

        self.nx, self.ny = I.shape[0], I.shape[1]

    def average(self, hyst_cor = True):

        N = self.N
        if self.VertSpecBack + 1 <= 1:
            raise Exception('VertSpecBack is %d, which means no averaging or hystersis correction is possible.' %n)

        I = np.empty((self.nx, self.ny, self.N/(self.VertSpecBack + 1)))
        dIdV = np.empty((self.nx, self.ny, self.N/(self.VertSpecBack + 1)))
        for i in range(self.nx):
            for j in range(self.ny):
                spec = spectra(self.V, self.I[i, j, :], self.dIdV[i, j, :])
                spec.z = self.z
                spec.hyst = self.hyst
                spec.VertSpecBack = self.VertSpecBack
                spec.average(hyst_cor = hyst_cor)
                I[i, j, 0:len(spec.I)] = spec.I
                dIdV[i, j, 0:len(spec.dIdV)] = spec.dIdV
        self.z = spec.z
        self.V = spec.V
        self.I = I
        self.dIdV = dIdV

    def normalize(self, kappa):
        I = np.empty((self.nx, self.ny, self.N))
        dIdV = np.empty((self.nx, self.ny, self.N))
        for i in range(self.nx):
            for j in range(self.ny):
                spec = spectra(self.V, self.I[i, j, :], self.dIdV[i, j, :])
                spec.z = self.z
                spec.normalize(kappa)
                I[i, j, :] = spec.I
                dIdV[i, j, :] = spec.dIdV
        self.I = I
        self.dIdV = dIdV

    #use command print(spectra_object) to print out a few relevant parameters
    def __str__(self):
        ret = 'label: ' + self.label +'\n'
        ret += 'nx, ny: %d, %d\n' %(self.nx, self.ny)
        ret += 'data points: %d\n' %self.N
        ret += 'VertSpecBack: %d\n' %self.VertSpecBack
        ret += 'LockinAmpl: %.1f mV\n' %self.LockinAmpl
        ret += 'Setpoint: %.1e A\n' %self.Current
        ret += 'Hystersis Correction: %d' %self.hyst
        return ret

def read_item(content, loc, format_):
    size = struct.calcsize(format_)
    return struct.unpack(format_, content[loc:loc+size])[0]

def load_specgrid_file(filename, stm = STM()):
    #find all the relevant parameters
    f = open(filename + '.dat', 'r')
    for line in f:
        if "ParVERT32" in line:
            Version = '3.2' #STMAFM Software version
            LockinRC_factor = 7960. #mutliplicative factor to get LockinRC param in HzLockinRC_factor = 7960.
            Current_index = 5 #column indexes for extracting current and dIdV
            dIdV_index = 4
        if "ParVERT30" in line:
            Version = '3.0'
            LockinRC_factor = 7960.
            Current_index = 4
            dIdV_index = 3
        if "ZPiezoconst" in line:
            ZPiezoconst = float(line[line.find('=')+1:-1])
        if "LockinRC" in line:
            LockinRC = float(line[line.find('=')+1:-1])
        if "Vertmandelay" in line:
            Vertmandelay = float(line[line.find('=')+1:-1])
        if "VertSpecBack" in line:
            VertSpecBack = int(line[line.find('=')+1:-1])
        if "LockinAmpl" in line:
            LockinAmpl = float(line[line.find('=')+1:-1]) #mV
        if "Current[A]" in line:
            Current = float(line[line.find('=')+1:-1]) #Amps
        if "DSP_Clock" in line:
            DSP_Clock = float(line[line.find('=')+1:-1]) #DSP Units to determine Speclength
        if "DAC-Type" in line:
            DAC_Type = float(line[line.find('=')+1:-4])
        if "Gainpreamp" in line:
            Gainpreamp = float(line[line.find('=')+1:-1])
    f.close()

    with open(filename, mode='rb') as file: # b is important -> binary
        content = file.read()
    version = read_item(content, 0, 'i')
    nx, ny = read_item(content, 4, 'i'), read_item(content, 8, 'i')
    dx, dy = read_item(content, 12, 'i'), read_item(content, 16, 'i')
    specxgrid, specygrid = read_item(content, 20, 'i'), read_item(content, 24, 'i')
    vertpoints = read_item(content, 28, 'i')
    vertmandelay = read_item(content, 32, 'i')
    vertmangain = read_item(content, 36, 'i')
    biasvoltage = read_item(content, 40, 'f')
    tunnelcurrent = read_item(content, 44, 'f')
    imagedatasize = read_item(content, 48, 'i')
    specgriddatasize = read_item(content, 52, 'i')
    specgridchan = read_item(content, 56, 'i')
    specgridchannelselectval = read_item(content, 60, 'i')
    specgriddatasize64 = read_item(content, 64, 'q')
    if version >= 4:
        xstart, xend = read_item(content, 72, 'i'), read_item(content, 76, 'i')
        ystart, yend = read_item(content, 80, 'i'), read_item(content, 84, 'i')
    else:
        xstart, ystart = 1, 1
        xend = int(nx/specxgrid) + 1
        yend = int(ny/specygrid) + 1
    V = np.empty(vertpoints)
    z = np.empty(vertpoints)
    for i in range(vertpoints):
        V[i] = read_item(content, 1024 + (i*8), 'f')
        z[i] = read_item(content, 1028 + (i*8), 'f')

    current = np.empty((xend-xstart + 1, yend-ystart + 1, vertpoints))
    conductance = np.empty((xend-xstart + 1, yend-ystart + 1, vertpoints))
    n = 0
    for i in range(current.shape[0]):
        for j in range(current.shape[1]):
            I = np.empty(vertpoints)
            dIdV = np.empty(vertpoints)
            for k in range(vertpoints):
                I[k] = read_item(content, 1032 + n*vertpoints*8 + k*8, 'f')
                dIdV[k] = read_item(content, 1028 + n*vertpoints*8 + k*8, 'f')
            current[i, j, :] = I
            conductance[i, j, :] = dIdV
            n += 1

    current *= stm.DAC_Voltage_Range / 2**DAC_Type / 10**Gainpreamp /1e6 #current in amps
    conductance *= stm.DAC_Voltage_Range /2**DAC_Type #meV
    V /= 1000.0 #volts
    ret = specgrid(V, current, conductance)
    ret.z = z * ZPiezoconst/1000.0 #Angstroms

    Speclength = Vertmandelay * vertpoints / DSP_Clock

    ret.label = filename[-23:-9]
    ret.ZPiezoconst = ZPiezoconst
    ret.LockinRC = LockinRC * LockinRC_factor #Hz
    ret.Speclength = Speclength
    ret.VertSpecBack = VertSpecBack
    ret.LockinAmpl = LockinAmpl
    ret.Current = Current
    ret.N = vertpoints
    #hysteresis correction factor
    hyst = int(vertpoints/Speclength/LockinRC/LockinRC_factor/np.pi)
    ret.hyst = hyst

    return ret
