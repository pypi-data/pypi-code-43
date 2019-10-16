#!/usr/local/bin/python
#-*- coding: UTF-8 -*-
#author:lol

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
import requests
import json
import jsonpath_rw_ext as jp
import smtplib, time, os
from email.mime.text import MIMEText
from email.header import Header

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
import pandas as pd


#处理dict中为unicode编码的转化去掉u'
def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value =decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv
#去掉list中unicode 编码的问题，去掉u'
def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv



#请求结果
def get_result_data(url):
    req = {}
    req = requests.get(url)
    req = decode_dict(req.json())
    return req

def assemble_html(project_name,html,job_url):
    '''发送html内容邮件'''
    #发送邮箱
    head = \
        """
        <head>
            <meta charset="utf-8">
            <STYLE TYPE="text/css" MEDIA=screen>

                table.dataframe {
                    border-collapse: collapse;
                    border: 2px solid #a19da2;
                    /*居中显示整个表格*/
                    margin: auto;
                }

                table.dataframe thead {
                    border: 2px solid #91c6e1;
                    background: #f1f1f1;
                    padding: 10px 10px 10px 10px;
                    color: #333333;
                }

                table.dataframe tbody {
                    border: 2px solid #91c6e1;
                    padding: 10px 10px 10px 10px;
                }

                table.dataframe tr {
                }

                table.dataframe th {
                    vertical-align: top;
                    font-size: 14px;
                    padding: 10px 10px 10px 10px;
                    color: #105de3;
                    font-family: arial;
                    text-align: center;
                }

                table.dataframe td {
                    text-align: center;
                    padding: 5px 5px 5px 5px;
                    word-wrap:break-word;
                    word-break:break-all;
                    white-space:normal;
                    max-width:500px;
                }

                body {
                    font-family: 宋体;
                }

                h1 {
                    color: #5db446
                }

                div.header h2 {
                    color: #0002e3;
                    font-family: 黑体;
                }

                div.content h2 {
                    text-align: center;
                    font-size: 28px;
                    text-shadow: 2px 2px 1px #de4040;
                    color: #fff;
                    font-weight: bold;
                    background-color: #008eb7;
                    line-height: 1.5;
                    margin: 20px 0;
                    box-shadow: 10px 10px 5px #888888;
                    border-radius: 5px;
                }

                h3 {
                    font-size: 22px;
                    background-color: rgba(0, 2, 227, 0.71);
                    text-shadow: 2px 2px 1px #de4040;
                    color: rgba(239, 241, 234, 0.99);
                    line-height: 1.5;
                }

                h4 {
                    color: #e10092;
                    font-family: 楷体;
                    font-size: 20px;
                    text-align: center;
                }

                td img {
                    /*width: 60px;*/
                    max-width: 300px;
                    max-height: 300px;
                }

            </STYLE>
        </head>
        """
    body = \
        """
        <body>

        <div align="center" class="header">
            <!--标题部分的信息-->
            <a href={job}><h1 align="center">接口参数fuzzy扫描结果展示</h1></a>
            <h2 align="center">{project}</h2>
        </div>

        <hr>

        <div class="content">
            <!--正文内容-->
            <h2> </h2>

            <div>
                <h4></h4>
                {df_html}

            </div>
            <hr>

            <p style="text-align: center">

            </p>
        </div>
        </body>
        """.format(project=project_name,df_html=html,job=job_url)
    html_msg = "<html>" + head + body + "</html>"
    html_msg = html_msg.replace('\n','').encode("utf-8")
    # print html_msg
    return html_msg


def send_mail_html(to,fro,subject,html,project_name,job_url,server='localhost'):
    
    
    print ('here')
    msg = MIMEText(html_msg,'html','utf-8')
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=False)
    msg['Subject'] = subject 
    server = smtplib.SMTP(server)
    #server.set_debuglevel(1)
    print ('here')
    server.sendmail(fro,to,msg.as_string())
    server.close()



def sendMail(to, fro, subject, text,server="localhost"):
    assert type(to)==list
    #assert type(fmiiles)==list
    msg = MIMEText(text,'utf-8')
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    
    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.close()


def color(val):
    if val == 'SUCCESS':
        color = 'green'
    elif val == 'FAIL':
        color = 'red'
    return 'background-color: %s' % color


def covertToHtml(result,title):
    d = {}
    index = 0
    # print len(result)
    for t in title:
        print (t)
        d[t] = result[index]
        index = index + 1
    df = pd.DataFrame(d)
    pd.set_option('display.max_rows',500)
    pd.set_option('display.max_columns',500)
    pd.set_option('display.max_colwidth',100)
    df = df[title]
    # h = df.to_html(index=False)
    h= (df.style.applymap(color,subset=['结果']).set_table_attributes('border="1" class="dataframe"').set_table_styles({'selector':'thead.tr','props':
        [('text-align','right')]}).hide_index().render())
    return h






if __name__ == "__main__":
   project_name = sys.argv[1]
   job_url = sys.argv[2]
   email_subject = sys.argv[3]
   url = "" + str(project_name) +  "&metrics=sqale_index%2Cduplicated_lines_density%2Cncloc%2Ccoverage%2Cbugs%2Ccode_smells%2Cvulnerabilities&ps=1000"
   print (url)
   req_test = get_result_data(url)
   name = jp.match('$.measures[0].metric',req_test)
   data = jp.match('$.measures[0].history[*]',req_test)
   print (type(data))
   name = ['日期','Bug个数']
   #print data
   #print (covertToHtml(name,data))    
   resultList=[]
   list_date =[]
   list_value=[]
   for i in range(len(data)):
       list_date.append(data[i]['date'])
       list_value.append(data[i]['value'])
   list_date.reverse()
   list_value.reverse()
   print (list_date)
   print (list_value)
   resultList.append(list_date[0:10])
   resultList.append(list_value[0:10])
   print (resultList) 
   html = covertToHtml(resultList,name)
   project_name =  project_name.replace('%3A','-')
   send_mail_html()
   #sendMail()




