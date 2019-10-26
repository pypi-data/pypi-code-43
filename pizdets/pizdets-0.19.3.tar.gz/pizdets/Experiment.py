import pizdets.pm as pm
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import time

from .ExperimentFiles import ExperimentFiles

class Experiment():
    def __init__(self,foldername,connect=True):
        self.files=ExperimentFiles(foldername)
        self.mixer_period=3000
        self.mixer_pulseWidth=2500
        if connect:
            self.dev=self.reconnect()
        self._read_pump_calibration()

        try:
            self._volume_death,self._volume_peace,self._volume_vacuum=pd.read_csv(self.files.volumes).iloc[-1,1:].astype(int)
            print("Remaining volumes read from %s"%self.files.volumes)
            print("\tvolume_vacuum = %d"%self._volume_vacuum)
            print("\tvolume_peace = %d"%self._volume_peace)
            print("\tvolume_death = %d"%self._volume_death)
            
        except IndexError:
            print("Enter available volumes")
            print("for vacuum - remaining volume in bottle")
            self._volume_vacuum=int(input("volume_vacuum (ml)"))
            self._volume_peace=int(input("volume_peace (ml)"))
            self._volume_death=int(input("volume_death (ml)"))
            self._write_volumes_file()
    def _read_pump_calibration(self,file=None):
            """
            read calibration of current experiment, or from another file
            """
            if file is None:
                _file = self.files.pump_calibration
            else:
                _file = file
            try:
                self._units_to_ml_p1,self._units_to_ml_p2,self._units_to_ml_p3=pd.read_csv(_file).iloc[-1,1:].astype(int)
                print("Pump coefficients read from %s"%_file)
                print("\tunits_to_ml_p1 = %d"%self._units_to_ml_p1)
                print("\tunits_to_ml_p2 = %d"%self._units_to_ml_p2)
                print("\tunits_to_ml_p3 = %d"%self._units_to_ml_p3)
            
            except IndexError:
                print("***Using uncallibrated pump coefficients!\n")
                self._units_to_ml_p1=215000
                self._units_to_ml_p2=215000
                self._units_to_ml_p3=215000
            if file is not None:
                # write calibration to current PExperiment folder
                self._write_pump_calibration_file()
 
    def calibrate_pump(self, pump=None, tube=None, requested_volume=None, real_volume=None, filename=None):
        """
        Put tube on a scale and measure real pumped volume
        """
        if filename is None:
            assert 0 < requested_volume < 20
            assert pump in ["vacuum", "peace", "death"]

            if real_volume is None:
                print("Sending %dml request to pump %s"%(requested_volume,pump))
                if pump=="vacuum":
                    self.vacuum(tube,requested_volume)
                if pump=="peace":
                    self.pump_peace(tube,requested_volume)
                if pump=="death":
                    self.pump_death(tube,requested_volume)
                real_volume=float(input("What was the real volume [ml]?"))

            if pump=="vacuum": self.units_to_ml_p3/=real_volume/requested_volume
            if pump=="peace": self.units_to_ml_p2/=real_volume/requested_volume
            if pump=="death":self.units_to_ml_p1/=real_volume/requested_volume
        else:
            self._read_pump_calibration(filename)
            
            
#properties
    @property
    def units_to_ml_p1(self):
        return self._units_to_ml_p1
    @units_to_ml_p1.setter
    def units_to_ml_p1(self,val):
        val=int(val)
        self._units_to_ml_p1=val
        self._write_pump_calibration_file()
    
    @property
    def units_to_ml_p2(self):
        return self._units_to_ml_p2
    @units_to_ml_p2.setter
    def units_to_ml_p2(self,val):
        val=int(val)
        self._units_to_ml_p2=val
        self._write_pump_calibration_file()
        
    @property
    def units_to_ml_p3(self):
        return self._units_to_ml_p3
    @units_to_ml_p3.setter
    def units_to_ml_p3(self,val):
        val=int(val)
        self._units_to_ml_p3=val
        self._write_pump_calibration_file()
        
    def _write_pump_calibration_file(self):
        with open(self.files.pump_calibration,"a") as f:
            row="%d,%d,%d"%(self.units_to_ml_p1,self.units_to_ml_p2,self.units_to_ml_p3)+"\n"
            f.write(str(pd.Timestamp.now(tz="Europe/Vienna"))+","+row)
            print("Wrote units_to_ml for vacuum(p1), peace(p2), death(p3) to %s file:"%self.files.pump_calibration)
            print(row)    
    
    @property
    def volume_vacuum(self):
        return self._volume_vacuum
    @volume_vacuum.setter
    def volume_vacuum(self,vol):
        assert type(vol) in [int,float]
        self._volume_vacuum=vol
        self._write_volumes_file()
    
    @property
    def volume_peace(self):
        return self._volume_peace
    @volume_peace.setter
    def volume_peace(self,vol):
        assert type(vol) in [int,float]
        self._volume_peace=vol
        self._write_volumes_file()
    
    @property
    def volume_death(self):
        return self._volume_death
    @volume_death.setter
    def volume_death(self,vol):
        assert type(vol) in [int,float]
        self._volume_death=vol
        self._write_volumes_file()
    
    
    def _write_volumes_file(self):
        with open(self.files.volumes,"a") as f:
            volume_row="%d,%d,%d"%(self.volume_death,self.volume_peace,self.volume_vacuum)+"\n"
            f.write(str(pd.Timestamp.now(tz="Europe/Vienna"))+","+volume_row)
#             print("Wrote vacuum, peace, death volumes to %s file:"%self.files.volumes)
#             print(volume_row)
    def logfile_write(self,text):
        assert type(text)==str
        with open(self.files.logfile,"a") as f:
            logtext=str(pd.Timestamp.now(tz="Europe/Vienna"))+"\t"+text+"\n"
            f.write(logtext)
    def logfile_open(self):
        return pd.read_csv(self.files.logfile,sep="\t")
    
    def valvepwm(self, tube,pwm):
        servomap={3: 0, 4: 1, 5: 2, 6: 3, 2: 4, 1: 5, 0: 6}
        exec("self.dev.request(pm.dev_msg.SetServoStateRequest(servo%d=%d))"%(servomap[tube],pwm))
        time.sleep(0.3)
        exec("self.dev.request(pm.dev_msg.SetServoStateRequest(servo%d=%d))"%(servomap[tube],0))
    def clamp(self,tube,state=1):
        if state==0: 
            self.valvepwm(tube,500)
        if state==1: #flow
            self.valvepwm(tube,2300)
    def selectTube(self,tube):
        assert 0<=tube<7
        
        for i in range(7):
            if i==tube:
#                 print(i,"is open")
                self.clamp(tube=i,state=1) 
            else:
#                 print(i,"is closed")
                self.clamp(tube=i,state=0)

    def pump_death(self,tube=5,vol=1):
        assert tube in [0,1,2,3,4,5,6]
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"death_start",str(vol)])+"\n"
            f.write(pumprow)
        
        self.selectTube(tube=tube)
        V=vol * self.units_to_ml_p1
        V=int(V)
        time.sleep(0.5)
        self.dev.request(pm.dev_msg.PumpRequest(pump1Volume = V))
        time.sleep(0.5)
        self.clamp(tube,0)
        self.volume_death-=vol
        
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"death",str(vol)])+"\n"
            f.write(pumprow)
        

    def pump_peace(self,tube=5,vol=1):
        assert tube in [0,1,2,3,4,5,6]
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"peace_start",str(vol)])+"\n"
            f.write(pumprow)
        self.selectTube(tube=tube)
        V=vol * self.units_to_ml_p2
        V=int(V)
        time.sleep(0.5)
        self.dev.request(pm.dev_msg.PumpRequest(pump2Volume = V))
        time.sleep(0.5)
        
        self.clamp(tube,0)
        self.volume_peace-=vol
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"peace",str(vol)])+"\n"
            f.write(pumprow)
            
    def vacuum(self,tube=5,vol=1):
        assert tube in [0,1,2,3,4,5,6]
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"vacuum_start",str(vol)])+"\n"
            f.write(pumprow)
        self.selectTube(tube=tube)
        V=vol * self.units_to_ml_p3
        V=int(V)
        time.sleep(0.5)
        self.dev.request(pm.dev_msg.PumpRequest(pump3Volume = V))
        time.sleep(0.5)
        self.clamp(tube,0)
        self.volume_vacuum-=vol
        
        with open(self.files.pump_data,"a") as f:
            pumprow=",".join([str(pd.Timestamp.now(tz="Europe/Vienna")),str(tube),"vacuum",str(vol)])+"\n"
            f.write(pumprow)
    
    def reconnect(self,device_index=0):
        # self.hub = pm.PMHub.local()
        self.hub = pm.PMHub("tcp://localhost:5555")

        self.dev = self.hub.get_devices()[device_index]
        self.logfile_write("reconnected")
        return self.dev
    def mix(self,state=1):
        self.dev.request(pm.dev_msg.SetMixerStateRequest(state=state,
                                                         period=self.mixer_period,
                                                         pulseWidth=self.mixer_pulseWidth))

    def get_laser_signal(self,tube,resistor1=100,
                    resistor2=10,
                    laserOnDelay=10,
                    laserOffDelay=1,
                    cycles=10,
                    bias=0):
        tube_mapping={0:0,
                      1:3,
                      2:1,
                      3:5,
                      4:2,
                      5:6,
                      6:4}
        tube=tube_mapping[tube]
        raw_laser_signal=self.dev.request(pm.dev_msg.ODMeasureRequest(tube=tube,
                                                                      laserOnDelay=laserOnDelay,
                                                                      laserOffDelay=laserOffDelay,
                                                                      cycles=cycles,
                                                                      bias=bias,
                                                                      resistor1=resistor1,
                                                                      resistor2=resistor2))
    
        return raw_laser_signal
    
    
    def get_4_signals(self,tube,**kwargs):
        s4=self.get_laser_signal(tube,**kwargs)
        return s4.onFS,s4.onSS,s4.offFS,s4.offFS
    
    def record(self,**kwargs):
        row=[]
        for i in range(7):
            row.append(self.get_4_signals(i,**kwargs))
        row=np.array(row).ravel()
        row=",".join(str(i) for i in np.array(row).ravel())
        t=str(pd.Timestamp.now(tz='Europe/Vienna'))[:-13]
        row=t+","+row+"\n"
        with open(self.files.raw_signal,"a") as f:
            f.write(row)
        return row
    
    def calibrate(self):
        print("calibrating onFS\n")
        lasermeans=np.zeros([7,10]) # 7 tubes x 10 measurements
        for tube in range(7):   
            print("change to tube %d"%(tube))
            mix(0)
            tm.sleep(5)
            mix(1)
            tm.sleep(2)
            for measurement in range(10):
                lasermeans[tube,measurement] = get_laser_signal(tube,r1,r2).onFS
                tm.sleep(0.6)
        weakest_tube=int(np.where(lasermeans.mean(1)==min(lasermeans.mean(1)))[0])
        coefficients=lasermeans.mean(1)/lasermeans.mean(1)[weakest_tube]

        df=pd.DataFrame(lasermeans)
        df.index=["tube_%d"%i for i in range(7)]
        df.plot.bar()
        return coefficients
    def df_update(self):
        pumptimes=pd.read_csv(self.files.pump_data)
        pumptimes.time=pd.to_datetime(pumptimes.time)
        pumptimes.time=pumptimes.time.apply(lambda x: x.tz_convert('Europe/Vienna'))
        self.pumptimes=pumptimes
        
        df=pd.read_csv(self.files.raw_signal)
        df=df[df.iloc[:,0]!="time"].dropna()
        df.time=pd.to_datetime(df.time)
        df.time=df.time.apply(lambda x: x.tz_localize('Europe/Vienna'))
        self.df=df
    
    
    def align_valves(self):
        self.reconnect()
        for t in range(7):
            self.valvepwm(t,1500)

    def open_valves(self):
        for t in range(7):
            self.clamp(t,1)
            time.sleep(0.2)
            
    def close_valves(self):
        for t in range(7):
            self.clamp(t,0)
            time.sleep(0.2)

    def test_lasers(self):
        self.record()
        self.df_update()
        self.df.iloc[-1,1::2].plot.bar()
        
    def plot(self,maximum=1,index=1,xmin=0,xmax=None,figsize=[14,6],savefig=False,
             fast=False,tubes=None):
        assert index in [1,2,3,4]
        assert maximum is None or maximum==1 or type(maximum)==list
        
        if not fast:
            self.df_update()
            
        l,h=[0,self.df.shape[0]]
        
        if type(xmin) is int:
            xmin=str(xmin)+"h"
        if type(xmax) is int:
            xmax=str(xmax)+"h"
        timemin=self.df.time[0]+pd.Timedelta(xmin)
        if xmax is not None:
            timemax=self.df.time.iloc[0]+pd.Timedelta(xmax)
        else:
            timemax=self.df.time.iloc[-1]
            
            
        #Transmittance measurements
        # meas=self.df.iloc[int(l+(h-l)*xmin):int(h-(h-l)*(1-xmax)),index::4].astype(int)
        meas=self.df[(self.df.time>timemin) & (self.df.time<timemax)].iloc[:,index::4].astype(int)
        meas.columns=["0-Ctrl","1-E.Coli","2-Orange","3-Yellow","4-MilkyXG","5-PinkXG","6-White"]
        if tubes is not None:
            assert all(x in range(7) for x in tubes)
            meas=meas.iloc[:,tubes]
        else:
            tubes=list(range(7))
        
#         pe.pumptimes=pe.pumptimes[pe.pumptimes.tube<7]
#         assert all(t in [0,1,2,3,4,5,6] for t in self.pumptimes.tube.unique())
        
        if maximum==1:
            meas=meas/meas.max(0)
        if type(maximum)==list:
            meas=meas/maximum
        fig,axs=plt.subplots(2,1,sharex=True,figsize=figsize,gridspec_kw={"height_ratios":[3,1]})
        ax_OD,ax_pump = axs

#         plt.tight_layout()
        ax_OD.plot(self.df.time[(self.df.time>timemin) & (self.df.time<timemax)],meas,"o:",markersize=0.4)
        ax_OD.invert_yaxis()
        pumptimes=self.pumptimes[(self.pumptimes.time>timemin) & (self.pumptimes.time<timemax)].copy()
        
#         pumptimes.vol/=10 #total pumped volume
#         pumptimes.vol*=50 #ug/ml

        for t in tubes:
            plt.plot("time","vol",data=pumptimes[(pumptimes.tube==t) & (pumptimes.pump=="death")],
                                 marker="x",linestyle=":")
        plt.gca().set_prop_cycle(None)
        for t in tubes:
            plt.plot("time","vol",data=pumptimes[(pumptimes.tube==t) & (pumptimes.pump=="peace")],
                                 marker="o",linestyle=":",fillstyle="none",alpha=0.7)
        plt.gca().set_prop_cycle(None)
        for t in tubes:
            plt.plot("time","vol",data=pumptimes[(pumptimes.tube==t) & (pumptimes.pump=="vacuum")],
                         marker="^",linestyle="None",fillstyle="none",alpha=0.2)
        
        if len(tubes)==1:
            t=tubes[0]
            data=pumptimes[(pumptimes.tube==t) & (pumptimes.pump=="death")]
            A=data.time
            B=data.vol
            for xy in zip(A, B):                                       # <--
                plt.annotate('%.1f' % xy[1], xy=xy, textcoords='data') # <--

            

        ax_pump.set_title("Pumped volumes")
        ax_pump.set_ylabel("Vol [ml]")
        ax_OD.set_ylabel("OD")
        ax_OD.legend(meas.columns)
        ax_OD.set_title("Growth curve")
#         ax_OD.set_yticks([])

        plt.xticks(rotation="vertical");
        axs[0].grid()
        axs[1].grid()
        if savefig:
            plt.savefig(self.files.main_folder+"/"+savefig,dpi=300,bbox_inches='tight')
            plt.close()
        return axs

