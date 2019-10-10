from queue import Queue 


#app后台有向无图 

class tbdag:
    arr=set()
    data=[
    ('gg_meta','gg'),('gg_meta','bd'),('gg_meta','t_gg_ent_bridge'),
    ('gg','gg_zhongbiao'),('gg','t_bd_xflv'),('gg','bd_dt'),
    ('gg_zhongbiao','qy_zhongbiao'),('gg_zhongbiao','xmjl_zhongbiao'),('gg_zhongbiao','app_gg_zhongbiao'),

    ('qy_zhongbiao','app_qy_zz'),('qy_zhongbiao','app_qy_query'),('qy_zhongbiao','app_gg_zhongbiao'),

    ('xmjl_zhongbiao','app_qy_zcry'),

    ('qy_zz','app_qy_zz'),('qy_zz','app_qy_query'),

    ('qy_base','app_qy_zz'),('qy_base','app_qy_query'),('qy_base','t_gg_ent_bridge'),

    ('qy_zcry','app_qy_zcry'),('qy_zcry','app_qy_query'),

    ('t_person','app_qy_query'),
    ('gg_html','gg_html_algo')
    ]
    arr=set(data)
    @staticmethod
    def get_next(item):
        data=[]
        for w in tbdag.arr:
            if w[0]==item:data.append(w[1])

        return data

    @staticmethod
    def get_pre(item):
        data=[]
        for w in tbdag.arr:
            if w[1]==item:data.append(w[0])
        return data

    @staticmethod
    def tplist(item):
        result=[item]
        q=Queue()
        q.put(item)
        while not q.empty():
            x=q.get()
            y=tbdag.get_next(x)
            if y !=[]:
                for w in y:
                    result.append(w)
                    q.put(w)
        return result








