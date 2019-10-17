try:
 import paramiko
 from paramiko import SSHClient, AutoAddPolicy
except:
 pass
try:
 import pexpect
except:
 pass
import subprocess
def sshandro(u,username,password,timeout=5):
 l="sshpass -p {} ssh -o ConnectTimeout={} -o StrictHostKeyChecking=no {}@{} echo alaala; exit".format(password,timeout,username,u)
 ssh = subprocess.Popen(l.split(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 p= ssh.communicate()
 try:
   ssh.kill()
 except:
   pass
 if 'alaala' in str(p[0]):
  return True
 else:
  return False
def sshlin(u,username,password,p=22,timeout=7):
 p='ssh -o StrictHostKeyChecking=no -p {} {}@{}'.format(p,username,u)
 try:
  child = pexpect.spawn(p)
  while True:
   try:
    child.expect(['.*:'],timeout=timeout)
   except:
    pass
   c=child.before
   c+= child.after
   #if "yes/no" in c:
    #child.send('yes\n')
   if (('login' in c.lower()) or ('user' in c.lower())):
    child.send(username+'\n')
   elif "pass" in c.lower():
    child.send(password+'\n')
    break
  try:
   child.expect('.*=.*',timeout=timeout)
  except:
   pass
  c= child.before
  child.close()
  for x in prompts:
   if x in c:
    return True
 except Exception as e:
  pass
 return False
def sshwin(ip,username,password,p=22,timeout=5):
 try:
  paramiko.util.log_to_file("filename.log")
  s = SSHClient()
  s.set_missing_host_key_policy(AutoAddPolicy())
  s.connect(ip, p,username=username, password=password,timeout=timeout)
  stdin, stdout, stderr = s.exec_command ("echo alawashere",timeout=timeout)
  r=stdout.read()
  s.close()
  if "alawashere" in r:
   return True
 except Exception as e:
  pass
 return False
