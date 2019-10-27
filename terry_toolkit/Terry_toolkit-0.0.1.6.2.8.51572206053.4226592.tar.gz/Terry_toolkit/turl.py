#coding=utf-8
import requests
import urllib.request
import sys

class Url:
    """Url相关的操作库



    """
    def open_url(self, url):
        """
        安全有效的打开url
        可以自动预测编码问题

        >>> open_url(url)

        """

        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        resp = requests.get(url,headers=headers) #请求


        # resp=requests.get(myurl)
        # print (resp.encoding)
        resp.encoding = resp.apparent_encoding
        # print (resp.encoding)
        txt = resp.text #获取响应的html内容

        # print (txt)
        return txt
    def open_url_v4(self, url):
        """
        安全有效的打开url

        >>> open_url(url)

        # req = request.build_opener(url)
        # req.add_header(
        #     'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0')
        # response = urllib.request.urlopen(req)
        # r = requests.get(url)
        # r.status_code
        # r.encoding = 'utf-8'
        # r.text
        # html = response.read().decode('utf8')  # gbk格式的
        # opener = urllib.request.build_opener()
        # opener.addheaders = [('User-agent',  # 添加模拟浏览器访问的header信息
        #                       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')]
        # html = opener.open(url).read().decode()
        # html = requests.get(url, timeout=10).content.decode('utf-8')


        """
        req = urllib.request.Request(url)
        req.add_header(
            'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0')
        response = urllib.request.urlopen(req)
        html=''
        type = sys.getfilesystemencoding()   # 关键
        try:
            print('utf')
            html = response.read().decode('utf-8').encode(type)  # 关键
        except:
            # html = response.read().decode('gb2312')
            print('gbk')

            html = response.read().decode('GB18030').encode(type)  # 关键
            print(html)
            return False

        return html
    def open_url_v1(self, url):
        # r = requests.get(url)
        r = requests.get(url, allow_redirects=True)

        print(r.url)
        print('r.status_code',r.status_code)
        print(' r.history', r.history)
        r.encoding='utf-8' #显式地指定网页编码，一般情况可以不用**

        return r.text
        pass
    def open_url_v2(self,url):
        # print '请求地址：{}'.format(url)
        '''
        '''
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel …) Gecko/20100101 Firefox/58.0'}
        resp = requests.get(url,headers=headers) #请求
        # print '请求完成'
        if not resp:
            # print '无响应内容'
            print('无响应内容')
            return
            html=requests.get(myurl)

        # print '响应:\nencoding={}'.format(resp.encoding)  #如果中文乱码，如果requests没有发现http headers中的charset
        # resp.encoding='utf-8' #设置响应编码（gbk、utf-8、gb2312）
        txt = resp.text.encode(resp.encoding) #获取响应的html内容
        # print '原始：\n{}'.format(txt)
        # print '响应:\nencoding={}'.format(resp.encoding)
        return txt

    def open_url_v3(self,url):
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel …) Gecko/20100101 Firefox/58.0'}
        resp = requests.get(url,headers=headers) #请求
        # print '请求完成'
        if not resp:
            # print '无响应内容'
            print('无响应内容')
            return
        print (resp.encoding)

        # print '响应:\nencoding={}'.format(resp.encoding)  #如果中文乱码，如果requests没有发现http headers中的charset
        # resp.encoding='utf-8' #设置响应编码（gbk、utf-8、gb2312）
        txt = resp.text.encode(resp.encoding) #获取响应的html内容

        return txt

    def open_url_v5(self,url):
        """
        自动编码获取内容

        >>> open_url_v5(url)


        """
        raw_html = urllib.request.urlopen(url).read()
    #     raw_html = requests.urlopen(url).read()
        if not raw_html:
            return ''
        best_match = ('', 0)
        for charset in ['utf-8', 'gbk', 'big5', 'gb18030']:
            try:
                unicode_html = raw_html.decode(charset, 'ignore')
                guess_html = unicode_html.encode(charset)
                if len(guess_html) == len(raw_html):
                    best_match = (charset, len(guess_html))
                    break
                elif len(guess_html) > best_match[1]:
                    best_match = (charset, len(guess_html))
            except:
                pass
        raw_html = raw_html.decode(best_match[0], 'ignore').encode('utf-8')
        return raw_html
