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

# mail_host = "smtp.163.com"  # 设置服务器
# mail_user = "idouko@163.com"  # 用户名
# mail_pass = "XYCoder02"  # 三方邮箱口令
# sender = 'idouko@163.com'# 发送者邮箱

mail_host = "partner.outlook.cn"
mail_user = "cm@saicmobility.com"
mail_pass = "Saic123456"  # 三方邮箱口令
sender = 'cm@saicmobility.com'# 发送者邮箱

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
            # 163 邮箱（25）
            # smtpObj = smtplib.SMTP()
            # smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            # smtpObj.login(mail_user, mail_pass)
            # smtpObj.sendmail(sender, receivers, message.as_string())
            # print("邮件发送成功")
            # smtpObj.quit()

            # outlook邮箱 (587)
            smtpObj = smtplib.SMTP(mail_host, 587)
            smtpObj.starttls()
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
    # Email().sendemail('这是一封来自财务的报表邮件','你','财务部',cc='m13451923928@163.com,786857294@qq.com',htmltext='')
    # Email().send_diagnose()

    # print(Email().commit_is_a_bug('T_ASR-14997_【ios】【司机端&乘客端】【IM】【ATE】发送超长文案时切换到发送语音，格式错乱，切换回文字后，键盘盖住文案 T_ASR-14992_【ios】【司机端&乘客端】【IM】【ATE】IM发送图片手动放大查看，图片比例失调','http://jira..com:8080/browse/?filter=-1'))

    Email().sendemail('工资明细','ios','weiwei.sun@hand-china.com','m18221031340@163.com,m13365169690@163.com,786857294@qq.com')
