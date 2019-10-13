###############################################################################
# Copyright (c) 2018, Urban Magnetometry Group.
#
# Produced at the University of California at Berkeley.
#
# Written by V. Dumont (vincentdumont11@gmail.com).
#
# All rights reserved.
#
# This file is part of NURI.
#
# For details, see github.com/vincentdumont/nuri.
#
# For details about use and distribution, please read NURI/LICENSE.
###############################################################################
def split_data():
    '''
    Take measurement files obtained from sample grabber and split
    them into individual hour files.
    
    Parameters
    ----------
    files : str
      Time data file 
    '''
    os.system('mkdir -p split_data')
    imag  = 0
    itime = 0
    dates = []
    tdata = open('2016-11-10_23-xx_time_v2.bin','rb')
    xdata = open('2016-11-10_23-xx_rawX_uT_3960Hz.bin','rb')
    ydata = open('2016-11-10_23-xx_rawY_uT_3960Hz.bin','rb')
    zdata = open('2016-11-10_23-xx_rawZ_uT_3960Hz.bin','rb')
    while True:
        try:
            tdata.seek(itime)
        except ValueError:
            tchunk.close()
            xchunk.close()
            ychunk.close()
            zchunk.close()
            break
        data = struct.unpack('<'+'qiBQddcdcdd',tdata.read(63))
        npts = int(data[1])
        tbeg = float(data[4])
        tbeg = datetime.fromtimestamp(tbeg).strftime('%Y-%-m-%-d_%-H')
        if tbeg not in dates:
            print(tbeg)
            dates.append(tbeg)
            if len(dates)>1:
                tchunk.close()
                xchunk.close()
                ychunk.close()
                zchunk.close()
            tchunk = open('split_data/%s-xx_time_v2.bin'%tbeg,'wb')
            xchunk = open('split_data/%s-xx_rawX_uT_3960Hz.bin'%tbeg,'wb')
            ychunk = open('split_data/%s-xx_rawY_uT_3960Hz.bin'%tbeg,'wb')
            zchunk = open('split_data/%s-xx_rawZ_uT_3960Hz.bin'%tbeg,'wb')
        data = [0,float(data[1]),float(data[2]),float(data[3]),
                float(data[4]),float(data[5]),str(data[6]),
                float(data[7]),str(data[8]),float(data[9]),
                float(data[10])]
        tchunk.write(struct.pack('<'+'qiBQddcdcdd',*data))
        itime+=63
        for i in range(npts):
            xdata.seek(imag)
            xchunk.write(xdata.read(8))
            ydata.seek(imag)
            ychunk.write(ydata.read(8))
            zdata.seek(imag)
            zchunk.write(zdata.read(8))
            imag+=8
        
