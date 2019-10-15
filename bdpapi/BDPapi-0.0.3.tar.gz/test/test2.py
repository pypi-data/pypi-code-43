

import requests


# parm = {'access_token': '12f803b5bbf9f7b62bb701588a6aaee5', 'ds_id': 'tb_1dd3308d87614eaa93b95ef4c2c944d6'}
parm = {'access_token': '12f803b5bbf9f7b62bb701588a6aaee5'}
# r = requests.get('https://open.bdp.cn/api/tb/list', params=parm)
r = requests.get('https://open.bdp.cn/api/ds/list', params=parm)
c = r.json()
print (c)