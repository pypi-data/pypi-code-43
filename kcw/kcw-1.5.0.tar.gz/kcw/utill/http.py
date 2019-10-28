import requests,traceback
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class Http:
    "http请求类"
    set_proxies=None  #设置代理
    set_cookies={} #设置请求cookie
    set_header={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'} #请求头
    set_timeout=10 #超时 20秒
    set_verify=False  #SSL 证书的验证 sll证书路径
    set_encoding="utf-8" #设置text输出编码
    set_session=False #是否启用会话

    get_header={} #响应头
    get_cookies={} #得到最后的响应cookie
    get_text='' #得到body响应内容
    get_content='' #得到二进制内容
    get_response='' #得到响应对象
    get_status_code=None #响应状态码
    
    req=None
    def gettext(self):
        """得到响应text"""
        return self.get_text
    def httpurl(self,url,method="GET",data=None,files=None):
        """模拟浏览器请求

        url : 目标地址

        method ：GET POST

        data：请求参数
        """
        if self.set_session:
            if self.req is None:
                self.req = requests.Session()
        else:
            if self.req is None:
                self.req = requests
        if self.set_cookies and isinstance(self.set_cookies,str):
            self.cookieserTdict()
        # print(self.req_header)
        try:
            response=self.req.request(method, url,data=data,files=files,proxies=self.set_proxies,cookies=self.set_cookies,headers=self.set_header,timeout=self.set_timeout,verify=self.set_verify)
        except Exception as e:
            print(traceback.print_exc())
            self.get_text=None
            self.get_content=None
            self.get_status_code=0
        else:
            response.encoding=self.set_encoding
            self.get_header=response.headers
            cookie=requests.utils.dict_from_cookiejar(response.cookies)
            if self.get_cookies and cookie:
                self.get_cookies=self.__merge(self.get_cookies,cookie)
            elif cookie:
                self.get_cookies=cookie
            if self.set_cookies:
                self.get_cookies=self.__merge(self.set_cookies,self.get_cookies)
            self.get_text=response.text
            self.get_content=response.content
            self.get_response=response
            self.get_status_code=int(response.status_code)
            # print(self.req_header)
    def __merge(self,dict1, dict2):
        "合并两个字典"
        C_dict = {}
        for key,value in dict1.items():
            C_dict[key]=value
        for key,value in dict2.items():
            C_dict[key]=value
        return C_dict
    def cookieserTdict(self):
        "cookies字符串转换字典"
        if isinstance(self.set_cookies,str):
            cok={}
            for line in self.set_cookies.split(";"):
                lists=line.split("=",1)
                # print(lists[])
                if lists[0]:
                    cok[lists[0]]=lists[1]
            self.set_cookies=cok