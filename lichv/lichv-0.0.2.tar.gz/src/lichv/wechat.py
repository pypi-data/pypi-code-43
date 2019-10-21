#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import requests
import datetime
import json
 
class Wechat:

    def __init__(self, appid='xxx', appsecret='xxxx'):
        self.appid = appid
        self.appsecret = appsecret

    def getTicket(self):
        result = None
        headers = {'content-type': 'application/json'}
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+self.appid+'&secret='+self.appsecret
        try:
            r = requests.get(url, headers=headers)
            r.encoding='utf-8'
            try:
                tmp = json.loads(r.text)
                if tmp and 'access_token' in tmp:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    expired_at = (datetime.datetime.now() + datetime.timedelta(seconds=int(tmp['expires_in']))).strftime('%Y-%m-%d %H:%M:%S')
                    result = {'access_token':tmp['access_token'],'created_at':now,'expires_in':tmp['expires_in'],'expired_at':expired_at}
            except Exception as e:
                pass
        except Exception as e:
            pass
        return result

    def sendTemplate(self,access_token,openid,template_id,data,url=''):
        result = None
        send_data = {
            "touser":openid,
            "template_id":template_id,
            "data":data
        }
        if url:
            send_data['url'] = url
        wechat_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='+access_token
        headers = {'content-type': 'application/json'}
        try:
            r = requests.post(wechat_url, data=json.dumps(send_data), headers=headers)
            r.encoding='utf-8'
            try:
                result = json.loads(r.text)
            except Exception as e:
                pass
        except Exception as e:
            pass
        return result

if __name__ == "__main__":
    service = Wechat( appid='wx3e4516ab7a091b13', appsecret='074603f16568bd289bbd2bed935d93cc')
    data = {
             "first": {
                 "value":"您有一个流程通过了审核！",
                 "color":"#173177"
             },
             "keyword1":{
                 "value":"信息系统项目管理师考前培训",
                 "color":"#173177"
             },
             "keyword2": {
                 "value":"08月24日",
                 "color":"#173177"
             },
             "remark":{
                 "value":"欢迎再次购买！",
                 "color":"#173177"
             }
           }
    token = service.getTicket()
    result = service.sendTemplate(token['access_token'],'od9fusj94u2_oYfUqJQUgWxnoI-s',"lsHGcsY6oFDxIIEszk-_Ngv58kTjsbRzsRGA4wLQ43U",data)
    print(result)

