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
   This code is dual licensed:

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   and

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

__version__ = "2.9.0"

import syslog
import os
import sys
import re
import socket
import ipaddress # needs python3.3, python2 backport doesn't work
# import random - Only needed for testing, so imported in line if needed.

import spf
import authres

import spf_engine.policydspfsupp
# import policydspfuser - Only imported if per-user settings are activated for
# efficiency.

if int(sys.version_info.major) < 3 or (int(sys.version_info.major) == 3 and \
    int(sys.version_info.minor) < 3):
    raise ImportError("Python 3.3 or later is required")
maj, minor, micro = spf.__version__.split(':')[0].split('.')
if int(micro) < 9:
    raise ImportError("At least pyspf 2.0.9 is required.")

syslog.openlog(os.path.basename(sys.argv[0]), syslog.LOG_PID, syslog.LOG_MAIL)
spf_engine.policydspfsupp._setExceptHook()

#############################################
def _cidrmatch(ip, netwrk):
    """Match connect IP against a CIDR network of other IP addresses."""

    address = ipaddress.ip_address(ip)
    try:
        network = ipaddress.IPv4Network(netwrk)
    except ipaddress.AddressValueError:
        network = ipaddress.IPv6Network(netwrk)
    return network.__contains__(address)

def _ipmatch(ip1, ip2):
    """Non-string matching of two IP addresses"""
    addr1 = ipaddress.ip_address(ip1)
    addr2 = ipaddress.ip_address(ip2)
    if addr1 == addr2:
        return True
    else:
        return False

def _get_rdns_lookup(ip):
    address = ipaddress.ip_address(ip)
    if isinstance(address, ipaddress.IPv4Address):
        components = address.exploded.split('.')
        return '.'.join(components[::-1]) + '.in-addr.arpa'    
    else:
        components = address.exploded.split(':')
        return '.'.join('.'.join(list(quad)) for quad in components)[::-1] + '.ip6.arpa'
#############################################
def _get_resultcodes(data, configData, scope):
    # Parse config options for SPF results to correct Posftix actions
    debugLevel = configData.get('debugLevel', 1)
    actions = {'defer':[], 'reject':[], 'prepend':[]}
    local = {'local_helo': False, 'local_mfrom': False}
    unused_results = ['Pass', 'None', 'Neutral', 'Softfail', 'Fail', 'Temperror', 'Permerror'] 
    helo_policy = ''
    mfrom_policy = ''
    reject_domain_list = []
    sender = data.get('sender')
    helo = data.get('helo_name')
    if debugLevel >= 5: syslog.syslog('_get_resultcodes: scope: {0}, Reject_Not_Pass_Domains: {1}, helo_policy: {2}, mfrom_policy: {3}'.format(scope, configData.get('Reject_Not_Pass_Domains'), configData.get('HELO_reject'),configData.get('Mail_From_reject')))
    if configData.get('Reject_Not_Pass_Domains'):
        reject_domains = (str(configData.get('Reject_Not_Pass_Domains')))
        reject_domain_list = reject_domains.split(',')
        if "@" in sender:
            sender_domain = sender.split('@', 1)[1]
        else:
            sender_domain = ''

    if scope == 'helo':
        helo_policy = configData.get('HELO_reject')
        if spf.domainmatch(reject_domain_list, helo):
            helo_policy = 'SPF_Not_Pass'
            local['local_helo'] = True
        if helo_policy == 'SPF_Not_Pass':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
                unused_results.remove('Softfail')
                actions['reject'].append('Softfail')
                unused_results.remove('Neutral')
                actions['reject'].append('Neutral')
            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: HELO_reject')
        elif helo_policy == 'Softfail':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
                unused_results.remove('Softfail')
                actions['reject'].append('Softfail')

            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: HELO_reject')
        elif helo_policy == 'Fail' or helo_policy == 'Null':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: HELO_reject')
        if debugLevel >= 5: syslog.syslog('Scope helo unused results: {0}'.format(unused_results))
    if scope == 'mfrom':
        mfrom_policy = configData.get('Mail_From_reject')
        if "@" in sender:
            sender_domain = sender.split('@', 1)[1]
        else:
            sender_domain = ''
        if spf.domainmatch(reject_domain_list, sender_domain):
            mfrom_policy = 'SPF_Not_Pass'
            local['local_mfrom'] = True
        if mfrom_policy == 'SPF_Not_Pass':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
                unused_results.remove('Softfail')
                actions['reject'].append('Softfail')
                unused_results.remove('Neutral')
                actions['reject'].append('Neutral')
            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: Mail_From_reject')
        elif mfrom_policy == 'Softfail':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
                unused_results.remove('Softfail')
                actions['reject'].append('Softfail')

            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: Mail_From_reject')
        elif mfrom_policy == 'Fail':
            try:
                unused_results.remove('Fail')
                actions['reject'].append('Fail')
            except:
                if debugLevel >= 2: syslog.syslog('Configuration File parsing error: Mail_From_reject')
        if debugLevel >= 5: syslog.syslog('Scope mfrom unused results: {0}'.format(unused_results))

    if (helo_policy == 'False' and scope == 'helo') or (mfrom_policy == 'False' and scope == 'mfrom'):
        for result in unused_results:
            actions['prepend'].append(result)
        if debugLevel >= 5: syslog.syslog('{0} policy false results: actions: {1} local {2}'.format(scope,actions,local))
        return(actions, local)
    if configData.get('TempError_Defer') == 'True':
        actions['defer'].append('Temperror')
        unused_results.remove('Temperror')
    if configData.get('PermError_reject') == 'True':
        actions['reject'].append('Permerror')
        unused_results.remove('Permerror')
    for result in unused_results:
        actions['prepend'].append(result)
    if debugLevel >= 5: syslog.syslog('{0} policy true results: actions: {1} local {2}'.format(scope,actions,local))
    return(actions, local)
#############################################
def _spfbypass(data, check_type, configData):
    debugLevel = configData.get('debugLevel', 1)
    if configData.get(check_type):
        if configData.get('Prospective'):
            ip = configData.get('Prospective')
        else:
            ip = data.get('client_address')
        bypass_list = (str(configData.get(check_type)))
        bypass_list_list = bypass_list.split(',')
        if check_type == 'skip_addresses' or check_type == 'Whitelist':
            if debugLevel >= 4: syslog.syslog ("{0} enabled.".format(check_type))
            for skip_network in bypass_list_list:
                try:
                    if _cidrmatch(ip, skip_network):
                        if check_type == 'skip_addresses':
                            comment = 'SPF check N/A for local connections - '
                        else:
                            comment = 'SPF skipped for whitelisted relay - '
                        if 'AR' in configData.get('Header_Type'):
                            try:
                                Header = str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                                    results = [authres.NoneAuthenticationResult(comment = \
                                    '{0} client-ip={1}; helo={2}; envelope-from={3}; receiver={4}'.format(comment, data.get('client_address', '<UNKNOWN>'),\
                                        data.get('helo_name', '<UNKNOWN>'), data.get('sender', '<UNKNOWN>'), data.get('recipient', '<UNKNOWN>'))
                                        )]))
                            except TypeError as x:
                                if str(x).startswith('sequence item 2'):
                                    if debugLevel >= 0:  syslog.syslog(syslog.LOG_ERR, 'Authserv_Id not set for authentication results header - invalid configuration.')
                                    raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                        else:
                            Header = ('X-Comment: ' + comment + 'client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                                % ( data.get('client_address', '<UNKNOWN>'),
                                    data.get('helo_name', '<UNKNOWN>'),
                                    data.get('sender', '<UNKNOWN>'),
                                    data.get('recipient', '<UNKNOWN>'),
                                    ))
                        if debugLevel >= 3: syslog.syslog(Header)
                        return (True, Header)
                except ValueError as msg:
                    Message = 'ERROR: {0} in {1} not IP network.  Message: {2}. Aborting whitelist processing.'.format(skip_network, check_type, msg)
                    if debugLevel >= 0: syslog.syslog(Message)
                    return (False, 'None')
            return (False, 'None')
        if check_type == 'Domain_Whitelist':
            if debugLevel >= 4: syslog.syslog ("Domain Whitelist enabled.")
            for domain in bypass_list_list:
                res = spf.check2(ip, domain, domain, querytime=configData.get('Whitelist_Lookup_Time'))
                domain_res = [res[0], res[1]]
                domain_res[0] = domain_res[0].lower()
                domain_res[0] = domain_res[0].capitalize()
                if domain_res[0] == 'Pass':
                    comment = 'SPF skipped for whitelisted relay domain - '
                    if 'AR' in configData.get('Header_Type'):
                        try:
                            Header = str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                                results = [authres.NoneAuthenticationResult(comment = \
                                '{0} client-ip={1}; helo={2}; envelope-from={3}; receiver={4}'.format(comment, data.get('client_address', '<UNKNOWN>'),\
                                    data.get('helo_name', '<UNKNOWN>'), data.get('sender', '<UNKNOWN>'), data.get('recipient', '<UNKNOWN>'))
                                    )]))
                        except TypeError as x:
                            if str(x).startswith('sequence item 2'):
                                if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR, 'Authserv_Id not set for authentication results header - invalid configuration.')
                                raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                    else:
                        Header = ('X-Comment: ' + comment + 'client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                            % ( data.get('client_address', '<UNKNOWN>'),
                                data.get('helo_name', '<UNKNOWN>'),
                                data.get('sender', '<UNKNOWN>'),
                                data.get('recipient', '<UNKNOWN>'),
                                ))
                    if debugLevel >= 3: syslog.syslog(Header)
                    return (True, Header)
            return (False, 'None')
        if check_type == 'Domain_Whitelist_PTR':
            if debugLevel >= 4: syslog.syslog ("PTR Domain Whitelist enabled.")
            try:
                # Try a reverse DNS lookup first and try and match against the domain list that way
                rDNSResults = spf.DNSLookup (_get_rdns_lookup(ip), 'ptr', timeout=configData.get('Whitelist_Lookup_Time'))
                if (len (rDNSResults) > 0):
                    rDNSName = rDNSResults [0][1]
                else:
                    # Reverse lookup didn't find any records, so don't continue with the check
                    rDNSName = None
            except spf.TempError as e:
                # DNS timeout - continue with the base SPF check.
                rDNSName = None
            if (rDNSName is not None):
                for domain in bypass_list_list:
                    if (rDNSName.endswith (domain)):
                        comment = 'SPF skipped for PTR whitelisted relay domain - '
                        if 'AR' in configData.get('Header_Type'):
                            try:
                                Header = str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                                    results = [authres.NoneAuthenticationResult(comment = \
                                    '{0} client-ip={1}; helo={2}; envelope-from={3}; receiver={4}'.format(comment, data.get('client_address', '<UNKNOWN>'),\
                                        data.get('helo_name', '<UNKNOWN>'), data.get('sender', '<UNKNOWN>'), data.get('recipient', '<UNKNOWN>'))
                                        )]))
                            except TypeError as x:
                                if str(x).startswith('sequence item 2'):
                                    if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR, 'Authserv_Id not set for authentication results header - invalid configuration.')
                                    raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                        else:
                            Header = ('X-Comment: ' + comment + 'client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                                % ( data.get('client_address', '<UNKNOWN>'),
                                    data.get('helo_name', '<UNKNOWN>'),
                                    data.get('sender', '<UNKNOWN>'),
                                    data.get('recipient', '<UNKNOWN>'),
                                    ))
                        if debugLevel >= 3: syslog.syslog(Header)
                        return (True, Header)
            return (False, 'None')
        if check_type == 'HELO_Whitelist':
            if debugLevel >= 4: syslog.syslog ("HELO Domain Whitelist enabled.")
            # Collect the IP addresses from the A/AAAA records of all HELO_Whitelist domains
            connectip = ipaddress.ip_address(ip)
            answerlist = []
            for domain in bypass_list_list:
                if domain == data.get('helo_name'):
                    try:
                        if debugLevel >= 5: syslog.syslog ("HELO Domain Whitelist domain match: {0}.".format(domain))
                        if isinstance(connectip,ipaddress.IPv4Address):
                            if debugLevel >= 5: syslog.syslog ("HELO Domain Whitelist domain: {0} is IPv4: {1}.".format(domain,connectip))
                            # DNS A lookup for IPv4 first: If A doesn't match connect IP, then skip
                            DNSAResults = spf.DNSLookup (domain, 'a', timeout=configData.get('Whitelist_Lookup_Time'))
                            if (len (DNSAResults) > 0):
                                for answer in DNSAResults:
                                    answerlist.append(answer[1])
                        if isinstance(connectip,ipaddress.IPv6Address):
                            if debugLevel >= 5: syslog.syslog ("HELO Domain Whitelist domain: {0} is IPv6: {1}.".format(domain,connectip))
                            # DNS AAAA lookup for IPv6
                            DNSAAAAResults = spf.DNSLookup (domain, 'aaaa', timeout=configData.get('Whitelist_Lookup_Time'))
                            if (len (DNSAAAAResults) > 0):
                                for answer in DNSAAAAResults:
                                    answerlist.append(answer[1])
                    except spf.TempError as e:
                        # DNS timeout - continue with the base SPF check.
                        pass
            if (answerlist is not None):
                for ipans in answerlist:
                    if _ipmatch(ipans,ip):
                        comment = 'SPF skipped for whitelisted HELO domain - '
                        if 'AR' in configData.get('Header_Type'):
                            try:
                                Header = str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                                    results = [authres.NoneAuthenticationResult(comment = \
                                    '{0} client-ip={1}; helo={2}; envelope-from={3}; receiver={4}'.format(comment, data.get('client_address', '<UNKNOWN>'),\
                                        data.get('helo_name', '<UNKNOWN>'), data.get('sender', '<UNKNOWN>'), data.get('recipient', '<UNKNOWN>'))
                                        )]))
                            except TypeError as x:
                                if str(x).startswith('sequence item 2'):
                                    syslog.syslog(syslog.LOG_ERR, 'Authserv_Id not set for authentication results header - invalid configuration.')
                                    raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                        else:
                            Header = ('X-Comment: ' + comment + 'client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                                % ( data.get('client_address', '<UNKNOWN>'),
                                    data.get('helo_name', '<UNKNOWN>'),
                                    data.get('sender', '<UNKNOWN>'),
                                    data.get('recipient', '<UNKNOWN>'),
                                    ))
                        if debugLevel >= 3: syslog.syslog(Header)
                        return (True, Header)
            return (False, 'None')
#############################################
def _rejectmessage(result, type, info, ip, recipient, configData):
    if result[3] == 'reject':
        rejectdefer = "rejected"
    elif result[3] == 'defer':
        rejectdefer = "deferred"
    url = ("http://www.openspf.net/Why?s={0};id={1};ip={2};r={3}"
              .format(type, info, ip, recipient))
    msg = configData.get('Reason_Message')
    return msg.format(
            rejectdefer=rejectdefer,
            spf=result[1],
            url=url,
    )

#############################################
def _spfcheck(data, instance_dict, configData, peruser, peruserconfigData):  #{{{1
    debugLevel = configData.get('debugLevel', 1)
    if not peruser:
        Void_Limit = configData.get('Void_Limit')
    else:
        Void_Limit = peruserconfigData.get('Void_Limit')
    spf.MAX_VOID_LOOKUPS = Void_Limit
    if configData.get('Prospective'):
        ip = configData.get('Prospective')
    else:
        ip = data.get('client_address')
    if ip == None:
        if debugLevel >= 2: syslog.syslog('spfcheck: No client address, exiting')
        return(( None, None, instance_dict, None))
    instance = data.get('instance')
    # The following if is only needed for testing.  Postfix 
    # will always provide instance.
    if not instance:
        import random
        instance = str(int(random.random()*100000))
    # This is to prevent multiple headers being prepended
    # for multi-recipient mail.
    if instance in instance_dict:
        found_instance = instance_dict[instance]
    else:
        found_instance = []
    # If this is not the first recipient for the message, we need to know if
    # there is a previous prepend to make sure we don't prepend more than once.
    if found_instance:
        if found_instance[5] != 'prepend':
            last_action = found_instance[3]
        else:
            last_action = found_instance[5]
    else:
        last_action = ""
    #  start query
    spfResult = None
    spfReason = None
    '''Data structure for results is a list of:
        [0] SPF result 
        [1] SPF reason
        [2] Identity (HELO/Mail From)
        [3] Action based on local policy
        [4] Header
        [5] last_action (need to know if we've prepended already)'''
    if debugLevel >= 4: syslog.syslog('Cached data for this instance: %s' % str(found_instance))
    if not found_instance or peruser:
        # Do not check SPF for localhost addresses
        if not peruser:
            skip_check = _spfbypass(data, 'skip_addresses', configData)
        else:
            skip_check = _spfbypass(data, 'skip_addresses', peruserconfigData)
            if debugLevel >= 4: syslog.syslog('skip_addresses check used peruser data')
        if skip_check[0]:
            skip_data = ["N/A", "Skip SPF checks on localhost", "N/A", "prepend", skip_check[1]]
            if last_action != 'prepend':
                skip_data.append('prepend')
                if not found_instance and not peruser:
                    instance_dict[instance] = skip_data
                return (('prepend', skip_check[1], instance_dict, None))
            else:
                return(( 'dunno', 'Header already pre-pended', instance_dict, None))
        # Whitelist designated IP addresses from SPF checks (e.g. secondary MX or 
        # known forwarders.
        if not peruser:
            ip_whitelist = _spfbypass(data, 'Whitelist', configData)
        else:
            ip_whitelist = _spfbypass(data, 'Whitelist', peruserconfigData)
            if debugLevel >= 4: syslog.syslog('Whitelist check used peruser data')
        if ip_whitelist:
            if ip_whitelist[0]:
                skip_data = ["N/A", "Skip SPF checks for whitelisted IP addresses", "N/A", "prepend", skip_check[1]]
                if last_action != 'prepend':
                    skip_data.append('prepend')
                    if not found_instance and not peruser:
                        instance_dict[instance] = skip_data
                if last_action != 'prepend':
                    return (('prepend', ip_whitelist[1], instance_dict, None))
                else:
                    return(( 'dunno', 'Header already pre-pended', instance_dict, None))
        # Whitelist designated Domain's sending addresses from SPF checks (e.g. 
        # known forwarders.
        if not peruser:
            domain_whitelist = _spfbypass(data, 'Domain_Whitelist', configData)
        else:
            domain_whitelist = _spfbypass(data, 'Domain_Whitelist', peruserconfigData)
            if debugLevel >= 4: syslog.syslog('Domain_Whitelist check used peruser data')
        if domain_whitelist:
            if domain_whitelist[0]:
                skip_data = ["N/A", "Skip SPF checks for whitelisted domains", "N/A", "prepend", skip_check[1]]
                if last_action != 'prepend':
                    skip_data.append('prepend')
                    if not found_instance and not peruser:
                        instance_dict[instance] = skip_data
                if last_action != 'prepend':
                    return (('prepend', domain_whitelist[1], instance_dict, None))
                else:
                    return(( 'dunno', 'Header already pre-pended', instance_dict, None))
        # Whitelist designated HELO/EHLO Domain's sending addresses from SPF
        # checks (e.g. known forwarders and hosts with broken SPF records).
        if not peruser:
            helo_whitelist = _spfbypass(data, 'HELO_Whitelist', configData)
        else:
            helo_whitelist = _spfbypass(data, 'HELO_Whitelist', peruserconfigData)
            if debugLevel >= 4: syslog.syslog('HELO_Whitelist check used peruser data')
        if helo_whitelist:
            if helo_whitelist[0]:
                skip_data = ["N/A", "Skip SPF checks for whitelisted HELO/EHLO names", "N/A", "prepend", skip_check[1]]
                if last_action != 'prepend':
                    skip_data.append('prepend')
                    if not found_instance and not peruser:
                        instance_dict[instance] = skip_data
                if last_action != 'prepend':
                    return (('prepend', helo_whitelist[1], instance_dict, None))
                else:
                    return(( 'dunno', 'Header already pre-pended', instance_dict, None))
        # Whitelist designated Domain's sending addresses from SPF checks (e.g.
        # known forwarders, but based on PTR match
        if not peruser:
            domain_whitelist = _spfbypass(data, 'Domain_Whitelist_PTR', configData)
        else:
            domain_whitelist = _spfbypass(data, 'Domain_Whitelist_PTR', peruserconfigData)
        if domain_whitelist:
            if domain_whitelist[0]:
                skip_data = ["N/A", "Skip SPF checks for whitelisted hosts (by PTR)", "N/A", "prepend", skip_check[1]]
                if last_action != 'prepend':
                    skip_data.append('prepend')
                    if not found_instance and not peruser:
                        instance_dict[instance] = skip_data
                if last_action != 'prepend':
                    return (('prepend', domain_whitelist[1], instance_dict, None))
                else:
                    return(( 'dunno', 'Header already pre-pended', instance_dict, None))
        receiver=socket.gethostname()
        sender = data.get('sender')
        helo = data.get('helo_name')
        if not sender and not helo:
            if debugLevel >= 2: syslog.syslog('spfcheck: No sender or helo, exiting')
            return(( None, None, instance_dict, None))
        if not peruser:
            Mail_From_pass_restriction = configData.get('Mail_From_pass_restriction')
            HELO_pass_restriction = configData.get('HELO_pass_restriction')
            HELO_reject = configData.get('HELO_reject')
            Mail_From_reject = configData.get('Mail_From_reject')
            if configData.get('No_Mail') == 'True':
                No_Mail = True
            else: No_Mail = False
        else:
            Mail_From_pass_restriction = peruserconfigData.get('Mail_From_pass_restriction')
            HELO_pass_restriction = peruserconfigData.get('HELO_pass_restriction')
            HELO_reject = peruserconfigData.get('HELO_reject')
            Mail_From_reject = peruserconfigData.get('Mail_From_reject')
            if peruserconfigData.get('No_Mail') == 'True':
                No_Mail = True
            else: No_Mail = False
        helo_result = ['None',]
        # First do HELO check
        #  if no helo name sent, use domain from sender for later use.
        if not helo:
            foo = sender.split('@', 1)
            if len(foo) <  2: helo = 'unknown'
            else: helo = foo[1]
        if HELO_reject != 'No_Check':
            helo_fake_sender = 'postmaster@' + helo
            heloquery = spf.query(i=ip, s=helo_fake_sender, h=helo, querytime=configData.get('Lookup_Time'))
            try:
                res = heloquery.check()
            except Exception as e:
                e = sys.exc_info()
                exceptionmessage = "Exception: %s, locals: %s" %(e, locals())
                syslog.syslog("Ouch, caught exc: %s" %exceptionmessage)
                return(( 'dunno', exceptionmessage, instance_dict, None))
            helo_result = [res[0], res[2]]
            helo_result.append('helo') 
            helo_result[0] = helo_result[0].lower()
            helo_result[0] = helo_result[0].capitalize()
            if (helo_result[0] == 'Permerror') or (helo_result[0] == 'Temperror'):
                isheloerror = True
            else:
                isheloerror = False
            if not peruser:
                helo_resultpolicy, local = _get_resultcodes(data, configData, 'helo')
            else:
                helo_resultpolicy, local = _get_resultcodes(data, peruserconfigData, 'helo')
            if debugLevel >= 2:
                syslog.syslog('spfcheck: pyspf result: "%s"' % str(helo_result))
            if HELO_reject == 'Null' and sender:
                helo_result.append('dunno')
            else:
                for poss_actions in helo_resultpolicy:
                    if helo_result[0] in helo_resultpolicy[poss_actions]:
                        action = poss_actions
                        helo_result.append(action)
                if local['local_helo']:
                    helo_result[1] = 'Receiver policy for SPF ' + helo_result[0]
            if sender == '':
                header_sender = '<>'
            else:
                header_sender = sender
            if helo_result[0] == 'None':
                helo_result[1] = "no SPF record"
            spfDetail = ('identity=%s; client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                % (helo_result[2], ip, helo, header_sender, data.get('recipient', '<UNKNOWN>')))
            if debugLevel >= 2:
                logdata = str(helo_result[0]) + "; " + spfDetail
                syslog.syslog(logdata)
            header = ''
            if 'SPF' in configData.get('Header_Type') and 'AR' in configData.get('Header_Type'):
                if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR, 'Header_Type includes both SPF and AR - invalid configuration.')
                raise SyntaxError('Header_Type includes both SPF and AR - invalid configuration.')
            if 'AR' in configData.get('Header_Type'):
                if not configData.get('Authserv_Id'):
                    raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                header += str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                    results = [authres.SPFAuthenticationResult(result = helo_result[0],
                    result_comment = helo_result[1],
                    smtp_helo = helo, smtp_helo_comment =
                    'client-ip={0}; helo={1}; envelope-from={2}; receiver={3}'.format(ip, helo, header_sender, data.get('recipient', '<UNKNOWN>')))]))
            else:
                header = 'Received-SPF: '+ helo_result[0] + ' (' + helo_result[1] +') ' + spfDetail
            if helo_result[3] != 'reject' and helo_result[3] != 'defer':
                helo_result.append(header)
                helo_result.append(helo_result[3])
                if HELO_pass_restriction and helo_result[0] == 'Pass':
                    restrict_name = HELO_pass_restriction
                    helo_result[3] = 'result_only'
                    helo_result[4] = restrict_name
                    helo_result[5] = 'restriction'
                if not peruser:
                    instance_dict[instance] = helo_result
            # Only act on the HELO result if it is authoritative.
            else:
                if helo_result[3] == 'reject':
                    if No_Mail:
                        # If only rejecting on "v=spf1 -all", we need to know now
                        if debugLevel >= 5: syslog.syslog('Pyspf Cached SPF record before HELO No_Mail check: {0}'.format(str(heloquery.cache[helo, 'TXT'][0][0])))
                        record = str(heloquery.cache[helo, 'TXT'][0][0])
                        if record != str("b'v=spf1 -all'"):
                            if last_action != 'prepend':
                                # Prepend instead of reject if it's not a no mail record
                                helo_result[3] = 'prepend'
                            else:
                                return(( 'dunno', 'Header already pre-pended', instance_dict, None))
                if helo_result[3] in ('reject', 'defer'): # It may not be reject anymore
                    header = _rejectmessage(helo_result, 'helo', helo, ip, data.get('recipient'), configData)
                    helo_result.append(header)
                    helo_result.append(helo_result[3])
                    if not peruser:
                        instance_dict[instance] = helo_result
                    return((helo_result[3], header, instance_dict, isheloerror ))
        # Second do Mail From Check
        if sender == '':
            if HELO_reject != 'No_Check':
                helo_result.append(header)
                helo_result.append(helo_result[3])
                if HELO_pass_restriction and helo_result[0] == 'Pass':
                    restrict_name = HELO_pass_restriction
                    helo_result[3] = 'result_only'
                    helo_result[4] = restrict_name
                    helo_result[5] = 'restriction'
                    if not peruser:
                        instance_dict[instance] = helo_result
                    return('result_only', restrict_name, instance_dict, None)
                if not peruser:
                    instance_dict[instance] = helo_result
                return(( helo_result[3], header, instance_dict, isheloerror ))
        else:
            if Mail_From_reject != 'No_Check':
                mfromquery = spf.query(i=ip, s=sender, h=helo, querytime=configData.get('Lookup_Time'))
                try:
                    mres = mfromquery.check()
                except Exception as e:
                    e = sys.exc_info()
                    exceptionmessage = "Exception: %s, locals: %s" %(e, locals())
                    syslog.syslog("Ouch, caught exc: %s" %exceptionmessage)
                    return(( 'dunno', exceptionmessage, instance_dict, None))
                mfrom_result = [mres[0], mres[2]]
                mfrom_result.append('mailfrom')
                mfrom_result[0] = mfrom_result[0].lower()
                mfrom_result[0] = mfrom_result[0].capitalize()
                if (mfrom_result[0] == 'Permerror') or (mfrom_result[0] == 'Temperror'):
                    ismfromerror = True
                else:
                    ismfromerror = False
                if not peruser:
                    mfrom_resultpolicy, local = _get_resultcodes(data, configData, 'mfrom')
                else:
                    mfrom_resultpolicy, local = _get_resultcodes(data, peruserconfigData, 'mfrom')
                if debugLevel >= 2:
                    syslog.syslog('spfcheck: pyspf result: "%s"' % str(mfrom_result))
                for poss_actions in mfrom_resultpolicy:
                    if mfrom_result[0] in mfrom_resultpolicy[poss_actions]:
                        action = poss_actions
                        mfrom_result.append(action)
                if local['local_mfrom']:
                    mfrom_result[1] = 'Receiver policy for SPF ' + mfrom_result[0]
                if mfrom_result[0] == 'None':
                    mfrom_result[1] = 'no SPF record'
                if mfrom_result[0] != 'None' or (mfrom_result[0] == 'None' and helo_result[0] == 'None'):
                    spfDetail = \
                        ('identity=%s; client-ip=%s; helo=%s; envelope-from=%s; receiver=%s '
                        % (mfrom_result[2], ip, helo, sender, data.get('recipient', '<UNKNOWN>')))
                    if debugLevel >= 2:
                        logdata = str(mfrom_result[0]) + "; " + spfDetail
                        syslog.syslog(logdata)
                    header = ''
                    if 'SPF' in configData.get('Header_Type') and 'AR' in configData.get('Header_Type'):
                        if debugLevel >= 0: syslog.syslog(syslog.LOG_ERR, 'Header_Type includes both SPF and AR - invalid configuration.')
                        raise SyntaxError('Header_Type includes both SPF and AR - invalid configuration.')
                    if 'AR' in configData.get('Header_Type'):
                        if not configData.get('Authserv_Id'):
                            raise SyntaxError('Authserv_Id not set for authentication results header - invalid configuration.')
                        header += str(authres.AuthenticationResultsHeader(authserv_id = configData.get('Authserv_Id'),
                            results = [authres.SPFAuthenticationResult(result = mfrom_result[0],
                            result_comment = mfrom_result[1],
                            smtp_mailfrom = spf.split_email(sender,'example.com')[1], smtp_mailfrom_comment =
                            'client-ip={0}; helo={1}; envelope-from={2}; receiver={3}'.format(ip, helo, sender, data.get('recipient', '<UNKNOWN>')))]))
                    else:
                        header = 'Received-SPF: '+ mfrom_result[0] + ' (' + mfrom_result[2] +') ' + spfDetail
                    if mfrom_result[3] != 'reject' and mfrom_result[3] != 'defer':
                        mfrom_result.append(header)
                        mfrom_result.append(mfrom_result[3])
                        if not peruser:
                            if debugLevel >= 4:syslog.syslog('not peruser')
                            instance_dict[instance] = mfrom_result
                if (Mail_From_pass_restriction and mfrom_result[0] == 'Pass') or \
                   (HELO_pass_restriction and helo_result[0] == 'Pass'):
                    if mfrom_result[0] == 'Pass':
                        restrict_name = Mail_From_pass_restriction
                        mfrom_result[3] = 'result_only'
                        mfrom_result[4] = restrict_name
                        mfrom_result[5] = 'restriction'
                        if not peruser:
                            instance_dict[instance] = mfrom_result
                    return('result_only', restrict_name, instance_dict, None)
                # Act on the Mail From result if it is authoritative.
                if mfrom_result[3] == 'reject' or mfrom_result[3] == 'defer':
                    if mfrom_result[3] == 'reject':
                        if No_Mail:
                            # If only rejecting on "v=spf1 -all", we need to know now
                            senderdomain = sender.split('@')[1]
                            if debugLevel >= 5: syslog.syslog('Pyspf Cached SPF record before mfrom No_Mail check: {0}'.format(str(mfromquery.cache[senderdomain, 'TXT'][0][0])))
                            mrecord = str(mfromquery.cache[senderdomain, 'TXT'][0][0])
                            if mrecord != str("b'v=spf1 -all'"):
                                if last_action != 'prepend':
                                    # Prepend instead of reject if it's not a no mail record
                                    mfrom_result[3] = 'prepend'
                                else:
                                    return(( 'dunno', 'Header already pre-pended', instance_dict, None ))
                    if mfrom_result[3] in ('reject', 'defer'): # It may not be reject anymore
                        header = _rejectmessage(mfrom_result, 'mfrom', sender, ip, data.get('recipient'), configData)
                        mfrom_result.append(header)
                        mfrom_result.append(mfrom_result[3])
                        if not peruser:
                            instance_dict[instance] = mfrom_result
                        return(( mfrom_result[3], header, instance_dict, ismfromerror ))
                if mfrom_result[3] != 'dunno' or helo_result[3] == 'dunno':
                    if last_action != 'prepend':
                        return(( 'prepend', header, instance_dict, None ))
                    else:
                        return(( 'dunno', 'Header already pre-pended', instance_dict, None ))
            else:
                if HELO_reject != 'No_Check':
                    if helo_result[3] == 'reject':
                        if No_Mail:
                            # If only rejecting on "v=spf1 -all", we need to know now
                            if debugLevel >= 5: syslog.syslog('Pyspf Cached SPF record before HELO No_Mail check: {0}'.format(str(heloquery.cache[helo, 'TXT'][0][0])))
                            record = str(heloquery.cache[helo, 'TXT'][0][0])
                            if record != str("b'v=spf1 -all'"):
                                if last_action != 'prepend':
                                    # Prepend instead of reject if it's not a no mail record
                                    helo_result[3] = 'prepend'
                                else:
                                    return(( 'dunno', 'Header already pre-pended', instance_dict, None ))
                    if helo_result[3] in ('reject', 'defer'): # It may not anymore
                        header = _rejectmessage(helo_result, 'helo', helo, ip, data.get('recipient'), configData)
                        if helo_result[3] == 'reject': # It may not anymore
                            return(( 'reject', header, instance_dict, isheloerror ))
                        if helo_result[3] == 'defer':
                            return(( 'defer', header, instance_dict, isheloerror ))
                    if last_action != 'prepend':
                        return(( 'prepend', header, instance_dict, None ))
                    else:
                        return(( 'dunno', 'Header already pre-pended', instance_dict, None ))
    else:
        cached_instance = instance_dict[instance]
        if cached_instance[3] == 'prepend':
            return(( 'dunno', 'Header already pre-pended', instance_dict, None ))
        else:
            return(( cached_instance[3], cached_instance[4], instance_dict, None ))
    return(( 'None', 'None', instance_dict, None ))

