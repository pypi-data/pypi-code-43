#! /usr/bin/python
from __future__ import print_function
import sys,os,datetime,subprocess
from . import Common, Config

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
		while p.poll() is None: continue
	else:
		return p

def run2(excuter,Wait=True):
	PIPE=subprocess.PIPE
	p=subprocess.Popen(excuter,stdout=PIPE,stderr=PIPE,shell=True)
	if Wait:
		p.wait()
		st=p.stderr.read()
		if len(st)>0:
			return "Childerr: "+ st +" ||| "+ p.stdout.read()
		else:
			return p.stdout.read()
	else:
		return p


def canBeCopied(folder,dest):
	if checkDest(dest)>(checkSrcSize(folder) * 0.05): return True
	return False

def checkSrcSize(folder):
	cmd="du -s %s"%folder
	lines=Common.run2(cmd)
	line=lines[0]
	try:
		csize=long(line.split()[0])
	except:
		csize=long(lines[-1].split()[2])
	return csize

def checkDest(dest):
	lines=Common.run2("df %s"%dest).split("\n")
	line=lines[1]
	try:
		csize=long(line.split()[3])
	except:
		csize=long(lines[2].split()[2])
	return csize

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def copy(src,dest,**kwargs):
	doneFolders=[]
	if src[-1]!="/": src+="/"
	logfile=kwargs.get("log-file",src+".bck_log")
	lstfile=kwargs.get("lst-file",src+".bck_lst")
	if os.path.exists(logfile):
		doneFolders=[l.strip() for l in open(logfile,'r').readlines()]
	logFile=open(logfile,"a")
	rsync_options=kwargs.get("rsync","")
	if not "no-scan" in kwargs and os.path.exists(lstfile):
		folders=Common.run("find %s -type d -links 2"%src).split("\n")
		lst=open(lstfile,"w")
		lst.write("\n".join(folders[:-1]))
		lst.close()
	else:
		folders=[l.strip() for l in open(lstfile,"r").readlines()]
		lst.write("\n".join(folders[:-1]))
	i=0
	for folder in folders:
		i+=1
		if folder=='': continue
		if folder  in doneFolders:
			eprint(folder,"copied before")
			continue
		if not canBeCopied(folder,dest):
			print("HDD is full, exiting....")
			exit(-125)	
		print ("Working on %s/%s: %s"%(i,total,folder))
		savePath="%s/%s"%(dest,folder.replace(src,dest))
		if not os.path.exists(savePath): os.makedirs(savePath)
		for file in Config.grab_files:
			print (datetime.datetime.now())
			res='rsync --safe-links %s %s %s %s'%(Config.rsync_options,rsync_options,folder,savePath)
			print(res)
			run(res,output=False)
			print (datetime.datetime.now())
		logFile.write(folder+"\n")
		logFile.flush()

if __name__=="__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("src", help="Source Directory")
	parser.add_argument("dest", help="Dest Mountpoint")
	parser.add_argument("-lg", "--log", help="Log File to use")
	parser.add_argument("-ls", "--lst", help="List File to use")
	parser.add_argument("-ns", "--no-scan", help="Don't rescan the folder, this needs a previous run")
	parser.add_argument("-rs", "--rsync", help="Extra rsync parameters")
	args = parser.parse_args()
	copy(args.src,args.dest,**vars(args))
