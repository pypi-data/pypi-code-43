from zlapp import forbiden_list,  app_settings
from lmf.dbv2 import db_query ,db_command



# def et_gg_meta(conp_src,conp_dst,conp_cfg):
#     quyus=db_query("select quyu from cfg where quyu!~'zljianzhu' ",dbtype="postgresql",conp=conp_cfg)['quyu'].tolist()
#     for w in forbiden_list:
#         print(w)
#         quyus.remove(w)
#     #quyus.append('zljianzhu_zljianzhu')
#     txt=':'.join(quyus)
#     sql="drop external table if exists public.et_gg_meta;"
#     db_command(sql,dbtype="postgresql",conp=conp_dst)
#     user,passwd,host,db,schema=conp_src 
#     sql="""
#     create  external table public.et_gg_meta(html_key bigint,
#     guid text,
#     gg_name text,
#     href text,
#     fabu_time timestamp,
#     ggtype text,
#     jytype text,
#     diqu text,
#     quyu text,
#     info text,
#     create_time timestamp,
#     xzqh text,
#     ts_title text,
#     bd_key bigint,
#     person text,
#     price text,
#     zhaobiaoren text,
#     zhongbiaoren text,
#     zbdl text,
#     zhongbiaojia float,
#     kzj float8,
#     xmmc text,
#     xmjl text,
#     xmjl_zsbh text,
#     xmdz text,
#     zbfs text,
#     xmbh text,
#     mine_info text
#     )
#     LOCATION ('pxf://dst.gg_meta?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=%s&PASS=%s&PARTITION_BY=quyu:enum&RANGE=anhui_anqing_ggzy:anhui_chaohu_ggzy')
#     FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
#     """%(user,passwd)
#     sql=sql.replace("anhui_anqing_ggzy:anhui_chaohu_ggzy",txt)
#     sql=sql.replace("192.168.4.183:5433",host)
#     db_command(sql,dbtype="postgresql",conp=conp_dst)

def et_gg_meta(conp_src,conp_dst,conp_cfg):
    quyus=forbiden_list
    quyus=','.join([ "'%s'"%w for w in quyus])
    sql="""
    create or replace  view  dst.gg_meta_1 as 
    select * from dst.gg_meta where quyu not in (%s)
    """%quyus
    db_command(sql,dbtype="postgresql",conp=conp_src)

    sql="drop external table if exists public.et_gg_meta;"
    db_command(sql,dbtype="postgresql",conp=conp_dst)
    user,passwd,host,db,schema=conp_src 
    sql="""
    create  external table public.et_gg_meta(html_key bigint,
    guid text,
    gg_name text,
    href text,
    fabu_time timestamp,
    ggtype text,
    jytype text,
    diqu text,
    quyu text,
    info text,
    create_time timestamp,
    xzqh text,
    ts_title text,
    bd_key bigint,
    person text,
    price text,
    zhaobiaoren text,
    zhongbiaoren text,
    zbdl text,
    zhongbiaojia float,
    kzj float8,
    xmmc text,
    xmjl text,
    xmjl_zsbh text,
    xmdz text,
    zbfs text,
    xmbh text,
    mine_info text
    )
    LOCATION ('pxf://dst.gg_meta_1?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=%s&PASS=%s&PARTITION_BY=html_key:int&RANGE=1:50000000&INTERVAL=200000')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(user,passwd)
 
    sql=sql.replace("192.168.4.183:5433",host)
    db_command(sql,dbtype="postgresql",conp=conp_dst)




def et_gg_html(conp_src,conp_dst):
    user,passwd,host,db,schema=conp_src 
    sql="""
    drop external table if exists public.et_gg_html;
    create  external table public.et_gg_html(html_key bigint,
    page text
    )
    LOCATION ('pxf://src.t_gg?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=%s&PASS=%s&PARTITION_BY=html_key:int&RANGE=1:40000000&INTERVAL=10000')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(user,passwd)
    sql=sql.replace("192.168.4.183:5433",host) 
    db_command(sql,dbtype="postgresql",conp=conp_dst)


def et_qy_base(conp_src,conp_dst):
    #conp_src=['postgres','since2015','192.168.4.188','bid','public']
    #conp_dst=['gpadmin','since2015','192.168.4.206','biaost','public']
    user,passwd,host,db,schema=conp_src 
    sql="""
    drop external table if exists public.et_qy_base;
    create  external table public.et_qy_base(ent_key bigint,    jgmc text,  tydm text,  zch text,   jgdm text,  entid text, clrq  timestamp(6),
        jgdz text,  fddbr text ,    jyfw text   ,jjhy    text, jglx text,   zczj    text,
    zczj_bz text,   zczj_sj text,   zczj_sj_bz text,    taxdm    text, fromtime timestamp(6),    totime  timestamp(6) , djbumen text, jyzt   text,
    engname text,bondnum text,  zggm text,  email    text, phone text,  website  text,staff_info    text,
    alias text, diaoxiaodate text,  diaoxiaoreason   text,zhuxiaodate text, zhuxiaoreason text, logo text,  sh_info text,   xzqh  text  )
        LOCATION ('pxf://public.qy_base?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/%s&USER=%s&PASS=%s')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,db,user,passwd)

    db_command(sql,dbtype="postgresql",conp=conp_dst)




def et_qy_zcry(conp_src,conp_dst):
    user,passwd,host,db,schema=conp_src 
    sql="""
        drop external table if exists public.et_qy_zcry;
    create  external table public.et_qy_zcry(ent_key bigint,    tydm text,  xzqh text,  ryzz_code text,
    href text,  name    text ,gender text,  zjhm text,  zj_type text,   zclb text,  zhuanye  text, zsbh text,   yzh  text ,youxiao_date text,   entname text, person_key bigint  )
        LOCATION ('pxf://public.qy_zcry?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/%s&USER=%s&PASS=%s&PARTITION_BY=person_key:int&RANGE=1:5000000&INTERVAL=10000')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,db,user,passwd)

    db_command(sql,dbtype="postgresql",conp=conp_dst)


def et_qy_zz(conp_src,conp_dst):
    user,passwd,host,db,schema=conp_src 
    sql="""
    drop external table if exists public.et_qy_zz;
    create  external table public.et_qy_zz(href text    ,zzbh text ,    gsd text ,  jglx text , zzmc text , bgdate text ,   eddate text ,   fbjg text , tydm text , fddbr text ,    
    zzlb text   ,entname text , jgdz text   ,qita    text ,ent_key bigint,  xzqh text   ,zzcode text ,  alias text  )
            LOCATION ('pxf://public.qy_zz?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/%s&USER=%s&PASS=%s')
            FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,db,user,passwd)
    db_command(sql,dbtype="postgresql",conp=conp_dst)



def et_t_person(conp_src,conp_dst):
    user,passwd,host,db,schema=conp_src 
    sql="""
        drop external table if exists public.et_t_person;
    create  external table public.et_t_person(person_key bigint,    name text,  zj_type text,   zjhm  text )
        LOCATION ('pxf://public.t_person?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/%s&USER=%s&PASS=%s')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,db,user,passwd)
    db_command(sql,dbtype="postgresql",conp=conp_dst)





def et_restart(tbname,loc='aliyun'):

    conp_cfg=app_settings[loc]['conp_cfg']
    conp_dst=app_settings[loc]['conp_app5']
    conp_src=app_settings[loc]['conp_gp']
    conp_src_md=app_settings[loc]['conp_md']

    if tbname=='gg_meta':
        sql="drop external table if exists public.et_%s;"%tbname
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp_dst)
        print("重建et_%s"%tbname)
        et_gg_meta(conp_src,conp_dst,conp_cfg)
    elif tbname in ['gg_html']:
        sql="drop external table if exists public.et_%s;"%tbname
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp_dst)
        print("重建et_%s"%tbname)
        f=eval("et_%s"%tbname)
        f(conp_src,conp_dst)
    elif tbname in ['qy_base','qy_zcry','qy_zz','t_person']:
        print("app5中%s"%tbname)
        sql="drop external table if exists public.et_%s;"%tbname
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp_dst)
        print("重建et_%s"%tbname)
        f=eval("et_%s"%tbname)
        f(conp_src_md,conp_dst)

        print("gp中%s"%tbname)
        sql="drop external table if exists public.et_%s;"%tbname
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp_src)
        print("重建et_%s"%tbname)
        f=eval("et_%s"%tbname)
        f(conp_src_md,conp_src)

    else:
        print("未知表")





