#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
from foxyproxy.upstream.register import RegisterUpstream
from foxyproxy.upstream.cloudfoxy import CloudFoxyConfig
from foxyproxy.upstream.cloudfoxy import CloudFoxy
from foxyproxy.upstream.globalplatform import GlobalPlatformPro
from foxyproxy.upstream.globalplatform import GlobalPlatformProConfig
from foxyproxy.upstream.base_upstream import BaseUpstreamConfig
from foxyproxy.upstream.base_upstream import BaseUpstream
from foxyproxy.upstream.linuxshell import LinuxShell
from foxyproxy.upstream.linuxshell import LinuxShellConfig
from foxyproxy.upstream.pythoncard import PythonCard
from foxyproxy.upstream.pythoncard import PythonCardConfig
# noinspection PyPep8Naming
try:
    from foxyproxy.upstream.python_ica import PythonICA
    from foxyproxy.upstream.python_postsignum import PythonPostsignum
except Exception:
    pass

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'
