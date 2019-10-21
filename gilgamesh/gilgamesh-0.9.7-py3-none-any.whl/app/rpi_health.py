import os
import zmq
import asyncio
from ..lib.kernel import GK
from ..lib.kontext import Kontext

class RPiHealth(GK):
    def __init__(self, *args, **kwargs):
        GK.__init__(self, *args, **kwargs)
        self.UPDATE_INTERVAL = kwargs['interval']

    async def cpu_temp_producer(self):
        """
        get temperature from thermal_zone0 (package temp on raspi)
        get 1min avg load from /proc
        """
        tags=dict()
        tags['temp_unit'] = 'C'
        tags['tags'] = 'monitor,temperature,load'
        measurement_name = 'cpu_temp'
        while True:
            await asyncio.sleep(self.UPDATE_INTERVAL)
            data = float(self.get_cpu_temp())
            tags['load'] = str(self.get_load())
            self.glog.debug("System Temp: {0} C".format(data))
            await self.send_data(self.dev_id, measurement_name, {'temp': data}, tags)

    async def free_mem_producer(self):
        """
        get total memory
        get free memory and calculate free percentage
        """
        tags=dict()
        tags['free_unit'] = 'MB'
        tags['tags'] = 'monitor,free,memory'
        measurement_name = 'free_mem'
        _ , total = self.get_free()
        tags['total'] = str(total)
        while True:
            await asyncio.sleep(self.UPDATE_INTERVAL)
            free, _ = self.get_free()
            tags['percent'] = str(round((free/total)*100, 1))
            self.glog.debug(f'Free Mem: {free}/{total} MB')
            await self.send_data(self.dev_id, measurement_name, {'free': free}, tags)

    def get_cpu_temp(self):
        temp = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
        return float(temp)/1000.0

    def get_load(self):
        load = os.popen('cat /proc/loadavg').readline()
        load_1min = load.split(" ")[0]
        return float(load_1min)

    def get_free(self):
        cmd = '''awk '{ if (/MemAvailable:/) {mem_available=$2}; if (/MemTotal:/) {mem_total=$2};
        if (mem_available && mem_total) {print int(mem_available/1024) " " int(mem_total/1024);exit}}' /proc/meminfo'''
        free, total = os.popen(cmd).readline().split(" ")
        return int(free), int(total)

def rpi_health_process(kcfg):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    kcfg['context'] = Kontext()
    kcfg['loop'] = loop
    
    rpi = RPiHealth(**kcfg)
    loop.create_task(rpi.cpu_temp_producer())
    loop.create_task(rpi.free_mem_producer())
    # gpio control for testing
    # loop.create_task(rpi.control())
    rpi.start()
