from __future__ import absolute_import

from mercurial.i18n import _
from mercurial import (
    bookmarks,
    destutil,
    error,
    extensions,
)
from . import (
    common,
    topicmap,
)
from .evolvebits import builddependencies

def _destmergebranch(orig, repo, action=b'merge', sourceset=None,
                     onheadcheck=True, destspace=None):
    # XXX: take destspace into account
    if sourceset is None:
        p1 = repo[b'.']
    else:
        # XXX: using only the max here is flacky. That code should eventually
        # be updated to take care of the whole sourceset.
        p1 = repo[max(sourceset)]
    top = None
    if common.hastopicext(repo):
        top = p1.topic()
    if top:
        revs = repo.revs(b'topic(%s) - obsolete()', top)
        deps, rdeps = builddependencies(repo, revs)
        heads = [r for r in revs if not rdeps[r]]
        if onheadcheck and p1.rev() not in heads:
            raise error.Abort(_(b"not at topic head, update or explicit"))

        # prune heads above the source
        otherheads = set(heads)
        pool = set([p1.rev()])
        while pool:
            current = pool.pop()
            otherheads.discard(current)
            pool.update(rdeps[current])
        if not otherheads:
            # nothing to do at the topic level
            bhead = ngtip(repo, p1.branch(), all=True)
            if not bhead:
                raise error.NoMergeDestAbort(_(b"nothing to merge"))
            elif 1 == len(bhead):
                return bhead[0]
            else:
                msg = _(b"branch '%s' has %d heads "
                        b"- please merge with an explicit rev")
                hint = _(b"run 'hg heads .' to see heads")
                raise error.ManyMergeDestAbort(msg % (p1.branch(), len(bhead)),
                                               hint=hint)
        elif len(otherheads) == 1:
            return otherheads.pop()
        else:
            msg = _(b"topic '%s' has %d heads "
                    b"- please merge with an explicit rev") % (top, len(heads))
            raise error.ManyMergeDestAbort(msg)
    return orig(repo, action, sourceset, onheadcheck, destspace=destspace)

def _destupdatetopic(repo, clean, check=None):
    """decide on an update destination from current topic"""
    if not common.hastopicext(repo):
        return None, None, None
    movemark = node = None
    topic = repo.currenttopic
    if topic:
        revs = repo.revs(b'.::topic(%s)', topic)
    else:
        revs = []
    if not revs:
        return None, None, None
    node = revs.last()
    if bookmarks.isactivewdirparent(repo):
        movemark = repo[b'.'].node()
    return node, movemark, None

def desthistedit(orig, ui, repo):
    if not common.hastopicext(repo):
        return None
    if not (ui.config(b'histedit', b'defaultrev', None) is None
            and repo.currenttopic):
        return orig(ui, repo)
    revs = repo.revs(b'::. and stack()')
    if revs:
        return revs.min()
    return None

def ngtip(repo, branch, all=False):
    """tip new generation"""
    ## search for untopiced heads of branch
    # could be heads((::branch(x) - topic()))
    # but that is expensive
    #
    # we should write plain code instead

    tmap = topicmap.gettopicrepo(repo).branchmap()
    if branch not in tmap:
        return []
    elif all:
        return tmap.branchheads(branch)
    else:
        return [tmap.branchtip(branch)]

def modsetup(ui):
    """run a uisetup time to install all destinations wrapping"""
    extensions.wrapfunction(destutil, '_destmergebranch', _destmergebranch)
    bridx = destutil.destupdatesteps.index(b'branch')
    destutil.destupdatesteps.insert(bridx, b'topic')
    destutil.destupdatestepmap[b'topic'] = _destupdatetopic
    extensions.wrapfunction(destutil, 'desthistedit', desthistedit)
