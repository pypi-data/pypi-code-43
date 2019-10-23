#!/usr/bin/env python
###############################################################################
# Copyright (c) 2018, Urban Magnetometry Group.
# Produced at the University of California at Berkeley.
# Written by V. Dumont (vincentdumont11@gmail.com).
# All rights reserved.
# This file is part of NURI.
# For details, see citymag.gitlab.io/nuri
# For details about use and distribution, please read NURI/LICENSE.
###############################################################################
import nuri,argparse,numpy
import matplotlib.pyplot as plt
from datetime import datetime

#######################################################################
# Extract input arguments, the available operations are the following:
# ---------------------------------------------------------------------
# activity - Get the activity from the Biomed stations
# download - Download Biomed sensor data from the Google Drive
# convert  - Prepare ensemble of data and convert them into new format
# wavelet  - Do wavelet plot of data
#######################################################################

parser = argparse.ArgumentParser(prog='nuri',description='Sensor Network Time-frequency analysis tool.')
parser.add_argument("operation", help='Operation to be run',choices=['activity','download','extract','convert','wavelet','psd','availability']) 
parser.add_argument("--date",metavar='',help='Starting date (format: YYYY-MM-HH)')
parser.add_argument("--delay",metavar='',type=int, help='Timestamp delay in seconds')
parser.add_argument("--dest",metavar='',help='Custom destination repository')
parser.add_argument("--gps",action='store_true',help='Where we consider GPS timing')
parser.add_argument("--length", metavar='',type=float, help='Time length (in seconds)')
parser.add_argument("--median",action='store_true',help='Divide time series by median value')
parser.add_argument("--mmin", metavar='',type=float,help='Minimum magnetic field')
parser.add_argument("--mmax", metavar='',type=float,help='Maximum magnetic field')
parser.add_argument("--offset", metavar='',default=0.,help='Timing offset')
parser.add_argument("--output", metavar='',help='Output file name')
parser.add_argument("--overlap",metavar='',type=float,help='Period to overlap data (in seconds)')
parser.add_argument("--path",metavar='',help='Path to data file or repository')
parser.add_argument("--period", metavar='',nargs=2, help='Time period (format: YYYY-MM-HH)')
parser.add_argument("--rate", metavar='',type=float,help='Targeted sampling rate (default: %(default)s)',)
parser.add_argument("--sensor", metavar='',help='Sensor type')
parser.add_argument("--station", metavar='',type=int, help='Station index number')
parser.add_argument("--trange",metavar='',nargs=2,type=int, help='Time range')
parser.add_argument("--tunit",metavar='',default='mins',help='Time frame unit',choices=['secs','mins','hrs'])
parser.add_argument("--ufactor", metavar='',default=1.,type=float,help='Factor from local to uT')
args = parser.parse_args()

####################################################################
# Check for non-analysis operations, otherwise load requested data
####################################################################

if args.operation=='activity':
    nuri.get_activity(args.date.split('-'))
elif args.operation=='download':
    nuri.download(args.period,args.date,args.length,args.station)
elif args.operation=='availability':
    nuri.plot_availability(args.path,args.period,args.sensor,args.station)
elif args.path==None and args.period==None:
    print('Please either select a file or a time period. Abort.')
    quit()
    
################################
# Convert datetime to timestamp
################################

if args.period==None:
    tmin,tmax = None,None
elif nuri.is_float(args.period[0])==False:
    tmin,tmax = nuri.str2timestamp(*args.period)
else:
    tmin,tmax = float(args.period[0]),float(args.period[1])
    
###############################
# Magnetic field data handling
###############################

if args.operation=='convert':
    tmin = datetime.utcfromtimestamp(tmin)
    tmax = datetime.utcfromtimestamp(tmax)
    offset = data_offset(tmin,tmax,args.station) if args.sensor=='biomed' else 0
    dataset = nuri.data_lookup(args.path,tmin,tmax,args.station,offset)
    nuri.biomed_converter(dataset,tmin,tmax,args.station,args.rate,args.dest)
else:
    data = nuri.get_data(tmin,tmax,args.path,args.sensor,station,args.rate)
    
###########################
# Plot wavelet spectrogram
###########################

if args.operation=='wavelet':
    print('Plot wavelet spectrogram')
    name = 'wavelet_%i-%i'%(tmin,tmax) if args.output==None else args.output
    nuri.plot_spectrogram(data,fname=name,tmin=tmin,tmax=tmax,mmin=args.mmin,mmax=args.mmax,median=args.median,tunit=args.tunit)

#################################
# Plot daily wavelet spectrogram
#################################

if args.operation=='psd':
    print('Plot daily wavelet spectrograms')
    name = 'psd_%i-%i'%(tmin,tmax) if args.output==None else args.output
    nuri.plot_psd(data,fname=name,tmin=tmin,tmax=tmax)

###########################
# Plot average time series
###########################

#if args.operaton=='average':
    
