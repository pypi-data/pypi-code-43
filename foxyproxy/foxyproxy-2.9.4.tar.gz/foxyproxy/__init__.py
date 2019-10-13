#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) Smart Arcs Ltd, Enigma Bridge Ltd, registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018


__copyright__ = "Smart Arcs Ltd"
__email__ = "support@smartarchitects.co.uk"
__status__ = "Beta"

# # noinspection PyUnresolvedReferences
# from foxyproxy.foxy_proxy_tcp import FoxyProxyTCP
# # noinspection PyUnresolvedReferences
# from foxyproxy.foxy_proxy_rest import FoxyProxyREST
# # noinspection PyUnresolvedReferences
# from foxyproxy.request_data import RequestData
# # noinspection PyUnresolvedReferences
# from foxyproxy.beacon_thread import BeaconThread


try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil

    # noinspection PyUnboundLocalVariable
    __path__ = pkgutil.extend_path(__path__, __name__)
