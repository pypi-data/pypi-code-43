import numpy,scipy
import matplotlib.pyplot as plt

class normalize():
    '''
    Quick & Dirty manual normalisation using spline interpolation.
    '''

    def __init__(self,data,step=3600*24,saved=None,play=True):

        self.data = data
            
        if saved!=None:
            self.points = numpy.loadtxt(saved,dtype='float')
        else:
            delta  = int((self.data.times.value[-1]-self.data.times.value[0])/step)
            points = numpy.array([[self.data.times.value[0]+i*step,numpy.median(self.data.value)] for i in range(delta+1)])
            self.points = numpy.vstack((points,[self.data.times.value[-1],numpy.median(self.data.value)]))

        self.co = scipy.interpolate.interp1d(self.points[:,0],self.points[:,1],kind='cubic')(self.data.times.value)

        if play:
            self.fig = plt.figure()
            plt.subplots_adjust(left=0.05, right=0.95, bottom=0.02, top=0.95, hspace=0.2, wspace=0)
            ax1 = plt.subplot2grid((4,1), (0, 0), rowspan=3)
            ax1.set_xlim(self.data.times.value[0],self.data.times.value[-1])
            ax1.plot(self.data.times.value,self.data.value,color='black',lw=0.3,zorder=2)
            ax1.axhline(y=numpy.median(self.data.value),color='grey',ls='dashed',zorder=2,lw=2,alpha=0.7)
            self.cont1  = ax1.scatter(self.points[:,0],self.points[:,1],marker='x',color='red',zorder=4)
            self.cont2, = ax1.plot(self.data.times.value,self.co,color='red',lw=1,zorder=3)
            self.ax1 = ax1
            ax2 = plt.subplot2grid((4,1), (3, 0),sharex=ax1)
            ax2.set_xlim(self.data.times.value[0],self.data.times.value[-1])
            self.norm, = ax2.plot(self.data.times.value,self.data.value/self.co,color='black',lw=0.3,zorder=1)
            self.ax2 = ax2
            self.fig.canvas.mpl_connect('key_press_event', self.press)
            plt.show()

        data.value[:] = (data.value / self.co) * numpy.median(data.value)
        self.data = data
        
    def press(self,event):
    
        if event.key in ['a','d',' ']:
            self.pts_edit(event)
            self.fitcont(event)
            self.fig.canvas.draw()
        if event.key=='s':
            print('|- Points and normalised spectrum saved!')
            outpts = open('saved.dat','w')
            for i in range (len(self.points)):
                sample = "{times:>15}{field:>20}".format(times=self.points[i,0],field=self.points[i,1])
                outpts.write(sample+'\n')
            outpts.close()
        if event.key=='q':
            print('|- Close window')
            plt.close()

    def pts_edit(self,event):

        if event.key=='a':
            self.points = numpy.vstack((self.points,[event.xdata,event.ydata]))
            self.points = self.points[self.points[:,0].argsort()]
        if event.key=='d':
            i = abs(self.points[:,0]-event.xdata).argmin()
            self.points = numpy.delete(self.points,i,axis=0)

    def fitcont(self,event):
    
        i = abs(self.points[:,0]-event.xdata).argmin()
        x = self.data.times.value[0] if i==0 else self.data.times.value[-1] if i==len(self.points)-1 else event.xdata
        self.points[i] = [x,event.ydata]
        self.co = scipy.interpolate.interp1d(self.points[:,0],self.points[:,1],kind='cubic')(self.data.times.value)
        self.cont1.remove()
        self.cont1 = self.ax1.scatter(self.points[:,0],self.points[:,1],marker='x',color='red',zorder=4)
        self.cont2.remove()
        self.cont2, = self.ax1.plot(self.data.times.value,self.co,color='red',lw=1,zorder=3)
        self.norm.remove()
        self.norm, = self.ax2.plot(self.data.times.value,self.data.value/self.co,color='black',lw=0.3,zorder=1)

    def get_updated_data(self):
        return self.data
