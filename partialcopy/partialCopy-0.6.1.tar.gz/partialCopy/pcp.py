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

def size_2_bytes(size):
	units = {"B": 1, "K": 10 ** 3, "M": 10 ** 6, "G": 10 ** 9, "T": 10 ** 12, "P":10**15}
	unit=size[-1]
	if unit not in units:
		return int(size)
	number=size[:-1]
	return int(float(number)*units[unit])

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
	doneFiles=[]
	partitions = {}
	copy_list = []
	badfiles = []
	bigfiles = {}

	if src[-1]!="/": src+="/"

	rsync_list=kwargs.get("rsync-list",src+"pcp_rsync_list/")
	if rsync_list==None: rsync_list=src+"pcp_rsync_list/"
	if kwargs["new"] or kwargs["modified_after"]:
		for file in os.listdir(rsync_list):
			pf=[f.strip() for f in open(rsync_list+"/"+file).readlines()]
			partitions[file.split(".")[-1]]={"files":pf[:],"remaining":0}
			doneFiles.extend(pf[:])
	print("Finding files to copy........")
	fparams=kwargs.get("find_params",None) if kwargs.get("find_params",None) else ""
	if kwargs["modified_after"]:
		fparams += " -newermt %s"%(kwargs["modified_after"])
	files=run("find  %s -type f  %s"%(src,fparams))

	files=files.split("\n")
	print("Found %s files"%str(len(files)-1))

	if kwargs.get("dest",None):
		if not os.path.exists(dest): os.makedirs(dest)
	if not os.path.exists(rsync_list): os.makedirs(rsync_list)
	if not kwargs["dest_size"]:
		dest_size=checkDest(dest)
		dest_limit=dest_size*0.95
		original_dest_limit=dest_limit
	else:
		dest_size=size_2_bytes(kwargs["dest_size"])
		dest_limit=dest_size
		original_dest_limit=dest_size

	for file in files:
		if file=="": continue
		if file in doneFiles: continue
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
			dest_limit=original_dest_limit
			copy_list.append(file)
			dest_limit-=fsize
	partitions[len(partitions.keys()) + 1] = {"files": copy_list, "remaining": dest_limit}
	for key in partitions:
		rl_name = rsync_list + "pcp." + str(key)
		if os.path.exists(rl_name) and not kwargs.get("force",None): continue
		rl = open(rl_name, "w")
		files_count = len(partitions[key]["files"])
		rl.write("\n".join(partitions[key]["files"]))
		rl.close()
		print("%s saved to %s, remaining %s" % (files_count, rl_name, sizeof_fmt(partitions[key]["remaining"])))

	if len(badfiles)>0:
		print ("The following files won't be copied")
		print ("\n".join(["\t"+b for b in badfiles]))
	if len(bigfiles.keys())>0:
		print ("The following files are big and can't be  copied to the current media type")
		print ("\n".join(["\t" +b for b in bigfiles.keys()]))
		print ("Total Big files",sizeof_fmt(sum(bigfiles.values())))

if __name__=="__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("src", help="Source Directory")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--dest", help="Destionation mountpoint")
	group.add_argument("--dest-size", help="Destination size, given in bytes or using 1 letter unit B,K,M,G,T,P")
	parser.add_argument("-s","--save-to",help="Where to save rsync list,default '$src/pcp_rsync_list/'")
	parser.add_argument("-f","--force",help="Rewrite all lists again",action = 'store_true')
	parser.add_argument("-n", "--new", help="Find New Files",action='store_true')
	parser.add_argument("-ma", "--modified-after", help="Find files modified after certain time (YYYY-mm-dd)")
	#parser.add_argument("-rs", "--rsync", help="Extra rsync parameters")
	parser.add_argument("-fp", "--find-params", help="Parameters to find command")
	args = parser.parse_args()
	copy(**vars(args))
