from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst import algo,bid,bid_bridge 
import traceback
from zlgp.dst import api
def add_quyu(quyu,tag='all',loc='aliyun'):
    print("---------------------------add--src(%s)-->dst---------------------------------"%quyu)
    if quyu.startswith('zlsys'):
        bid.add_quyu(quyu,tag,loc=loc)

        bid_bridge.add_quyu(quyu,tag,loc=loc)

        api.add_quyu(quyu,tag,loc=loc)

    elif quyu.startswith('zlshenpi'):


        api.add_quyu(quyu,tag,loc='loc')

    else:

        bid.add_quyu(quyu,'cdc',loc=loc)

        bid_bridge.add_quyu(quyu,tag,loc=loc)

        algo.add_quyu(quyu,tag,loc=loc)

        api.add_quyu(quyu,tag,loc=loc)



def restart_quyu(quyu,loc='aliyun'):
    print("---------------------------restart--src(%s)-->dst---------------------------------"%quyu)
    if quyu.startswith('zlsys'):
        bid.restart_quyu(quyu,loc=loc)

        bid_bridge.restart_quyu(quyu,loc=loc)

        api.restart_quyu(quyu,loc=loc)

    elif quyu.startswith('zlshenpi'):


        api.restart_quyu(quyu,loc=loc)
    else:

        bid.api.restart_quyu(quyu,loc=loc)

        bid_bridge.restart_quyu(quyu,loc=loc)

        algo.api.restart_quyu(quyu,loc=loc)

        api.restart_quyu(quyu,loc=loc)





#---------------------------------