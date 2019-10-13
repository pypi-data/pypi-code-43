#!/usr/bin/env python
import nuri,mlpy,numpy,os
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
path = '/Users/vincent/Google\ Drive/research/UrbanMagnetometry/Processed\ Data/1Hz/'
data = nuri.get_data('2016-5-2','2016-6-6',path,station=4,sensor='biomed')
n,i,length = 1,600*28,3600
omega0 = 6
scales = mlpy.wavelet.autoscales(N=length,dt=1,dj=0.05,wf='morlet',p=omega0)
while i+1<len(data):
    spec = mlpy.wavelet.cwt(data.value[i:i+length],dt=1,scales=scales,wf='morlet',p=omega0)
    spec = numpy.abs(spec)**2
    freq = (omega0 + numpy.sqrt(2.0 + omega0 ** 2)) / (4 * numpy.pi * scales[1:])
    idx = abs(freq-1e-2).argmin()
    fig = plt.figure(figsize=(40,7),dpi=50)
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(spec[:idx],extent=[0,length,freq[idx],freq[0]],aspect='auto',
               interpolation='nearest',cmap='jet',norm=LogNorm(0.000001,0.1))
    plt.grid(False)
    plt.savefig('image-%04i'%n)
    plt.close()
    n+=1
    i+=10
    if n==1001: break
os.system('ffmpeg -r 25 -f image2 -i image-%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p wavelet.mp4')
os.system('rm image*')
