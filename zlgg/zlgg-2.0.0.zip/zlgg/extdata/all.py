

 
from zlgg.clear import  tb_clear,ps_clear
from zlgg.extdata.table import tb 
from zlgg.extdata.ps import ps 
from zlgg.core import to_arr 

def extall(page,krr):

    tbs=tb_clear(page)

    p=ps_clear(page)
    if tbs is None:tbs_dict=None
    else:

        tbs_dict=[tb(tbpage,krr) for tbpage in tbs]

    p_dict=ps(p,krr)
    data={"tbs":tbs_dict,'ps':p_dict}
    return data
