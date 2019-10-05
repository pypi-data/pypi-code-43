# __init__.py - topic extension
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""support for topic branches

Topic branches are lightweight branches which disappear when changes are
finalized (move to the public phase).

Compared to bookmark, topic is reference carried by each changesets of the
series instead of just the single head revision.  Topic are quite similar to
the way named branch work, except they eventually fade away when the changeset
becomes part of the immutable history. Changeset can belong to both a topic and
a named branch, but as long as it is mutable, its topic identity will prevail.
As a result, default destination for 'update', 'merge', etc...  will take topic
into account. When a topic is active these operations will only consider other
changesets on that topic (and, in some occurrence, bare changeset on same
branch).  When no topic is active, changeset with topic will be ignored and
only bare one on the same branch will be taken in account.

There is currently two commands to be used with that extension: 'topics' and
'stack'.

The 'hg topics' command is used to set the current topic, change and list
existing one. 'hg topics --verbose' will list various information related to
each topic.

The 'stack' will show you information about the stack of commit belonging to
your current topic.

Topic is offering you aliases reference to changeset in your current topic
stack as 's#'. For example, 's1' refers to the root of your stack, 's2' to the
second commits, etc. The 'hg stack' command show these number. 's0' can be used
to refer to the parent of the topic root. Updating using `hg up s0` will keep
the topic active.

Push behavior will change a bit with topic. When pushing to a publishing
repository the changesets will turn public and the topic data on them will fade
away. The logic regarding pushing new heads will behave has before, ignore any
topic related data. When pushing to a non-publishing repository (supporting
topic), the head checking will be done taking topic data into account.
Push will complain about multiple heads on a branch if you push multiple heads
with no topic information on them (or multiple public heads). But pushing a new
topic will not requires any specific flag. However, pushing multiple heads on a
topic will be met with the usual warning.

The 'evolve' extension takes 'topic' into account. 'hg evolve --all'
will evolve all changesets in the active topic. In addition, by default. 'hg
next' and 'hg prev' will stick to the current topic.

Be aware that this extension is still an experiment, commands and other features
are likely to be change/adjusted/dropped over time as we refine the concept.

topic-mode
==========

The topic extension can be configured to ensure the user do not forget to add
a topic when committing a new topic::

    [experimental]
    # behavior when commit is made without an active topic
    topic-mode = ignore # do nothing special (default)
    topic-mode = warning # print a warning
    topic-mode = enforce # abort the commit (except for merge)
    topic-mode = enforce-all # abort the commit (even for merge)
    topic-mode = random # use a randomized generated topic (except for merge)
    topic-mode = random-all # use a randomized generated topic (even for merge)

Single head enforcing
=====================

The extensions come with an option to enforce that there is only one heads for
each name in the repository at any time.

::

    [experimental]
    enforce-single-head = yes

Publishing behavior
===================

Topic vanish when changeset move to the public phases. Moving to the public
phase usually happens on push, but it is possible to update that behavior. The
server needs to have specific config for this.

* everything pushed become public (the default)::

    [phase]
    publish = yes

* nothing push turned public::

    [phase]
    publish = no

* topic branches are not published, changeset without topic are::

    [phase]
    publish = no
    [experimental]
    topic.publish-bare-branch = yes

In addition, the topic extension adds a ``--publish`` flag on :hg:`push`. When
used, the pushed revisions are published if the push succeeds. It also applies
to common revisions selected by the push.

One can prevent any publishing to happens in a repository using::

    [experimental]
    topic.allow-publish = no

"""

from __future__ import absolute_import

import functools
import re
import time
import weakref

from mercurial.i18n import _
from mercurial import (
    bookmarks,
    changelog,
    cmdutil,
    commands,
    context,
    error,
    extensions,
    hg,
    localrepo,
    lock as lockmod,
    merge,
    namespaces,
    node,
    obsolete,
    patch,
    phases,
    pycompat,
    registrar,
    scmutil,
    templatefilters,
    templatekw,
    util,
)

from . import (
    common,
    compat,
    constants,
    destination,
    discovery,
    flow,
    randomname,
    revset as topicrevset,
    stack,
    topicmap,
)

cmdtable = {}
command = registrar.command(cmdtable)
colortable = {b'topic.active': b'green',
              b'topic.list.unstablecount': b'red',
              b'topic.list.headcount.multiple': b'yellow',
              b'topic.list.behindcount': b'cyan',
              b'topic.list.behinderror': b'red',
              b'stack.index': b'yellow',
              b'stack.index.base': b'none dim',
              b'stack.desc.base': b'none dim',
              b'stack.shortnode.base': b'none dim',
              b'stack.state.base': b'dim',
              b'stack.state.clean': b'green',
              b'stack.index.current': b'cyan',       # random pick
              b'stack.state.current': b'cyan bold',  # random pick
              b'stack.desc.current': b'cyan',        # random pick
              b'stack.shortnode.current': b'cyan',   # random pick
              b'stack.state.orphan': b'red',
              b'stack.state.content-divergent': b'red',
              b'stack.state.phase-divergent': b'red',
              b'stack.summary.behindcount': b'cyan',
              b'stack.summary.behinderror': b'red',
              b'stack.summary.headcount.multiple': b'yellow',
              # default color to help log output and thg
              # (first pick I could think off, update as needed
              b'log.topic': b'green_background',
              b'topic.active': b'green',
              }

__version__ = b'0.17.1'

testedwith = b'4.5.2 4.6.2 4.7 4.8 4.9 5.0 5.1'
minimumhgversion = b'4.5'
buglink = b'https://bz.mercurial-scm.org/'

if util.safehasattr(registrar, 'configitem'):

    from mercurial import configitems

    configtable = {}
    configitem = registrar.configitem(configtable)

    configitem(b'experimental', b'enforce-topic',
               default=False,
    )
    configitem(b'experimental', b'enforce-single-head',
               default=False,
    )
    configitem(b'experimental', b'topic-mode',
               default=None,
    )
    configitem(b'experimental', b'topic.publish-bare-branch',
               default=False,
    )
    configitem(b'experimental', b'topic.allow-publish',
               default=configitems.dynamicdefault,
    )
    configitem(b'_internal', b'keep-topic',
               default=False,
    )
    configitem(b'experimental', b'topic-mode.server',
               default=configitems.dynamicdefault,
    )

    def extsetup(ui):
        # register config that strictly belong to other code (thg, core, etc)
        #
        # To ensure all config items we used are registered, we register them if
        # nobody else did so far.
        from mercurial import configitems
        extraitem = functools.partial(configitems._register, ui._knownconfig)
        if (b'experimental' not in ui._knownconfig
                or not ui._knownconfig[b'experimental'].get(b'thg.displaynames')):
            extraitem(b'experimental', b'thg.displaynames',
                      default=None,
            )
        if (b'devel' not in ui._knownconfig
                or not ui._knownconfig[b'devel'].get(b'random')):
            extraitem(b'devel', b'randomseed',
                      default=None,
            )

# we need to do old style declaration for <= 4.5
templatekeyword = registrar.templatekeyword()
post45template = r'requires=' in templatekeyword.__doc__

def _contexttopic(self, force=False):
    if not (force or self.mutable()):
        return b''
    return self.extra().get(constants.extrakey, b'')
context.basectx.topic = _contexttopic

def _contexttopicidx(self):
    topic = self.topic()
    if not topic or self.obsolete():
        # XXX we might want to include s0 here,
        # however s0 is related to  'currenttopic' which has no place here.
        return None
    revlist = stack.stack(self._repo, topic=topic)
    try:
        return revlist.index(self.rev())
    except IndexError:
        # Lets move to the last ctx of the current topic
        return None
context.basectx.topicidx = _contexttopicidx

stackrev = re.compile(br'^s\d+$')
topicrev = re.compile(br'^t\d+$')

hastopicext = common.hastopicext

def _namemap(repo, name):
    revs = None
    if stackrev.match(name):
        idx = int(name[1:])
        tname = topic = repo.currenttopic
        if topic:
            ttype = b'topic'
            revs = list(stack.stack(repo, topic=topic))
        else:
            ttype = b'branch'
            tname = branch = repo[None].branch()
            revs = list(stack.stack(repo, branch=branch))
    elif topicrev.match(name):
        idx = int(name[1:])
        ttype = b'topic'
        tname = topic = repo.currenttopic
        if not tname:
            raise error.Abort(_(b'cannot resolve "%s": no active topic') % name)
        revs = list(stack.stack(repo, topic=topic))

    if revs is not None:
        try:
            r = revs[idx]
        except IndexError:
            if ttype == b'topic':
                msg = _(b'cannot resolve "%s": %s "%s" has only %d changesets')
            elif ttype == b'branch':
                msg = _(b'cannot resolve "%s": %s "%s" has only %d non-public changesets')
            raise error.Abort(msg % (name, ttype, tname, len(revs) - 1))
        # t0 or s0 can be None
        if r == -1 and idx == 0:
            msg = _(b'the %s "%s" has no %s')
            raise error.Abort(msg % (ttype, tname, name))
        return [repo[r].node()]
    if name not in repo.topics:
        return []
    node = repo.changelog.node
    return [node(rev) for rev in repo.revs(b'topic(%s)', name)]

def _nodemap(repo, node):
    ctx = repo[node]
    t = ctx.topic()
    if t and ctx.phase() > phases.public:
        return [t]
    return []

def uisetup(ui):
    destination.modsetup(ui)
    discovery.modsetup(ui)
    topicmap.modsetup(ui)
    setupimportexport(ui)

    extensions.afterloaded(b'rebase', _fixrebase)

    flow.installpushflag(ui)

    entry = extensions.wrapcommand(commands.table, b'commit', commitwrap)
    entry[1].append((b't', b'topic', b'',
                     _(b"use specified topic"), _(b'TOPIC')))

    entry = extensions.wrapcommand(commands.table, b'push', pushoutgoingwrap)
    entry[1].append((b't', b'topic', b'',
                     _(b"topic to push"), _(b'TOPIC')))

    entry = extensions.wrapcommand(commands.table, b'outgoing',
                                   pushoutgoingwrap)
    entry[1].append((b't', b'topic', b'',
                     _(b"topic to push"), _(b'TOPIC')))

    extensions.wrapfunction(cmdutil, 'buildcommittext', committextwrap)
    extensions.wrapfunction(merge, 'update', mergeupdatewrap)
    # We need to check whether t0 or b0 or s0 is passed to override the default update
    # behaviour of changing topic and I can't find a better way
    # to do that as scmutil.revsingle returns the rev number and hence we can't
    # plug into logic for this into mergemod.update().
    extensions.wrapcommand(commands.table, b'update', checkt0)

    try:
        evolve = extensions.find(b'evolve')
        extensions.wrapfunction(evolve.rewriteutil, "presplitupdate",
                                presplitupdatetopic)
    except (KeyError, AttributeError):
        pass

    cmdutil.summaryhooks.add(b'topic', summaryhook)

    if not post45template:
        templatekw.keywords[b'topic'] = topickw
        templatekw.keywords[b'topicidx'] = topicidxkw
    # Wrap workingctx extra to return the topic name
    extensions.wrapfunction(context.workingctx, '__init__', wrapinit)
    # Wrap changelog.add to drop empty topic
    extensions.wrapfunction(changelog.changelog, 'add', wrapadd)

def reposetup(ui, repo):
    if not isinstance(repo, localrepo.localrepository):
        return # this can be a peer in the ssh case (puzzling)

    repo = repo.unfiltered()

    if repo.ui.config(b'experimental', b'thg.displaynames') is None:
        repo.ui.setconfig(b'experimental', b'thg.displaynames', b'topics',
                          source=b'topic-extension')

    class topicrepo(repo.__class__):

        # attribute for other code to distinct between repo with topic and repo without
        hastopicext = True

        def _restrictcapabilities(self, caps):
            caps = super(topicrepo, self)._restrictcapabilities(caps)
            caps.add(b'topics')
            return caps

        def commit(self, *args, **kwargs):
            backup = self.ui.backupconfig(b'ui', b'allowemptycommit')
            try:
                if self.currenttopic != self[b'.'].topic():
                    # bypass the core "nothing changed" logic
                    self.ui.setconfig(b'ui', b'allowemptycommit', True)
                return super(topicrepo, self).commit(*args, **kwargs)
            finally:
                self.ui.restoreconfig(backup)

        def commitctx(self, ctx, *args, **kwargs):
            topicfilter = topicmap.topicfilter(self.filtername)
            if topicfilter != self.filtername:
                other = self.filtered(topicmap.topicfilter(self.filtername))
                other.commitctx(ctx, *args, **kwargs)

            if isinstance(ctx, context.workingcommitctx):
                current = self.currenttopic
                if current:
                    ctx.extra()[constants.extrakey] = current
            if (isinstance(ctx, context.memctx)
                and ctx.extra().get(b'amend_source')
                and ctx.topic()
                and not self.currenttopic):
                # we are amending and need to remove a topic
                del ctx.extra()[constants.extrakey]
            return super(topicrepo, self).commitctx(ctx, *args, **kwargs)

        @property
        def topics(self):
            if self._topics is not None:
                return self._topics
            topics = set([b'', self.currenttopic])
            for c in self.set(b'not public()'):
                topics.add(c.topic())
            topics.remove(b'')
            self._topics = topics
            return topics

        @property
        def currenttopic(self):
            return self.vfs.tryread(b'topic')

        # overwritten at the instance level by topicmap.py
        _autobranchmaptopic = True

        def branchmap(self, topic=None):
            if topic is None:
                topic = getattr(self, '_autobranchmaptopic', False)
            topicfilter = topicmap.topicfilter(self.filtername)
            if not topic or topicfilter == self.filtername:
                return super(topicrepo, self).branchmap()
            return self.filtered(topicfilter).branchmap()

        def branchheads(self, branch=None, start=None, closed=False):
            if branch is None:
                branch = self[None].branch()
            if self.currenttopic:
                branch = b"%s:%s" % (branch, self.currenttopic)
            return super(topicrepo, self).branchheads(branch=branch,
                                                      start=start,
                                                      closed=closed)

        def invalidatevolatilesets(self):
            # XXX we might be able to move this to something invalidated less often
            super(topicrepo, self).invalidatevolatilesets()
            self._topics = None

        def peer(self):
            peer = super(topicrepo, self).peer()
            if getattr(peer, '_repo', None) is not None: # localpeer
                class topicpeer(peer.__class__):
                    def branchmap(self):
                        usetopic = not self._repo.publishing()
                        return self._repo.branchmap(topic=usetopic)
                peer.__class__ = topicpeer
            return peer

        def transaction(self, desc, *a, **k):
            ctr = self.currenttransaction()
            tr = super(topicrepo, self).transaction(desc, *a, **k)
            if desc in (b'strip', b'repair') or ctr is not None:
                return tr

            reporef = weakref.ref(self)
            if self.ui.configbool(b'experimental', b'enforce-single-head'):
                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    origvalidator = tr.validator
                else:
                    origvalidator = tr._validator

                def validator(tr2):
                    repo = reporef()
                    flow.enforcesinglehead(repo, tr2)
                    origvalidator(tr2)

                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    tr.validator = validator
                else:
                    tr._validator = validator

            topicmodeserver = self.ui.config(b'experimental',
                                             b'topic-mode.server', b'ignore')
            ispush = (desc.startswith(b'push') or desc.startswith(b'serve'))
            if (topicmodeserver != b'ignore' and ispush):
                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    origvalidator = tr.validator
                else:
                    origvalidator = tr._validator

                def validator(tr2):
                    repo = reporef()
                    flow.rejectuntopicedchangeset(repo, tr2)
                    return origvalidator(tr2)
                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    tr.validator = validator
                else:
                    tr._validator = validator

            elif (self.ui.configbool(b'experimental', b'topic.publish-bare-branch')
                    and (desc.startswith(b'push')
                         or desc.startswith(b'serve'))
                    ):
                origclose = tr.close
                trref = weakref.ref(tr)

                def close():
                    repo = reporef()
                    tr2 = trref()
                    flow.publishbarebranch(repo, tr2)
                    origclose()
                tr.close = close
            allow_publish = self.ui.configbool(b'experimental',
                                               b'topic.allow-publish',
                                               True)
            if not allow_publish:
                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    origvalidator = tr.validator
                else:
                    origvalidator = tr._validator

                def validator(tr2):
                    repo = reporef()
                    flow.reject_publish(repo, tr2)
                    return origvalidator(tr2)
                if util.safehasattr(tr, 'validator'): # hg <= 4.7
                    tr.validator = validator
                else:
                    tr._validator = validator

            # real transaction start
            ct = self.currenttopic
            if not ct:
                return tr
            ctwasempty = stack.stack(self, topic=ct).changesetcount == 0

            reporef = weakref.ref(self)

            def currenttopicempty(tr):
                # check active topic emptiness
                repo = reporef()
                csetcount = stack.stack(repo, topic=ct).changesetcount
                empty = csetcount == 0
                if empty and not ctwasempty:
                    ui.status(b"active topic '%s' is now empty\n" % ct)
                    trnames = getattr(tr, 'names', getattr(tr, '_names', ()))
                    if (b'phase' in trnames
                            or any(n.startswith(b'push-response')
                                   for n in trnames)):
                        ui.status(_(b"(use 'hg topic --clear' to clear it if needed)\n"))
                hint = _(b"(see 'hg help topics' for more information)\n")
                if ctwasempty and not empty:
                    if csetcount == 1:
                        msg = _(b"active topic '%s' grew its first changeset\n%s")
                        ui.status(msg % (ct, hint))
                    else:
                        msg = _(b"active topic '%s' grew its %s first changesets\n%s")
                        ui.status(msg % (ct, csetcount, hint))

            tr.addpostclose(b'signalcurrenttopicempty', currenttopicempty)
            return tr

    repo.__class__ = topicrepo
    repo._topics = None
    if util.safehasattr(repo, 'names'):
        repo.names.addnamespace(namespaces.namespace(
            b'topics', b'topic', namemap=_namemap, nodemap=_nodemap,
            listnames=lambda repo: repo.topics))

if post45template:
    @templatekeyword(b'topic', requires={b'ctx'})
    def topickw(context, mapping):
        """:topic: String. The topic of the changeset"""
        ctx = context.resource(mapping, b'ctx')
        return ctx.topic()

    @templatekeyword(b'topicidx', requires={b'ctx'})
    def topicidxkw(context, mapping):
        """:topicidx: Integer. Index of the changeset as a stack alias"""
        ctx = context.resource(mapping, b'ctx')
        return ctx.topicidx()
else:
    def topickw(**args):
        """:topic: String. The topic of the changeset"""
        return args[b'ctx'].topic()

    def topicidxkw(**args):
        """:topicidx: Integer. Index of the changeset as a stack alias"""
        return args[b'ctx'].topicidx()

def wrapinit(orig, self, repo, *args, **kwargs):
    orig(self, repo, *args, **kwargs)
    if not hastopicext(repo):
        return
    if constants.extrakey not in self._extra:
        if getattr(repo, 'currenttopic', b''):
            self._extra[constants.extrakey] = repo.currenttopic
        else:
            # Empty key will be dropped from extra by another hack at the changegroup level
            self._extra[constants.extrakey] = b''

def wrapadd(orig, cl, manifest, files, desc, transaction, p1, p2, user,
            date=None, extra=None, p1copies=None, p2copies=None,
            filesadded=None, filesremoved=None):
    if constants.extrakey in extra and not extra[constants.extrakey]:
        extra = extra.copy()
        del extra[constants.extrakey]
    # hg <= 4.9 (0e41f40b01cc)
    kwargs = {}
    if p1copies is not None:
        kwargs['p1copies'] = p1copies
    if p2copies is not None:
        kwargs['p2copies'] = p2copies
    # hg <= 5.0 (f385ba70e4af)
    if filesadded is not None:
        kwargs['filesadded'] = filesadded
    if filesremoved is not None:
        kwargs['filesremoved'] = filesremoved
    return orig(cl, manifest, files, desc, transaction, p1, p2, user,
                date=date, extra=extra, **kwargs)

# revset predicates are automatically registered at loading via this symbol
revsetpredicate = topicrevset.revsetpredicate

@command(b'topics', [
        (b'', b'clear', False, b'clear active topic if any'),
        (b'r', b'rev', [], b'revset of existing revisions', _(b'REV')),
        (b'l', b'list', False, b'show the stack of changeset in the topic'),
        (b'', b'age', False, b'show when you last touched the topics'),
        (b'', b'current', None, b'display the current topic only'),
    ] + commands.formatteropts,
    _(b'hg topics [TOPIC]'))
def topics(ui, repo, topic=None, **opts):
    """View current topic, set current topic, change topic for a set of revisions, or see all topics.

    Clear topic on existing topiced revisions::

      hg topics --rev <related revset> --clear

    Change topic on some revisions::

      hg topics <newtopicname> --rev <related revset>

    Clear current topic::

      hg topics --clear

    Set current topic::

      hg topics <topicname>

    List of topics::

      hg topics

    List of topics sorted according to their last touched time displaying last
    touched time and the user who last touched the topic::

      hg topics --age

    The active topic (if any) will be prepended with a "*".

    The `--current` flag helps to take active topic into account. For
    example, if you want to set the topic on all the draft changesets to the
    active topic, you can do:
        `hg topics -r "draft()" --current`

    The --verbose version of this command display various information on the state of each topic."""

    clear = opts.get('clear')
    list = opts.get('list')
    rev = opts.get('rev')
    current = opts.get('current')
    age = opts.get('age')

    if current and topic:
        raise error.Abort(_(b"cannot use --current when setting a topic"))
    if current and clear:
        raise error.Abort(_(b"cannot use --current and --clear"))
    if clear and topic:
        raise error.Abort(_(b"cannot use --clear when setting a topic"))
    if age and topic:
        raise error.Abort(_(b"cannot use --age while setting a topic"))

    touchedrevs = set()
    if rev:
        touchedrevs = scmutil.revrange(repo, rev)

    if topic:
        topic = topic.strip()
        if not topic:
            raise error.Abort(_(b"topic name cannot consist entirely of whitespaces"))
        # Have some restrictions on the topic name just like bookmark name
        scmutil.checknewlabel(repo, topic, b'topic')

        rmatch = re.match(br'[-_.\w]+', topic)
        if not rmatch or rmatch.group(0) != topic:
            helptxt = _(b"topic names can only consist of alphanumeric, '-'"
                        b" '_' and '.' characters")
            raise error.Abort(_(b"invalid topic name: '%s'") % topic, hint=helptxt)

    if list:
        ui.pager(b'topics')
        if clear or rev:
            raise error.Abort(_(b"cannot use --clear or --rev with --list"))
        if not topic:
            topic = repo.currenttopic
        if not topic:
            raise error.Abort(_(b'no active topic to list'))
        return stack.showstack(ui, repo, topic=topic,
                               opts=pycompat.byteskwargs(opts))

    if touchedrevs:
        if not obsolete.isenabled(repo, obsolete.createmarkersopt):
            raise error.Abort(_(b'must have obsolete enabled to change topics'))
        if clear:
            topic = None
        elif opts.get('current'):
            topic = repo.currenttopic
        elif not topic:
            raise error.Abort(b'changing topic requires a topic name or --clear')
        if repo.revs(b'%ld and public()', touchedrevs):
            raise error.Abort(b"can't change topic of a public change")
        wl = lock = txn = None
        try:
            wl = repo.wlock()
            lock = repo.lock()
            txn = repo.transaction(b'rewrite-topics')
            rewrote = _changetopics(ui, repo, touchedrevs, topic)
            txn.close()
            if topic is None:
                ui.status(b'cleared topic on %d changesets\n' % rewrote)
            else:
                ui.status(b'changed topic on %d changesets to "%s"\n' % (rewrote,
                                                                         topic))
        finally:
            lockmod.release(txn, lock, wl)
            repo.invalidate()
        return

    ct = repo.currenttopic
    if clear:
        if ct:
            st = stack.stack(repo, topic=ct)
            if not st:
                ui.status(_(b'clearing empty topic "%s"\n') % ct)
        return _changecurrenttopic(repo, None)

    if topic:
        if not ct:
            ui.status(_(b'marked working directory as topic: %s\n') % topic)
        return _changecurrenttopic(repo, topic)

    ui.pager(b'topics')
    # `hg topic --current`
    ret = 0
    if current and not ct:
        ui.write_err(_(b'no active topic\n'))
        ret = 1
    elif current:
        fm = ui.formatter(b'topic', pycompat.byteskwargs(opts))
        namemask = b'%s\n'
        label = b'topic.active'
        fm.startitem()
        fm.write(b'topic', namemask, ct, label=label)
        fm.end()
    else:
        _listtopics(ui, repo, opts)
    return ret

@command(b'stack', [
        (b'c', b'children', None,
            _(b'display data about children outside of the stack'))
    ] + commands.formatteropts,
    _(b'hg stack [TOPIC]'))
def cmdstack(ui, repo, topic=b'', **opts):
    """list all changesets in a topic and other information

    List the current topic by default.

    The --verbose version shows short nodes for the commits also.
    """
    if not topic:
        topic = None
    branch = None
    if topic is None and repo.currenttopic:
        topic = repo.currenttopic
    if topic is None:
        branch = repo[None].branch()
    ui.pager(b'stack')
    return stack.showstack(ui, repo, branch=branch, topic=topic,
                           opts=pycompat.byteskwargs(opts))

@command(b'debugcb|debugconvertbookmark', [
        (b'b', b'bookmark', b'', _(b'bookmark to convert to topic')),
        (b'', b'all', None, _(b'convert all bookmarks to topics')),
    ],
    _(b'[-b BOOKMARK] [--all]'))
def debugconvertbookmark(ui, repo, **opts):
    """Converts a bookmark to a topic with the same name.
    """

    bookmark = opts.get('bookmark')
    convertall = opts.get('all')

    if convertall and bookmark:
        raise error.Abort(_(b"cannot use '--all' and '-b' together"))
    if not (convertall or bookmark):
        raise error.Abort(_(b"you must specify either '--all' or '-b'"))

    bmstore = repo._bookmarks

    nodetobook = {}
    for book, revnode in bmstore.items():
        if nodetobook.get(revnode):
            nodetobook[revnode].append(book)
        else:
            nodetobook[revnode] = [book]

    # a list of nodes which we have skipped so that we don't print the skip
    # warning repeatedly
    skipped = []

    actions = {}

    lock = wlock = tr = None
    try:
        wlock = repo.wlock()
        lock = repo.lock()
        if bookmark:
            try:
                node = bmstore[bookmark]
            except KeyError:
                raise error.Abort(_(b"no such bookmark exists: '%s'") % bookmark)

            revnum = repo[node].rev()
            if len(nodetobook[node]) > 1:
                ui.status(_(b"skipping revision '%d' as it has multiple bookmarks "
                          b"on it\n") % revnum)
                return
            targetrevs = _findconvertbmarktopic(repo, bookmark)
            if targetrevs:
                actions[(bookmark, revnum)] = targetrevs

        elif convertall:
            for bmark, revnode in sorted(bmstore.items()):
                revnum = repo[revnode].rev()
                if revnum in skipped:
                    continue
                if len(nodetobook[revnode]) > 1:
                    ui.status(_(b"skipping '%d' as it has multiple bookmarks on"
                              b" it\n") % revnum)
                    skipped.append(revnum)
                    continue
                if bmark == b'@':
                    continue
                targetrevs = _findconvertbmarktopic(repo, bmark)
                if targetrevs:
                    actions[(bmark, revnum)] = targetrevs

        if actions:
            try:
                tr = repo.transaction(b'debugconvertbookmark')
                for ((bmark, revnum), targetrevs) in sorted(actions.items()):
                    _applyconvertbmarktopic(ui, repo, targetrevs, revnum, bmark, tr)
                tr.close()
            finally:
                tr.release()
    finally:
        lockmod.release(lock, wlock)

# inspired from mercurial.repair.stripbmrevset
CONVERTBOOKREVSET = b"""
not public() and (
    ancestors(bookmark(%s))
    and not ancestors(
        (
            (head() and not bookmark(%s))
            or (bookmark() - bookmark(%s))
        ) - (
            descendants(bookmark(%s))
            - bookmark(%s)
        )
    )
)
"""

def _findconvertbmarktopic(repo, bmark):
    """find revisions unambiguously defined by a bookmark

    find all changesets under the bookmark and under that bookmark only.
    """
    return repo.revs(CONVERTBOOKREVSET, bmark, bmark, bmark, bmark, bmark)

def _applyconvertbmarktopic(ui, repo, revs, old, bmark, tr):
    """apply bookmark conversion to topic

    Sets a topic as same as bname to all the changesets under the bookmark
    and delete the bookmark, if topic is set to any changeset

    old is the revision on which bookmark bmark is and tr is transaction object.
    """

    rewrote = _changetopics(ui, repo, revs, bmark)
    # We didn't changed topic to any changesets because the revset
    # returned an empty set of revisions, so let's skip deleting the
    # bookmark corresponding to which we didn't put a topic on any
    # changeset
    if rewrote == 0:
        return
    ui.status(_(b'changed topic to "%s" on %d revisions\n') % (bmark,
              rewrote))
    ui.debug(b'removing bookmark "%s" from "%d"' % (bmark, old))
    bookmarks.delete(repo, tr, [bmark])

def _changecurrenttopic(repo, newtopic):
    """changes the current topic."""

    if newtopic:
        with repo.wlock():
            with repo.vfs.open(b'topic', b'w') as f:
                f.write(newtopic)
    else:
        if repo.vfs.exists(b'topic'):
            repo.vfs.unlink(b'topic')

def _changetopics(ui, repo, revs, newtopic):
    """ Changes topic to newtopic of all the revisions in the revset and return
    the count of revisions whose topic has been changed.
    """
    rewrote = 0
    p1 = None
    p2 = None
    successors = {}
    for r in revs:
        c = repo[r]

        def filectxfn(repo, ctx, path):
            try:
                return c[path]
            except error.ManifestLookupError:
                return None
        fixedextra = dict(c.extra())
        ui.debug(b'old node id is %s\n' % node.hex(c.node()))
        ui.debug(b'origextra: %r\n' % fixedextra)
        oldtopic = fixedextra.get(constants.extrakey, None)
        if oldtopic == newtopic:
            continue
        if newtopic is None:
            del fixedextra[constants.extrakey]
        else:
            fixedextra[constants.extrakey] = newtopic
        fixedextra[constants.changekey] = c.hex()
        if b'amend_source' in fixedextra:
            # TODO: right now the commitctx wrapper in
            # topicrepo overwrites the topic in extra if
            # amend_source is set to support 'hg commit
            # --amend'. Support for amend should be adjusted
            # to not be so invasive.
            del fixedextra[b'amend_source']
        ui.debug(b'changing topic of %s from %s to %s\n' % (
            c, oldtopic or b'<none>', newtopic or b'<none>'))
        ui.debug(b'fixedextra: %r\n' % fixedextra)
        # While changing topic of set of linear commits, make sure that
        # we base our commits on new parent rather than old parent which
        # was obsoleted while changing the topic
        p1 = c.p1().node()
        p2 = c.p2().node()
        if p1 in successors:
            p1 = successors[p1][0]
        if p2 in successors:
            p2 = successors[p2][0]
        mc = context.memctx(repo,
                            (p1, p2),
                            c.description(),
                            c.files(),
                            filectxfn,
                            user=c.user(),
                            date=c.date(),
                            extra=fixedextra)

        # phase handling
        commitphase = c.phase()
        overrides = {(b'phases', b'new-commit'): commitphase}
        with repo.ui.configoverride(overrides, b'changetopic'):
            newnode = repo.commitctx(mc)

        successors[c.node()] = (newnode,)
        ui.debug(b'new node id is %s\n' % node.hex(newnode))
        rewrote += 1

    # create obsmarkers and move bookmarks
    # XXX we should be creating marker as we go instead of only at the end,
    # this makes the operations more modulars
    scmutil.cleanupnodes(repo, successors, b'changetopics')

    # move the working copy too
    wctx = repo[None]
    # in-progress merge is a bit too complex for now.
    if len(wctx.parents()) == 1:
        newid = successors.get(wctx.p1().node())
        if newid is not None:
            hg.update(repo, newid[0], quietempty=True)
    return rewrote

def _listtopics(ui, repo, opts):
    fm = ui.formatter(b'topics', pycompat.byteskwargs(opts))
    activetopic = repo.currenttopic
    namemask = b'%s'
    if repo.topics:
        maxwidth = max(len(t) for t in repo.topics)
        namemask = b'%%-%is' % maxwidth
    if opts.get('age'):
        # here we sort by age and topic name
        topicsdata = sorted(_getlasttouched(repo, repo.topics))
    else:
        # here we sort by topic name only
        topicsdata = (
            (None, topic, None, None)
            for topic in sorted(repo.topics)
        )
    for age, topic, date, user in topicsdata:
        fm.startitem()
        marker = b' '
        label = b'topic'
        active = (topic == activetopic)
        if active:
            marker = b'*'
            label = b'topic.active'
        if not ui.quiet:
            # registering the active data is made explicitly later
            fm.plain(b' %s ' % marker, label=label)
        fm.write(b'topic', namemask, topic, label=label)
        fm.data(active=active)

        if ui.quiet:
            fm.plain(b'\n')
            continue
        fm.plain(b' (')
        if date:
            if age == -1:
                timestr = b'empty and active'
            else:
                timestr = templatefilters.age(date)
            fm.write(b'lasttouched', b'%s', timestr, label=b'topic.list.time')
        if user:
            fm.write(b'usertouched', b' by %s', user, label=b'topic.list.user')
        if date:
            fm.plain(b', ')
        data = stack.stack(repo, topic=topic)
        if ui.verbose:
            fm.write(b'branches+', b'on branch: %s',
                     b'+'.join(data.branches), # XXX use list directly after 4.0 is released
                     label=b'topic.list.branches')

            fm.plain(b', ')
        fm.write(b'changesetcount', b'%d changesets', data.changesetcount,
                 label=b'topic.list.changesetcount')

        if data.unstablecount:
            fm.plain(b', ')
            fm.write(b'unstablecount', b'%d unstable',
                     data.unstablecount,
                     label=b'topic.list.unstablecount')

        headcount = len(data.heads)
        if 1 < headcount:
            fm.plain(b', ')
            fm.write(b'headcount', b'%d heads',
                     headcount,
                     label=b'topic.list.headcount.multiple')

        if ui.verbose:
            # XXX we should include the data even when not verbose

            behindcount = data.behindcount
            if 0 < behindcount:
                fm.plain(b', ')
                fm.write(b'behindcount', b'%d behind',
                         behindcount,
                         label=b'topic.list.behindcount')
            elif -1 == behindcount:
                fm.plain(b', ')
                fm.write(b'behinderror', b'%s',
                         _(b'ambiguous destination: %s') % data.behinderror,
                         label=b'topic.list.behinderror')
        fm.plain(b')\n')
    fm.end()

def _getlasttouched(repo, topics):
    """
    Calculates the last time a topic was used. Returns a generator of 4-tuples:
    (age in seconds, topic name, date, and user who last touched the topic).
    """
    curtime = time.time()
    for topic in topics:
        age = -1
        user = None
        maxtime = (0, 0)
        trevs = repo.revs(b"topic(%s)", topic)
        # Need to check for the time of all changesets in the topic, whether
        # they are obsolete of non-heads
        # XXX: can we just rely on the max rev number for this
        for revs in trevs:
            rt = repo[revs].date()
            if rt[0] >= maxtime[0]:
                # Can store the rev to gather more info
                # latesthead = revs
                maxtime = rt
                user = repo[revs].user()
            # looking on the markers also to get more information and accurate
            # last touch time.
            obsmarkers = compat.getmarkers(repo, [repo[revs].node()])
            for marker in obsmarkers:
                rt = marker.date()
                if rt[0] > maxtime[0]:
                    user = marker.metadata().get(b'user', user)
                    maxtime = rt

        username = stack.parseusername(user)
        if trevs:
            age = curtime - maxtime[0]

        yield (age, topic, maxtime, username)

def summaryhook(ui, repo):
    t = getattr(repo, 'currenttopic', b'')
    if not t:
        return
    # i18n: column positioning for "hg summary"
    ui.write(_(b"topic:  %s\n") % ui.label(t, b'topic.active'))

_validmode = [
    b'ignore',
    b'warning',
    b'enforce',
    b'enforce-all',
    b'random',
    b'random-all',
]

def _configtopicmode(ui):
    """ Parse the config to get the topicmode
    """
    topicmode = ui.config(b'experimental', b'topic-mode')

    # Fallback to read enforce-topic
    if topicmode is None:
        enforcetopic = ui.configbool(b'experimental', b'enforce-topic')
        if enforcetopic:
            topicmode = b"enforce"
    if topicmode not in _validmode:
        topicmode = _validmode[0]

    return topicmode

def commitwrap(orig, ui, repo, *args, **opts):
    if not hastopicext(repo):
        return orig(ui, repo, *args, **opts)
    with repo.wlock():
        topicmode = _configtopicmode(ui)
        ismergecommit = len(repo[None].parents()) == 2

        notopic = not repo.currenttopic
        mayabort = (topicmode == b"enforce" and not ismergecommit)
        maywarn = (topicmode == b"warning"
                   or (topicmode == b"enforce" and ismergecommit))

        mayrandom = False
        if topicmode == b"random":
            mayrandom = not ismergecommit
        elif topicmode == b"random-all":
            mayrandom = True

        if topicmode == b'enforce-all':
            ismergecommit = False
            mayabort = True
            maywarn = False

        hint = _(b"see 'hg help -e topic.topic-mode' for details")
        if opts.get('topic'):
            t = opts['topic']
            with repo.vfs.open(b'topic', b'w') as f:
                f.write(t)
        elif opts.get('amend'):
            pass
        elif notopic and mayabort:
            msg = _(b"no active topic")
            raise error.Abort(msg, hint=hint)
        elif notopic and maywarn:
            ui.warn(_(b"warning: new draft commit without topic\n"))
            if not ui.quiet:
                ui.warn((b"(%s)\n") % hint)
        elif notopic and mayrandom:
            with repo.vfs.open(b'topic', b'w') as f:
                f.write(randomname.randomtopicname(ui))
        return orig(ui, repo, *args, **opts)

def committextwrap(orig, repo, ctx, subs, extramsg):
    ret = orig(repo, ctx, subs, extramsg)
    if hastopicext(repo):
        t = repo.currenttopic
        if t:
            ret = ret.replace(b"\nHG: branch",
                              b"\nHG: topic '%s'\nHG: branch" % t)
    return ret

def pushoutgoingwrap(orig, ui, repo, *args, **opts):
    if opts.get('topic'):
        topicrevs = repo.revs(b'topic(%s) - obsolete()', opts['topic'])
        opts.setdefault('rev', []).extend(topicrevs)
    return orig(ui, repo, *args, **opts)

def mergeupdatewrap(orig, repo, node, branchmerge, force, *args, **kwargs):
    matcher = kwargs.get('matcher')
    partial = not (matcher is None or matcher.always())
    wlock = repo.wlock()
    isrebase = False
    ist0 = False
    try:
        ret = orig(repo, node, branchmerge, force, *args, **kwargs)
        if not hastopicext(repo):
            return ret
        # The mergeupdatewrap function makes the destination's topic as the
        # current topic. This is right for merge but wrong for rebase. We check
        # if rebase is running and update the currenttopic to topic of new
        # rebased commit. We have explicitly stored in config if rebase is
        # running.
        ot = repo.currenttopic
        if repo.ui.hasconfig(b'experimental', b'topicrebase'):
            isrebase = True
        if repo.ui.configbool(b'_internal', b'keep-topic'):
            ist0 = True
        if ((not partial and not branchmerge) or isrebase) and not ist0:
            t = b''
            pctx = repo[node]
            if pctx.phase() > phases.public:
                t = pctx.topic()
            with repo.vfs.open(b'topic', b'w') as f:
                f.write(t)
            if t and t != ot:
                repo.ui.status(_(b"switching to topic %s\n") % t)
            if ot and not t:
                st = stack.stack(repo, topic=ot)
                if not st:
                    repo.ui.status(_(b'clearing empty topic "%s"\n') % ot)
        elif ist0:
            repo.ui.status(_(b"preserving the current topic '%s'\n") % ot)
        return ret
    finally:
        wlock.release()

def checkt0(orig, ui, repo, node=None, rev=None, *args, **kwargs):

    thezeros = set([b't0', b'b0', b's0'])
    backup = repo.ui.backupconfig(b'_internal', b'keep-topic')
    try:
        if node in thezeros or rev in thezeros:
            repo.ui.setconfig(b'_internal', b'keep-topic', b'yes',
                              source=b'topic-extension')
        return orig(ui, repo, node=node, rev=rev, *args, **kwargs)
    finally:
        repo.ui.restoreconfig(backup)

def _fixrebase(loaded):
    if not loaded:
        return

    def savetopic(ctx, extra):
        if ctx.topic():
            extra[constants.extrakey] = ctx.topic()

    def setrebaseconfig(orig, ui, repo, **opts):
        repo.ui.setconfig(b'experimental', b'topicrebase', b'yes',
                          source=b'topic-extension')
        return orig(ui, repo, **opts)

    def new_init(orig, *args, **kwargs):
        runtime = orig(*args, **kwargs)

        if util.safehasattr(runtime, 'extrafns'):
            runtime.extrafns.append(savetopic)

        return runtime

    try:
        rebase = extensions.find(b"rebase")
        extensions.wrapfunction(rebase.rebaseruntime, '__init__', new_init)
        # This exists to store in the config that rebase is running so that we can
        # update the topic according to rebase. This is a hack and should be removed
        # when we have better options.
        extensions.wrapcommand(rebase.cmdtable, b'rebase', setrebaseconfig)
    except KeyError:
        pass

## preserve topic during import/export

def _exporttopic(seq, ctx):
    topic = ctx.topic()
    if topic:
        return b'EXP-Topic %s' % topic
    return None

def _importtopic(repo, patchdata, extra, opts):
    if b'topic' in patchdata:
        extra[b'topic'] = patchdata[b'topic']

def setupimportexport(ui):
    """run at ui setup time to install import/export logic"""
    cmdutil.extraexport.append(b'topic')
    cmdutil.extraexportmap[b'topic'] = _exporttopic
    cmdutil.extrapreimport.append(b'topic')
    cmdutil.extrapreimportmap[b'topic'] = _importtopic
    patch.patchheadermap.append((b'EXP-Topic', b'topic'))

## preserve topic during split

def presplitupdatetopic(original, repo, ui, prev, ctx):
    # Save topic of revision
    topic = None
    if util.safehasattr(ctx, 'topic'):
        topic = ctx.topic()

    # Update the working directory
    original(repo, ui, prev, ctx)

    # Restore the topic if need
    if topic:
        _changecurrenttopic(repo, topic)
