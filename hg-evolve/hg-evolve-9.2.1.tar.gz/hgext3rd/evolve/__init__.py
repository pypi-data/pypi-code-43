# Copyright 2011 Peter Arrenbrecht <peter.arrenbrecht@gmail.com>
#                Logilab SA        <contact@logilab.fr>
#                Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Patrick Mezard <patrick@mezard.eu>
#                Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""extends Mercurial feature related to Changeset Evolution

This extension:

- provides several commands to mutate history and deal with resulting issues,
- enable the changeset-evolution feature for Mercurial,
- improves some aspect of the early implementation in Mercurial core,

Note that a version dedicated to server usage only (no local working copy) is
available as 'evolve.serveronly'.

While many feature related to changeset evolution are directly handled by core
this extensions contains significant additions recommended to any user of
changeset evolution.

With the extension various evolution events will display warning (new unstable
changesets, obsolete working copy parent, improved error when accessing hidden
revision, etc).

In addition, the extension contains better discovery protocol for obsolescence
markers. This means less obs-markers will have to be pushed and pulled around,
speeding up such operation.

Some improvement and bug fixes available in newer version of Mercurial are also
backported to older version of Mercurial by this extension. Some older
experimental protocol are also supported for a longer time in the extensions to
help people transitioning. (The extensions is currently compatible down to
Mercurial version 4.4).

New Config::

    [experimental]
    # Set to control the behavior when pushing draft changesets to a publishing
    # repository. Possible value:
    # * ignore: current core behavior (default)
    # * warn: proceed with the push, but issue a warning
    # * abort: abort the push
    auto-publish = ignore

    # For some large repository with few markers, the current  for obsolescence
    # markers discovery can get in the way. You can disable it with the
    # configuration option below. This means all pushes and pulls will
    # re-exchange all markers every time.
    evolution.obsdiscovery = yes

Obsolescence Markers Discovery
==============================

The evolve extension containts an experimental new protocol to discover common
markers between local and remote repositories.

"Large" repositories (hundreds of thousands) will take some time to warm the
necessary cache. Some key algorithm has a naive implementation that can result
in large memory or CPU Load.

The following config controls the new protocol::

  [experimental]

  # enable new discovery protocol
  # default to "yes"
  obshashrange = yes

  # control cache warming at the end of transaction
  #   yes:  warm all caches at the end of each transaction
  #         (recommended for server),
  #   off:  warm no caches at the end of transaction,
  #         (no cache overhead during transaction,
  #          but cache will be warm from scratch on usage)
  #   auto: warm cache at the end of server side transaction(ie: push)
  #         (default).
  obshashrange.warm-cache = 'auto'

When you switch to using this protocol, we recommand that you explicitly warm
cache for your server side repositories.::

  $ hg debugupdatecache

It is recommended to enable the blackbox extension. It gathers useful data about
the experiment. It is shipped with Mercurial so no extra install is needed::

    [extensions]
    blackbox =

Finally some extra options are available to help tame the experimental
implementation of some of the algorithms::

    [experimental]
    # restrict cache size to reduce memory consumption
    obshashrange.lru-size = 2000 # default is 2000

    # automatically disable obshashrange related computation and capabilities
    # if the repository has more than N revisions.  This is meant to help large
    # server deployment to enable the feature on smaller repositories while
    # ensuring no large repository will get affected.
    obshashrange.max-revs = 100000 # default is None

For very large repositories, it might be useful to disable obsmarkers
discovery (Make sure you follow release announcement to know when you can turn
it back on)::

    [experimental]
    evolution.obsdiscovery = no

Effect Flag Experiment
======================

Evolve also records what changed between two evolutions of a changeset. For
example, having this information is helpful to understand what changed between
an obsolete changeset and its tipmost successors.

Evolve currently records:

    - Meta changes, user, date
    - Tree movement, branch and parent, did the changeset moved?
    - Description, was the commit description edited
    - Diff, was there apart from potential diff change due to rebase a change in the diff?

These flags are lightweight and can be combined, so it's easy to see if 4
evolutions of the same changeset has just updated the description or if the
content changed and you need to review again the diff.

The effect flag recording is enabled by default in Evolve 6.4.0 so you have
nothing to do to enjoy it. Now every new evolution that you create will have
the effect flag attached.

The following config control the effect flag recording::

  [experimental]
  # uncomment to deactivate the registration of effect flags in obs markers
  # evolution.effect-flags = false

You can display the effect flags with the command obslog, so if you have a
changeset and you update only the message, you will see::

    $ hg commit -m "WIP
    $ hg commit -m "A better commit message!"
    $ hg obslog .
   @  8e9045855628 (3133) A better commit message!
   |
   x  7863a5bb5763 (3132) WIP
        rewritten(description) by Boris Feld <boris.feld@octobus.net> (Fri Jun 02 12:00:24 2017 +0200) as 8e9045855628

Servers does not need to activate the effect flag recording. Effect flags that
you create will not cause interference with other clients or servers without
the effect flag recording.

Templates
=========

Evolve ship several templates that you can use to have a better visibility
about your obs history:

  - precursors, for each obsolete changeset show the closest visible
    precursors.
  - successors, for each obsolete changeset show the closest visible
    successors. It is useful when your working directory is obsolete to see
    what are its successors. This information can also be retrieved with the
    obslog command and the --all option.
  - obsfate, for each obsolete changeset display a line summarizing what
    changed between the changeset and its successors. Depending on the
    verbosity level (-q and -v) it display the changeset successors, the users
    that created the obsmarkers and the date range of these changes.

    The template itself is not complex, the data are basically a list of
    successortset. Each successorset is a dict with these fields:

      - "verb", how did the revision changed, pruned or rewritten for the moment
      - "users" a sorted list of users that have create obs marker between current
        changeset and one of its successor
      - "min_date" the tiniest date of the first obs marker between current
        changeset and one of its successor
      - "max_date" the biggest date between current changeset and one of its
        successor
      - "successors" a sorted list of locally know successors node ids
      - "markers" the raw list of changesets.
"""

evolutionhelptext = b"""
Obsolescence markers make it possible to mark changesets that have been
deleted or superset in a new version of the changeset.

Unlike the previous way of handling such changes, by stripping the old
changesets from the repository, obsolescence markers can be propagated
between repositories. This allows for a safe and simple way of exchanging
mutable history and altering it after the fact. Changeset phases are
respected, such that only draft and secret changesets can be altered (see
:hg:`help phases` for details).

Obsolescence is tracked using "obsolete markers", a piece of metadata
tracking which changesets have been made obsolete, potential successors for
a given changeset, the moment the changeset was marked as obsolete, and the
user who performed the rewriting operation. The markers are stored
separately from standard changeset data can be exchanged without any of the
precursor changesets, preventing unnecessary exchange of obsolescence data.

The complete set of obsolescence markers describes a history of changeset
modifications that is orthogonal to the repository history of file
modifications. This changeset history allows for detection and automatic
resolution of edge cases arising from multiple users rewriting the same part
of history concurrently.

Current feature status
======================

This feature is still in development.  If you see this help, you have enabled an
extension that turned this feature on.

Obsolescence markers will be exchanged between repositories that explicitly
assert support for the obsolescence feature (this can currently only be done
via an extension).

Instability
===========

Rewriting changesets might introduce instability.

There are two main kinds of instability: orphaning and diverging.

Orphans are changesets left behind when their ancestors are rewritten.
Divergence has two variants:

* Content-divergence occurs when independent rewrites of the same changesets
  lead to different results.

* Phase-divergence occurs when the old (obsolete) version of a changeset
  becomes public.

It is possible to prevent local creation of orphans by using the following config::

    [experimental]
    evolution=createmarkers,allnewcommands,exchange

You can also enable that option explicitly::

    [experimental]
    evolution=createmarkers,allnewcommands,allowunstable,exchange

or simply::

    [experimental]
    evolution=all
""".strip()

import sys
import struct

try:
    from mercurial import registrar
    registrar.templatekeyword # new in hg-3.8
except ImportError:
    from . import metadata
    raise ImportError(b'evolve needs Mercurial version %s or above' %
                      min(metadata.testedwith.split()))

import mercurial
from mercurial import util

from mercurial import obsolete

from mercurial import (
    bookmarks as bookmarksmod,
    cmdutil,
    commands,
    context,
    dirstate,
    error,
    help,
    hg,
    lock as lockmod,
    node,
    patch,
    pycompat,
    revset,
    scmutil,
)

from mercurial.i18n import _
from mercurial.node import nullid

from . import (
    compat,
    debugcmd,
    cmdrewrite,
    state,
    evolvecmd,
    exthelper,
    metadata,
    obscache,
    obsexchange,
    obshashtree,
    obshistory,
    rewind,
    safeguard,
    templatekw,
    utility,
)

TROUBLES = compat.TROUBLES
__version__ = metadata.__version__
testedwith = metadata.testedwith
minimumhgversion = metadata.minimumhgversion
buglink = metadata.buglink

# Flags for enabling optional parts of evolve
commandopt = b'allnewcommands'

obsexcmsg = utility.obsexcmsg
shorttemplate = utility.shorttemplate

colortable = {b'evolve.node': b'yellow',
              b'evolve.user': b'green',
              b'evolve.rev': b'blue',
              b'evolve.short_description': b'',
              b'evolve.date': b'cyan',
              b'evolve.current_rev': b'bold',
              b'evolve.verb': b'',
              b'evolve.operation': b'bold'
              }

_pack = struct.pack
_unpack = struct.unpack

aliases, entry = cmdutil.findcmd(b'commit', commands.table)

# This extension contains the following code
#
# - Extension Helper code
# - Obsolescence cache
# - ...
# - Older format compat

eh = exthelper.exthelper()
eh.merge(debugcmd.eh)
eh.merge(evolvecmd.eh)
eh.merge(obsexchange.eh)
eh.merge(obshashtree.eh)
eh.merge(safeguard.eh)
eh.merge(obscache.eh)
eh.merge(obshistory.eh)
eh.merge(templatekw.eh)
eh.merge(compat.eh)
eh.merge(cmdrewrite.eh)
eh.merge(rewind.eh)
uisetup = eh.finaluisetup
extsetup = eh.finalextsetup
reposetup = eh.finalreposetup
cmdtable = eh.cmdtable
configtable = eh.configtable
revsetpredicate = eh.revsetpredicate
templatekeyword = eh.templatekeyword

# Configuration
eh.configitem(b'experimental', b'evolutioncommands', [])
eh.configitem(b'experimental', b'evolution.allnewcommands', None)
eh.configitem(b'experimental', b'prunestrip', False)

# pre hg 4.0 compat

if not util.safehasattr(dirstate.dirstate, 'parentchange'):
    import contextlib

    @contextlib.contextmanager
    def parentchange(self):
        '''Context manager for handling dirstate parents.

        If an exception occurs in the scope of the context manager,
        the incoherent dirstate won't be written when wlock is
        released.
        '''
        self._parentwriters += 1
        yield
        # Typically we want the "undo" step of a context manager in a
        # finally block so it happens even when an exception
        # occurs. In this case, however, we only want to decrement
        # parentwriters if the code in the with statement exits
        # normally, so we don't have a try/finally here on purpose.
        self._parentwriters -= 1
    dirstate.dirstate.parentchange = parentchange

#####################################################################
### Option configuration                                          ###
#####################################################################

@eh.reposetup # must be the first of its kin.
def _configureoptions(ui, repo):
    # If no capabilities are specified, enable everything.
    # This is so existing evolve users don't need to change their config.
    evolveopts = repo.ui.configlist(b'experimental', b'evolution')
    if not evolveopts:
        evolveopts = [b'all']
        repo.ui.setconfig(b'experimental', b'evolution', evolveopts, b'evolve')
    if obsolete.isenabled(repo, b'exchange'):
        # if no config explicitly set, disable bundle1
        if not isinstance(repo.ui.config(b'server', b'bundle1'), bytes):
            repo.ui.setconfig(b'server', b'bundle1', False)

    class trdescrepo(repo.__class__):

        def transaction(self, desc, *args, **kwargs):
            tr = super(trdescrepo, self).transaction(desc, *args, **kwargs)
            tr.desc = desc
            return tr

    repo.__class__ = trdescrepo

@eh.uisetup
def _configurecmdoptions(ui):
    # Unregister evolve commands if the command capability is not specified.
    #
    # This must be in the same function as the option configuration above to
    # guarantee it happens after the above configuration, but before the
    # extsetup functions.
    evolvecommands = ui.configlist(b'experimental', b'evolutioncommands')
    evolveopts = ui.configlist(b'experimental', b'evolution')
    if evolveopts and (commandopt not in evolveopts
                       and b'all' not in evolveopts):
        # We build whitelist containing the commands we want to enable
        whitelist = set()
        for cmd in evolvecommands:
            matchingevolvecommands = [e for e in cmdtable.keys() if cmd in e]
            if not matchingevolvecommands:
                raise error.Abort(_(b'unknown command: %s') % cmd)
            elif len(matchingevolvecommands) > 1:
                matchstr = b', '.join(matchingevolvecommands)
                msg = _(b"ambiguous command specification: '%s' matches [%s]")
                raise error.Abort(msg % (cmd, matchstr))
            else:
                whitelist.add(matchingevolvecommands[0])
        for disabledcmd in set(cmdtable) - whitelist:
            del cmdtable[disabledcmd]

#####################################################################
### experimental behavior                                         ###
#####################################################################

getrevs = obsolete.getrevs

#####################################################################
### Additional Utilities                                          ###
#####################################################################

# This section contains a lot of small utility function and method

# - Function to create markers
# - useful alias pstatus and pdiff (should probably go in evolve)
# - "troubles" method on changectx
# - function to travel through the obsolescence graph
# - function to find useful changeset to stabilize


### Useful alias

@eh.uisetup
def setupparentcommand(ui):

    _alias, statuscmd = cmdutil.findcmd(b'status', commands.table)
    pstatusopts = [o for o in statuscmd[1] if o[1] != b'rev']

    @eh.command(b'pstatus', pstatusopts)
    def pstatus(ui, repo, *args, **kwargs):
        """show status combining committed and uncommited changes

        This show the combined status of the current working copy parent commit and
        the uncommitted change in the working copy itself. The status displayed
        match the content of the commit that a bare :hg:`amend` will creates.

        See :hg:`help status` for details."""
        kwargs['rev'] = [b'.^']
        return statuscmd[0](ui, repo, *args, **kwargs)

    _alias, diffcmd = cmdutil.findcmd(b'diff', commands.table)
    pdiffopts = [o for o in diffcmd[1] if o[1] != b'rev']

    @eh.command(b'pdiff', pdiffopts)
    def pdiff(ui, repo, *args, **kwargs):
        """show diff combining committed and uncommited changes

        This show the combined diff of the current working copy parent commit and
        the uncommitted change in the working copy itself. The diff displayed
        match the content of the commit that a bare :hg:`amend` will creates.

        See :hg:`help diff` for details."""
        kwargs['rev'] = [b'.^']
        return diffcmd[0](ui, repo, *args, **kwargs)

@eh.uisetup
def _installalias(ui):
    if ui.config(b'alias', b'odiff', None) is None:
        ui.setconfig(b'alias', b'odiff',
                     b"diff --hidden --rev 'limit(predecessors(.),1)' --rev .",
                     b'evolve')

### Unstable revset symbol

@eh.revsetpredicate(b'unstable()')
def revsetunstable(repo, subset, x):
    """Changesets with instabilities.
    """
    revset.getargs(x, 0, 0, b'unstable takes no arguments')
    troubled = set()
    troubled.update(getrevs(repo, b'orphan'))
    troubled.update(getrevs(repo, b'phasedivergent'))
    troubled.update(getrevs(repo, b'contentdivergent'))
    troubled = revset.baseset(troubled)
    troubled.sort() # set is non-ordered, enforce order
    return subset & troubled

@eh.revsetpredicate(b'troubled()')    # legacy name
def revsettroubled(repo, subset, x):
    return revsetunstable(repo, subset, x)

### Obsolescence graph

# XXX SOME MAJOR CLEAN UP TO DO HERE XXX

def _precursors(repo, s, includeidentical=False):
    """Precursor of a changeset"""
    cs = set()
    nm = repo.changelog.nodemap
    markerbysubj = repo.obsstore.predecessors
    node = repo.changelog.node
    for r in s:
        for p in markerbysubj.get(node(r), ()):
            if not includeidentical and p[2] & rewind.identicalflag:
                continue
            pr = nm.get(p[0])
            if pr is not None:
                cs.add(pr)
    cs -= repo.changelog.filteredrevs # nodemap has no filtering
    return cs

def _allprecursors(repo, s):  # XXX we need a better naming
    """transitive precursors of a subset"""
    node = repo.changelog.node
    toproceed = [node(r) for r in s]
    seen = set()
    allsubjects = repo.obsstore.predecessors
    while toproceed:
        nc = toproceed.pop()
        for mark in allsubjects.get(nc, ()):
            np = mark[0]
            if np not in seen:
                seen.add(np)
                toproceed.append(np)
    nm = repo.changelog.nodemap
    cs = set()
    for p in seen:
        pr = nm.get(p)
        if pr is not None:
            cs.add(pr)
    cs -= repo.changelog.filteredrevs # nodemap has no filtering
    return cs

def _successors(repo, s):
    """Successors of a changeset"""
    cs = set()
    node = repo.changelog.node
    nm = repo.changelog.nodemap
    markerbyobj = repo.obsstore.successors
    for r in s:
        for p in markerbyobj.get(node(r), ()):
            for sub in p[1]:
                sr = nm.get(sub)
                if sr is not None:
                    cs.add(sr)
    cs -= repo.changelog.filteredrevs # nodemap has no filtering
    return cs

def _allsuccessors(repo, s, haltonflags=0):  # XXX we need a better naming
    """transitive successors of a subset

    haltonflags allows to provide flags which prevent the evaluation of a
    marker.  """
    node = repo.changelog.node
    toproceed = [node(r) for r in s]
    seen = set()
    allobjects = repo.obsstore.successors
    while toproceed:
        nc = toproceed.pop()
        for mark in allobjects.get(nc, ()):
            if mark[2] & haltonflags:
                continue
            for sub in mark[1]:
                if sub == nullid:
                    continue # should not be here!
                if sub not in seen:
                    seen.add(sub)
                    toproceed.append(sub)
    nm = repo.changelog.nodemap
    cs = set()
    for s in seen:
        sr = nm.get(s)
        if sr is not None:
            cs.add(sr)
    cs -= repo.changelog.filteredrevs # nodemap has no filtering
    return cs

#####################################################################
### Extending revset and template                                 ###
#####################################################################

# this section add several useful revset symbol not yet in core.
# they are subject to changes


### XXX I'm not sure this revset is useful
@eh.revsetpredicate(b'suspended()')
def revsetsuspended(repo, subset, x):
    """Obsolete changesets with non-obsolete descendants.
    """
    revset.getargs(x, 0, 0, b'suspended takes no arguments')
    suspended = revset.baseset(getrevs(repo, b'suspended'))
    suspended.sort()
    return subset & suspended


@eh.revsetpredicate(b'predecessors(set)')
def revsetpredecessors(repo, subset, x):
    """Immediate predecessors of changesets in set.
    """
    s = revset.getset(repo, revset.fullreposet(repo), x)
    s = revset.baseset(_precursors(repo, s))
    s.sort()
    return subset & s


@eh.revsetpredicate(b'precursors(set)')   # legacy name for predecessors
def revsetprecursors(repo, subset, x):
    return revsetpredecessors(repo, subset, x)


@eh.revsetpredicate(b'allpredecessors(set)')
def revsetallpredecessors(repo, subset, x):
    """Transitive predecessors of changesets in set.
    """
    s = revset.getset(repo, revset.fullreposet(repo), x)
    s = revset.baseset(_allprecursors(repo, s))
    s.sort()
    return subset & s


@eh.revsetpredicate(b'allprecursors(set)')   # legacy name for allpredecessors
def revsetallprecursors(repo, subset, x):
    return revsetallpredecessors(repo, subset, x)


@eh.revsetpredicate(b'successors(set)')
def revsetsuccessors(repo, subset, x):
    """Immediate successors of changesets in set.
    """
    s = revset.getset(repo, revset.fullreposet(repo), x)
    s = revset.baseset(_successors(repo, s))
    s.sort()
    return subset & s

@eh.revsetpredicate(b'allsuccessors(set)')
def revsetallsuccessors(repo, subset, x):
    """Transitive successors of changesets in set.
    """
    s = revset.getset(repo, revset.fullreposet(repo), x)
    s = revset.baseset(_allsuccessors(repo, s))
    s.sort()
    return subset & s


#####################################################################
### Various trouble warning                                       ###
#####################################################################

# This section take care of issue warning to the user when troubles appear

def _warnobsoletewc(ui, repo, prevnode=None, wasobs=None):
    rev = repo[b'.']

    if not rev.obsolete():
        return

    if rev.node() == prevnode and wasobs:
        return
    msg = _(b"working directory parent is obsolete! (%s)\n")
    shortnode = node.short(rev.node())

    ui.warn(msg % shortnode)

    # Check that evolve is activated for performance reasons
    evolvecommandenabled = any(b'evolve' in e for e in cmdtable)
    if ui.quiet or not evolvecommandenabled:
        return

    # Show a warning for helping the user to solve the issue
    reason, successors = obshistory._getobsfateandsuccs(repo, rev.node())

    if reason == b'pruned':
        solvemsg = _(b"use 'hg evolve' to update to its parent successor")
    elif reason == b'diverged':
        debugcommand = b"hg evolve --list --content-divergent"
        basemsg = _(b"%s has diverged, use '%s' to resolve the issue")
        solvemsg = basemsg % (shortnode, debugcommand)
    elif reason == b'superseed':
        msg = _(b"use 'hg evolve' to update to its successor: %s")
        solvemsg = msg % successors[0]
    elif reason == b'superseed_split':
        msg = _(b"use 'hg evolve' to update to its tipmost successor: %s")

        if len(successors) <= 2:
            solvemsg = msg % b", ".join(successors)
        else:
            firstsuccessors = b", ".join(successors[:2])
            remainingnumber = len(successors) - 2
            successorsmsg = _(b"%s and %d more") % (firstsuccessors, remainingnumber)
            solvemsg = msg % successorsmsg
    else:
        raise ValueError(reason)

    ui.warn(b"(%s)\n" % solvemsg)

if util.safehasattr(context, '_filterederror'): # <= hg-4.5
    @eh.wrapfunction(context, '_filterederror')
    def evolve_filtererror(original, repo, changeid):
        """build an exception to be raised about a filtered changeid

        This is extracted in a function to help extensions (eg: evolve) to
        experiment with various message variants."""
        if repo.filtername.startswith(b'visible'):

            unfilteredrepo = repo.unfiltered()
            rev = repo[scmutil.revsingle(unfilteredrepo, changeid)]
            reason, successors = obshistory._getobsfateandsuccs(unfilteredrepo, rev.node())

            # Be more precise in case the revision is superseed
            if reason == b'superseed':
                reason = _(b"successor: %s") % successors[0]
            elif reason == b'superseed_split':
                if len(successors) <= 2:
                    reason = _(b"successors: %s") % b", ".join(successors)
                else:
                    firstsuccessors = b", ".join(successors[:2])
                    remainingnumber = len(successors) - 2
                    successorsmsg = _(b"%s and %d more") % (firstsuccessors, remainingnumber)
                    reason = _(b"successors: %s") % successorsmsg

            msg = _(b"hidden revision '%s'") % changeid
            hint = _(b'use --hidden to access hidden revisions; %s') % reason
            return error.FilteredRepoLookupError(msg, hint=hint)
        msg = _(b"filtered revision '%s' (not in '%s' subset)")
        msg %= (changeid, repo.filtername)
        return error.FilteredRepoLookupError(msg)

@eh.wrapcommand(b"update")
@eh.wrapcommand(b"pull")
def wrapmayobsoletewc(origfn, ui, repo, *args, **opts):
    """Warn that the working directory parent is an obsolete changeset"""
    ctx = repo[b'.']
    node = ctx.node()
    isobs = ctx.obsolete()

    def warnobsolete():
        _warnobsoletewc(ui, repo, node, isobs)
    wlock = None
    try:
        wlock = repo.wlock()
        repo._afterlock(warnobsolete)
        res = origfn(ui, repo, *args, **opts)
    finally:
        lockmod.release(wlock)
    return res

@eh.wrapcommand(b"parents")
def wrapparents(origfn, ui, repo, *args, **opts):
    res = origfn(ui, repo, *args, **opts)
    _warnobsoletewc(ui, repo)
    return res

@eh.wrapfunction(mercurial.exchange, 'push')
def push(orig, repo, *args, **opts):
    """Add a hint for "hg evolve" when troubles make push fails
    """
    try:
        return orig(repo, *args, **opts)
    except error.Abort as ex:
        hint = _(b"use 'hg evolve' to get a stable history "
                 b"or --force to ignore warnings")
        if (len(ex.args) >= 1
            and ex.args[0].startswith(b'push includes ')
            and ex.hint is None):
            ex.hint = hint
        raise

def summaryhook(ui, repo):
    evolvestate = state.cmdstate(repo)
    if evolvestate:
        # i18n: column positioning for "hg summary"
        ui.status(_(b'evolve: (evolve --continue)\n'))

@eh.extsetup
def obssummarysetup(ui):
    cmdutil.summaryhooks.add(b'evolve', summaryhook)

#####################################################################
### Old Evolve extension content                                  ###
#####################################################################

### new command
#############################

@eh.uisetup
def _installimportobsolete(ui):
    entry = cmdutil.findcmd(b'import', commands.table)[1]
    entry[1].append((b'', b'obsolete', False,
                     _(b'mark the old node as obsoleted by '
                       b'the created commit')))

def _getnodefrompatch(patch, dest):
    patchnode = patch.get(b'nodeid')
    if patchnode is not None:
        dest[b'node'] = node.bin(patchnode)

@eh.wrapfunction(mercurial.cmdutil, 'tryimportone')
def tryimportone(orig, ui, repo, hunk, parents, opts, *args, **kwargs):
    expected = {b'node': None}
    if not util.safehasattr(hunk, 'get'): # hg < 4.6
        oldextract = patch.extract

        def extract(*args, **kwargs):
            ret = oldextract(*args, **kwargs)
            _getnodefrompatch(ret, expected)
            return ret
        try:
            patch.extract = extract
            ret = orig(ui, repo, hunk, parents, opts, *args, **kwargs)
        finally:
            patch.extract = oldextract
    else:
        _getnodefrompatch(hunk, expected)
        ret = orig(ui, repo, hunk, parents, opts, *args, **kwargs)
    created = ret[1]
    if (opts[b'obsolete'] and None not in (created, expected[b'node'])
        and created != expected[b'node']):
        tr = repo.transaction(b'import-obs')
        try:
            metadata = {b'user': ui.username()}
            repo.obsstore.create(tr, expected[b'node'], (created,),
                                 metadata=metadata)
            tr.close()
        finally:
            tr.release()
    return ret


def _deprecatealias(oldalias, newalias):
    '''Deprecates an alias for a command in favour of another

    Creates a new entry in the command table for the old alias. It creates a
    wrapper that has its synopsis set to show that is has been deprecated.
    The documentation will be replace with a pointer to the new alias.
    If a user invokes the command a deprecation warning will be printed and
    the command of the *new* alias will be invoked.

    This function is loosely based on the extensions.wrapcommand function.
    '''
    try:
        aliases, entry = cmdutil.findcmd(newalias, cmdtable)
    except error.UnknownCommand:
        # Commands may be disabled
        return
    for alias, e in cmdtable.items():
        if e is entry:
            break

    synopsis = b'(DEPRECATED)'
    if len(entry) > 2:
        fn, opts, _syn = entry
    else:
        fn, opts, = entry
    deprecationwarning = _(b'%s have been deprecated in favor of %s\n') % (
        oldalias, newalias)

    def newfn(*args, **kwargs):
        ui = args[0]
        ui.warn(deprecationwarning)
        util.checksignature(fn)(*args, **kwargs)
    newfn.__doc__ = pycompat.sysstr(deprecationwarning + b' (DEPRECATED)')
    cmdwrapper = eh.command(oldalias, opts, synopsis)
    cmdwrapper(newfn)

@eh.extsetup
def deprecatealiases(ui):
    _deprecatealias(b'gup', b'next')
    _deprecatealias(b'gdown', b'previous')

def _gettopic(ctx):
    """handle topic fetching with or without the extension"""
    return getattr(ctx, 'topic', lambda: b'')()

def _gettopicidx(ctx):
    """handle topic fetching with or without the extension"""
    return getattr(ctx, 'topicidx', lambda: None)()

def _getcurrenttopic(repo):
    return getattr(repo, 'currenttopic', b'')

def _prevupdate(repo, displayer, target, bookmark, dryrun, mergeopt):
    if dryrun:
        repo.ui.write(_(b'hg update %s;\n') % target)
        if bookmark is not None:
            repo.ui.write(_(b'hg bookmark %s -r %s;\n')
                          % (bookmark, target))
    else:
        updatecheck = None
        # --merge is passed, we don't need to care about commands.update.check
        # config option
        if mergeopt:
            updatecheck = b'none'
        try:
            ret = hg.updatetotally(repo.ui, repo, target.node(), None,
                                   updatecheck=updatecheck)
        except error.Abort as exc:
            # replace the hint to mention about --merge option
            exc.hint = _(b'do you want --merge?')
            raise
        if not ret:
            tr = lock = None
            try:
                lock = repo.lock()
                tr = repo.transaction(b'previous')
                if bookmark is not None:
                    bmchanges = [(bookmark, target.node())]
                    repo._bookmarks.applychanges(repo, tr, bmchanges)
                else:
                    bookmarksmod.deactivate(repo)
                tr.close()
            finally:
                lockmod.release(tr, lock)

    if not repo.ui.quiet:
        displayer.show(target)

def _findprevtarget(repo, displayer, movebookmark=False, topic=True):
    target = bookmark = None
    wkctx = repo[None]
    p1 = wkctx.parents()[0]
    parents = p1.parents()
    currenttopic = _getcurrenttopic(repo)

    # we do not filter in the 1 case to allow prev to t0
    if currenttopic and topic and _gettopicidx(p1) != 1:
        parents = [repo[utility._singlesuccessor(repo, ctx)] if ctx.mutable() else ctx
                   for ctx in parents]
        parents = [ctx for ctx in parents if ctx.topic() == currenttopic]

    # issue message for the various case
    if p1.node() == node.nullid:
        repo.ui.warn(_(b'already at repository root\n'))
    elif not parents and currenttopic:
        repo.ui.warn(_(b'no parent in topic "%s"\n') % currenttopic)
        repo.ui.warn(_(b'(do you want --no-topic)\n'))
    elif len(parents) == 1:
        target = parents[0]
        bookmark = None
        if movebookmark:
            bookmark = repo._activebookmark
    else:
        header = _(b"multiple parents, choose one to update:")
        prevs = [p.rev() for p in parents]
        choosedrev = utility.revselectionprompt(repo.ui, repo, prevs, header)
        if choosedrev is None:
            for p in parents:
                displayer.show(p)
            repo.ui.warn(_(b'multiple parents, explicitly update to one\n'))
        else:
            target = repo[choosedrev]
    return target, bookmark

@eh.command(
    b'previous',
    [(b'B', b'move-bookmark', False,
        _(b'move active bookmark after update')),
     (b'm', b'merge', False, _(b'bring uncommitted change along')),
     (b'', b'no-topic', False, _(b'ignore topic and move topologically')),
     (b'n', b'dry-run', False,
        _(b'do not perform actions, just print what would be done'))],
    b'[OPTION]...',
    helpbasic=True)
def cmdprevious(ui, repo, **opts):
    """update to parent revision

    Displays the summary line of the destination for clarity."""
    wlock = None
    dryrunopt = opts['dry_run']
    mergeopt = opts['merge']
    if not dryrunopt:
        wlock = repo.wlock()
    try:
        wkctx = repo[None]
        wparents = wkctx.parents()
        if len(wparents) != 1:
            raise error.Abort(_(b'merge in progress'))
        if not mergeopt:
            # we only skip the check if noconflict is set
            if ui.config(b'commands', b'update.check') == b'noconflict':
                pass
            else:
                cmdutil.bailifchanged(repo, hint=_(b'do you want --merge?'))

        topic = not opts.get("no_topic", False)
        hastopic = bool(_getcurrenttopic(repo))

        template = shorttemplate
        if topic and hastopic:
            template = utility.stacktemplate

        displayer = compat.changesetdisplayer(ui, repo, {b'template': template})

        target, bookmark = _findprevtarget(repo, displayer,
                                           opts.get('move_bookmark'), topic)
        if target is not None:
            backup = repo.ui.backupconfig(b'_internal', b'keep-topic')
            try:
                if topic and _getcurrenttopic(repo) != _gettopic(target):
                    repo.ui.setconfig(b'_internal', b'keep-topic', b'yes',
                                      source=b'topic-extension')
                _prevupdate(repo, displayer, target, bookmark, dryrunopt,
                            mergeopt)
            finally:
                repo.ui.restoreconfig(backup)
            return 0
        else:
            return 1
    finally:
        lockmod.release(wlock)

@eh.command(
    b'next',
    [(b'B', b'move-bookmark', False,
        _(b'move active bookmark after update')),
     (b'm', b'merge', False, _(b'bring uncommitted change along')),
     (b'', b'evolve', True, _(b'evolve the next changeset if necessary')),
     (b'', b'no-topic', False, _(b'ignore topic and move topologically')),
     (b'n', b'dry-run', False,
      _(b'do not perform actions, just print what would be done'))],
    b'[OPTION]...',
    helpbasic=True)
def cmdnext(ui, repo, **opts):
    """update to next child revision

    If necessary, evolve the next changeset. Use --no-evolve to disable this
    behavior.

    Displays the summary line of the destination for clarity.
    """
    wlock = None
    dryrunopt = opts['dry_run']
    if not dryrunopt:
        wlock = repo.wlock()
    try:
        wkctx = repo[None]
        wparents = wkctx.parents()
        if len(wparents) != 1:
            raise error.Abort(_(b'merge in progress'))

        children = [ctx for ctx in wparents[0].children() if not ctx.obsolete()]
        topic = _getcurrenttopic(repo)
        filtered = set()
        template = shorttemplate
        if topic and not opts.get("no_topic", False):
            filtered = set(ctx for ctx in children if ctx.topic() != topic)
            children = [ctx for ctx in children if ctx not in filtered]
            template = utility.stacktemplate
            opts['stacktemplate'] = True
        displayer = compat.changesetdisplayer(ui, repo, {b'template': template})

        # check if we need to evolve while updating to the next child revision
        needevolve = False
        aspchildren = evolvecmd._aspiringchildren(repo, [repo[b'.'].rev()])
        if topic:
            filtered.update(repo[c] for c in aspchildren
                            if repo[c].topic() != topic)
            aspchildren = [ctx for ctx in aspchildren if ctx not in filtered]

        # To catch and prevent the case when `next` would get confused by split,
        # lets filter those aspiring children which can be stablized on one of
        # the aspiring children itself.
        aspirants = set(aspchildren)
        for aspchild in aspchildren:
            possdests = evolvecmd._possibledestination(repo, aspchild)
            if possdests & aspirants:
                filtered.add(aspchild)
        aspchildren = [ctx for ctx in aspchildren if ctx not in filtered]
        if aspchildren:
            needevolve = True

        # check if working directory is clean before we evolve the next cset
        if needevolve and opts['evolve']:
            hint = _(b'use `hg amend`, `hg revert` or `hg shelve`')
            cmdutil.bailifchanged(repo, hint=hint)

        if not (opts['merge'] or (needevolve and opts['evolve'])):
            # we only skip the check if noconflict is set
            if ui.config(b'commands', b'update.check') == b'noconflict':
                pass
            else:
                cmdutil.bailifchanged(repo, hint=_(b'do you want --merge?'))

        if len(children) == 1:
            c = children[0]
            return _updatetonext(ui, repo, c, displayer, opts)
        elif children:
            cheader = _(b"ambiguous next changeset, choose one to update:")
            crevs = [c.rev() for c in children]
            choosedrev = utility.revselectionprompt(ui, repo, crevs, cheader)
            if choosedrev is None:
                ui.warn(_(b"ambiguous next changeset:\n"))
                for c in children:
                    displayer.show(c)
                ui.warn(_(b"explicitly update to one of them\n"))
                return 1
            else:
                return _updatetonext(ui, repo, repo[choosedrev], displayer, opts)
        else:
            if not opts['evolve'] or not aspchildren:
                if filtered:
                    ui.warn(_(b'no children on topic "%s"\n') % topic)
                    ui.warn(_(b'do you want --no-topic\n'))
                else:
                    ui.warn(_(b'no children\n'))
                if aspchildren:
                    msg = _(b'(%i unstable changesets to be evolved here, '
                            b'do you want --evolve?)\n')
                    ui.warn(msg % len(aspchildren))
                return 1
            elif len(aspchildren) > 1:
                cheader = _(b"ambiguous next (unstable) changeset, choose one to"
                            b" evolve and update:")
                choosedrev = utility.revselectionprompt(ui, repo,
                                                        aspchildren, cheader)
                if choosedrev is None:
                    ui.warn(_(b"ambiguous next (unstable) changeset:\n"))
                    for c in aspchildren:
                        displayer.show(repo[c])
                    ui.warn(_(b"(run 'hg evolve --rev REV' on one of them)\n"))
                    return 1
                else:
                    return _nextevolve(ui, repo, repo[choosedrev], opts)
            else:
                return _nextevolve(ui, repo, aspchildren[0], opts)
    finally:
        lockmod.release(wlock)

def _nextevolve(ui, repo, aspchildren, opts):
    """logic for hg next command to evolve and update to an aspiring children"""

    cmdutil.bailifchanged(repo)
    evolvestate = state.cmdstate(repo, opts={b'command': b'next',
                                             b'bookmarkchanges': []})
    with repo.wlock(), repo.lock():
        tr = repo.transaction(b"evolve")
        with util.acceptintervention(tr):
            result = evolvecmd._solveone(ui, repo, repo[aspchildren],
                                         evolvestate, opts.get('dry_run'),
                                         False,
                                         lambda: None, category=b'orphan',
                                         stacktmplt=opts.get('stacktemplate',
                                                             False))
    # making sure a next commit is formed
    if result[0] and result[1]:
        ui.status(_(b'working directory is now at %s\n')
                  % ui.label(bytes(repo[b'.']), b'evolve.node'))
    return 0

def _updatetonext(ui, repo, child, displayer, opts):
    """ logic for `hg next` command to update to children and move bookmarks if
    required """
    bm = repo._activebookmark
    shouldmove = opts.get('move_bookmark') and bm is not None
    if opts.get('dry_run'):
        ui.write(_(b'hg update %s;\n') % child)
        if shouldmove:
            ui.write(_(b'hg bookmark %s -r %s;\n') % (bm, child))
    else:
        updatecheck = None
        # --merge is passed, we don't need to care about commands.update.check
        # config option
        if opts['merge']:
            updatecheck = b'none'
        try:
            ret = hg.updatetotally(ui, repo, child.node(), None,
                                   updatecheck=updatecheck)
        except error.Abort as exc:
            # replace the hint to mention about --merge option
            exc.hint = _(b'do you want --merge?')
            raise

        if not ret:
            lock = tr = None
            try:
                lock = repo.lock()
                tr = repo.transaction(b'next')
                if shouldmove:
                    bmchanges = [(bm, child.node())]
                    repo._bookmarks.applychanges(repo, tr, bmchanges)
                else:
                    bookmarksmod.deactivate(repo)
                tr.close()
            finally:
                lockmod.release(tr, lock)
    if not ui.quiet:
        displayer.show(child)
    return 0

@eh.wrapcommand(b'commit')
def commitwrapper(orig, ui, repo, *arg, **kwargs):
    tr = None
    if kwargs.get('amend', False):
        wlock = lock = None
    else:
        wlock = repo.wlock()
        lock = repo.lock()
    try:
        obsoleted = kwargs.get('obsolete', [])
        if obsoleted:
            obsoleted = repo.set(b'%lr', obsoleted)
        result = orig(ui, repo, *arg, **kwargs)
        if not result: # commit succeeded
            new = repo[b'tip']
            oldbookmarks = []
            markers = []
            for old in obsoleted:
                oldbookmarks.extend(repo.nodebookmarks(old.node()))
                markers.append((old, (new,)))
            if markers:
                obsolete.createmarkers(repo, markers, operation=b"amend")
            bmchanges = []
            for book in oldbookmarks:
                bmchanges.append((book, new.node()))
            if oldbookmarks:
                if not wlock:
                    wlock = repo.wlock()
                if not lock:
                    lock = repo.lock()
                tr = repo.transaction(b'commit')
                repo._bookmarks.applychanges(repo, tr, bmchanges)
                tr.close()
        return result
    finally:
        lockmod.release(tr, lock, wlock)

@eh.wrapcommand(b'strip', extension=b'strip', opts=[
    (b'', b'bundle', None, _(b"delete the commit entirely and move it to a "
                             b"backup bundle")),
    ])
def stripwrapper(orig, ui, repo, *revs, **kwargs):
    if (not ui.configbool(b'experimental', b'prunestrip')
        or kwargs.get('bundle', False)):
        return orig(ui, repo, *revs, **kwargs)

    if kwargs.get('force'):
        ui.warn(_(b"warning: --force has no effect during strip with evolve "
                  b"enabled\n"))
    if kwargs.get('no_backup', False):
        ui.warn(_(b"warning: --no-backup has no effect during strips with "
                  b"evolve enabled\n"))

    revs = list(revs) + kwargs.pop('rev', [])
    revs = set(scmutil.revrange(repo, revs))
    revs = repo.revs(b"(%ld)::", revs)
    kwargs['rev'] = []
    kwargs['new'] = []
    kwargs['successor'] = []
    kwargs['biject'] = False
    return cmdrewrite.cmdprune(ui, repo, *revs, **kwargs)

@eh.extsetup
def oldevolveextsetup(ui):
    entry = cmdutil.findcmd(b'commit', commands.table)[1]
    entry[1].append((b'o', b'obsolete', [],
                     _(b"make commit obsolete this revision (DEPRECATED)")))

@eh.wrapfunction(obsolete, '_checkinvalidmarkers')
def _checkinvalidmarkers(orig, markers):
    """search for marker with invalid data and raise error if needed

    Exist as a separated function to allow the evolve extension for a more
    subtle handling.
    """
    if r'debugobsconvert' in sys.argv:
        return
    for mark in markers:
        if node.nullid in mark[1]:
            msg = _(b'bad obsolescence marker detected: invalid successors nullid')
            hint = _(b'You should run `hg debugobsconvert`')
            raise error.Abort(msg, hint=hint)

@eh.command(
    b'debugobsconvert',
    [(b'', b'new-format', obsexchange._bestformat, _(b'Destination format for markers.'))],
    b'')
def debugobsconvert(ui, repo, new_format):
    origmarkers = repo.obsstore._all  # settle version
    if new_format == repo.obsstore._version:
        msg = _(b'New format is the same as the old format, not upgrading!')
        raise error.Abort(msg)
    with repo.lock():
        f = repo.svfs(b'obsstore', b'wb', atomictemp=True)
        known = set()
        markers = []
        for m in origmarkers:
            # filter out invalid markers
            if nullid in m[1]:
                m = list(m)
                m[1] = tuple(s for s in m[1] if s != nullid)
                m = tuple(m)
            if m in known:
                continue
            known.add(m)
            markers.append(m)
        ui.write(_(b'Old store is version %d, will rewrite in version %d\n') % (
            repo.obsstore._version, new_format))
        for data in obsolete.encodemarkers(markers, True, new_format):
            f.write(data)
        f.close()
    ui.write(_(b'Done!\n'))


def _helploader(ui):
    return help.gettext(evolutionhelptext)

@eh.uisetup
def _setuphelp(ui):
    for entry in help.helptable:
        if entry[0] == b"evolution":
            break
    else:
        help.helptable.append(([b"evolution"], _(b"Safely Rewriting History"),
                               _helploader))
        help.helptable.sort()

evolvestateversion = 0

def _evolvemessage():
    _msg = _(b'To continue:    hg evolve --continue\n'
             b'To abort:       hg evolve --abort\n'
             b'To stop:        hg evolve --stop\n'
             b'(also see `hg help evolve.interrupted`)')
    return cmdutil._commentlines(_msg)

@eh.uisetup
def setupevolveunfinished(ui):
    if not util.safehasattr(cmdutil, 'unfinishedstates'):
        from mercurial import state as statemod
        _msg = _(b'To continue:    hg evolve --continue\n'
                 b'To abort:       hg evolve --abort\n'
                 b'To stop:        hg evolve --stop\n'
                 b'(also see `hg help evolve.interrupted`)')
        statemod.addunfinished(b'evolve', fname=b'evolvestate',
                               continueflag=True, stopflag=True,
                               statushint=_msg,
                               abortfunc=evolvecmd.hgabortevolve)
        statemod.addunfinished(b'pick', fname=b'pickstate', continueflag=True,
                               abortfunc=cmdrewrite.hgabortpick)
    else:
        # compat <= hg-5.0 (5f2f6912c9e6)
        estate = (b'evolvestate', False, False, _(b'evolve in progress'),
                  _(b"use 'hg evolve --continue' or 'hg evolve --abort' to abort"))
        cmdutil.unfinishedstates.append(estate)
        pstate = (b'pickstate', False, False, _(b'pick in progress'),
                  _(b"use 'hg pick --continue' or 'hg pick --abort' to abort"))
        cmdutil.unfinishedstates.append(pstate)

        afterresolved = (b'evolvestate', _(b'hg evolve --continue'))
        pickresolved = (b'pickstate', _(b'hg pick --continue'))
        cmdutil.afterresolvedstates.append(afterresolved)
        cmdutil.afterresolvedstates.append(pickresolved)

    if util.safehasattr(cmdutil, 'STATES'):
        statedata = (b'evolve', cmdutil.fileexistspredicate(b'evolvestate'),
                     _evolvemessage)
        cmdutil.STATES = (statedata, ) + cmdutil.STATES

@eh.wrapfunction(hg, 'clean')
def clean(orig, repo, *args, **kwargs):
    ret = orig(repo, *args, **kwargs)
    util.unlinkpath(repo.vfs.join(b'evolvestate'), ignoremissing=True)
    return ret
