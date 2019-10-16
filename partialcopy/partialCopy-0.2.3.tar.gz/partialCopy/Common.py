import subprocess
import shlex

####################################################
##                                                ##
##    Common Function used in differnet modules   ##
##                                                ##
####################################################

#Run a command on the system shell
#Input: command and Wait Flag
#Output: Program outstream or error stream in case program printed on error stream

def run(excuter,Wait=True,output=True):
        PIPE=subprocess.PIPE
        if output:      p=subprocess.Popen(excuter,stdout=PIPE,stderr=PIPE,shell=True)
        else: p=subprocess.Popen(excuter,stdout=None,stderr=None,shell=True)
        if Wait and output:
                st=p.stderr.read()
                if len(st)>0:
                        return "Childerr: "+ st
                else:
                        return p.stdout.read()
        elif Wait:
                while p.poll() is None:
                        continue

        else:
                return p



#def run(excuter,Wait=True):

 #       PIPE=subprocess.PIPE
 #       p=subprocess.Popen(excuter,stdout=PIPE,stderr=PIPE,shell=True)
 #       if Wait:
 #               p.wait()
 #               st=p.stderr.read()
 #               if len(st)>0:
#                        return "Childerr: "+ st +" ||| "+ p.stdout.read()
#                else:
#                        return p.stdout.read()
#        else:
#                return p


def run2(excuter,Wait=True):
	print "command in run2 is "+excuter
        PIPE=subprocess.PIPE
        p=subprocess.Popen(excuter,stdout=PIPE,stderr=PIPE,shell=True)
        if Wait:
		print "system is waiting "
                p.wait()
		st=p.stderr.read()
                if len(st)>0:
                        return "Childerr: "+ st +" ||| "+ p.stdout.read()
                else:
                        return p.stdout.read()
        else:
                return p
