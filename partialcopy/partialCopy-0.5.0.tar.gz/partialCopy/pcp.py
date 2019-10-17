#! /usr/bin/python
from __future__ import print_function
import sys,os,datetime,subprocess
from . import Common, Config

def run(excuter,Wait=True,output=True):
	PIPE=subprocess.PIPE
	print ("Running",excuter)
	if output:      p=subprocess.Popen(excuter,stdout=PIPE,stderr=PIPE,shell=True)
	else: p=subprocess.Popen(excuter,stdout=None,stderr=None,shell=True)
	if Wait and output:
		out=""
		while p.poll() is None:
			out+= "".join(p.stdout.readlines())
		return out
	elif Wait:
		while p.poll() is None: 
			continue
		return p.returncode
	else:
		return p
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
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
	lines=Common.run2("df -B1 %s"%dest).split("\n")
	line=lines[1]
	try:
		csize=long(line.split()[3])
	except:
		csize=long(lines[2].split()[2])
	print("Dest Size is", sizeof_fmt(csize))
	return csize

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def copy(src,dest,**kwargs):
	print (kwargs)
#if kwargs["dry_run"]:	 print("Running in Dry run mode")
	doneFiles=[]
	if src[-1]!="/": src+="/"
	#logfile=kwargs.get("log",src+".pcp_log")
	#if logfile==None: logfile=src+".pcp_log"
	#lstfile=kwargs.get("lst",src+".pcp_lst")
	#if lstfile==None: lstfile=src+".pcp_lst"
	rsync_list=kwargs.get("rsync-list",src+".pcp_rsync_list/")
	if rsync_list==None: rsync_list=src+".pcp_rsync_list/"
	#if os.path.exists(logfile):
	#	doneFolders=[l.strip() for l in open(logfile,'r').readlines()]
	#	logFile=open(logfile,"a")
	#else: logFile = open(logfile, "w")

	#rsync_options=kwargs.get("rsync","")
	#if rsync_options  == None: rsync_options=""
	#if  kwargs["no_scan"] and os.path.exists(lstfile):
	#	files=[l.strip() for l in open(lstfile,"r").readlines()]
	#else:
	print("Finding files to copy........")
	fparams=kwargs.get("find_params",None) if kwargs.get("find_params",None) else ""
	files=run("find  %s -type f  %s"%(src,fparams))
	#	print(lstfile)
	#	lst=open(lstfile,"w")
	#	lst.write(files)
	#	lst.close()
	#	print("Wrote file list to %s"%lstfile)
	files=files.split("\n")
	print("Found %s files"%str(len(files)-1))


	if not os.path.exists(dest): os.makedirs(dest)
	if not os.path.exists(rsync_list): os.makedirs(rsync_list)
	dest_size=checkDest(dest)
	dest_limit=dest_size*0.95
	original_dest_limit=dest_limit
	partitions={}
	copy_list=[]
	badfiles=[]
	bigfiles={}
	for file in files:
		if file=="": continue
		try:
			fsize=float(os.path.getsize(file))
		except:
			badfiles.append(file)
			continue
		if fsize<=dest_limit:
			copy_list.append(file)
			dest_limit-=fsize
		else:
			if fsize > original_dest_limit:
				bigfiles[file]=fsize
				continue
			added=False
			for key in partitions:
				if fsize < partitions[key]["remaining"]:
					partitions[key]["files"].append(file)
					partitions[key]["remaining"]-=fsize
					added=True
					break
			if added: continue
			partitions[len(partitions.keys())+1]={"files":copy_list,"remaining":dest_limit}
			copy_list=[]
#			if kwargs["dry_run"]:
			dest_limit=original_dest_limit
			copy_list.append(file)
			dest_limit-=fsize
#			else:
#				print("HDD is full, breaking....")
#				break
	for key in partitions:
		rl_name = rsync_list + ".pcp." + str(key)
		rl = open(rl_name, "w")
		files_count = len(partitions[key]["files"])
		rl.write("\n".join(partitions[key]["files"]))
		rl.close()
		print("%s saved to %s, remaining %s" % (files_count, rl_name, sizeof_fmt(partitions[key]["remaining"])))
#	if not kwargs["dry_run"]:
#		print (datetime.datetime.now())
#		res='rsync --safe-links %s %s --files %s %s'%(Config.rsync_options,rsync_options,rsync_list[-1],savePath)
#		print(res)
#		code=run(res,output=False)
#		print (datetime.datetime.now())
#		if code==0:
#			files=open(rsync_list[-1]).read()
#			logFile.write(files)
#			logFile.flush()
	if len(badfiles)>0:
		print ("The following files won't be copied")
		print ("\n".join(["\t"+b for b in badfiles]))
	if len(bigfiles.keys())>0:
		print ("The following files are big and can't be  copied to the current media type")
		print ("\n".join(["\t" +b for b in  bigfiles.keys()]))
		print ("Total Big files",sizeof_fmt(sum(bigfiles.values())))

if __name__=="__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("src", help="Source Directory")
	parser.add_argument("dest", help="Dest Mountpoint")
	#parser.add_argument("-lg", "--log", help="Log File to use")
	#parser.add_argument("-ls", "--lst", help="List File to use")
	parser.add_argument("-s","--save-to",help="Where to save rsync list")
	#parser.add_argument("-ns", "--no-scan", help="Don't rescan the folder, this needs a previous run",action='store_true')
	#parser.add_argument("-d", "--dry-run", help="don't run rsync, just break file list, assume equal size drives",action='store_true')
	#parser.add_argument("-rs", "--rsync", help="Extra rsync parameters")
	parser.add_argument("-fp", "--find-params", help="Parameters to find command")
	args = parser.parse_args()
	copy(**vars(args))
