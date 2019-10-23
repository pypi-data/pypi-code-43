#!/usr/bin/env python
import nuri,numpy,os
import matplotlib.pyplot as plt

for i,f in enumerate(numpy.arange(1,20.02,0.02)):
    print(round(f,2))
    omega = 2.*numpy.pi*f
    time_interval = 1
    plt.figure(figsize=(15,5))
    x2 = numpy.linspace(0,time_interval,21)
    y2 = numpy.sin(x2*omega+numpy.pi/2)
    plt.plot(x2,y2,marker='o',color='black')
    x1 = numpy.linspace(0,time_interval,1000)
    y1 = numpy.sin(x1*omega+numpy.pi/2)
    plt.plot(x1,y1,lw=1,color='red')
    plt.xlim(0,1)
    plt.ylim(-1.1,1.1)
    plt.xlabel('Time [second]')
    plt.ylabel('Amplitude')
    plt.title('Signal Frequency: %.2f Hz'%f)
    plt.tight_layout()
    plt.savefig('image-%04i'%(i+1),dpi=150)
    plt.close()

os.system('ffmpeg -r 25 -f image2 -i image-%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p fft.mp4')
os.system('rm image*')
os.system('open fft.mp4')
