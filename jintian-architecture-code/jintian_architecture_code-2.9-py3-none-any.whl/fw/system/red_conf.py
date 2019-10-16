import configparser
import os
from com.fw.base.base_exception import BaseException
import sys




class SystemConf(object):
    def __init__(self):
        work_dir = os.getcwd()

        if("com" in work_dir):
            work_dir = work_dir[:work_dir.index("com")-1]

        resource_dir = os.path.join(work_dir, 'resource','system.conf')

        if os.path.exists(resource_dir) == False:

            f = open(resource_dir, 'w')
            f.close()

            raise BaseException("缺少必要配置文件，请填写配置文件...")

        self.cf = configparser.ConfigParser()
        self.cf.read(resource_dir)

    def get_value(self, group, name):
        return self.cf.get(group, name)

    def get_group_item(self, group):
        return self.cf.items(group);

    def has_group(self,grop):
        return self.cf.has_section(grop)

system_conf = SystemConf();

