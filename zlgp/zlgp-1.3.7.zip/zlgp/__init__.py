
gp_settings={
    "kunming":{
        "conp_cfg":['postgres','since2015','192.168.169.89','postgres','public'],

        "conp_gp":['developer','zhulong!123','192.168.169.91:5433','base_db','public'],

        "conp_pg_zlmine":['postgres','since2015','192.168.169.89','zlmine','t_bd']
    }
    ,

    "aliyun":{
        "conp_cfg":['postgres','since2015','192.168.4.201','postgres','public'],

        "conp_gp":['developer','zhulong!123','192.168.4.183:5433','base_db','public'],

        "conp_pg_zlmine":['postgres','since2015','192.168.4.201','zlmine','t_bd']
    }

}

from zlgp.api import add_quyu_src,restart_quyu_src
from zlgp.api import add_quyu_greenplum,restart_quyu_greenplum
from zlgp.api import add_quyu_union,restart_quyu_union

from zlgp.api import f_all,f_zlshenpi