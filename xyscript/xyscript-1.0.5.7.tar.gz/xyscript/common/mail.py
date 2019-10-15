#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage 
from email.header import Header
from email.mime.base import MIMEBase
from email.utils import parseaddr,formataddr
from xyscript.source.html import diagnosemail_body, diagnosemail_header,mergemail_body
from xyscript.source.image import jsonfileicon
import base64,os

mail_host = "smtp.163.com"  # 设置服务器
mail_user = "idouko@163.com"  # 用户名
mail_pass = "XYCoder02"  # 三方邮箱口令
sender = 'idouko@163.com'# 发送者邮箱
receivers = ['m18221031340@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

class Email():
    def __init__(self,receiver=None):
        global receivers
        # print(receiver)
        if receiver is not None and len(receiver) > 0:
            receivers = receiver
        # print (receivers)
        # print(receivers)

    def send_package_email(self,success,url=None,image=None):
        global receivers
        string = ""
        if success:
            string = "您好！\n      项目打包成功，详情如下：\n 项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        else:
            string = "您好！\n      项目打包失败，请注意查看错误日志！信息如下：\n项目地址：%s\n打包分支：%s\n打包平台：%s\n打包网络环境：%s\n版本号：%s\n编译号：%s\n" %(address,branch,platform,env,version,build)
        Email(receivers).sendemail(string,"此邮件来自自动化打包","iOS项目组",image='/Users/v-sunweiwei/Downloads/timg.jpeg')

    def send_diagnose(self,git_objc=None):
        global receivers
        
        content_string = diagnosemail_body.format(project_url=git_objc['project_url']
                                                ,project_name=git_objc['project_name']
                                                ,user_name=git_objc['user_name']
                                                ,branch_name=git_objc['branch_name']
                                                ,commit_content=git_objc['commit_content']
                                                ,commit_url=git_objc['commit_url']
                                                ,commit_id=git_objc['commit_id']
                                                ,date=git_objc['date']
                                                ,result=git_objc['result']
                                                ,result_detail=git_objc['result_detail'])
        content = "<!DOCTYPE html><html lang=\"en\">" +  diagnosemail_header + content_string + "</html>"
        content = content.replace('\n','').encode("utf-8")

        image_name = 'jsonfileicon' + '.png'
        tmp = open(image_name, 'wb')
        tmp.write(base64.b64decode(jsonfileicon))
        tmp.close()
        # 收件人
        if 'user_email' in git_objc:
            receivers = git_objc['user_email']
        # 抄送人    
        cc = None
        if git_objc['cc'] is not None:
            cc = git_objc['cc']

        Email(receivers).sendemail(None,"此邮件来自代码自动诊断","iOS项目组",cc=cc,htmltext=content,image=image_name,filepath=git_objc['file_path'])
        os.remove(image_name)

    def send_merge_result(self,merge_result):
        global receivers
        
        content_string = mergemail_body.format(project_name=merge_result['project_name']
                                                ,package_branch=merge_result['package_branch']
                                                ,end_time=merge_result['end_time']
                                                ,start_time=merge_result['start_time'])
        # 壳工程
        shell_array = merge_result['shell']
        submodule_array = merge_result['submodule']
        private_modules = merge_result['private_module']
        shell_dom = ''
        for shell in shell_array:
            # 此处jiraurl需要用替换bug号
            bug_list = '&nbsp;'
            if 'jiraurl' in merge_result.keys():
                bug_list = self.commit_is_a_bug(shell['info'],merge_result['jiraurl'])
            
            shell_dom = shell_dom + '<tr><td>'+ shell['user'] +'</td><td>'+ shell['date'] +'</td><td>'+ shell['info'] +'</td><td>' + bug_list + '</td></tr>'
            # print(shell_dom)
        content_string = content_string.replace('<&shell_list&>',shell_dom)

        # 子模块
        sub_dom = ''
        for sub in submodule_array:
            sub_dom = sub_dom + '<H3>' + sub['name'] + '</H3>'
            sub_commit_dom = '<tr class="table-header" style="background-color: gray"><td>提交人</td><td>提交时间</td><td>提交内容</td><td>备注</td></tr>'
            for sub_commit in sub['commit_log']:
                sub_commit_link = '&nbsp;'
                if 'jiraurl' in merge_result.keys():
                    sub_commit_link = self.commit_is_a_bug(sub_commit['info'],merge_result['jiraurl'])
                sub_commit_dom = sub_commit_dom + '<tr><td>'+ sub_commit['user'] +'</td><td>' + sub_commit['date'] + '</td><td>' + sub_commit['info'] + '</td><td>' + sub_commit_link + '</td></tr>'
            sub_commit_dom = '<table class="result_table_shell" >' + sub_commit_dom + '</table>'
            sub_dom = sub_dom + sub_commit_dom
            # print(sub_dom)
        content_string = content_string.replace('<&submodule_list&>',sub_dom)

        # 共享库 private_module
        private_dom = ''
        for sub in private_modules:
            private_dom = sub_dom + '<H3>' + sub['name'] + '</H3>'
            sub_commit_dom = '<tr class="table-header" style="background-color: gray"><td>提交人</td><td>提交时间</td><td>提交内容</td><td>备注</td></tr>'
            for sub_commit in sub['commit_log']:
                sub_commit_link = '&nbsp;'
                if 'jiraurl' in merge_result.keys():
                    sub_commit_link = self.commit_is_a_bug(sub_commit['info'],merge_result['jiraurl'])
                sub_commit_dom = sub_commit_dom + '<tr><td>'+ sub_commit['user'] +'</td><td>' + sub_commit['date'] + '</td><td>' + sub_commit['info'] + '</td><td>' + sub_commit_link + '</td></tr>'
            sub_commit_dom = '<table class="result_table_shell" >' + sub_commit_dom + '</table>'
            private_dom = private_dom + sub_commit_dom
            # print(sub_dom)
        content_string = content_string.replace('<&private_modules&>',private_dom)
        
        
        content = "<!DOCTYPE html><html lang=\"en\">" +  diagnosemail_header + content_string + "</html>"
        # print(content)
        content = content.replace('\n','').encode("utf-8")

        cc = None
        if merge_result['cc'] is not None:
            cc = merge_result['cc']

        Email(receivers).sendemail(None,"此邮件来自代码合并","iOS项目组",cc=cc,htmltext=content)

    def commit_is_a_bug(self,commit,url):
        if commit is None or len(commit) <= 0 :
            return None
        
        commit_array = commit.split(' ')

        bug_list_array = []
        for commit_item in commit_array:
            item_array = commit_item.split('_')
            if len(item_array)>=3 and item_array[0] == 'T' and '-' in item_array[1]:
                url_filter = url.replace('',item_array[1])
                link_string = '<a href="' + url_filter + '" style="word-wrap:break-word;">' + item_array[1] + '</a>'
                bug_list_array.append(link_string)

        return ''.join(bug_list_array)
        

    def get_html_text(self,html_path):
        with open(html_path,'r') as f:
            # print(f.read())
            content = f.read()
            self.sendemail(None,"此邮件来自代码自动诊断","iOS项目组",htmltext=content,image='/Users/v-sunweiwei/Desktop//xyscript/xyscript/source/img/jsonfileicon.png',filepath='/Users/v-sunweiwei/Desktop/extension/人力图.jpg')


    def sendemail(self, content ,subject, form_name, cc=None ,htmltext=None ,image=None , filepath=None):
        """
        发送邮件
        content 正文文本
        subject 副标题
        form_name 邮件来源文本
        cc
        htmltext 网页
        image 图片
        filepath 附件
        """
        global receivers
        
        subject = subject#邮件来源
        #构建信息体
        message = MIMEMultipart('alternative') 
        
        #下面的主题，发件人，收件人，日期是显示在邮件页面上的。
        message['From'] = formataddr([form_name, sender])
        message['To'] = ";".join(receivers)
        message['Subject'] = Header(subject, 'utf-8')#编码方式
        if cc != None:
            message["Cc"] = cc
            receivers = receivers + cc.split(';')
            print(receivers)

        #构造文字内容   
        text = content    
        text_plain = MIMEText(text,'plain', 'utf-8')    
        message.attach(text_plain)    

        if image != None:
            #构造图片链接
            sendimagefile=open(image,'rb').read()
            image = MIMEImage(sendimagefile)
            image.add_header('Content-ID','<image1>')
            image["Content-Disposition"] = 'attachment; filename="testimage.png"'
            message.attach(image)

        if htmltext != None:
            #构造html
            #发送正文中的图片:由于包含未被许可的信息，网易邮箱定义为垃圾邮件，报554 DT:SPM ：<p><img src="cid:image1"></p>
            message.attach(MIMEText(htmltext,'html','utf-8')) 


        if filepath != None:
            #构造附件
            sendfile=open(filepath,'rb').read()
            text_att = MIMEText(sendfile, 'base64', 'utf-8') 
            text_att["Content-Type"] = 'application/octet-stream'  
            #以下附件可以重命名成aaa.txt  
            file_name = (filepath.split("/")[-1])
            text_att["Content-Disposition"] = 'attachment; filename="%s"' %(file_name)
            text_att.add_header('Content-ID','<file1>')
            #另一种实现方式
            # text_att.add_header('Content-Disposition', 'attachment', filename='aaa.txt')
            #以下中文测试不ok
            #text_att["Content-Disposition"] = u'attachment; filename="中文附件.txt"'.decode('utf-8')
            message.attach(text_att)  

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            # smtpObj.ehlo()
            # smtpObj.starttls()
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print("无法发送邮件,原因是:" + str(e))

if __name__ == "__main__":
    # Email('m18221031340@163.com').send_package_email(False)
    # Email('m18221031340@163.com').send_diagnose('/Users/v-sunweiwei/Desktop//iosTestDemo/build/reports/report.json','content')
    # Email(['m18221031340@163.com'])
    # Email().get_html_text('/Users/v-sunweiwei/Desktop//xyscript/xyscript/source/htmlx/diagnosemail.html')
    Email().sendemail('这是一封来自财务的报表邮件','你','财务部',cc='m13451923928@163.com,786857294@qq.com',htmltext='<!DOCTYPE html><html lang="en">    <head>        <title></title>        <meta charset="UTF-8">        <meta name="viewport" content="width=device-width, initial-scale=1">        <style>            .content{                padding: 20px;                border:10px solid rgb(108, 172, 218)            }            .file-content{                display: inline-block;            }            .file-content span{                display: block;                text-align:center;            }            .file-content a{                text-decoration: none;                color:black;            }            .result_table{                width:100%;                border:0;                cellspacing:1;                 cellpadding:0;                border-collapse: collapse;            }            .table-header td{                color: white;            }            table td{                padding-left: 10px;            }            table,table tr th, table tr td {                border:1px solid #ccc;                }            table tr td a{                text-decoration: none;                color:#1b69b6;            }            #result-text{                width: 70%;                resize: none;            }        </style>    </head>            <body>        <div class="content">            <h4>\xe6\x82\xa8\xe5\xa5\xbd\xef\xbc\x9a</h4>            <h4>&nbsp;&nbsp;&nbsp;&nbsp;\xe9\x92\x88\xe5\xaf\xb9iOS\xe9\xa1\xb9\xe7\x9b\xae\xe6\x9c\x80\xe8\xbf\x91\xe4\xb8\x80\xe6\xac\xa1\xe7\x9a\x84\xe4\xbb\xa3\xe7\xa0\x81\xe5\x90\x88\xe5\xb9\xb6\xef\xbc\x8c\xe7\xbb\x93\xe6\x9e\x9c\xe5\xa6\x82\xe4\xb8\x8b\xef\xbc\x9a</h4>            <h5>\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0\xef\xbc\x9aios-shell-driver</h5>            <h5>\xe5\x90\x88\xe5\xb9\xb6\xe5\x88\x86\xe6\x94\xaf\xef\xbc\x9azuche-test</h5>            <h5>\xe6\x9c\xac\xe6\xac\xa1\xe5\x90\x88\xe5\xb9\xb6\xe6\x97\xb6\xe9\x97\xb4\xef\xbc\x9a2019-10-15 10:10:36</h5>            <h5>\xe4\xb8\x8a\xe4\xb8\x80\xe6\xac\xa1\xe5\x90\x88\xe5\xb9\xb6\xe6\x97\xb6\xe9\x97\xb4\xef\xbc\x9a2019-10-09 17:44:19 +0800</h5>            <H3>\xe5\xa3\xb3\xe5\xb7\xa5\xe7\xa8\x8b</H3>            <table class="result_table_shell" >                <tr class="table-header" style="background-color: gray">                    <td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td>                    <td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td>                    <td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td>                    <td>\xe5\xa4\x87\xe6\xb3\xa8</td>                </tr>                <tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-14 17:16:04 +0800</td><td>test ci2</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-14 16:13:44 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-14 16:10:56 +0800</td><td>test ci1</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-14 15:57:48 +0800</td><td>test ci</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-14 14:00:27 +0800</td><td>test ci</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-12 14:33:53 +0800</td><td>zuche-test\xe4\xbf\xae\xe6\x94\xb9\xe5\xad\x90\xe6\xa8\xa1\xe5\x9d\x97\xe5\x88\x86\xe6\x94\xaf</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-12 12:19:05 +0800</td><td>\xe6\x9b\xb4\xe6\x96\xb0podfile</td><td></td></tr><tr><td>mark<huzhibin@saicmobility.com></td><td>2019-10-12 10:38:35 +0800</td><td>\xe6\x9b\xb4\xe6\x96\xb0navigationbar\xe5\x81\x8f\xe7\xa7\xbb\xe9\x87\x8f\xe4\xbf\xae\xe6\xad\xa3\xe5\xba\x93\xe5\xbc\x95\xe7\x94\xa8</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-12 10:06:56 +0800</td><td>\xe5\x9f\x8b\xe7\x82\xb9\xe7\xa9\xba\xe6\x96\xb9\xe6\xb3\x95\xe6\x81\xa2\xe5\xa4\x8d</td><td></td></tr><tr><td>yaohongbing<yaohongbing@saicmobility.com></td><td>2019-10-11 21:07:06 +0800</td><td>\xe5\x8e\xbb\xe9\x99\xa4\xe5\xaf\xb9SXRuntime.h\xe7\x9a\x84\xe4\xbe\x9d\xe8\xb5\x96</td><td></td></tr><tr><td>jiangjie<jiangjie@saicmobility.com></td><td>2019-10-11 17:53:58 +0800</td><td>\xe6\x9b\xb4\xe6\x96\xb0projconfig\xef\xbc\x8c\xe5\xad\x90\xe6\xa8\xa1\xe5\x9d\x97\xe4\xbd\xbf\xe7\x94\xa8zuche-develop</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-11 15:28:24 +0800</td><td>Merge branch \'zuche-test\' into zuche-Develop</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-11 15:27:36 +0800</td><td>1\xe3\x80\x81\xe5\x9f\x8b\xe7\x82\xb9 2\xe3\x80\x81\xe4\xb8\xbe\xe7\x89\x8c\xe6\x8c\x89\xe9\x92\xae\xe5\x87\xba\xe7\x8e\xb0\xe6\x97\xb6\xe6\x9c\xba</td><td></td></tr><tr><td>langguangyu<langguangyu@saicmobility.com></td><td>2019-10-11 13:48:21 +0800</td><td>\xe5\xa2\x9e\xe5\x8a\xa0\xe6\x89\x8b\xe6\x9c\xba\xe5\x8f\xb7\xe5\x88\xa4\xe8\xb4\xa3\xe9\xbb\x98\xe8\xae\xa4\xe6\xad\xa3\xe5\x88\x99\xe8\xa1\xa8\xe8\xbe\xbe\xe5\xbc\x8f \xe4\xbf\x9d\xe6\x8c\x81\xe7\xa7\x9f\xe8\xbd\xa6\xe5\xae\xa2\xe6\x88\xb7\xe7\xab\xaf\xe6\x9c\x8d\xe5\x8a\xa1\xe7\xab\xaf\xe6\xad\xa3\xe5\x88\x99\xe8\xa1\xa8\xe8\xbe\xbe\xe5\xbc\x8f\xe4\xb8\x80\xe8\x87\xb4</td><td></td></tr><tr><td>jiangjie<jiangjie@saicmobility.com></td><td>2019-10-10 16:48:59 +0800</td><td>Merge branch \'zuche-Develop\' into zuche-test</td><td></td></tr><tr><td>jiangjie<jiangjie@saicmobility.com></td><td>2019-10-10 16:48:48 +0800</td><td>\xe5\xaf\xbc\xe8\x88\xaa\xe6\xa0\x8f\xe9\x97\xae\xe9\xa2\x98\xef\xbc\x8c\xe5\x9b\x9e\xe9\x80\x80 saicscout</td><td></td></tr><tr><td>saicnj<saicnj@admindeMac-mini.local></td><td>2019-10-10 15:43:01 +0800</td><td>setup ci file</td><td></td></tr><tr><td>jiangjie<jiangjie@saicmobility.com></td><td>2019-10-10 15:32:20 +0800</td><td>Merge branch \'zuche-Develop\' into zuche-test</td><td></td></tr><tr><td>jiangjie<jiangjie@saicmobility.com></td><td>2019-10-10 15:32:03 +0800</td><td>\xe6\xb3\xa8\xe9\x87\x8a\xe5\x86\x85\xe5\xad\x98\xe6\xa3\x80\xe6\xb5\x8b\xe4\xbb\xa3\xe7\xa0\x81\xef\xbc\x8c\xe5\x9b\xa0\xe5\xaf\xbc\xe8\x87\xb4\xe5\xaf\xbc\xe8\x88\xaa\xe6\xa0\x8f\xe5\x87\xba\xe9\x94\x99</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-10 10:34:17 +0800</td><td>\xe5\x88\xa0\xe9\x99\xa4fabric</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-09 17:50:29 +0800</td><td>\xe4\xbf\xae\xe6\x94\xb9\xe5\x88\x86\xe6\x94\xaf\xe9\x85\x8d\xe7\xbd\xae\xe6\x96\x87\xe4\xbb\xb6</td><td></td></tr><tr><td>v-sunweiwei<v-sunweiwei@saicmobility.com></td><td>2019-10-09 17:44:19 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr>            </table>            <H3>submodules/module-login</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:20 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:34:51 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-risk-control</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:36 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:36:14 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-update</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>Ryan Jin</td><td>2019-10-13 09:49:08 +0800</td><td>add guide class</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-11 10:33:17 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 17:19:32 +0800</td><td>Merge branch \'zuche-test\' of https://gitlab.saicmobility.com/saic-app-ios/module-update into zuche-test</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:44:16 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:53:03 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:40:23 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-09 17:45:04 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr></table><H3>submodules/module-driver-main</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 22:01:37 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 21:58:11 +0800</td><td>T_ASR-19876_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe8\xa1\x8c\xe7\xa8\x8b\xe8\xaf\xa6\xe6\x83\x85\xe9\xa1\xb5\xe9\x9d\xa2\xef\xbc\x8c\xe4\xb8\xbe\xe7\x89\x8c\xe6\x8c\x89\xe9\x92\xae\xe4\xb8\x8b\xe6\x96\xb9\xe6\x9c\x89\xe6\x9d\xa1\xe7\xba\xbf T_ASR-19856_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe8\xa1\x8c\xe7\xa8\x8b\xe8\xaf\xa6\xe6\x83\x85\xe9\xa1\xb5\xe9\x9d\xa2\xef\xbc\x8c\xe5\xa4\x8d\xe5\x88\xb6\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7\xef\xbc\x8c\xe6\x88\x90\xe5\x8a\x9f\xe5\x90\x8e\xe5\xbc\xb9\xe5\x87\xba\xe7\x9a\x84toast\xe6\x8f\x90\xe7\xa4\xba\xe6\xa0\xb7\xe5\xbc\x8f\xe9\x9c\x80\xe5\x81\x9a\xe4\xbf\xae\xe6\x94\xb9 T_ASR-19849_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe4\xb8\xbe\xe7\x89\x8c\xe5\x88\x86\xe4\xba\xab\xe8\x87\xb3QQ\xef\xbc\x8c\xe5\x88\x86\xe4\xba\xab\xe6\x88\x90\xe5\x8a\x9f\xe5\x90\x8e\xef\xbc\x8c\xe8\xbf\x94\xe5\x9b\x9e\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xafAPP\xef\xbc\x8c\xe5\x8e\xbb\xe6\x8e\x89\xe5\x88\x86\xe4\xba\xab\xe6\x88\x90\xe5\x8a\x9ftoast\xe6\x8f\x90\xe7\xa4\xba</td><td><a href="http://jira.saicmobility.com:8080/browse/ASR-19876?filter=-1" style="word-wrap:break-word;">ASR-19876</a><a href="http://jira.saicmobility.com:8080/browse/ASR-19856?filter=-1" style="word-wrap:break-word;">ASR-19856</a><a href="http://jira.saicmobility.com:8080/browse/ASR-19849?filter=-1" style="word-wrap:break-word;">ASR-19849</a></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 16:13:16 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 14:56:15 +0800</td><td>\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0</td><td></td></tr><tr><td>mark</td><td>2019-10-14 14:35:54 +0800</td><td>\xe4\xbc\x98\xe5\x8c\x96\xe5\xbc\xb9\xe7\xaa\x97\xe9\x80\xbb\xe8\xbe\x91</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 13:57:33 +0800</td><td>test ci</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 10:47:02 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 10:02:09 +0800</td><td>Revert "\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0"</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 09:54:17 +0800</td><td>\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0</td><td></td></tr><tr><td>mark</td><td>2019-10-14 09:44:50 +0800</td><td>\xe5\xbc\xb9\xe7\xaa\x97\xe4\xbf\x9d\xe7\x95\x99\xe7\xbc\x93\xe5\xad\x98\xe8\xae\xb0\xe5\xbd\x95\xe6\x97\xb6\xe9\x97\xb4\xe6\x94\xb9\xe4\xb8\xba5\xe5\x88\x86\xe9\x92\x9f</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 16:07:48 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>mark</td><td>2019-10-12 16:02:42 +0800</td><td>T_ASR-19666 \xe9\xa6\x96\xe9\xa1\xb5\xef\xbc\x8c\xe5\x8c\x85\xe8\xbd\xa6\xe8\xae\xa2\xe5\x8d\x95\xef\xbc\x8c\xe6\xb2\xa1\xe6\x9c\x89\xe6\x98\xbe\xe7\xa4\xba\xe7\x94\xa8\xe8\xbd\xa6\xe6\x97\xb6\xe9\x95\xbf</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 16:00:00 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 15:26:04 +0800</td><td>\xe5\x9f\x8b\xe7\x82\xb9\xe8\xb0\x83\xe7\x94\xa8</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 15:25:03 +0800</td><td>\xe5\x9f\x8b\xe7\x82\xb9\xe8\xb0\x83\xe7\x94\xa8</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 14:14:07 +0800</td><td>\xe5\x8c\x85\xe8\xbd\xa6\xe5\xa4\x9a\xe6\x97\xa5\xe7\xac\xac\xe4\xba\x8c\xe5\xa4\xa9\xe5\xbc\x80\xe5\xa7\x8b\xe5\x89\x8d\xe4\xb8\x8d\xe5\x87\xba\xe7\x8e\xb0\xe6\x8e\xa5\xe6\x9c\xba\xe7\x89\x8c\xe9\x97\xae\xe9\xa2\x98</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 13:40:19 +0800</td><td>\xe6\xbb\x91\xe5\x9d\x97\xe6\x96\x87\xe5\xad\x97\xe6\x94\xb9\xe5\x8f\x98\xe5\x90\x8e\xe5\x86\x8d\xe5\x87\xba\xe7\x8e\xb0\xe6\x8c\x89\xe9\x92\xae</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 10:06:53 +0800</td><td>\xe4\xba\x8c\xe6\xac\xa1\xe7\xa1\xae\xe8\xae\xa4\xe7\xa9\xba\xe6\x96\xb9\xe6\xb3\x95</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 17:45:06 +0800</td><td>\xe9\x80\x80\xe5\x87\xba\xe9\x87\x8d\xe8\xbf\x9b\xe4\xb8\xbe\xe7\x89\x8c\xe6\x8c\x89\xe9\x92\xae</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:10 +0800</td><td>setup ci file</td><td></td></tr></table><H3>submodules/module-driver-trip</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>wangxingming</td><td>2019-10-14 18:29:13 +0800</td><td>toast\xe6\x9b\xbf\xe6\x8d\xa2</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:13 +0800</td><td>setup ci file</td><td></td></tr></table><H3>submodules/module-driver-trip-history</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:44:10 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:37:12 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-message</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>wangxingming</td><td>2019-10-14 16:10:33 +0800</td><td>T_ASR-19851_\xe9\x80\x9a\xe7\x9f\xa5\xe6\x97\xb6\xe9\x97\xb4\xe6\xa0\xbc\xe5\xbc\x8f</td><td><a href="http://jira.saicmobility.com:8080/browse/ASR-19851?filter=-1" style="word-wrap:break-word;">ASR-19851</a></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:15 +0800</td><td>setup ci file</td><td></td></tr></table>            <H3>submodules/module-login</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:20 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:34:51 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-risk-control</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:36 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:36:14 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-update</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>Ryan Jin</td><td>2019-10-13 09:49:08 +0800</td><td>add guide class</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-11 10:33:17 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 17:19:32 +0800</td><td>Merge branch \'zuche-test\' of https://gitlab.saicmobility.com/saic-app-ios/module-update into zuche-test</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:44:16 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:53:03 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:40:23 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-09 17:45:04 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr></table><H3>submodules/module-driver-main</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 22:01:37 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 21:58:11 +0800</td><td>T_ASR-19876_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe8\xa1\x8c\xe7\xa8\x8b\xe8\xaf\xa6\xe6\x83\x85\xe9\xa1\xb5\xe9\x9d\xa2\xef\xbc\x8c\xe4\xb8\xbe\xe7\x89\x8c\xe6\x8c\x89\xe9\x92\xae\xe4\xb8\x8b\xe6\x96\xb9\xe6\x9c\x89\xe6\x9d\xa1\xe7\xba\xbf T_ASR-19856_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe8\xa1\x8c\xe7\xa8\x8b\xe8\xaf\xa6\xe6\x83\x85\xe9\xa1\xb5\xe9\x9d\xa2\xef\xbc\x8c\xe5\xa4\x8d\xe5\x88\xb6\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7\xef\xbc\x8c\xe6\x88\x90\xe5\x8a\x9f\xe5\x90\x8e\xe5\xbc\xb9\xe5\x87\xba\xe7\x9a\x84toast\xe6\x8f\x90\xe7\xa4\xba\xe6\xa0\xb7\xe5\xbc\x8f\xe9\x9c\x80\xe5\x81\x9a\xe4\xbf\xae\xe6\x94\xb9 T_ASR-19849_\xe3\x80\x90sit\xe7\x8e\xaf\xe5\xa2\x83\xe3\x80\x91-\xe3\x80\x90IOS\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xaf\xe3\x80\x91\xe4\xb8\xbe\xe7\x89\x8c\xe5\x88\x86\xe4\xba\xab\xe8\x87\xb3QQ\xef\xbc\x8c\xe5\x88\x86\xe4\xba\xab\xe6\x88\x90\xe5\x8a\x9f\xe5\x90\x8e\xef\xbc\x8c\xe8\xbf\x94\xe5\x9b\x9e\xe5\x8f\xb8\xe6\x9c\xba\xe7\xab\xafAPP\xef\xbc\x8c\xe5\x8e\xbb\xe6\x8e\x89\xe5\x88\x86\xe4\xba\xab\xe6\x88\x90\xe5\x8a\x9ftoast\xe6\x8f\x90\xe7\xa4\xba</td><td><a href="http://jira.saicmobility.com:8080/browse/ASR-19876?filter=-1" style="word-wrap:break-word;">ASR-19876</a><a href="http://jira.saicmobility.com:8080/browse/ASR-19856?filter=-1" style="word-wrap:break-word;">ASR-19856</a><a href="http://jira.saicmobility.com:8080/browse/ASR-19849?filter=-1" style="word-wrap:break-word;">ASR-19849</a></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 16:13:16 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 14:56:15 +0800</td><td>\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0</td><td></td></tr><tr><td>mark</td><td>2019-10-14 14:35:54 +0800</td><td>\xe4\xbc\x98\xe5\x8c\x96\xe5\xbc\xb9\xe7\xaa\x97\xe9\x80\xbb\xe8\xbe\x91</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 13:57:33 +0800</td><td>test ci</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-14 10:47:02 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 10:02:09 +0800</td><td>Revert "\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0"</td><td></td></tr><tr><td>yaohongbing</td><td>2019-10-14 09:54:17 +0800</td><td>\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x9b\xb4\xe6\x96\xb0</td><td></td></tr><tr><td>mark</td><td>2019-10-14 09:44:50 +0800</td><td>\xe5\xbc\xb9\xe7\xaa\x97\xe4\xbf\x9d\xe7\x95\x99\xe7\xbc\x93\xe5\xad\x98\xe8\xae\xb0\xe5\xbd\x95\xe6\x97\xb6\xe9\x97\xb4\xe6\x94\xb9\xe4\xb8\xba5\xe5\x88\x86\xe9\x92\x9f</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 16:07:48 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>mark</td><td>2019-10-12 16:02:42 +0800</td><td>T_ASR-19666 \xe9\xa6\x96\xe9\xa1\xb5\xef\xbc\x8c\xe5\x8c\x85\xe8\xbd\xa6\xe8\xae\xa2\xe5\x8d\x95\xef\xbc\x8c\xe6\xb2\xa1\xe6\x9c\x89\xe6\x98\xbe\xe7\xa4\xba\xe7\x94\xa8\xe8\xbd\xa6\xe6\x97\xb6\xe9\x95\xbf</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 16:00:00 +0800</td><td>merge zuche-Develop into zuche-test</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 15:26:04 +0800</td><td>\xe5\x9f\x8b\xe7\x82\xb9\xe8\xb0\x83\xe7\x94\xa8</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 15:25:03 +0800</td><td>\xe5\x9f\x8b\xe7\x82\xb9\xe8\xb0\x83\xe7\x94\xa8</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 14:14:07 +0800</td><td>\xe5\x8c\x85\xe8\xbd\xa6\xe5\xa4\x9a\xe6\x97\xa5\xe7\xac\xac\xe4\xba\x8c\xe5\xa4\xa9\xe5\xbc\x80\xe5\xa7\x8b\xe5\x89\x8d\xe4\xb8\x8d\xe5\x87\xba\xe7\x8e\xb0\xe6\x8e\xa5\xe6\x9c\xba\xe7\x89\x8c\xe9\x97\xae\xe9\xa2\x98</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 13:40:19 +0800</td><td>\xe6\xbb\x91\xe5\x9d\x97\xe6\x96\x87\xe5\xad\x97\xe6\x94\xb9\xe5\x8f\x98\xe5\x90\x8e\xe5\x86\x8d\xe5\x87\xba\xe7\x8e\xb0\xe6\x8c\x89\xe9\x92\xae</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-12 10:06:53 +0800</td><td>\xe4\xba\x8c\xe6\xac\xa1\xe7\xa1\xae\xe8\xae\xa4\xe7\xa9\xba\xe6\x96\xb9\xe6\xb3\x95</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 17:45:06 +0800</td><td>\xe9\x80\x80\xe5\x87\xba\xe9\x87\x8d\xe8\xbf\x9b\xe4\xb8\xbe\xe7\x89\x8c\xe6\x8c\x89\xe9\x92\xae</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:10 +0800</td><td>setup ci file</td><td></td></tr></table><H3>submodules/module-driver-trip</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>wangxingming</td><td>2019-10-14 18:29:13 +0800</td><td>toast\xe6\x9b\xbf\xe6\x8d\xa2</td><td></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:13 +0800</td><td>setup ci file</td><td></td></tr></table><H3>submodules/module-driver-trip-history</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>saicnj</td><td>2019-10-10 15:44:10 +0800</td><td>setup ci file</td><td></td></tr><tr><td>v-sunweiwei</td><td>2019-10-10 09:37:12 +0800</td><td>Merge branch \'Develop\' into zuche-Develop</td><td></td></tr></table><H3>submodules/module-message</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>wangxingming</td><td>2019-10-14 16:10:33 +0800</td><td>T_ASR-19851_\xe9\x80\x9a\xe7\x9f\xa5\xe6\x97\xb6\xe9\x97\xb4\xe6\xa0\xbc\xe5\xbc\x8f</td><td><a href="http://jira.saicmobility.com:8080/browse/ASR-19851?filter=-1" style="word-wrap:break-word;">ASR-19851</a></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:15 +0800</td><td>setup ci file</td><td></td></tr></table><H3>SCShare</H3><table class="result_table_shell" ><tr class="table-header" style="background-color: gray"><td>\xe6\x8f\x90\xe4\xba\xa4\xe4\xba\xba</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe6\x97\xb6\xe9\x97\xb4</td><td>\xe6\x8f\x90\xe4\xba\xa4\xe5\x86\x85\xe5\xae\xb9</td><td>\xe5\xa4\x87\xe6\xb3\xa8</td></tr><tr><td>wangxingming</td><td>2019-10-14 16:10:33 +0800</td><td>T_ASR-19851_\xe9\x80\x9a\xe7\x9f\xa5\xe6\x97\xb6\xe9\x97\xb4\xe6\xa0\xbc\xe5\xbc\x8f</td><td><a href="http://jira.saicmobility.com:8080/browse/ASR-19851?filter=-1" style="word-wrap:break-word;">ASR-19851</a></td></tr><tr><td>saicnj</td><td>2019-10-10 15:43:15 +0800</td><td>setup ci file</td><td></td></tr></table>        </div>    </body>        </html>')
    # Email().send_diagnose()

    # print(Email().commit_is_a_bug('T_ASR-14997_【ios】【司机端&乘客端】【IM】【ATE】发送超长文案时切换到发送语音，格式错乱，切换回文字后，键盘盖住文案 T_ASR-14992_【ios】【司机端&乘客端】【IM】【ATE】IM发送图片手动放大查看，图片比例失调','http://jira..com:8080/browse/?filter=-1'))

    # Email().sendemail('工资明细','ios','weiwei.sun@hand-china.com','m18221031340@163.com,m13365169690@163.com,786857294@qq.com')
