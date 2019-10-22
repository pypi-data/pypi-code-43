#!/usr/bin/python
__author__ = 'pawel'

#--- XNAT ---
import sys
import os
import csv
import shutil
#--------------

#--------------
import pycurl
import json
from StringIO import StringIO
from urllib import urlencode
import datetime
#--------------

#--------------
# import matplotlib
# # switch off X-windows (used for storing in png format)
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.ndimage as ndi
#--------------


#-------------- INIT mMR ----------------
import nipet
import pviews
#-----------------------------------------


def time_stamp():
    now    = datetime.datetime.now()
    nowstr = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)
    return nowstr

def create_dir(pth):
    if not os.path.exists(pth):
        os.makedirs(pth)


#----------------------------------------------------------------------------------------------------------
def get_xnatList(usrpwd, xnaturi, cookie=''):
    buffer = StringIO()
    c = pycurl.Curl()
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    else:
        c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.URL, xnaturi )
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    # convert to json dictionary in python
    outjson = json.loads( buffer.getvalue() )
    return outjson['ResultSet']['Result']

def get_xnat(usrpwd, xnaturi, cookie='', frmt='json'):
    buffer = StringIO()
    c = pycurl.Curl()
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    else:
        c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.URL, xnaturi )
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    # convert to json dictionary in python
    if frmt=='':
        output = buffer.getvalue()
    elif frmt=='json':
        output = json.loads( buffer.getvalue() )
    return output

def get_xnatFile(usrpwd, xnaturi, fname, cookie=''):
    try:
        fn = open(fname, 'wb')
        c = pycurl.Curl()
        if cookie:
            c.setopt(pycurl.COOKIE, cookie)
        else:
            c.setopt(c.USERPWD, usrpwd)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(c.VERBOSE, 0)
        c.setopt(c.URL, xnaturi )
        c.setopt(c.WRITEDATA, fn)
        c.setopt(pycurl.FOLLOWLOCATION, 0)
        c.setopt(pycurl.NOPROGRESS, 0)
        c.perform()
        c.close()
        fn.close()
    except pycurl.error as pe:
        print ' '
        print '=============================================================='
        print 'e> pycurl error:', pe
        print '=============================================================='
        print ' '
        print 'w> no data:', sbjid, sbjlb
        return -1
    else:
        print '--------'
        print 'i> pycurl download done.'
        print '--------'
    return 0
#----------------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------
def put_xnat(usrpwd, xnaturi, cookie=''):
    """e.g., create a container"""
    c = pycurl.Curl()
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    else:
        c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.URL, xnaturi )
    c.setopt(c.CUSTOMREQUEST, 'PUT')
    c.perform()
    c.close()

def del_xnat(usrpwd, xnaturi, cookie=''):
    """e.g., create a container"""
    c = pycurl.Curl()
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    else:
        c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.URL, xnaturi )
    c.setopt(c.CUSTOMREQUEST, 'DELETE')
    c.perform()
    c.close()

def post_xnat(usrpwd, xnaturi, post_data, verbose=0, PUT=False):
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.VERBOSE, verbose)
    c.setopt(c.URL, xnaturi )
    if PUT: c.setopt(c.CUSTOMREQUEST, 'PUT')
    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    return buffer.getvalue()

def put_xnatFile(usrpwd, xnaturi, filepath, cookie=''):
    """upload file to xnat server"""
    c = pycurl.Curl()
    if cookie:
        c.setopt(pycurl.COOKIE, cookie)
    else:
        c.setopt(c.USERPWD, usrpwd)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.NOPROGRESS, 0)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.URL, xnaturi )
    c.setopt(c.HTTPPOST, [('fileupload', (c.FORM_FILE, filepath,)),])
    c.perform()
    c.close()
#----------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------
def put_xnatPetMrRes(usrpwd, xnatsbj, sbjix, lbl, frmt, fpth):
    # get the experiment id
    eid = get_xnatList(usrpwd, xnatsbj+'/' +sbjix+ '/experiments?xsiType=xnat:petmrSessionData&format=json&columns=ID')
    # prepare the uri
    xnaturi = xnatsbj+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/' +lbl+ '?xsi:type=xnat:resourceCatalog&format='+frmt
    xnat_put(usrpwd, xnaturi)
    # upload
    xnaturi = xnatsbj+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/' +lbl+ '/files'
    xnat_upload(usrpwd, xnaturi, fpth)



#----------------------------------------------------------------------------------------------------------
def pltQC(hst, outpth, Cnt):
    T = hst['dur']
    # plot headcurve:
    plt.figure(0)
    prm, = plt.plot(range(T), hst['phc']/1000, 'k', label='prompts')
    rnd, = plt.plot(range(T), hst['dhc']/1000, 'r', label='delayeds')
    plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=.5)
    plt.ylabel('kcounts')
    plt.xlabel('seconds')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    plt.savefig(os.path.join(outpth, 'headcurve.png'), format='png', dpi=300)

    # plot centre of mass:
    plt.figure(1)
    scmass = ndi.filters.gaussian_filter(hst['cmass'], 5, mode='mirror')
    plt.plot(scmass,'k')
    plt.grid(b=True, which='major', color='k', linestyle=':', linewidth=.5)
    plt.ylabel('cm')
    plt.xlabel('seconds')
    plt.savefig(os.path.join(outpth, 'mass_centre.png'), format='png', dpi=300)
    # ---
    #find the peak in hc to get the zooming-in range
    # i = np.argmax(hst['phc'])
    # ymin = np.floor( min(hst['cmass'][i:i+300]) )
    # ymax = np.ceil( max(hst['cmass'][i+100:]) )

    # prompt peak
    HCpeakIdx = np.nanargmax(hst['phc'])
    # the centre of mass peak has to be just around the prompt peak
    CMpeakIdx = np.nanargmax(hst['cmass'][:HCpeakIdx+60])
    # lowest point after the peak
    lcmss = np.nanmin(hst['cmass'][CMpeakIdx:])
    # get the index of the point
    il = CMpeakIdx + np.nanargmin(hst['cmass'][CMpeakIdx:])
    ymin = np.floor(lcmss*10)/10
    ymax = np.nanmax(hst['cmass'][il:])
    # range
    Rng = ymax-ymin
    if Rng<0.5:  ymax += 0.5-Rng
    plt.ylim([ymin, ymax])
    plt.xlim([0,hst['dur']])
    plt.savefig(os.path.join(outpth, 'mass_centre_zoom.png'), format='png', dpi=300)


#----------------------------------------------------------------------------------------------------------




#==========================================================================================================
# DOWNLOAD XNAT DATA AND PROCESS
#----------------------------------------------------------------------------------------------------------
def processData(xc, ip, sbj, plist, frms, txLUT, axLUT, Cnt, xnat_upload=False):
    """download then process the LM/norm data and store"""

    # ip: index of previously processed subject list (if exists)
    # sbj: subject attributes
    # opth: output path
    # plist: list of processed subjects (uses ip index)

    sbjix = sbj['ID']
    sbjid = sbj['ID'][9:]
    sbjlb = sbj['label']
    idate = sbj['insert_date']

    #core path
    core_path = os.path.join(xc['opth'], sbjid+'_'+sbjlb)
    # norm path
    npth = os.path.join(core_path, 'norm')
    # LM path
    lmpth = os.path.join(core_path, 'LM')
    # processing output path
    outpth = os.path.join(core_path, 'output')
    # destination output files
    qcfiles = os.path.join(xc['qcpth'], sbjid +'_'+ sbjlb)

    # output file names and their xnat content tags
    qccharts = [['headcurve.png','mass_centre.png','mass_centre_zoom.png'],['CURVE','COM','COMZ']]
    qcvideos = [['pView_dyn.mp4','pViews_6.mp4'],['PVD','PVS']]



    # get the experiment ID
    try:
        eid = get_xnatList(xc['usrpwd'], xc['sbjs']+'/' +sbjix+ '/experiments?xsiType=xnat:petmrSessionData&format=json&columns=ID')
    except ValueError as ve:
        print '-------------------'
        print 'e> Value Error:', ve
        print '   for subject:', sbjix
        print '-------------------'
    # if no experiments, just skip the rest
    if not eid:
        print 'w> no data for:', sbjid, sbjlb
        if ip>=0: del plist[ip]
        plist.append([sbjid, sbjlb, idate, 'n', time_stamp(), 'n', time_stamp()])

        # return empty stuff
        return []

    else:
        create_dir(npth)
        create_dir(lmpth)
        create_dir(outpth)

        # get the list of norm files
        nrmfiles = get_xnatList(xc['usrpwd'], xc['sbjs']+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/Norm/files')
        # download the norm files:
        for i in range(len(nrmfiles)):
            status = get_xnatFile( xc['usrpwd'], xc['url']+nrmfiles[i]['URI'], os.path.join(npth, nrmfiles[i]['Name']) )
            if status<0:
                if ip>=0: del plist[ip]
                print 'w> no NORM data:', sbjid, sbjlb
                plist.append([sbjid, sbjlb, idate, 'n', time_stamp(), 'n', time_stamp()])
                return []

        # get the list of LM files
        lmfiles = get_xnatList(xc['usrpwd'], xc['sbjs']+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/LM/files')
        # download the LM files:
        for i in range(len(lmfiles)):
            # check if the file is already downloaded:
            if  os.path.isfile ( os.path.join(lmpth, lmfiles[i]['Name']) ) and \
                str( os.path.getsize( os.path.join(lmpth, lmfiles[i]['Name']) ) )==lmfiles[i]['Size']:
                    print 'i> file of the same size,',lmfiles[i]['Name'], 'already exists: skipping download.'
            else:
                status = get_xnatFile( xc['usrpwd'], xc['url']+lmfiles[i]['URI'], os.path.join(lmpth, lmfiles[i]['Name']) )
                if status<0:
                    if ip>=0: del plist[ip]
                    print 'w> no LM data:', sbjid, sbjlb
                    plist.append([sbjid, sbjlb, idate, 'n', time_stamp(), 'n', time_stamp()])
                    return []

        #------------------------------------------------------
        if ip>=0: del plist[ip]

        # explore the input
        folderin = os.path.dirname(lmpth)
        datain = nipet.mmraux.explore_input(folderin, Cnt)
        # check if all data is present
        data_required = [['lm_dcm', 'lm_bf', 'nrm_dcm', 'nrm_bf'],
                        ['lm_ima', 'nrm_ima']]
        dcm_chck = [i in datain for i in data_required[0]]
        ima_chck = [i in datain for i in data_required[1]]
        if all(dcm_chck) or all(ima_chck):
            print 'i> all data present.'
        else:
            print 'e> data missing for', sbjid, sbjlb
            plist.append([sbjid, sbjlb, idate, 'n', time_stamp(), 'n', time_stamp()])
            return []
        #------------------------------------------------------
        

        # process the LM data:
        for i in range(len(lmfiles)):
            if os.path.splitext(lmfiles[i]['Name'])[1]=='.bf':
                # =================================================================================processing---------
                #-get basic time info of the LM data:
                nele, ttags, addrs = nipet.lm.mmr_lmproc.lminfo(os.path.join(lmpth, lmfiles[i]['Name']))
                nitag = (ttags[1]-ttags[0]+999)/1000
                print 'i> duration by integrating time tags [s]:', nitag

                #time difference between acquisition and norm QC
                nipet.mmraux.time_diff_norm_acq(datain)
                #histogram the LM data
                hst = nipet.lm.mmrhist.hist(datain, txLUT, axLUT, Cnt, frms=frms)
                #get video views of the projection data
                pviews.video_dyn11(hst, frms, outpth, axLUT, Cnt)
                pviews.video_frm(hst, outpth, Cnt)
                #-plot the head-curve and centre of mass
                plt.close('all')
                pltQC(hst, outpth, Cnt)

                # XNAT UPLOAD
                if xnat_upload:
                    # store the QC attributes to xnat
                    xnatAsses = xc['sbjs']+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/assessors/LMQC_' +sbjid+ '_' +sbjlb

                    try:
                        put_xnat(xc['usrpwd'], xnatAsses+'?xsiType=avid:avidLMQcManualAssessorData')
                        put_xnat(xc['usrpwd'], xnatAsses+'?avid:avidLMQcManualAssessorData/rater=Pawel')
                        put_xnat(xc['usrpwd'], xnatAsses+'?avid:avidLMQcManualAssessorData/startTime='+str(ttags[0]/1000.))
                        put_xnat(xc['usrpwd'], xnatAsses+'?avid:avidLMQcManualAssessorData/endTime='+str(ttags[1]/1000.))
                        put_xnat(xc['usrpwd'], xnatAsses+'?avid:avidLMQcManualAssessorData/duration='+str((ttags[1]-ttags[0])/1000.) )
                    except ValueError as ve:
                        print ' '
                        print '=============================================================='
                        print 'e> value error:', ve
                        print '=============================================================='
                        print ' '
                    else:
                        print '--------'
                        print 'i> QC attributes uploaded to XNAT.'
                        print '--------'

                    #sent the qc files to desired destination (qcpth + xnat)
                    xnatChart = xc['sbjs']+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/CHARTS'
                    put_xnat(xc['usrpwd'], xnatChart+'?xsi:type=xnat:resourceCatalog&format=PNG')
                    xnatVideo = xc['sbjs']+'/' +sbjix+ '/experiments/' + eid[0]['ID'] + '/resources/VIDEOS'
                    put_xnat(xc['usrpwd'], xnatVideo+'?xsi:type=xnat:resourceCatalog&format=MP4')

                create_dir(qcfiles)

                for fn in os.listdir(outpth):
                    #------------------------------------------------
                    #copy the media files to dropobox or xnat
                    if fn.endswith(".png") or fn.endswith(".mp4"):
                        try:
                            shutil.copy( os.path.join(outpth,fn), os.path.join(qcfiles,fn) )
                        except IOError as e:
                            print ' '
                            print '=============================================================='
                            print 'IO error:', e
                            print '=============================================================='
                            print ' '
                        except shutil.Error as e:
                            print ' '
                            print '=============================================================='
                            print 'shutil error:', e
                            print '=============================================================='
                            print ' '
                        else:
                            print '--------'
                            print 'i> file:', os.path.join(outpth,fn), 'copied to:', os.path.join(qcfiles,fn)
                            print '--------'
                    #------------------------------------------------

                    if xnat_upload:
                        if fn==qccharts[0][0]:
                            put_xnatFile(xc['usrpwd'], xnatChart+'/files?content='+qccharts[1][0], os.path.join(outpth, qccharts[0][0]) )
                        elif fn==qccharts[0][1]:
                            put_xnatFile(xc['usrpwd'], xnatChart+'/files?content='+qccharts[1][1], os.path.join(outpth, qccharts[0][1]) )
                        elif fn==qccharts[0][2]:
                            put_xnatFile(xc['usrpwd'], xnatChart+'/files?content='+qccharts[1][2], os.path.join(outpth, qccharts[0][2]) )
                        elif fn==qcvideos[0][0]:
                            put_xnatFile(xc['usrpwd'], xnatVideo+'/files?content='+qcvideos[1][0], os.path.join(outpth, qcvideos[0][0]) )
                        elif fn==qcvideos[0][1]:
                            put_xnatFile(xc['usrpwd'], xnatVideo+'/files?content='+qcvideos[1][1], os.path.join(outpth, qcvideos[0][1]) )

                #remove the downloaded LM file
                if xc['rmvlm']:   os.remove(os.path.join(lmpth, lmfiles[i]['Name']))
                # =================================================================================--------------------

                print ' '
                print 'i> finished processing LM for:', sbjid, sbjlb
                if xnat_upload:
                    plist.append([sbjid, sbjlb, idate, 'y', time_stamp(), 'n', time_stamp()])
                else:
                    plist.append([sbjid, sbjlb, idate, 'n', time_stamp(), 'n', time_stamp()])
                return hst

        
#----------------------------------------------------------------------------------------------------------

#==========================================================================================================
#==========================================================================================================
