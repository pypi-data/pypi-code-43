from zlgp.src import add_quyu_src,restart_quyu_src

from zlgp.dst import add_quyu_greenplum,restart_quyu_greenplum 
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
from lmf.tool import mythread 
import sys 
import os 
import time 
from zlapp import add_quyu_app
from zlgp import gp_settings
import traceback

def add_quyu_union(quyu,tag,loc='aliyun',mod='111'):

    if mod[0]=='1':add_quyu_src(quyu,tag,loc=loc)
    if mod[1]=='1':add_quyu_greenplum(quyu,tag,loc=loc)
    if mod[2]=='1':add_quyu_app(quyu,loc=loc)

def restart_quyu_union(quyu,loc='aliyun',mod='111'):

    if mod[0]=='1':restart_quyu_src(quyu,loc=loc)
    if mod[0]=='1':restart_quyu_greenplum(quyu,loc=loc)
    #if mod[0]=='1':restart_quyu_app(quyu,loc=loc)


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__



def f_all_thread(num,tag='all',loc='aliyun',mod='110',beg=0,end=None):
    conp_cfg=gp_settings[loc]['conp_cfg']
    quyus=db_query("""SELECT quyu  FROM "public"."cfg" where quyu!~'^zljianzhu' order by quyu """
            ,dbtype="postgresql",conp=conp_cfg)['quyu'].tolist()
    def f(quyu):
        try:
            blockPrint()
            add_quyu_union(quyu,tag=tag,loc=loc,mod=mod)
        except:
            print(quyu,"出错")
        finally:
            enablePrint()


    quyus=quyus[beg:end] if end is not None else  quyus[beg:]
    mythread(quyus,f).run(num)



########add_all###################




def f_all(f,tag,loc='aliyun',start=0,end=None):
    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')
        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng;"""
        ,dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zljianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zljianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public']).iat[0,0]
    df.index=df['sheng']

    total_remain=total
    for sheng in  df.index:
        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            #测试几个
            total_sheng_remain-=1
            total_remain-=1
            if total-total_remain<=start:continue
            if end is not None:
                if total - total_remain>end:return 
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                f(quyu,tag,loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()



def f_zlshenpi(f,tag,loc='aliyun'):

    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlshenpi')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlshenpi' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlshenpi')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlshenpi' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public']).iat[0,0]
    df.index=df['sheng']

    total_remain=total
    for sheng in  df.index:
        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            #测试几个
            #if total-total_remain==2:return
            total_sheng_remain-=1
            total_remain-=1
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                f(quyu,tag,loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()


#add_quyu_union_all('cdc','aliyun')
#f_all(add_quyu_union,'all')


#f_zlshenpi(add_quyu_union,'all')