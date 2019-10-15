# Copyright (c) Jeremías Casteglione <jrmsdev@gmail.com>
# See LICENSE file.

#
# deploy actions root/sumode pre
#

# register plugins (order really matters)

import _sadm.plugin.sadm
import _sadm.plugin.sadmenv

# os stuff should be done before sync assets are deployed

import _sadm.plugin.os
import _sadm.plugin.os.pkg
import _sadm.plugin.os.user

# deploy assets after all os stuff was done but before services/apps setup
# so services/apps deploy can use built (already deployed) assets
import _sadm.plugin.sync

# network (pre) plugins

import _sadm.plugin.network.iptables

#
# deploy user mode actions
#

# vcs clone should happen between network and service stuff
import _sadm.plugin.vcs.clone

# docker stuff
import _sadm.plugin.docker

#
# deploy actions root/sumode pre
#

# service plugins

import _sadm.plugin.service.postfix
import _sadm.plugin.service.docker

import _sadm.plugin.service.munin
import _sadm.plugin.service.munin_node

# services that depend on apache should go before it
# so apache is restarted after all deps were setup
import _sadm.plugin.service.apache

# network (post) plugins

import _sadm.plugin.network.fail2ban
