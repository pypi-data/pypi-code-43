#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : spark_submit
# @Time         : 2019-07-16 16:50
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
import yaml
import os


def spark(config=None, **kwargs):
    """

    :param config: 配置文件
    :param kwargs:
    :return:
        ~/infra-client/bin/spark-submit
        --name SparkApp
        --cluster zjyprc-hadoop
        --master yarn-cluster
        --queue production.miui_group.browser.miui_browser_zjy_1
        --num-executors 64
        --executor-cores 2
        --executor-memory 6g
        --driver-memory 6g
        --conf spark.yarn.job.owners=yuanjie
        --conf spark.yarn.alert.phone.number=18550288233
        --conf spark.yarn.alert.mail.address=yuanjie@xiaomi.com
        --conf spark.driver.maxResultSize=4g
        --conf spark.sql.catalogImplementation=in-memory
        --conf "spark.executor.extraJavaOptions=-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:MaxDirectMemorySize=512m"
        --class WordVectorTrain
         Spark-Nanjing-1.0-SNAPSHOT.jar
    """
    if config:
        if os.path.exists(config):
            try:
                with open(config) as f:
                    _ = yaml.safe_load(f)
                config_map = _ if isinstance(_, dict) else {}
            except Exception as e:
                print("读取配置文件错误：%s" % e.__str__())
                config_map = {}
        else:
            print("未找到配置文件")
            config_map = {}
    else:
        config_map = {}

    opt = {**config_map, **kwargs}

    # _dic = {'class': 'WordVectorTrainPlus',
    #         'jar': 'Spark-Nanjing-1.0-SNAPSHOT.jar',
    #         'name': 'SparkApp',
    #         'owners': 'yuanjie',
    #         'phone': 18550288233,
    #         'mail': 'yuanjie@xiaomi.com',
    #         'num_executors': 64,
    #         'executor_cores': 2,
    #         'driver_memory': '6g',
    #         'executor_memory': '6g',
    #         'master': 'yarn-cluster',
    #         'cluster': 'zjyprc-hadoop',
    #         'queue': 'production.miui_group.browser.miui_browser_zjy_1'}
    # with open('./spark_config.yml', 'w') as f:
    #     yaml.dump({**_dic, **opt}, f, default_flow_style=False)
    # print(opt)

    cmd = f"""
            ~/infra-client/bin/spark-submit
            --cluster {opt.get('cluster', 'zjyprc-hadoop')}
            --master {opt.get('master', 'yarn-cluster')}
            --queue {opt.get('queue', 'production.miui_group.browser.miui_browser_zjy_1')}
            --name {opt.get('name', 'SparkApp')}
            --num-executors {opt.get('num_executors', 8)}
            --executor-cores {opt.get('executor_cores', 2)}
            --executor-memory {opt.get('executor_memory', '6g')}
            --driver-memory {opt.get('driver_memory', '6g')}
            --conf spark.sql.autoBroadcastJoinThreshold={opt.get('BroadcastJoinThreshold', -1)}
            --conf spark.driver.executor.directMemoryOverhead=8g
            --conf spark.driver.maxResultSize=4g
            --conf spark.yarn.executor.memoryOverhead=8g
            --conf spark.yarn.executor.directMemoryOverhead=8g
            --conf spark.yarn.executor.jvmMemoryOverhead=4g
            --conf spark.yarn.job.owners={opt.get('owners')}
            --conf spark.yarn.alert.phone.number={opt.get('phone')}
            --conf spark.yarn.alert.mail.address={opt.get('mail')}
            --conf spark.sql.catalogImplementation=in-memory
            --conf "spark.executor.extraJavaOptions=-XX:+PrintGCDetails -XX:+PrintGCTimeStamps -XX:MaxDirectMemorySize=4096m"
            --class {opt.get('class', '😝 请指定类名')}
             {opt.get('jar', 'Spark-Nanjing-1.0-SNAPSHOT.jar')}
            """
    print(cmd)
    # print(cmd.replace('\n', ' '))
    os.popen(cmd.strip().replace('\n', ' ')).read()


if __name__ == '__main__':
    spark('./spark.yml')

# class SparkSubmit(object):
#
#     def __init__(self, config="/Users/yuanjie/Desktop/Projects/Python/tql-CLI/clidog/clis/spark_submit.yml", **kwargs):
#         with open(config) as f:
#             cfg = {**yaml.safe_load(f), **kwargs}
#         print(cfg)
#         for k, v in cfg.items():
#             setattr(self, k, v)
#
#         cmd = f"""
#                 ~/infra-client/bin/spark-submit
#                 --name {self.name}
#                 --cluster {self.cluster}
#                 --master yarn-cluster
#                 --queue {self.queue}
#                 --num-executors {self.num_executors}
#                 --executor-cores {self.executor_cores}
#                 --executor-memory {self.executor_memory}
#                 --driver-memory {self.driver_memory}
#                 --conf spark.yarn.job.owners={self.owners}
#                 --conf spark.yarn.alert.phone.number={self.phone}
#                 --conf spark.yarn.alert.mail.address={self.mail}
#                 --conf spark.driver.maxResultSize=4g
#                 --conf spark.sql.catalogImplementation=in-memory
#                 --class {self.main_class}
#                 {self.jar}
#                 """
#         print(cmd)
#         os.popen(cmd).read()
