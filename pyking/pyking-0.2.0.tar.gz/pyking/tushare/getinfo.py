import requests
import json

url = 'http://www.kingtql.xyz:888/'


def Refresh():
    '''
    刷新数据库中的股票信息
    '''
    cc = 'Refresh'
    url1 = url + cc
    html = requests.get(url1)
    ret = html.json()
    return ret


def Search(style: str, info: str):
    """
    股票信息查询
    参数1：查询方式 
      可选项:'symbol'或'name'
    参数2：参数值 
      例:'603696'或'中联重科'
    """
    cc = 'Search'
    url2 = url + cc
    if style != '':
        if style == 'symbol':
            data = {
                'style': 'symbol',
                'symbol': info,
                'name': ''
            }
        if style == 'name':
            data = {
                'style': 'name',
                'symbol': '',
                'name': info,
            }
    else:
        return '查询方式为空'
    html = requests.post(url2, data=data)
    ret = html.json()
    return ret
