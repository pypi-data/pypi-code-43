from __future__ import absolute_import

from mercurial import (
    commands,
    error,
    exchange,
    extensions,
    node,
    phases,
)

from mercurial.i18n import _

from . import (
    compat,
)

def enforcesinglehead(repo, tr):
    branchmap = repo.filtered(b'visible').branchmap()
    for name, heads in compat.branchmapitems(branchmap):
        if len(heads) > 1:
            hexs = [node.short(n) for n in heads]
            raise error.Abort(_(b'%d heads on "%s"') % (len(heads), name),
                              hint=(b', '.join(hexs)))

def publishbarebranch(repo, tr):
    """Publish changeset without topic"""
    if b'node' not in tr.hookargs: # no new node
        return
    startnode = node.bin(tr.hookargs[b'node'])
    topublish = repo.revs(b'not public() and (%n:) - hidden() - topic()', startnode)
    if topublish:
        cl = repo.changelog
        nodes = [cl.node(r) for r in topublish]
        repo._phasecache.advanceboundary(repo, tr, phases.public, nodes)

def rejectuntopicedchangeset(repo, tr):
    """Reject the push if there are changeset without topic"""
    if b'node' not in tr.hookargs: # no new revs
        return

    startnode = node.bin(tr.hookargs[b'node'])

    mode = repo.ui.config(b'experimental', b'topic-mode.server', b'ignore')

    untopiced = repo.revs(b'not public() and (%n:) - hidden() - topic()', startnode)
    if untopiced:
        num = len(untopiced)
        fnode = repo[untopiced.first()].hex()[:10]
        if num == 1:
            msg = _(b"%s") % fnode
        else:
            msg = _(b"%s and %d more") % (fnode, num - 1)
        if mode == b'warning':
            fullmsg = _(b"pushed draft changeset without topic: %s\n")
            repo.ui.warn(fullmsg % msg)
        elif mode == b'enforce':
            fullmsg = _(b"rejecting draft changesets: %s")
            raise error.Abort(fullmsg % msg)
        else:
            repo.ui.warn(_(b"unknown 'topic-mode.server': %s\n" % mode))

def reject_publish(repo, tr):
    """prevent a transaction to be publish anything"""
    published = set()
    for r, (o, n) in tr.changes[b'phases'].items():
        if n == phases.public:
            published.add(r)
    if published:
        r = min(published)
        msg = b"rejecting publishing of changeset %s" % repo[r]
        if len(published) > 1:
            msg += b' and %d others' % (len(published) - 1)
        raise error.Abort(msg)

def wrappush(orig, repo, remote, *args, **kwargs):
    """interpret the --publish flag and pass it to the push operation"""
    newargs = kwargs.copy()
    if kwargs.pop('publish', False):
        opargs = kwargs.get('opargs')
        if opargs is None:
            opargs = {}
        newargs[r'opargs'] = opargs.copy()
        newargs[r'opargs'][b'publish'] = True
    return orig(repo, remote, *args, **newargs)

def extendpushoperation(orig, self, *args, **kwargs):
    publish = kwargs.pop('publish', False)
    orig(self, *args, **kwargs)
    self.publish = publish

def wrapphasediscovery(orig, pushop):
    orig(pushop)
    if getattr(pushop, 'publish', False):
        if not pushop.remotephases.publishing:
            unfi = pushop.repo.unfiltered()
            droots = pushop.remotephases.draftroots
            revset = b'%ln and (not public() or %ln::)'
            future = list(unfi.set(revset, pushop.futureheads, droots))
            pushop.outdatedphases = future

def installpushflag(ui):
    entry = extensions.wrapcommand(commands.table, b'push', wrappush)
    if not any(opt for opt in entry[1] if opt[1] == b'publish'): # hg <= 4.9
        entry[1].append((b'', b'publish', False,
                         _(b'push the changeset as public')))
    extensions.wrapfunction(exchange.pushoperation, '__init__',
                            extendpushoperation)
    extensions.wrapfunction(exchange, '_pushdiscoveryphase', wrapphasediscovery)
    exchange.pushdiscoverymapping[b'phase'] = exchange._pushdiscoveryphase
