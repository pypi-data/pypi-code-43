
import time
from zlapp import app_settings
from zlapp.greenplum.api_dag import  tbdag  

#重新生成单个表
def update_tb(name,loc='aliyun'):

    exec("from zlapp.greenplum import %s"%name)

    f=eval('%s.update_%s'%(name,name))
    conp_app5=list(app_settings[loc]['conp_app5'])
    conp_gp=list(app_settings[loc]['conp_gp'])
    conp_app1=list(app_settings[loc]['conp_app1'])


    if name in ['gg_html','gg_html_algo']:
        f(conp_gp,conp_app1)
    elif name in ['qy_zz','qy_base','qy_zcry','t_person'] :
        print("app5中%s 更新"%name)
        f(conp_app5)
        print("gp中%s 更新"%name)
        f(conp_gp)
    else:

        f(conp_app5)

#重新生成表的所有拓扑序列
def plan_tb(name,loc='aliyun'):
    print(time.asctime(time.localtime()))
    if name=='all':
        plan_tb('gg_meta')
        plan_tb('gg_html')
        return 
    tbs=tbdag.tplist(name)
    print("准备更新tbs--",tbs)
    for tb in tbs:
        print("本次更新计划--",tb)
        update_tb(tb,loc)
    print(time.asctime(time.localtime()))



# def update_all(loc):
#     bg=time.time()

#     names=['gg_meta','gg_html','gg','gg_zhongbiao','qy_zhongbiao','xmjl_zhongbiao','app_gg_zhongbiao','app_qy_zz'
#     ,'app_qy_zcry','t_gg_ent_bridge','app_qy_query','bd_dt','bd','t_bd_xflv']

#     for name in names:
#         print(name)
#         update_tb(name,loc)



# def update_all(static=None):
#     bg=time.time()
#     update_gg_meta()
#     update_gg()
#     gg_html.update_gg_html()
#     if static is not None:
#         update_qy_base()
#         update_qy_zcry()
#         update_qy_zz()
#         update_t_person()

#     ###应用表部分
#     update_gg_zhongbiao()
#     update_qy_zhongbiao()
#     xmjl_zhongbiao.update_xmjl_zhongbiao()
#     update_app_gg_zhongbiao()
#     update_app_qy_zz()
#     update_app_qy_zcry()
#     update_t_gg_ent_bridge()
#     update_app_qy_query()
#     bd_dt.update_bd_dt()
#     t_bd_xflv.update_t_bd_xflv()
#     ed=time.time()

#     cost=int(ed-bg)

#     print("耗时 %d 秒"%cost)

#update_all()










