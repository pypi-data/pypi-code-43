# -*- coding: utf-8 -*-
#
#  Tumgreyspf
#  Copyright © 2004-2005, Sean Reifschneider, tummy.com, ltd.
#
#  pypolicyd-spf changes
#  Copyright © 2007-16 Scott Kitterman <scott@kitterman.com>
'''
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import syslog
import os
import sys
import re
import stat
import socket


#  default values
defaultConfigData = {
        'debugLevel' : 1,
        'HELO_reject' : 'Fail',
        'Mail_From_reject' : 'Fail',
        'PermError_reject' : 'False',
        'TempError_Defer'  : 'False',
        'skip_addresses' : '127.0.0.0/8,::ffff:127.0.0.0/104,::1',
        'TestOnly' : 1,
        'SPF_Enhanced_Status_Codes' : 'Yes',
        'Header_Type' : 'SPF',
        'Hide_Receiver' : 'Yes',
        'Authserv_Id' : 'HOSTNAME',
        'Lookup_Time' : 20,
        'Whitelist_Lookup_Time' : 10,
        'Void_Limit' : 2,
        'Reason_Message' : 'Message {rejectdefer} due to: {spf}. Please see {url}',
        'No_Mail' : False,
        'Mock' : False,
	# For milter front end
        'Socket': 'local:/run/pyspf-milter/pyspf-milter.sock',
        'PidFile': '/run/pyspf-milter/pyspf-milter.pid',
        'UserID': 'pyspf-milter',
        'UMask': 7,
        'InternalHosts': '127.0.0.1',
        'IntHosts': False,
        'MacroListVerify': '',
        }


#################################
class ConfigException(Exception):
    '''Exception raised when there's a configuration file error.'''
    pass


####################################################################
def _processConfigFile(filename = None, config = None, useSyslog = 1,
        useStderr = 0):
    '''Load the specified config file, exit and log errors if it fails,
    otherwise return a config dictionary.'''

    import spf_engine.policydspfsupp
    if config == None: config = spf_engine.policydspfsupp.defaultConfigData
    if filename != None:
        try:
            _readConfigFile(filename, config)
        except Exception as e:
            if useSyslog:
                syslog.syslog(e.args[0])
            if useStderr:
                sys.stderr.write('%s\n' % e.args[0])
            sys.exit(1)
    return(config)


#################
class ExceptHook:
    def __init__(self, useSyslog = 1, useStderr = 0):
        self.useSyslog = useSyslog
        self.useStderr = useStderr

    def __call__(self, etype, evalue, etb):
        import traceback
        import sys
        tb = traceback.format_exception(*(etype, evalue, etb))
        for line in tb:
            if self.useSyslog:
                syslog.syslog(line)
            if self.useStderr:
                sys.stderr.write(line)

####################
def _setExceptHook():
    sys.excepthook = ExceptHook(useSyslog = 1, useStderr = 1)


def _make_authserv_id(as_id):
    """Determine Authserv_Id if needed"""
    if as_id == 'HOSTNAME':
        as_id = socket.gethostname()
    return as_id

###############################################################
commentRx = re.compile(r'^(.*)#.*$')
def _readConfigFile(path, configData = None, configGlobal = {}):
    '''Reads a configuration file from the specified path, merging it
    with the configuration data specified in configData.  Returns a
    dictionary of name/value pairs based on configData and the values
    read from path.'''

    debugLevel = configGlobal.get('debugLevel', 0)
    if debugLevel >= 5: syslog.syslog('readConfigFile: Loading "%s"' % path)
    if configData == None: configData = {}
    nameConversion = {
            'debugLevel' : int,
            'HELO_reject' : str,
            'Mail_From_reject' : str,
            'PermError_reject' : str,
            'TempError_Defer' : str,
            'Mail_From_pass_restriction' : str,
            'HELO_pass_restriction' : str,
            'Prospective' : str,
            'Whitelist' : str,
            'skip_addresses': str,
            'HELO_Whitelist': str,
            'Domain_Whitelist' : str,
            'Domain_Whitelist_PTR': str,
            'No_Mail': str,
            'Reject_Not_Pass_Domains' : str,
            'Per_User' : str,
            'TestOnly' : int,
            'defaultSeedOnly' : int,
            'SPF_Enhanced_Status_Codes' : str,
            'Header_Type' : str,
            'Hide_Receiver' : str,
            'Authserv_Id' : str,
            'Lookup_Time' : int,
            'Whitelist_Lookup_Time': int,
            'Void_Limit'  : int,
            'Reason_Message' : str,
            'Mock' : bool,
            # For milter front end
            'Socket': str,
            'PidFile': str,
            'UserID': str,
            'UMask': 'int',
            'InternalHosts': str,
            'IntHosts': 'bool',
            'MacroListVerify': str,
            }


    #  check to see if it's a file
    try:
        mode = os.stat(path)[0]
    except OSError as e:
        if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR,'ERROR stating "%s": %s' % ( path, e.strerror ))
        return(configData)
    if not stat.S_ISREG(mode):
        if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR,'ERROR: is not a file: "%s", mode=%s' % ( path, oct(mode) ))
        return(configData)

    #  load file
    fp = open(path, 'r')
    while 1:
        line = fp.readline()
        if not line: break

        #  parse line
        line = (line.split('#', 1)[0]).strip()
        if debugLevel >= 3: syslog.syslog(str(line))
        if not line: continue
        data = [q.strip() for q in line.split('=')]
        if len(data) != 2:
            if len(data) == 1:
                if debugLevel >= 1:
                    syslog.syslog('Configuration item "%s" not defined in file "%s"'
                        % ( line, path ))
            else:
                syslog.syslog('ERROR parsing line "%s" from file "%s"'
                    % ( line, path ))
            continue
        name, value = data

        #  check validity of name
        conversion = nameConversion.get(name)
        if conversion == None:
            if debugLevel >= 0: syslog.syslog('ERROR: Unknown name "%s" in file "%s"' % ( name, path ))
            continue

        if debugLevel >= 5: syslog.syslog('readConfigFile: Found entry "%s=%s"'
                % ( name, value ))
        configData[name] = conversion(value)
    fp.close()
    try:
        if debugLevel >= 5: syslog.syslog('Authserv_Id before: {0}'.format(configData['Authserv_Id']))
        configData['Authserv_Id'] = _make_authserv_id(configData['Authserv_Id'])
        if debugLevel >= 5: syslog.syslog('Authserv_Id after: {0}'.format(configData['Authserv_Id']))
    except:
        pass
    
    return(configData)

