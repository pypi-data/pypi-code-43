#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Check SPF results and provide recommended action back to Postfix.
#
#  Tumgreyspf source
#  Copyright © 2004-2005, Sean Reifschneider, tummy.com, ltd.
#  <jafo@tummy.com>
#
#  pypolicyd-spf
#  Copyright © 2007-16, Scott Kitterman <scott@kitterman.com>
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

def main():
    __version__ = "2.9.1"

    import syslog
    import os
    import socket
    import sys
    import re

    import spf_engine
    import spf_engine.policydspfsupp as policydspfsupp
    # import policydspfuser - Only imported if per-user settings are activated for
    # efficiency.

    if int(sys.version_info.major) < 3 or (int(sys.version_info.major) == 3 and \
            int(sys.version_info.minor) < 3):
        raise ImportError("Python 3.3 or later is required")

    syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID, syslog.LOG_MAIL)
    policydspfsupp._setExceptHook()

    #  load config file  {{{1
    #  Default location:
    configFile = '/etc/python-policyd-spf/policyd-spf.conf'
    if len(sys.argv) > 1:
        if sys.argv[1] in ( '-?', '--help', '-h' ):
            print('usage: policyd-spf [<configfilename>]')
            sys.exit(1)
        configFile = sys.argv[1]

    configGlobal = policydspfsupp._processConfigFile(filename = configFile)

    #  loop reading data  {{{1
    debugLevel = configGlobal.get('debugLevel', 1)
    if debugLevel >= 3: syslog.syslog('Starting')
    instance_dict = {'0':'init',}
    instance_dict.clear()
    data = {}
    lineRx = re.compile(r'^\s*([^=\s]+)\s*=(.*)$')
    while 1:
        # Python readline assumes ascii here, but sometimes it's not
        lineraw = sys.stdin.buffer.readline()
        line = lineraw.decode('UTF-8',errors='replace')
        if not line: break
        line = line.rstrip()
        if debugLevel >= 4: syslog.syslog('Read line: "%s"' % line)

        #  end of entry  {{{2
        if not line:
            peruser = False
            peruserconfigData = []
            rejectAction = ''
            deferAction = ''
            if debugLevel >= 4: syslog.syslog('Found the end of entry')
            configData = dict(list(configGlobal.items()))
            if configData.get('defaultSeedOnly') is not None:
                syslog.syslog(syslog.LOG_ERR,'WARNING: Deprecated Config Option defaultSeedOnly in use in: {0}'.format(configFile ))

            if configData.get('Mock'):
                sys.stdout.write('action=dunno mock header field that should be ignored\n\n')
                continue
            if not data.get('recipient'):
                data['recipient'] = 'none'
            if configData.get('Per_User'):
                import spf_engine.policydspfuser
                peruserconfigData, peruser = spf_engine.policydspfuser._datacheck(configData, data.get('recipient'))
                if debugLevel >= 2 and peruser: syslog.syslog('Per user configuration data in use for: %s' \
                    % str(data.get('recipient')))
            if configData.get('Hide_Receiver') != 'No':
                data['recipient'] = '<UNKNOWN>'
            if debugLevel >= 3: syslog.syslog('Config: %s' % str(configData))
            #  run the checkers  {{{3
            checkerValue = None
            checkerReason = None
            checkerValue, checkerReason, instance_dict, iserror = \
                    spf_engine._spfcheck(data, instance_dict, configData,
                    peruser, peruserconfigData)

            if not peruser:
                TestOnly = configData.get('defaultSeedOnly')
                TestOnly = configData.get('TestOnly')
            else:
                TestOnly = peruserconfigData.get('defaultSeedOnly')
                TestOnly = peruserconfigData.get('TestOnly')
            if TestOnly == 0 and checkerValue != 'prepend':
                checkerValue = None
                checkerReason = None

            if configData.get('SPF_Enhanced_Status_Codes') == 'No':
                rejectAction = '550'
                deferAction = 'defer_if_permit'
            else:
                if iserror:
                    rejectAction = '550 5.7.24'
                    deferAction = 'defer_if_permit 4.7.24'
                else:
                    rejectAction = '550 5.7.23'
                    deferAction = 'defer_if_permit 4.7.24'

            #  handle results  {{{3
            if debugLevel >= 3: syslog.syslog('Action: {0}: Text: {1} Reject action: {2}'.format(checkerValue, checkerReason, rejectAction))
            if checkerValue == 'reject':
                if debugLevel >= 1: syslog.syslog('{0} {1}'.format(rejectAction, checkerReason))
                sys.stdout.write('action={0} {1}\n\n'.format(rejectAction, checkerReason))

            elif checkerValue == 'prepend':
                if configData.get('Prospective'):
                    sys.stdout.write('action=dunno\n\n')
                else:
                    if configData.get('Header_Type') != 'None':
                        if debugLevel >= 1: syslog.syslog('prepend {0}'.format(checkerReason))
                        try:
                            sys.stdout.write('action=prepend %s\n\n' % checkerReason)
                        except UnicodeEncodeError:
                            sys.stdout.write('action=prepend %s\n\n' % str(checkerReason.encode("UTF-8"))[1:].strip("'"))
                    else:
                        if debugLevel >= 1: syslog.syslog('Header field not prepended: {0}'.format(checkerReason))
                        sys.stdout.write('action=dunno\n\n')

            elif checkerValue == 'defer':
                if debugLevel >= 1: syslog.syslog('{0} {1}'.format(deferAction, checkerReason))
                try:
                    sys.stdout.write('action={0} {1}\n\n'.format(deferAction, checkerReason))
                except UnicodeEncodeError:
                    sys.stdout.write('action={0} {1}\n\n'.format(deferAction, str(checkerReason.encode("UTF-8"))[1:].strip("'")))

            elif checkerValue == 'warn':
                try:
                   sys.stdout.write('action=warn %s\n\n' % checkerReason)
                except UnicodeEncodeError:
                    sys.stdout.write('action=warn %s\n\n' % str(checkerReason.encode("UTF-8"))[1:].strip("'"))

            elif checkerValue == 'result_only':
                if debugLevel >= 1: syslog.syslog('result_only {0}'.format(checkerReason))
                try:
                    sys.stdout.write('action=%s\n\n' % checkerReason)
                except UnicodeEncodeError:
                    sys.stdout.write('action=%s\n\n' % str(checkerReason.encode("UTF-8"))[1:].strip("'"))

            else:
                sys.stdout.write('action=dunno\n\n')

            #  end of record  {{{3
            sys.stdout.flush()
            data = {}
            continue

        #  parse line  {{{2
        m = lineRx.match(line)
        if not m: 
            if debugLevel >= 0: syslog.syslog('ERROR: Could not match line "%s"' % line)
            continue

        #  save the string  {{{2
        key = m.group(1)
        value = m.group(2)
        if key not in [ 'protocol_state', 'protocol_name', 'queue_id' ]:
            value = value.lower()
        data[key] = value

    if debugLevel >= 3: syslog.syslog('Normal exit')
