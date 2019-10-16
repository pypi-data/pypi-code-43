# !/usr/bin/env python
# coding=utf-8

from pzhive import pzhive

cursor = pzhive.connect(host="gdc-sparkserver09-horton.i.nease.net",
                        port=20010,
                        auth="KERBEROS",
                        configuration={"hive.server2.proxy.user": "mpay_bu"},
                        kerberos_service_name="hive",
                        kerberos_service_host="gdc-sparkserver09-horton.i.nease.net",
                        database="default")

cursor.execute("show tables")
print(cursor.fetchall())

cursor.close()

print("=====================================================")


cursor = pzhive.connect(host="gdc-sparkserver09-horton.i.nease.net",
                        port=20010,
                        auth="KERBEROS",
                        configuration={"hive.server2.proxy.user": "mpay_bu"},
                        kerberos_service_name="hive",
                        database="default")

cursor.execute("show tables")
print(cursor.fetchall())

cursor.close()

print("=====================================================")

cursor = pzhive.connect_by_zk(zk_url="monitor.zk.gdc.x.netease.com:2181",
                              zk_name_space="kyuubi-mpay-ha",
                              auth="KERBEROS",
                              configuration={"hive.server2.proxy.user": "mpay_bu"},
                              kerberos_service_name="hive",
                              kerberos_service_host="_host",
                              database="default")

cursor.execute("show tables")
print(cursor.fetchall())

cursor.close()

print("=====================================================")

cursor = pzhive.connect_by_zk(zk_url="monitor.zk.gdc.x.netease.com:2181",
                              zk_name_space="kyuubi-mpay-ha",
                              auth="KERBEROS",
                              configuration={"hive.server2.proxy.user": "mpay_bu"},
                              kerberos_service_name="hive")

cursor.execute("show tables")
print(cursor.fetchall())

cursor.close()

print("=====================================================")

cursor = pzhive.connect_by_zk(zk_url="monitor.zk.gdc.x.netease.com:2181",
                              zk_name_space="kyuubiserver",
                              auth="KERBEROS",
                              configuration={"hive.server2.proxy.user": "hadoop"},
                              kerberos_service_name="hive",
                              kerberos_service_host="hiveserver",
                              database="default")

cursor.execute("show tables")
print(cursor.fetchall())
