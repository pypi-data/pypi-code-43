import psutil
import json
from datetime import datetime
from time import sleep


def process_log(path):
    process_list = []
    aggregate_time = 10
    file_path = path + "/process_log"

    for _ in range(aggregate_time):
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'exe', 'cmdline'])
            except psutil.NoSuchProcess:
                pass
            else:
                process_list.append(pinfo)

        with open(file_path, 'a') as process_file:
            process_file.write(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n")
            for process in process_list:
                process_file.write(json.dumps(process))
                process_file.write('\n')
            process_file.write('------------------------------\n')
        process_list = []
        sleep(1)
