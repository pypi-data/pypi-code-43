from __future__ import absolute_import

import collections
import weakref

from mercurial.i18n import _
from mercurial import (
    bundle2,
    discovery,
    error,
    exchange,
    extensions,
    util,
)
from . import (
    common,
    compat,
)

try:
    from mercurial import wireproto
    wireproto.branchmap
except (AttributeError, ImportError): # <= hg-4.5
    from mercurial import wireprotov1server as wireproto

def _headssummary(orig, pushop, *args, **kwargs):
    # In mercurial > 4.3, we receive the pushop as arguments
    repo = pushop.repo.unfiltered()
    remote = pushop.remote

    publishing = (b'phases' not in remote.listkeys(b'namespaces')
                  or bool(remote.listkeys(b'phases').get(b'publishing', False)))

    if not common.hastopicext(pushop.repo):
        return orig(pushop, *args, **kwargs)
    elif ((publishing or not remote.capable(b'topics'))
            and not getattr(pushop, 'publish', False)):
        return orig(pushop, *args, **kwargs)

    publishedset = ()
    remotebranchmap = None
    origremotebranchmap = remote.branchmap
    publishednode = [c.node() for c in pushop.outdatedphases]
    publishedset = repo.revs(b'ancestors(%ln + %ln)',
                             publishednode,
                             pushop.remotephases.publicheads)

    rev = repo.unfiltered().changelog.nodemap.get

    def remotebranchmap():
        # drop topic information from changeset about to be published
        result = collections.defaultdict(list)
        for branch, heads in compat.branchmapitems(origremotebranchmap()):
            if b':' not in branch:
                result[branch].extend(heads)
            else:
                namedbranch = branch.split(b':', 1)[0]
                for h in heads:
                    r = rev(h)
                    if r is not None and r in publishedset:
                        result[namedbranch].append(h)
                    else:
                        result[branch].append(h)
        for heads in result.values():
            heads.sort()
        return result

    class repocls(repo.__class__):
        # awful hack to see branch as "branch:topic"
        def __getitem__(self, key):
            ctx = super(repocls, self).__getitem__(key)
            oldbranch = ctx.branch
            rev = ctx.rev()

            def branch():
                branch = oldbranch()
                if rev in publishedset:
                    return branch
                topic = ctx.topic()
                if topic:
                    branch = b"%s:%s" % (branch, topic)
                return branch

            ctx.branch = branch
            return ctx

        def revbranchcache(self):
            rbc = super(repocls, self).revbranchcache()
            localchangelog = self.changelog

            def branchinfo(rev, changelog=None):
                if changelog is None:
                    changelog = localchangelog
                branch, close = changelog.branchinfo(rev)
                if rev in publishedset:
                    return branch, close
                topic = repo[rev].topic()
                if topic:
                    branch = b"%s:%s" % (branch, topic)
                return branch, close

            rbc.branchinfo = branchinfo
            return rbc

    oldrepocls = repo.__class__
    try:
        repo.__class__ = repocls
        if remotebranchmap is not None:
            remote.branchmap = remotebranchmap
        unxx = repo.filtered(b'unfiltered-topic')
        repo.unfiltered = lambda: unxx
        pushop.repo = repo
        summary = orig(pushop)
        for key, value in summary.items():
            if b':' in key: # This is a topic
                if value[0] is None and value[1]:
                    summary[key] = ([value[1][0]], ) + value[1:]
        return summary
    finally:
        if r'unfiltered' in vars(repo):
            del repo.unfiltered
        repo.__class__ = oldrepocls
        if remotebranchmap is not None:
            remote.branchmap = origremotebranchmap

def wireprotobranchmap(orig, repo, proto):
    if not common.hastopicext(repo):
        return orig(repo, proto)
    oldrepo = repo.__class__
    try:
        class repocls(repo.__class__):
            def branchmap(self):
                usetopic = not self.publishing()
                return super(repocls, self).branchmap(topic=usetopic)
        repo.__class__ = repocls
        return orig(repo, proto)
    finally:
        repo.__class__ = oldrepo


# Discovery have deficiency around phases, branch can get new heads with pure
# phases change. This happened with a changeset was allowed to be pushed
# because it had a topic, but it later become public and create a new branch
# head.
#
# Handle this by doing an extra check for new head creation server side
def _nbheads(repo):
    data = {}
    for b in repo.branchmap().iterbranches():
        if b':' in b[0]:
            continue
        data[b[0]] = len(b[1])
    return data

def handlecheckheads(orig, op, inpart):
    """This is used to check for new heads when publishing changeset"""
    orig(op, inpart)
    if not common.hastopicext(op.repo) or op.repo.publishing():
        return
    tr = op.gettransaction()
    if tr.hookargs[b'source'] not in (b'push', b'serve'): # not a push
        return
    tr._prepushheads = _nbheads(op.repo)
    reporef = weakref.ref(op.repo)
    if util.safehasattr(tr, 'validator'): # hg <= 4.7
        oldvalidator = tr.validator
    else:
        oldvalidator = tr._validator

    def validator(tr):
        repo = reporef()
        if repo is not None:
            repo.invalidatecaches()
            finalheads = _nbheads(repo)
            for branch, oldnb in tr._prepushheads.items():
                newnb = finalheads.pop(branch, 0)
                if oldnb < newnb:
                    msg = _(b'push create a new head on branch "%s"' % branch)
                    raise error.Abort(msg)
            for branch, newnb in finalheads.items():
                if 1 < newnb:
                    msg = _(b'push create more than 1 head on new branch "%s"'
                            % branch)
                    raise error.Abort(msg)
        return oldvalidator(tr)
    if util.safehasattr(tr, 'validator'): # hg <= 4.7
        tr.validator = validator
    else:
        tr._validator = validator
handlecheckheads.params = frozenset()

def _pushb2phases(orig, pushop, bundler):
    if common.hastopicext(pushop.repo):
        checktypes = (b'check:heads', b'check:updated-heads')
        hascheck = any(p.type in checktypes for p in bundler._parts)
        if not hascheck and pushop.outdatedphases:
            exchange._pushb2ctxcheckheads(pushop, bundler)
    return orig(pushop, bundler)

def wireprotocaps(orig, repo, proto):
    caps = orig(repo, proto)
    if common.hastopicext(repo) and repo.peer().capable(b'topics'):
        caps.append(b'topics')
    return caps

def modsetup(ui):
    """run at uisetup time to install all destinations wrapping"""
    extensions.wrapfunction(discovery, '_headssummary', _headssummary)
    extensions.wrapfunction(wireproto, 'branchmap', wireprotobranchmap)
    extensions.wrapfunction(wireproto, '_capabilities', wireprotocaps)
    # we need a proper wrap b2 part stuff
    extensions.wrapfunction(bundle2, 'handlecheckheads', handlecheckheads)
    bundle2.handlecheckheads.params = frozenset()
    bundle2.parthandlermapping[b'check:heads'] = bundle2.handlecheckheads
    if util.safehasattr(bundle2, 'handlecheckupdatedheads'):
        # we still need a proper wrap b2 part stuff
        extensions.wrapfunction(bundle2, 'handlecheckupdatedheads', handlecheckheads)
        bundle2.handlecheckupdatedheads.params = frozenset()
        bundle2.parthandlermapping[b'check:updated-heads'] = bundle2.handlecheckupdatedheads
    extensions.wrapfunction(exchange, '_pushb2phases', _pushb2phases)
    exchange.b2partsgenmapping[b'phase'] = exchange._pushb2phases
