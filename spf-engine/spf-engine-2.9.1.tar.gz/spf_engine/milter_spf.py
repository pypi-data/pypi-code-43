#! /usr/bin/python3
# Derived from dkim-milter.py code:
# Author: Stuart D. Gathman <stuart@bmsi.com>
# Copyright 2007 Business Management Systems, Inc.
# This code is under GPL.  See COPYING for details.
# and:
# dkimpy-milter: A DKIM signing/verification Milter application
# Author: Scott Kitterman <scott@kitterman.com>
# Copyright 2018 Scott Kitterman
# spf-milter.py:
# Author: Scott Kitterman <scott@kitterman.com>
# Copyright 2019 Scott Kitterman
"""    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

import sys
import syslog
import Milter
import authres
import os
import tempfile
import re
from Milter.utils import parse_addr, parseaddr
import spf_engine
import spf_engine.policydspfsupp as config
from spf_engine.util import drop_privileges
from spf_engine.policydspfsupp import _setExceptHook
from spf_engine.util import write_pid
from spf_engine.util import own_socketfile
from spf_engine.util import fold

__version__ = "2.9.1"
FWS = re.compile(r'\r?\n[ \t]+')


class spfMilter(Milter.Base):
    "Milter to check SPF.  Each connection gets its own instance."

    def __init__(self):
        self.mailfrom = None
        self.id = Milter.uniqueID()
        self.instance_dict = {'0':'init',}
        self.instance_dict.clear()
        self.data = {}

    @Milter.noreply
    def connect(self, hostname, unused, hostaddr):
        self.internal_connection = False
        self.external_connection = False
        self.hello_name = None
        # sometimes people put extra space in sendmail config, so we strip
        self.receiver = self.getsymval('j').strip()
        try:
            self.Authserv_Id = milterconfig['Authserv_Id']
        except:
            self.Authserv_Id = self.receiver
        if hostaddr and len(hostaddr) > 0:
            ipaddr = hostaddr[0]
            if milterconfig['IntHosts']:
                if milterconfig['IntHosts'].match(ipaddr):
                    self.internal_connection = True
        else:
            ipaddr = ''
        self.connectip = ipaddr
        self.data['client_address'] = ipaddr
        self.data['helo_name'] = hostname
        self.data['recipient'] = '<UNKNOWN>'
        if milterconfig.get('MacroList') and not self.internal_connection:
            macrolist = milterconfig.get('MacroList')
            for macro in macrolist:
                macroname = macro.split('|')[0]
                macroname = '{' + macroname + '}'
                macroresult = self.getsymval(macroname)
                if ((len(macro.split('|')) == 1 and macroresult) or macroresult
                        in macro.split('|')[1:]):
                    self.external_connection = True
        if self.internal_connection:
            connecttype = 'INTERNAL'
        else:
            connecttype = 'EXTERNAL'
        if milterconfig.get('debugLevel') >= 1:
            syslog.syslog("connect from {0} at {1} {2}"
                          .format(hostname, hostaddr, connecttype))
        return Milter.CONTINUE

    # multiple messages can be received on a single connection
    # envfrom (MAIL FROM in the SMTP protocol) seems to mark the start
    # of each message.
    def envfrom(self, f, *str):
        if milterconfig.get('debugLevel') >= 2:
            syslog.syslog("mail from: {0} {1}".format(f, str))
        self.mailfrom = f
        t = parse_addr(f)
        if len(t) == 2:
            t[1] = t[1].lower()
            domain = t[1]
        else:
            domain = 'localhost.localdomain'
        self.canon_from = '@'.join(t)
        self.arheaders = []
        self.arresults = []
        self.data['sender'] = self.canon_from 
        if (not self.internal_connection or self.external_connection) and self.connectip:
            return self.check_spf()
        return Milter.CONTINUE

    @Milter.noreply
    def header(self, name, val):
        lname = name.lower()
        if lname == 'authentication-results':
            self.arheaders.append(val)
        return Milter.CONTINUE

    @Milter.noreply
    def eoh(self):
        self.bodysize = 0
        return Milter.CONTINUE

    @Milter.noreply
    def body(self, chunk):        # copy body to temp file
        return Milter.CONTINUE

    def eom(self):
        if self.arresults:
            h = results=self.arresults[0]
            h = fold(str(h))
            if milterconfig.get('debugLevel') >= 2:
                syslog.syslog(str(h))
            name, val = str(h).split(': ', 1)
            self.addheader(name, val, 0)
        return Milter.CONTINUE


    def check_spf(self):
        peruser = False
        perusermilterconfig = []
        rejectAction = ''
        deferAction = ''
        if not self.data.get('recipient'):
            self.data['recipient'] = 'none'
        if milterconfig.get('debugLevel') >= 3: syslog.syslog('Config: %s' % str(milterconfig))
        #  run the checkers  {{{3
        checkerValue = None
        checkerReason = None
        checkerValue, checkerReason, self.instance_dict, iserror = \
                spf_engine._spfcheck(self.data, self.instance_dict, milterconfig,
                peruser, perusermilterconfig)

        TestOnly = milterconfig.get('TestOnly')
        if TestOnly == 0 and checkerValue != 'prepend':
            checkerValue = None
            checkerReason = None

        if milterconfig.get('SPF_Enhanced_Status_Codes') == 'No':
            rejectAction = ''
            deferAction = 'defer_if_permit'
        else:
            if iserror:
                rejectAction = '5.7.24'
                deferAction = '4.7.24'
            else:
                rejectAction = '5.7.23'
                deferAction = '4.7.24'

        #  handle results  {{{3
        if milterconfig.get('Header_Type') != 'None' and checkerValue != 'reject':
            if milterconfig.get('debugLevel') >= 3: syslog.syslog('{0} {1}'.format('Header text', checkerReason))
            self.arresults.append(checkerReason)
        if milterconfig.get('debugLevel') >= 3: syslog.syslog('Action: {0}: Text: {1} Reject action: {2}'.format(checkerValue, checkerReason, rejectAction))

        if checkerValue == 'reject':
            if milterconfig.get('debugLevel') >= 1: syslog.syslog('{0} {1}'.format(rejectAction, checkerReason))
            self.setreply(str(550), rejectAction, checkerReason)
            return Milter.REJECT

        elif checkerValue == 'prepend':
            if milterconfig.get('Prospective'):
                return Milter.CONTINUE
            else:
                if milterconfig.get('Header_Type') != 'None':
                    if milterconfig.get('debugLevel') >= 1: syslog.syslog('prepend {0}'.format(checkerReason))
                else:
                    if milterconfig.get('debugLevel') >= 1: syslog.syslog('Header field not prepended: {0}'.format(checkerReason))
                return Milter.CONTINUE

        elif checkerValue == 'defer':
            if milterconfig.get('debugLevel') >= 1: syslog.syslog('{0} {1}'.format(deferAction, checkerReason))
            self.setreply(str(450), deferAction, checkerReason)
            return Milter.TEMPFAIL

        elif checkerValue == 'result_only':
            return Milter.SKIP
        else:
            return Milter.CONTINUE


def main():
    # Ugh, but there's no easy way around this.
    global milterconfig
    configFile = '/usr/local/etc/python-policyd-spf/policyd-spf.conf'
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-?', '--help', '-h'):
            print('usage: pyspf-milter [<configfilename>]')
            sys.exit(1)
        configFile = sys.argv[1]
    milterconfig = config._processConfigFile(filename=configFile)
    # Unlike policyd, milter interface only suppports authres
    if milterconfig.get('Header_Type') != 'None':
        milterconfig['Header_Type'] = 'AR'
    # Per user configurations not supported on milter interface
    milterconfig['Per_User'] = False
    facility = eval("syslog.LOG_{0}".format('MAIL'))
    syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID, facility)
    _setExceptHook()
    pid = write_pid(milterconfig)
    Milter.factory = spfMilter
    Milter.set_flags(Milter.CHGHDRS + Milter.ADDHDRS)
    miltername = 'pyspf-filter'
    socketname = milterconfig.get('Socket')
    syslog.syslog('pyspf-milter started:{0} user:{1}'
                  .format(pid, milterconfig.get('UserID')))
    sys.stdout.flush()
    Milter.runmilter(miltername, socketname, 240)
    own_socketfile(milterconfig)
    drop_privileges(milterconfig)

if __name__ == "__main__":
    main()
