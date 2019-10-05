# Code dedicated to adding various "safeguard" around evolution
#
# Some of these will be pollished and upstream when mature. Some other will be
# replaced by better alternative later.
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from mercurial.i18n import _

from mercurial import (
    configitems,
    error,
)

from . import exthelper

eh = exthelper.exthelper()

# hg <= 4.8
if b'auto-publish' not in configitems.coreitems.get(b'experimental', {}):

    eh.configitem(b'experimental', b'auto-publish', b'publish')

    @eh.reposetup
    def setuppublishprevention(ui, repo):

        class noautopublishrepo(repo.__class__):

            def checkpush(self, pushop):
                super(noautopublishrepo, self).checkpush(pushop)
                behavior = self.ui.config(b'experimental', b'auto-publish')
                nocheck = behavior not in (b'warn', b'abort')
                if nocheck or getattr(pushop, 'publish', False):
                    return
                remotephases = pushop.remote.listkeys(b'phases')
                publishing = remotephases.get(b'publishing', False)
                if publishing:
                    if pushop.revs is None:
                        published = self.filtered(b'served').revs(b"not public()")
                    else:
                        published = self.revs(b"::%ln - public()", pushop.revs)
                    if published:
                        if behavior == b'warn':
                            self.ui.warn(_(b'%i changesets about to be published\n')
                                         % len(published))
                        elif behavior == b'abort':
                            msg = _(b'push would publish 1 changesets')
                            hint = _(b"behavior controlled by "
                                     b"'experimental.auto-publish' config")
                            raise error.Abort(msg, hint=hint)

        repo.__class__ = noautopublishrepo
