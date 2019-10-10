from zlhawq.data import zl_shenpi_dict

import sys
def write_zlshenpi():
    txts=["from collections import defaultdict","from zlapp.all import *"]
    roads=['\n','def choose_func_zlshenpi(quyu):','   roads={']
    zlshenpi_quyus=zl_shenpi_dict['zlshenpi']
    zlshenpi_quyus=list(set(zlshenpi_quyus))
    zlshenpi_quyus.sort()

    for quyu in zlshenpi_quyus:
        db,schema=quyu.split('_')[0],'_'.join(quyu.split('_')[1:])

        r="""       "%s":ext_%s,"""%(quyu,schema)

 
        roads.append(r)
    roads.append('       }')
    roads.append('   a=defaultdict(lambda :None)')
    roads.append('   a.update(roads)')
    roads.append('   return a[quyu]')
    ts='\n'.join(txts) 
    rs='\n'.join(roads)
    with open(sys.path[0]+"\\zlshenpi_work.py",'w',encoding='utf8' ) as f:
        f.write(ts)
        f.write(rs)
