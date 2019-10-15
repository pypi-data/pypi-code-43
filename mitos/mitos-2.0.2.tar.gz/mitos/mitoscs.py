'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

client/server inplementation of the mitos webserver compute component

Layout
-------

There are three components: 
- The server has one process that puts new jobs in the job queue
- and one process processing results from the result queue.
- A client (there can be many) retrieves a job from the job queue, 
  computes the job with MITOS, and returns the results in 
  the result queue.
  
Operation
---------

Start the server: 
    mitoscs.py server

Start a client:
    mitoscs.py client

Clean shutdown (clients are allowed to finish and return their current job):
    mitoscs.pt quit

Unclean shutdown (server processes are immediately stopped - clients behaviour is undefined.):
    mitoscs.pt kill

Get status info:
    mitoscs.pt status
    
Kill a single client
    mitoscs.py CLIENTNAME (as shown in status)

Logging
-------

both client and server will log with loglevel INFO to file CONFIG.QUEUE_LOGFILE

status info is frequently updated in CONFIG.QUEUE_STATUSFILE

Error Mails
-----------

Are sent by the clients in case of repeated connection problems (>1 day). 
All other errors are sent by the server process. Errors mails are sent in the 
following cases: 

- repeated connection problems (>1 day)
- an exception caused by mitos (the details on the exception can be found in 
  trace.log in the work dir)

- queue server has seen no client for more than a day
- queue server recognizes a (non idle) client that is working for more than a day
  on the same thing
- queue server recognizes an idle client that has sent no alive signal for more 
  than a day
- exception in the loop of the job queue server  
- exception in the loop of the result queue server  
- exit of the server 


Server (Job Queue Process)
--------------------------

The aim of this process is to take the jobfiles deposited by the server,  
store the data in a job-dict and put this in the queue. In order to allow
cancelling jobs from the webserver this is done such that at most one job 
is in the job queue.  

The process repeats a loop doing the following:

1 check for quit signal. If set: 
  - recover jobs from the queue
  - stop loop

2 check client information for the following:
  - no client seen for more than a day
  - a client works for more than a day on the same thing
  - an idle client sent no alive signal for more than a day  
  in all three cases log messages are written and error mails are sent 

3 if job files is available and job queue is empty
  -> create job dictionary (containing all the data from the job file, 
     the sequence)  
  -> put the job dictionary in the queue
  -> rename the .job file to .wrk

  the option --ignore-new-jobs alters the behaviour such that 
  only job files are considered that have been created before the server 
  process was started (i.e. a modification time smaller than the start time) 

4 if no job was queued (no job-file available or queue 'full')
  then go to sleep for the number of seconds specified with the 
  --sleep parameter   

In case of an Exception: 
- jobs in the queue are recovered (due to client errors more
  than one job may be in the queue)
  -> the corresponding .wrk file is renamed to .job
- exeception information is written to the log file
- mail is sent to the admin 
- (clean) shutdown is signaled to other components 

Server (Result Queue Process)
-----------------------------

The result queue server repeatedly:

1 check for abort signal 
  - if hard abort: stop immediately 
  - otherwise only stop if there are no more clients 
2 get a result from the result queue
3 unzip the results 
4 copy the directory and the zip to the web server path
5 rename the jobfile: .wrk to .log
6 send email to user including the link to the results
  if the error flag is set then user and admin is informed that an error happened
  
  If the option --no-user-mail is set, then no mail is sent to the user. 
  
These steps are in a try-except block. In case of any error: 
- log is written and admin mail is sent.
- hard abort signal is set (when the result queue is down then no partial results 
  could be received anyway) 

Client
------

client accesses the job and results queue and executes the following loop:
1 check svn-revision (if mismatch raise an error)
2 check if quit flag is set. If so abort.    
3 try to get a job from job queue (a dict containing the necessary data)
  - X second timeout is used as specified with (--sleep)
  - if nothing is in the queue then start over
4 create the job directory (i.e. WRKPATH/HASH/) containing the fasta file 
5 run mitos
6 zip results and append the zip data to the job dict 
7 put the results (the job dict) in the result queue
8 clean up (remove zip and directory)
  - if --keep is given on the command line then nothing is deleted  
  - the case that client and server are working on the same WKRPATH 
    is handled. If in step 4 the directory already exists nothing is 
    deleted. 

step 5 (MITOS) is enclosed in try-except if anything fails the following happens
- a file trace.log containing the Traceback is created in the job directory  
- an error logged
- an error flag is set in the job dict 
- the client continues !

in case of connection problems (EOFError, socket.error) the client function 
is restarted after period SLEEPTIME which is a global variable
- SLEEPTIME is initialised with 1
- after each connection problem SLEEPTIME is doubled
- after a successful job retrival the SLEEPTIME is reset to 1
- if SLEEPTIME gets greater than MAXSLEEP the client is aborted 
  (causing a mail to QUEUE_ADM)

Uncaught Exceptions are logged, an mail to QUEUE_ADM is sent and the client is 
aborted.

necessary programs
------------------
zip, svn

special run mode
----------------

the options --ignore-new-jobs --no-user-mail are intended for the case that 
some erroneous jobs need to be restarted without noticing the users.
'''

import fcntl
import glob
import json
import logging
import logging.handlers
from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import SyncManager, DictProxy
from multiprocessing.queues import Empty
import os
import shutil

from smtplib import SMTP
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr

import socket
import io
import subprocess
import sys
from time import sleep, time, strftime, localtime
import traceback

from mitos import mitos

import CONFIG


# global variable for managing progressively increasing wait
# times in case of connection errors
SLEEPTIME = 1
MAXSLEEP = 32768  # compares to at least 3/4 days without connection
ONEDAY = 86400
# ONEDAY = 120

class RevisionMismatch( Exception ):
    pass

class TimeoutException( Exception ):
    pass

class ZIPError( Exception ):
    pass

class QueueManager( SyncManager ): pass


def send_email( sender, recipient, subject, body ):
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode( body_charset )
        except UnicodeError:
            pass
        else:
            break

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr( sender )
    recipient_name, recipient_addr = parseaddr( recipient )

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str( Header( str( sender_name ), header_charset ) )
    recipient_name = str( Header( str( recipient_name ), header_charset ) )

    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode( 'ascii' )
    recipient_addr = recipient_addr.encode( 'ascii' )

    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = MIMEText( body.encode( body_charset ), 'plain', body_charset )
    msg['From'] = formataddr( ( sender_name, sender_addr ) )
    msg['To'] = formataddr( ( recipient_name, recipient_addr ) )
    msg['Subject'] = Header( str( subject ), header_charset )

    # Send the message via SMTP to EMAILSERVER
    smtp = SMTP( CONFIG.EMAILSERVER )
    smtp.sendmail( sender, recipient, msg.as_string() )
    smtp.quit()


def change_permissions( path, perm ):
    """
    recursively set permissions in a path
    @param path the path
    @perm the permissions to set
    """

    os.chmod( path, perm )

    for root, dirs, files in os.walk( path ):
        for momo in dirs:
            change_permissions( os.path.join( root, momo ), perm )
        for momo in files:
            os.chmod( os.path.join( root, momo ), perm )

def check_clients( stad ):
    """
    check the state of the clients for 
    a) > 1 day of not seeing any client
    b) > 1 day that an idle client did not signaled that he is alive 
    
    in both cases an error is logged. 
    in case b) the corresponding client is removed from the status data stucture
    @param stad status data stucture
    @return nothing   
    """

    # if the last time a client was seen is more than 1day ago:
    # send error message, write log message, and reset time to
    # now (otherwise mails would be sent in sleept-intervals)
    if ( stad["time_client"] == None and time() - stad["time_server"] > ONEDAY ) or\
        ( stad["time_client"] != None and time() - stad["time_client"] > ONEDAY ):

        senderr( "server (job queue)", "no client since > 1 day" )
        logging.error( "no client since > 1 day" )
        stad.update( [( "time_client", time() )] )

    # if a client is idle for more than a day
    # mail a massage and remove the client (assume as dead)
    for k in list(stad.keys()):
        if k == "quit" or k == "revision" or k.startswith( "time" ) or k.startswith( "jobs_" ):
            continue

#        print k, "status_since", time() - stad[k]["status_since"]
#        print k, "alive", time() - stad[k]["alive"]

        if stad[k]["status"] != "idle" and time() - stad[k]["status_since"] > ONEDAY:
            logging.error( "client %s working on %s for more than one day" % ( k, stad[k]["status"] ) )
            senderr( "mitos ", "client %s working on %s for more than one day -> removed from list" % ( k, stad[k]["status"] ) )
            logging.info( "%s logged out" % k )
            del stad[k]
            continue

        if stad[k]["status"] == "idle" and time() - stad[k]["alive"] > ONEDAY:
            logging.error( "last alive from client %s more than one day ago" % ( k ) )
            senderr( "mitos ", "last alive from client %s more than one day ago" % ( k ) )
            logging.info( "%s logged out" % k )
            del stad[k]
            continue

def count_clients( stad, status = None ):
    """
    count the number of clients registered in the stad
    @param stad status data
    @param status only count clients with the given status, if None count all
    @return number
    """

    count = 0
    for k in list(stad.keys()):
        if k == "quit" or k == "revision" or k.startswith( "time" ) or k.startswith( "jobs_" ):
            continue

        if stad[k]["status"] == "offline":
            logging.info( "client %s logged out" % k )
            del stad[k]
            continue

        if status == None or stad[k]["status"] == status:
            count += 1

    return count

def getrevision():
    """
    get the svn revision number from the output of svn info
    @return revision number 
    """

    try:
        revision = None
        _p = subprocess.Popen( ["svn", "info"], stdout = subprocess.PIPE )
        svninfo = _p.communicate()[0]
        for line in svninfo.split( "\n" ):
            if line.startswith( "Revision" ):
                revision = line.split()[1]
                break
        if revision == None:
            raise Exception( "RevisionError" )
        _p = None
    except:
        logging.error( "could not get revision number" )
        raise

    return revision

def getrevisiondate():
    """
    get the svn revision date 
    @return revision date 
    """

    try:
        revision = None
        _p = subprocess.Popen( ["svn", "info"], stdout = subprocess.PIPE )
        svninfo = _p.communicate()[0]
        for line in svninfo.split( "\n" ):
            if line.startswith( "Last Changed Date" ):
                revision = line.split()[3]
                break
        if revision == None:
            raise Exception( "RevisionError" )
        _p = None
    except:
        logging.error( "could not get revision number" )
        raise

    return revision

def print_status( stad, jobq, f ):
    """
    print status info into stream f
    
    @param stad status data
    @param jobq jobqueue
    @param f file stream
    """

    f.write( "MITOS revision %s (%s)\n" % ( getrevision(), getrevisiondate() ) )

    if stad["time_server"] == None:
        f.write( "running since is invalid\n" )
    else:
        f.write( "running since %s\n" % strftime( "%d.%m.%Y %H:%M:%S", localtime ( stad["time_server"] ) ) )

    f.write( "current time %s\n" % strftime( "%d.%m.%Y %H:%M:%S", localtime() ) )
    if "quit" in stad:
        f.write( "shutting down %s\n" % stad["quit"] )

    f.write( "last client contact " )
    if stad["time_client"] == None:
        f.write( "never" )
    else:
        f.write( "%s" % strftime( "%d.%m.%Y %H:%M:%S", localtime ( stad["time_client"] ) ) )
    f.write( "\n" )
    f.write( "last result received " )
    if stad["time_result"] == None:
        f.write( "never" )
    else:
        f.write( "%s" % strftime( "%d.%m.%Y %H:%M:%S", localtime ( stad["time_result"] ) ) )
    f.write( "\n" )

    f.write( "====jobs====\n" )
    f.write( "  %d waiting\n" % ( stad["jobs_available"] ) )
    f.write( "  %d queued\n" % ( not jobq.empty() ) )

    f.write( "clients: %d / %d idle \n" % ( count_clients( stad, "idle" ), count_clients( stad, None ) ) )
    idle = 0
    busy = 0

    for k in list(stad.keys()):
        if k == "quit" or k == "revision" or k.startswith( "time" ) or k.startswith( "jobs_" ):
            continue

        if stad[k]["status"] == "offline":
            logging.info( "client %s logged out" % k )
            del stad[k]
            continue

        atm = stad[k]["alive"]
        stm = stad[k]["status_since"]

        if stad[k]["status"] == "idle":
            idle += 1
            f.write( "%s idle since %s last seen %s \n" % ( k, \
                            strftime( "%d.%m.%Y %H:%M:%S", localtime ( stm ) ), \
                            strftime( "%d.%m.%Y %H:%M:%S", localtime ( atm ) ) ) )
        else:
            busy += 1
            f.write( "%s %s... since %s \n" % ( k, stad[k]["status"][:8], \
                            strftime( "%d.%m.%Y %H:%M:%S", localtime ( stm ) ) ) )

        if "quit" in stad and stad["quit"] == k:
            f.write( "     will quit\n" )

    f.write( "====history====\n" )
    f.write( "  %d finished last week\n" % ( stad["jobs_loggedw"] ) )
    f.write( "  %d finished last month\n" % ( stad["jobs_loggedm"] ) )
    f.write( "  %d finished last year\n" % ( stad["jobs_loggedy"] ) )

#    qlen = len( available )
#    if not jobq.empty():
#        qlen += 1


def recoverjobs( jobq ):
    """
    get all jobs in the job queue and rename the corresponding wrk file to job
    @param[in] jobq the job queue
    """

    logging.info( "recovering queued jobs" )
    # recoved the queued job (if any)
    while not jobq.empty():
        try:
            job = jobq.get()
        except:
            logging.error( "could not recover any job from queue" )
            break

        try:
            shutil.move( CONFIG.TOMCATPATH + job["hsh"] + ".wrk", CONFIG.TOMCATPATH + job["hsh"] + ".job" )
        except:
            logging.error( "could not recover %s from queue" % ( job["hash"] ) )

        logging.info( "job %s recovered" % job["hash"] )

def resetjobs():
    """
    check for .wrk files in the directory 
    -> rename to .job
    -> remove partial data in the directory 
    """
    jobs = glob.glob( CONFIG.TOMCATPATH + "/*.wrk" )

    for j in jobs:
        base = os.path.splitext( j )[0]

        f = open( base + ".wrk", "r" )
        job = json.load( f )
        f.close()

        hsh = job["hash"]

        shutil.move( j, base + ".job" )
        for f in glob.glob( base + "/*" ):
            if os.path.isdir( f ):
                shutil.rmtree( f )
            elif not f.endswith( "sequence.fas" ):
                os.remove( f )

        logging.info( "reseted job %s" % hsh )

def senderr( foo, problem ):
    """
    send an email to the admin
    @param foo string describing the place where the error occured, ie the function
    @param problem string giving the problem
    """

    # Prepare e-mail
    msg = """host: {host}
foo: {foo}
problem : {problem}
""".format( foo = foo, problem = problem, host = socket.gethostname() )

    # send e-mail
    try:
        send_email( "mitos@bioinf.uni-leipzig.de", CONFIG.QUEUE_ADM, "MITOS error", msg )

#        server = SMTP()
#        server.connect( CONFIG.QUEUE_MAILSERVER )
#        server.sendmail( "mitos@bioinf.uni-leipzig.de", CONFIG.QUEUE_ADM, msg )
#        server.close()
    except Exception as inst:
        logging.warning( "email error: " + str( inst ) )


def update_access( stad ):
    """
    update access info for the last days
    """

    available = glob.glob( CONFIG.TOMCATPATH + "/*.job" )
    stad.update( [( "jobs_available", len( available ) )] )

    # get logged jobs
    logged = glob.glob( CONFIG.TOMCATPATH + "/*.log" )
#    for l in logged:
#        print l, time() - os.path.getmtime( l )

    # get those in the time range of interest
    cnt = len( [ x for x in logged  if ( time() - os.path.getmtime( x ) ) <= 7 * ONEDAY  ] )
    stad.update( [( "jobs_loggedw", cnt )] )

    cnt = len( [ x for x in logged  if ( time() - os.path.getmtime( x ) ) <= 31 * ONEDAY  ] )
    stad.update( [( "jobs_loggedm", cnt )] )

    cnt = len( [ x for x in logged  if ( time() - os.path.getmtime( x ) ) <= 365 * ONEDAY  ] )
    stad.update( [( "jobs_loggedy", cnt )] )


def client( keep, sleept ):
    """
    connect to the server queue and get jobs from the job queue 
    this mitos result is zipped and sent back via the result 
    queue
    
    @param keep keep temporary files and dirs
    @paran sleept seconds to wait for a job from the queue
    """

    # get info on the client (svn revision, hostname, and pid)
    revision = getrevision()
    host = socket.gethostname()
    pid = os.getpid()
    clientname = host + "-" + str( pid )

    # get job and result queue and the status data structure
    QueueManager.register( 'get_jobq' )
    QueueManager.register( 'get_resq' )
    QueueManager.register( 'get_stad' )
    m = QueueManager( address = ( CONFIG.QUEUE_IP, CONFIG.QUEUE_PORT ), authkey = CONFIG.QUEUE_KEY )
    m.connect()
    jobq = m.get_jobq()
    resq = m.get_resq()
    stad = m.get_stad()

    # log output
    logging.info( "client running %s (v%s)" % ( clientname, revision ) )

    # set initial status
    stad.update( [( clientname, {"status":"idle", "status_since": time(), "alive":time()} )] )

    # main client loop

    loop = True

    while loop:
        # reset job (just to be sure)
        job = {}

        # check status for abort signal
        if "quit" in stad and ( stad["quit"].startswith( "all" ) or stad["quit"] == clientname ):
            logging.info( "received quit signal" )
            break

        # check client and server version. in case of mismatch abort
        if stad["revision"] != revision:
            logging.error( "revision mismatch client: %s server: %s" \
                          % ( revision, stad["revision"] ) )
            raise RevisionMismatch

        # try to get a job
        # - if queue empty just update status info and start over
        try:
            job = jobq.get( timeout = sleept )
        except Empty:
            stad.update( [( clientname, {"status":"idle", \
                                         "status_since": stad[clientname]["status_since"], \
                                         "alive":time()} )] )
            continue
        except:
            raise

        # a successful job retrieval
        # - reset the SLEEPTIME
        # - update status info
        # - store client name in the job
        logging.info( "received job %s" % job["hash"] )
        SLEEPTIME = 1
        stad.update( [( clientname, {"status":job["hash"], "status_since": time(), \
                                     "alive":time()} )] )
        job["host"] = clientname

        # create job dir and fasta file if necessary
        # - if already existing -> assume that client runs in the same path as server
        # - else just save the info that the client is working in the same directory
        #   as the server -> because the dir should not be deleted later
        fastafile = CONFIG.WRKPATH + job["hash"] + "/sequence.fas"
        if not os.path.exists( CONFIG.WRKPATH + job["hash"] ) and not os.path.exists( fastafile ):
            os.mkdir( CONFIG.WRKPATH + job["hash"] )
            f = open( fastafile, "w" )
            f.write( job["fasta"] )
            f.close()
            samedir = False
        else:
            samedir = True

        # run mitos
        # - in case of an exception save the exception in the job work directory, set the error
        #   flag in the job, and write log message. the results are later zipped anyway
        #   and sent to the server.
        featurelist = []
        try:
            # Start the scans
            # print ( fastafile, code, cutoff,  evalue, finovl,  maxovl, clipfac, fragovl,  fragfac,  ststrange,  prot,  trna,  rrna )
            featurelist = mitos( fastafile, job["code"], cutoff = job["cutoff"], \
                                 minevalue = job["evalue"], finovl = job["finovl"], \
                                 maxovl = job["maxovl"], clipfac = job["clipfac"], \
                                 fragovl = job["fragovl"], fragfac = job["fragfac"], \
                                 ststrange = job["ststrange"], prot = job["prot"],
                                 trna = job["trna"], rrna = job["rrna"] )

#            # read fasta
#            f = open( fastafile, "r" )
#            # parse fasta header
#            acclist = f.readline()[1:].strip()
#            f.close()
#
#            acc = []
#            for a in acclist:
#                if a.isalnum() or a == "_" or a == "-":
#                    acc.append( a )
#                else:
#                    break
#
#            if len( acc ) == 0:
#                acc = "UNK"
#            else:
#                acc = "".join( acc )

#            "_".join( acclist )
#            acc = acclist[0]
#            for i in range( 1, len( acclist ) ):
#                acc += "_" + acclist[i]

#            print  ( CONFIG.WRKPATH + job["hash"] )
#            print "%s/result" % ( CONFIG.WRKPATH + job["hash"] )



        except KeyboardInterrupt:
            logging.error( "MITOS was aborted during excecution of %s" % job["hash"] )
            job["error"] = "MITOS was aborted during excution by KeyboardInterrupt on %s" % ( clientname )
            loop = False
        except:
            stream = io.StringIO()
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_exception( exceptionType, exceptionValue, exceptionTraceback, file = stream )
            e = stream.getvalue()
            f = open( "%s/%s/trace.log" % ( CONFIG.WRKPATH, job["hash"] ), "a" )
            f.write( e )
            f.close()
            logging.error( "error in MITOS " + e )
            job["error"] = e
            stream.close()

        # zip the job work directory
        # read the zip in a string and save it in the job
        # return everything to the server
        ret = subprocess.call( "cd {path}; zip -9 -y -r -q {hash}.zip {hash}/".format( path = CONFIG.WRKPATH, hash = job["hash"] ), shell = True )
        if ret != 0:
            logging.error( "zip returned non zero %d" % ret )
            raise ZIPError

        f = open( CONFIG.WRKPATH + job["hash"] + ".zip" )
        job["zip"] = f.read()
        f.close()

        # remove dir and zip file
        if not keep and not samedir:
            shutil.rmtree( CONFIG.WRKPATH + job["hash"] )
            os.remove( CONFIG.WRKPATH + job["hash"] + ".zip" )

        resq.put( job )
        logging.info( "returned results %s" % job["hash"] )

        # status update
        stad.update( [( clientname, {"status":"idle", "status_since": time(), "alive":time()} )] )

    stad.pop( clientname, None )
    return False

def server( jobq, stad, sleept, newjobs ):
    """
    checks for new jobs (.job files) and delivers them to a queue
    this is done such that at most one job is queued 
    @param jobq the queue to put the job in
    @param stad status distionary
    @param sleept how long to sleep befor checking again for a new job file
    @param newjobs accept only job files created before the server was started iff false;
        otherwise process all jobfiles 
    """

    logging.info( "job queue started" )

    while 1:
        try:
            # check status for abort signal
            if "quit" in stad and ( stad["quit"].startswith( "all" ) ):
                recoverjobs( jobq )
                break

            # update info if a client was seen
            if count_clients( stad ) > 0:
                stad.update( [( "time_client", time() )] )

            update_access( stad )


            # check clients availability and result response times
            # are within reasonable limits
            check_clients( stad )


            delivered = False  # has something been delivered to the queue?

#            print "get lock"
#            lock = open( "%s/.lock" % ( CONFIG.WRKPATH ), "w" )
#            os.chmod( "%s/.lock" % ( CONFIG.WRKPATH ), 775 )
#            fcntl.flock( lock.fileno(), fcntl.LOCK_EX )
#            print "got lock"

            # get available jobs sorted by modification time
            available = glob.glob( CONFIG.TOMCATPATH + "/*.job" )
            available.sort( key = lambda x: os.path.getmtime( x ) )

            # remove jobs created after the server start
            if not newjobs:
                available = [ x for x in available if os.path.getmtime( x ) < stad["time_server"] ]

            sf = open( CONFIG.QUEUE_STATUSFILE, "w" )
            print_status( stad, jobq, sf )
            sf.close()

            # check if there are jobs available and the queue is empty
            if len( available ) > 0 and jobq.empty():
                path = os.path.splitext( available[0] )[0]
                shutil.move( available[0], path + ".wrk" )

                f = open( path + ".wrk", "r" )
#                cols = f.readline().strip().split( "|" )
                job = json.load( f )
                f.close()

#                hsh = cols[0]
#                 # save file contents of the uploaded fasta file
# #                fastafile = CONFIG.WRKPATH + hsh + "/sequence.fas"
#                 fastafile = CONFIG.TOMCATPATH + job["hsh"] + "/sequence.fas"
#
#                 f = open( fastafile, "r" )
#                 fastacontent = f.read()
#                 f.close()

                # get job description from string
#                job = {"hash": hsh, \
#                       "name": cols[1], \
#                       "email": cols[2], \
#                       "code": int( cols[3] ), \
#                       "filename": cols[4], \
#                       "clipfac": float( cols[5] ), \
#                       "evalue": float( cols[6] ), \
#                       "ststrange": int( cols[7] ), \
#                       "finovl": float( cols[8] ), \
#                       "fragovl": float( cols[9] ) / 100, \
#                       "fragfac": float( cols[10] ), \
#                       "maxovl": float( cols[11] ) / 100, \
#                       "prot": int( cols[12] ), \
#                       "trna": int( cols[13] ), \
#                       "rrna": int( cols[14] ), \
#                       "cutoff": "%" + cols[15], \
#                       "fasta": fastacontent }
#                 job["fasta"] = fastacontent

                # check if there are requests from clients
#                logging.info( "sending job %s" % hsh )
                logging.info( "sending job %s" % job["hash"] )
                jobq.put( job )
                delivered = True

#            fcntl.flock( lock.fileno(), fcntl.LOCK_UN )
#            lock.close()

            if not delivered:
                sleep( sleept )

        except Exception as inst:
            recoverjobs( jobq )
            stream = io.StringIO()
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_exception( exceptionType, exceptionValue, exceptionTraceback, file = stream )
            logging.error( "server (job queue) error: %s" % ( str( inst ) ) )
            logging.error( stream.getvalue() )
            stream.close()

            # signal (clean) shutdown to other components: result queue and clients
            stad.update( [( "quit", "allclean" )] )

            # signal the admin
            senderr( "server (job queue)", "aborting due to an exception. clean shutdown request has been issued." )

            break

    logging.info( "job queue server stopped " )

def rserver( resq, statd, sleept, usermail ):
    """
    receives results from the clients
    unzips them and copies it to the webserver direcory, 
    send mail to the user
    @param resq the queue to check for results
    @param usermail true iff mail to user should be sent    
    """

    logging.info( "result queue started " )

    while 1:

        res = {}
        try:
            # check status for abort signal
            if "quit" in stad and stad["quit"].startswith( "all" ) :
                if statd["quit"] == "allclean" and count_clients( stad ) > 0:
                    logging.info( "not all results returned. will wait longer." )
                else:
                    break

            try:
                res = resq.get( timeout = sleept )
            except Empty:
                continue
            except:
                raise


            logging.info( "received result %s from %s" % ( res["hash"], res["host"] ) )

            # update info that a result was seen
            stad.update( [( "time_result", time() )] )

            # unzip
            f = open( CONFIG.TOMCATPATH + res["hsh"] + ".zip", "w" )
            f.write( res["zip"] )
            f.close()

#            print "unzip", res["hsh"]
            ret = subprocess.call( "cd {path}; unzip -u -o -q {hash}.zip".format( path = CONFIG.TOMCATPATH, hash = res["hsh"] ), shell = True )
            if ret != 0:
                raise ZIPError

            # change permission of everything
            change_permissions( "{path}/{hash}/".format( path = CONFIG.TOMCATPATH, hash = res["hsh"] ) , 0o777 )
            change_permissions( "{path}/{hash}.zip".format( path = CONFIG.TOMCATPATH, hash = res["hsh"] ) , 0o777 )

#             if CONFIG.TOMCATPATH != CONFIG.WRKPATH:
#                 newpath = CONFIG.TOMCATPATH + res["hsh"] + "/"
#                 if os.path.exists( newpath ):
#                     logging.warning( "target path already existing %s" % newpath )
#                     shutil.rmtree( newpath )
#                 shutil.copytree( CONFIG.WRKPATH + res["hsh"], newpath )

            # handle wrk file (rename to log)
            shutil.move( "%s/%s.wrk" % ( CONFIG.TOMCATPATH, res["hsh"] ), "%s/%s.log" % ( CONFIG.TOMCATPATH, res["hsh"] ), )
#            change_permissions( "{path}/{hash}.log".format( path = CONFIG.TOMCATPATH, hash = res["hsh"] ) , 0777 )

            if "error" in res:
                senderr( "mitos", "job %s caused an error in mitos.\nexecuting client: %s\n%s " % ( res["hash"], res["host"], res["error"] ) )

            if res["email"] != "None":
                # Prepare e-mail
#                msg = "To: " + res["email"] + "\n"
#                msg += "Subject: MITOS results\n"
#                msg += "\n"
                msg = ""
                msg += "Dear %s,\n\n" % ( res["name"] )
                if "error" in res:
                    msg += """
MITOS experienced some unexpected error.
The administrators have been notified.    
You may get in contact with us by replying to this email .

Please mention the job ID: {hsh}

Sorry for the inconvenience,
MITOS 
""".format( hsh = res["hsh"] )
                else:
                    if "jobid" in res and res["jobid"] != "":
                        msg += "The results for the job: {jobid}\n".format( jobid = res["jobid"] )
                    else:
                        msg += "The results for your request file: {filename}\n".format( filename = res["filename"] )

                    msg += """can be found at: 
http://{url}result.py?hash={hsh}

Do not hesitate to contact us if you have any questions or
problems regarding MITOS or its results. You can do so by
simply answering to this email.

Regards, 
MITOS

P.S.: If the link is broken over several lines you may need
to copy the link manually to the browser. The link must be
of the form 
http://{url}result.py?hash=HASH 
where HASH consists of 8 numbers or characters.

""" .format( url = CONFIG.WEBPATH, hsh = res["hsh"] )

		    msg += "\n\n"
                # send e-mail (if not disabled)
            if usermail:
                try:
                    send_email( "mitos@bioinf.uni-leipzig.de", res["email"], "MITOS results", msg )
                except Exception as inst:
                    logging.warning( "email error: " + str( inst ) )

            logging.info( "finished job %s" % res["hash"] )

        except Exception as inst:
            stream = io.StringIO()
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_exception( exceptionType, exceptionValue, exceptionTraceback, file = stream )
            logging.error( "server (result queue) error: %s" % ( str( inst ) ) )
            logging.error( stream.getvalue() )

            senderr( "server (result queue)", "aborting due to an exception" )

            # signal (unclean) shutdown to other components: job queue and clients
            stad.update( [( "quit", "alldirty" )] )

            break

    logging.info( "result queue stopped" )

if __name__ == '__main__':
    from optparse import OptionParser, OptionGroup

    usage = """usage: %prog [options] [command]
server: start the server 
client: start a client
quit  : clean shutdown (clients are allowed to finish)
kill  : dirty shutdown (server processes are stopped immediately)
status: Get status info
clientname: clean shutdown client"""
    parser = OptionParser( usage )
    parser.add_option( "-s", '--sleep', dest = "sleep", action = "store", type = "int", default = 60, help = "#sec to sleep polling a queue or jobdir" )
    parser.add_option( "-l", '--log', dest = "log", action = "store", default = None, help = "log file" )

    group = OptionGroup( parser, "server options" )
    group.add_option( '--no-user-mail', dest = "usermail", action = "store_false", default = True, help = "disable mails sent to users" )
    group.add_option( '--ignore-new-jobs', dest = "newjobs", action = "store_false", default = True, help = "process only jobs added before start of the server" )
    parser.add_option_group( group )

    group = OptionGroup( parser, "client options" )
    group.add_option( "--keep", action = "store_true", default = False, help = "keep temporary files (default: delete)" )
    parser.add_option_group( group )

    ( options, args ) = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel( logging.INFO )
    formatter = logging.Formatter( CONFIG.LOGFMT )

    ch = logging.StreamHandler()
    ch.setLevel( logging.WARNING )
    ch.setFormatter( formatter )
    logger.addHandler( ch )

    if len( args ) != 1:
        logging.error( "no command given" )
        sys.exit()

    fh = None
    if os.path.exists( CONFIG.QUEUE_LOGFILE ):
        fh = logging.handlers.WatchedFileHandler( CONFIG.QUEUE_LOGFILE )
    elif options.log != None:
        fh = logging.handlers.WatchedFileHandler( options.log )

    if fh == None:
        logging.warning( "neither QUEUE_LOGFILE nor -l specified. will not log to file." )
    else:
        fh.setLevel( logging.INFO )
        fh.setFormatter( formatter )
        logger.addHandler( fh )


    if args[0] == "server":
        logging.info( "starting server" )
        senderr( "mitos", "MITOS has been started." )
        jobq = Queue()  # job queue
        resq = Queue()  # result queue

        mgr = Manager()
        stad = mgr.dict()

        QueueManager.register( 'get_jobq', callable = lambda:jobq )
        QueueManager.register( 'get_resq', callable = lambda:resq )
        QueueManager.register( 'get_stad', callable = lambda:stad, proxytype = DictProxy )
        m = QueueManager( address = ( '', CONFIG.QUEUE_PORT ), authkey = CONFIG.QUEUE_KEY )
#        qserver = m.get_server()
        m.start()

        stad.update( [( "revision", getrevision() ), \
                      ( "time_client", None ), \
                      ( "time_result", None ), \
                      ( "time_server", time() ), \
                      ( "jobs_available", 0 ), \
                      ( "jobs_loggedw", 0 ), \
                      ( "jobs_loggedm", 0 ), \
                      ( "jobs_loggedy", 0 )  ] )

        # start process serving jobs to available clients
        s = Process( target = server, args = ( jobq, stad, options.sleep, options.newjobs ) )
        s.start()
#        print "job server started"

        # start process collecting results from clients
        sr = Process( target = rserver, args = ( resq, stad, options.sleep, options.usermail, ) )
        sr.start()

        s.join()
        sr.join()

        # reset any jobs that might still be running
        resetjobs()
        m.shutdown()
        senderr( "mitos", "MITOS has been shutdown." )

    elif args[0] == "client":
        host = socket.gethostname()
        pid = os.getpid()
        clientname = host + "-" + str( pid )

        cont = True
        while cont:
            try:
                cont = client( keep = options.keep, sleept = options.sleep )
            except EOFError:
                logging.info( "connection lost. starting over in %ds" % ( SLEEPTIME ) )
                if SLEEPTIME > MAXSLEEP:
                    senderr( foo = "client::main", problem = "abort due to repeated connection error" )
                    cont = False
                sleep( SLEEPTIME )
                SLEEPTIME *= 2
            except socket.error:
                logging.info( "socket error. starting over in %ds" % ( SLEEPTIME ) )
                if SLEEPTIME > MAXSLEEP:
                    senderr( foo = "client::main", problem = "abort due to repeated connection error" )
                    cont = False
                sleep( SLEEPTIME )
                SLEEPTIME *= 2
            except KeyboardInterrupt:
                logging.info( "client aborted by keyboard interupt." )

                cont = False
            except Exception as inst:
                stream = io.StringIO()
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                traceback.print_exception( exceptionType, exceptionValue, exceptionTraceback, file = stream )
                e = stream.close()

                logging.error( "client error: %s. aborting" % ( str( inst ) ) )
                logging.error( e )

                senderr( foo = "client %s" % clientname, problem = "abort due to exception: %s" % e )
                cont = False

        logging.info( "client stopped " )

    else:
        # get job and result queue and the status data structure
        try:
            QueueManager.register( 'get_jobq' )
            QueueManager.register( 'get_stad' )
            m = QueueManager( address = ( CONFIG.QUEUE_IP, CONFIG.QUEUE_PORT ), authkey = CONFIG.QUEUE_KEY )
            m.connect()
            jobq = m.get_jobq()
            stad = m.get_stad()
        except:
            sys.stderr.write( "could not connect\n" )
            sys.exit()
        if args[0] == "quit" or args[0] == "exit":
            stad.update( [( "quit", "allclean" )] )
            sys.stderr.write( "quit signal has been sent. please wait for termination.\n" )
        elif args[0] == "halt" or args[0] == "kill":
            stad.update( [( "quit", "alldirty" )] )
            sys.stderr.write( "kill signal has been sent. \n" )
        elif args[0] == "status":
            print_status( stad, jobq, sys.stdout )
            check_clients( stad )
        elif args[0] in stad:
            stad.update( [( "quit", args[0] )] )
            sys.stderr.write( "kill signal has been set for %s \n" % args[0] )
        else:
            sys.stderr.write( "unknown command\n" )
            sys.exit()

        sf = open( CONFIG.QUEUE_STATUSFILE, "w" )
        print_status( stad, jobq, sf )
        sf.close()

    logging.shutdown()
