import psutil
from time import sleep
from datetime import datetime


def system_log(path):
    aggregate_time = 10
    file_path = path + "/system_log"
    cpu_sum = 0
    disk_sum = 0
    memory_sum = 0
    swap_sum = 0

    for _ in range(aggregate_time):
        cpu_percent = psutil.cpu_percent()

        memory_usage = round(psutil.virtual_memory().used / 1024 ** 2, 2)
        memory_all = round(psutil.virtual_memory().total / 1024 ** 2, 2)
        memory_percent = psutil.virtual_memory().percent

        disk_usage = round(psutil.disk_usage('/').used / 1024 ** 2, 2)
        disk_all = round(psutil.disk_usage('/').total / 1024 ** 2, 2)
        disk_percent = psutil.disk_usage('/').percent

        swap_percent = psutil.swap_memory().percent

        with open(file_path, 'a') as sys_file:
            sys_file.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\t")
            sys_file.write("CPU Usage: {}% \t".format(cpu_percent))
            sys_file.write("Memory Usage: {0}/{1}MB ({2}%)\t".format(memory_usage, memory_all, memory_percent))
            sys_file.write("Disk Usage: {0}/{1}MB ({2}%)\t".format(disk_usage, disk_all, disk_percent))
            sys_file.write("Swap Usage: {}%\t".format(swap_percent))
            sys_file.write("\n")

        cpu_sum += cpu_percent
        disk_sum += disk_percent
        memory_sum += memory_percent
        swap_sum += swap_percent

        sleep(1)

    with open(file_path, 'a') as sys_file:
        sys_file.write("----------Average----------\n")
        sys_file.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\t")
        sys_file.write("CPU Usage: {}%\t".format(round(cpu_sum / aggregate_time, 2)))
        sys_file.write("Memory Usage: {}%\t".format(round(memory_sum / aggregate_time, 2)))
        sys_file.write("Disk Usage: {}%\t".format(round(disk_sum / aggregate_time, 2)))
        sys_file.write("Swap Usage: {}%\t".format(round(swap_sum / aggregate_time, 2)))
