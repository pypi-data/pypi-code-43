# Code dedicated to display and exploration of the obsolescence history
#
# This module content aims at being upstreamed enventually.
#
# Copyright 2017 Octobus SAS <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import re

from mercurial import (
    commands,
    error,
    graphmod,
    patch,
    obsutil,
    node as nodemod,
    pycompat,
    scmutil,
    util,
)

from mercurial.i18n import _

from . import (
    compat,
    exthelper,
)

eh = exthelper.exthelper()

# Config
efd = {b'default': True} # pass a default value unless the config is registered

@eh.extsetup
def enableeffectflags(ui):
    item = (getattr(ui, '_knownconfig', {})
            .get(b'experimental', {})
            .get(b'evolution.effect-flags'))
    if item is not None:
        item.default = True
        efd.clear()

@eh.command(
    b'obslog|olog',
    [(b'G', b'graph', True, _(b"show the revision DAG")),
     (b'r', b'rev', [], _(b'show the specified revision or revset'), _(b'REV')),
     (b'a', b'all', False, _(b'show all related changesets, not only precursors')),
     (b'p', b'patch', False, _(b'show the patch between two obs versions')),
     (b'f', b'filternonlocal', False, _(b'filter out non local commits')),
     ] + commands.formatteropts,
    _(b'hg olog [OPTION]... [REV]'))
def cmdobshistory(ui, repo, *revs, **opts):
    """show the obsolescence history of the specified revisions

    If no revision range is specified, we display the log for the current
    working copy parent.

    By default this command prints the selected revisions and all its
    precursors. For precursors pointing on existing revisions in the repository,
    it will display revisions node id, revision number and the first line of the
    description. For precursors pointing on non existing revisions in the
    repository (that can happen when exchanging obsolescence-markers), display
    only the node id.

    In both case, for each node, its obsolescence marker will be displayed with
    the obsolescence operation (rewritten or pruned) in addition of the user and
    date of the operation.

    The output is a graph by default but can deactivated with the option
    '--no-graph'.

    'o' is a changeset, '@' is a working directory parent, 'x' is obsolete,
    and '+' represents a fork where the changeset from the lines below is a
    parent of the 'o' merge on the same line.

    Paths in the DAG are represented with '|', '/' and so forth.

    Returns 0 on success.
    """
    ui.pager(b'obslog')
    revs = list(revs) + opts['rev']
    if not revs:
        revs = [b'.']
    revs = scmutil.revrange(repo, revs)

    if opts['graph']:
        return _debugobshistorygraph(ui, repo, revs, opts)

    revs.reverse()
    _debugobshistoryrevs(ui, repo, revs, opts)

def _successorsandmarkers(repo, ctx):
    """compute the raw data needed for computing obsfate
    Returns a list of dict, one dict per successors set
    """
    ssets = obsutil.successorssets(repo, ctx.node(), closest=True)

    # closestsuccessors returns an empty list for pruned revisions, remap it
    # into a list containing an empty list for future processing
    if ssets == []:
        ssets = [[]]

    # Try to recover pruned markers
    succsmap = repo.obsstore.successors
    fullsuccessorsets = [] # successor set + markers
    for sset in ssets:
        if sset:
            fullsuccessorsets.append(compat.wrap_succs(sset))
        else:
            # successorsset return an empty set() when ctx or one of its
            # successors is pruned.
            # In this case, walk the obs-markers tree again starting with ctx
            # and find the relevant pruning obs-makers, the ones without
            # successors.
            # Having these markers allow us to compute some information about
            # its fate, like who pruned this changeset and when.

            # XXX we do not catch all prune markers (eg rewritten then pruned)
            # (fix me later)
            foundany = False
            for mark in succsmap.get(ctx.node(), ()):
                if not mark[1]:
                    foundany = True
                    sset = compat._succs()
                    sset.markers.add(mark)
                    fullsuccessorsets.append(sset)
            if not foundany:
                fullsuccessorsets.append(compat._succs())

    values = []
    for sset in fullsuccessorsets:
        values.append({b'successors': sset, b'markers': sset.markers})

    return values

class obsmarker_printer(compat.changesetprinter):
    """show (available) information about a node

    We display the node, description (if available) and various information
    about obsolescence markers affecting it"""

    def __init__(self, ui, repo, *args, **kwargs):

        if kwargs.pop('obspatch', False):
            if compat.changesetdiffer is None:
                kwargs['matchfn'] = scmutil.matchall(repo)
            else:
                kwargs['differ'] = scmutil.matchall(repo)

        super(obsmarker_printer, self).__init__(ui, repo, *args, **kwargs)
        diffopts = kwargs.get('diffopts', {})

        # Compat 4.6
        if not util.safehasattr(self, "_includediff"):
            self._includediff = diffopts and diffopts.get(b'patch')

        self.template = diffopts and diffopts.get(b'template')
        self.filter = diffopts and diffopts.get(b'filternonlocal')

    def show(self, ctx, copies=None, matchfn=None, **props):
        if self.buffered:
            self.ui.pushbuffer(labeled=True)

            changenode = ctx.node()

            _props = {b"template": self.template}
            fm = self.ui.formatter(b'debugobshistory', _props)

            _debugobshistorydisplaynode(fm, self.repo, changenode)

            markerfm = fm.nested(b"markers")

            # Succs markers
            if self.filter is False:
                succs = self.repo.obsstore.successors.get(changenode, ())
                succs = sorted(succs)

                for successor in succs:
                    _debugobshistorydisplaymarker(markerfm, successor,
                                                  ctx.node(), self.repo,
                                                  self._includediff)

            else:
                r = _successorsandmarkers(self.repo, ctx)

                for succset in sorted(r):
                    markers = succset[b"markers"]
                    if not markers:
                        continue
                    successors = succset[b"successors"]
                    _debugobshistorydisplaysuccsandmarkers(markerfm, successors, markers, ctx.node(), self.repo, self._includediff)

            markerfm.end()

            markerfm.plain(b'\n')
            fm.end()

            self.hunk[ctx.node()] = self.ui.popbuffer()
        else:
            ### graph output is buffered only
            msg = b'cannot be used outside of the graphlog (yet)'
            raise error.ProgrammingError(msg)

    def flush(self, ctx):
        ''' changeset_printer has some logic around buffering data
        in self.headers that we don't use
        '''
        pass

def patchavailable(node, repo, successors):
    if node not in repo:
        return False, b"context is not local"

    if len(successors) == 0:
        return False, b"no successors"
    elif len(successors) > 1:
        return False, b"too many successors (%d)" % len(successors)

    succ = successors[0]

    if succ not in repo:
        return False, b"successor is unknown locally"

    # Check that both node and succ have the same parents
    nodep1, nodep2 = repo[node].p1(), repo[node].p2()
    succp1, succp2 = repo[succ].p1(), repo[succ].p2()

    if nodep1 != succp1 or nodep2 != succp2:
        return False, b"changesets rebased"

    return True, succ

def getmarkerdescriptionpatch(repo, basedesc, succdesc):
    # description are stored without final new line,
    # add one to avoid ugly diff
    basedesc += b'\n'
    succdesc += b'\n'

    # fake file name
    basename = b"changeset-description"
    succname = b"changeset-description"

    d = compat.strdiff(basedesc, succdesc, basename, succname)
    uheaders, hunks = d

    # Copied from patch.diff
    text = b''.join(sum((list(hlines) for hrange, hlines in hunks), []))
    patch = b"\n".join(uheaders + [text])

    return patch

class missingchangectx(object):
    ''' a minimal object mimicking changectx for change contexts
    references by obs markers but not available locally '''

    def __init__(self, repo, nodeid):
        self._repo = repo
        self._node = nodeid

    def node(self):
        return self._node

    def obsolete(self):
        # If we don't have it locally, it's obsolete
        return True

def cyclic(graph):
    """Return True if the directed graph has a cycle.
    The graph must be represented as a dictionary mapping vertices to
    iterables of neighbouring vertices. For example:

    >>> cyclic({1: (2,), 2: (3,), 3: (1,)})
    True
    >>> cyclic({1: (2,), 2: (3,), 3: (4,)})
    False

    Taken from: https://codereview.stackexchange.com/a/86067

    """
    visited = set()
    o = object()
    path = [o]
    path_set = set(path)
    stack = [iter(graph)]
    while stack:
        for v in sorted(stack[-1]):
            if v in path_set:
                path_set.remove(o)
                return path_set
            elif v not in visited:
                visited.add(v)
                path.append(v)
                path_set.add(v)
                stack.append(iter(graph.get(v, ())))
                break
        else:
            path_set.remove(path.pop())
            stack.pop()
    return False

def _obshistorywalker(repo, revs, walksuccessors=False, filternonlocal=False):
    """ Directly inspired by graphmod.dagwalker,
    walk the obs marker tree and yield
    (id, CHANGESET, ctx, [parentinfo]) tuples
    """

    # Get the list of nodes and links between them
    candidates, nodesucc, nodeprec = _obshistorywalker_links(repo, revs, walksuccessors)

    # Shown, set of nodes presents in items
    shown = set()

    def isvalidcandidate(candidate):
        """ Function to filter candidates, check the candidate succ are
        in shown set
        """
        return nodesucc.get(candidate, set()).issubset(shown)

    # While we have some nodes to show
    while candidates:

        # Filter out candidates, returns only nodes with all their successors
        # already shown
        validcandidates = list(filter(isvalidcandidate, candidates))

        # If we likely have a cycle
        if not validcandidates:
            cycle = cyclic(nodesucc)
            assert cycle

            # Then choose a random node from the cycle
            breaknode = sorted(cycle)[0]
            # And display it by force
            repo.ui.debug(b'obs-cycle detected, forcing display of %s\n'
                          % nodemod.short(breaknode))
            validcandidates = [breaknode]

        # Display all valid candidates
        for cand in sorted(validcandidates):
            # Remove candidate from candidates set
            candidates.remove(cand)
            # And remove it from nodesucc in case of future cycle detected
            try:
                del nodesucc[cand]
            except KeyError:
                pass

            shown.add(cand)

            # Add the right changectx class
            if cand in repo:
                changectx = repo[cand]
            else:
                if filternonlocal is False:
                    changectx = missingchangectx(repo, cand)
                else:
                    continue

            if filternonlocal is False:
                relations = nodeprec.get(cand, ())
            else:
                relations = obsutil.closestpredecessors(repo, cand)
            # print("RELATIONS", relations, list(closestpred))
            childrens = [(graphmod.PARENT, x) for x in relations]
            # print("YIELD", changectx, childrens)
            yield (cand, graphmod.CHANGESET, changectx, childrens)

def _obshistorywalker_links(repo, revs, walksuccessors=False):
    """ Iterate the obs history tree starting from revs, traversing
    each revision precursors recursively.
    If walksuccessors is True, also check that every successor has been
    walked, which ends up walking on all connected obs markers. It helps
    getting a better view with splits and divergences.
    Return a tuple of:
    - The list of node crossed
    - The dictionnary of each node successors, values are a set
    - The dictionnary of each node precursors, values are a list
    """
    precursors = repo.obsstore.predecessors
    successors = repo.obsstore.successors
    nodec = repo.changelog.node

    # Parents, set of parents nodes seen during walking the graph for node
    nodesucc = dict()
    # Childrens
    nodeprec = dict()

    nodes = [nodec(r) for r in revs]
    seen = set(nodes)

    # Iterate on each node
    while nodes:
        node = nodes.pop()

        precs = precursors.get(node, ())

        nodeprec[node] = []

        for prec in sorted(precs):
            precnode = prec[0]

            # Mark node as prec successor
            nodesucc.setdefault(precnode, set()).add(node)

            # Mark precnode as node precursor
            nodeprec[node].append(precnode)

            # Add prec for future processing if not node already processed
            if precnode not in seen:
                seen.add(precnode)
                nodes.append(precnode)

        # Also walk on successors if the option is enabled
        if walksuccessors:
            for successor in successors.get(node, ()):
                for succnodeid in successor[1]:
                    if succnodeid not in seen:
                        seen.add(succnodeid)
                        nodes.append(succnodeid)

    return sorted(seen), nodesucc, nodeprec

def _debugobshistorygraph(ui, repo, revs, opts):

    displayer = obsmarker_printer(ui, repo.unfiltered(), obspatch=True,
                                  diffopts=pycompat.byteskwargs(opts),
                                  buffered=True)
    edges = graphmod.asciiedges
    walker = _obshistorywalker(repo.unfiltered(), revs, opts.get('all', False),
                               opts.get('filternonlocal', False))
    compat.displaygraph(ui, repo, walker, displayer, edges)

def _debugobshistoryrevs(ui, repo, revs, opts):
    """ Display the obsolescence history for revset
    """
    fm = ui.formatter(b'debugobshistory', pycompat.byteskwargs(opts))
    precursors = repo.obsstore.predecessors
    successors = repo.obsstore.successors
    nodec = repo.changelog.node
    unfi = repo.unfiltered()
    nodes = [nodec(r) for r in revs]

    seen = set(nodes)

    while nodes:
        ctxnode = nodes.pop()

        _debugobshistorydisplaynode(fm, unfi, ctxnode)

        succs = successors.get(ctxnode, ())

        markerfm = fm.nested(b"markers")
        for successor in sorted(succs):
            includediff = opts and opts.get("patch")
            _debugobshistorydisplaymarker(markerfm, successor, ctxnode, unfi, includediff)
        markerfm.end()

        precs = precursors.get(ctxnode, ())
        for p in sorted(precs):
            # Only show nodes once
            if p[0] not in seen:
                seen.add(p[0])
                nodes.append(p[0])
    fm.end()

def _debugobshistorydisplaynode(fm, repo, node):
    if node in repo:
        _debugobshistorydisplayctx(fm, repo[node])
    else:
        _debugobshistorydisplaymissingctx(fm, node)

def _debugobshistorydisplayctx(fm, ctx):
    shortdescription = ctx.description().strip()
    if shortdescription:
        shortdescription = shortdescription.splitlines()[0]

    fm.startitem()
    fm.write(b'node', b'%s', bytes(ctx),
             label=b"evolve.node")
    fm.plain(b' ')

    fm.write(b'rev', b'(%d)', ctx.rev(),
             label=b"evolve.rev")
    fm.plain(b' ')

    fm.write(b'shortdescription', b'%s', shortdescription,
             label=b"evolve.short_description")
    fm.plain(b'\n')

def _debugobshistorydisplaymissingctx(fm, nodewithoutctx):
    hexnode = nodemod.short(nodewithoutctx)
    fm.startitem()
    fm.write(b'node', b'%s', hexnode,
             label=b"evolve.node evolve.missing_change_ctx")
    fm.plain(b'\n')

def _debugobshistorydisplaymarker(fm, marker, node, repo, includediff=False):
    succnodes = marker[1]
    date = marker[4]
    metadata = dict(marker[3])

    fm.startitem()
    fm.plain(b'  ')

    # Detect pruned revisions
    if len(succnodes) == 0:
        verb = b'pruned'
    else:
        verb = b'rewritten'

    fm.write(b'verb', b'%s', verb,
             label=b"evolve.verb")

    effectflag = metadata.get(b'ef1')
    if effectflag is not None:
        try:
            effectflag = int(effectflag)
        except ValueError:
            effectflag = None
    if effectflag:
        effect = []

        # XXX should be a dict
        if effectflag & DESCCHANGED:
            effect.append(b'description')
        if effectflag & METACHANGED:
            effect.append(b'meta')
        if effectflag & USERCHANGED:
            effect.append(b'user')
        if effectflag & DATECHANGED:
            effect.append(b'date')
        if effectflag & BRANCHCHANGED:
            effect.append(b'branch')
        if effectflag & PARENTCHANGED:
            effect.append(b'parent')
        if effectflag & DIFFCHANGED:
            effect.append(b'content')

        if effect:
            fmteffect = fm.formatlist(effect, b'effect', sep=b', ')
            fm.write(b'effect', b'(%s)', fmteffect)

    if len(succnodes) > 0:
        fm.plain(b' as ')

        shortsnodes = (nodemod.short(succnode) for succnode in sorted(succnodes))
        nodes = fm.formatlist(shortsnodes, b'succnodes', sep=b', ')
        fm.write(b'succnodes', b'%s', nodes,
                 label=b"evolve.node")

    operation = metadata.get(b'operation')
    if operation:
        fm.plain(b' using ')
        fm.write(b'operation', b'%s', operation, label=b"evolve.operation")

    fm.plain(b' by ')

    fm.write(b'user', b'%s', metadata[b'user'],
             label=b"evolve.user")
    fm.plain(b' ')

    fm.write(b'date', b'(%s)', fm.formatdate(date),
             label=b"evolve.date")

    # initial support for showing note
    if metadata.get(b'note'):
        fm.plain(b'\n    note: ')
        fm.write(b'note', b"%s", metadata[b'note'], label=b"evolve.note")

    # Patch display
    if includediff is True:
        _patchavailable = patchavailable(node, repo, marker[1])

        if _patchavailable[0] is True:
            succ = _patchavailable[1]

            basectx = repo[node]
            succctx = repo[succ]
            # Description patch
            descriptionpatch = getmarkerdescriptionpatch(repo,
                                                         basectx.description(),
                                                         succctx.description())

            if descriptionpatch:
                # add the diffheader
                diffheader = b"diff -r %s -r %s changeset-description\n" %\
                             (basectx, succctx)
                descriptionpatch = diffheader + descriptionpatch

                def tolist(text):
                    return [text]

                fm.plain(b"\n")

                for chunk, label in patch.difflabel(tolist, descriptionpatch):
                    chunk = chunk.strip(b'\t')
                    if chunk and chunk != b'\n':
                        fm.plain(b'    ')
                    fm.write(b'desc-diff', b'%s', chunk, label=label)

            # Content patch
            diffopts = patch.diffallopts(repo.ui, {})
            matchfn = scmutil.matchall(repo)
            firstline = True
            linestart = True
            for chunk, label in patch.diffui(repo, node, succ, matchfn,
                                             opts=diffopts):
                if firstline:
                    fm.plain(b'\n')
                    firstline = False
                if linestart:
                    fm.plain(b'    ')
                    linestart = False
                if chunk == b'\n':
                    linestart = True
                fm.write(b'patch', b'%s', chunk, label=label)
        else:
            nopatch = b"    (No patch available, %s)" % _patchavailable[1]
            fm.plain(b"\n")
            # TODO: should be in json too
            fm.plain(nopatch)

    fm.plain(b"\n")

def _debugobshistorydisplaysuccsandmarkers(fm, succnodes, markers, node, repo, includediff=False):
    """
    This function is a duplication of _debugobshistorydisplaymarker modified
    to accept multiple markers as input.
    """
    fm.startitem()
    fm.plain(b'  ')

    # Detect pruned revisions
    verb = _successorsetverb(succnodes, markers)[b"verb"]

    fm.write(b'verb', b'%s', verb,
             label=b"evolve.verb")

    # Effect flag
    metadata = [dict(marker[3]) for marker in markers]
    ef1 = [data.get(b'ef1') for data in metadata]

    effectflag = 0
    for ef in ef1:
        if ef:
            effectflag |= int(ef)

    if effectflag:
        effect = []

        # XXX should be a dict
        if effectflag & DESCCHANGED:
            effect.append(b'description')
        if effectflag & METACHANGED:
            effect.append(b'meta')
        if effectflag & USERCHANGED:
            effect.append(b'user')
        if effectflag & DATECHANGED:
            effect.append(b'date')
        if effectflag & BRANCHCHANGED:
            effect.append(b'branch')
        if effectflag & PARENTCHANGED:
            effect.append(b'parent')
        if effectflag & DIFFCHANGED:
            effect.append(b'content')

        if effect:
            fmteffect = fm.formatlist(effect, b'effect', sep=b', ')
            fm.write(b'effect', b'(%s)', fmteffect)

    if len(succnodes) > 0:
        fm.plain(b' as ')

        shortsnodes = (nodemod.short(succnode) for succnode in sorted(succnodes))
        nodes = fm.formatlist(shortsnodes, b'succnodes', sep=b', ')
        fm.write(b'succnodes', b'%s', nodes,
                 label=b"evolve.node")

    # Operations
    operations = compat.markersoperations(markers)
    if operations:
        fm.plain(b' using ')
        fm.write(b'operation', b'%s', b", ".join(operations), label=b"evolve.operation")

    fm.plain(b' by ')

    # Users
    users = compat.markersusers(markers)
    fm.write(b'user', b'%s', b", ".join(users),
             label=b"evolve.user")
    fm.plain(b' ')

    # Dates
    dates = compat.markersdates(markers)
    if dates:
        min_date = min(dates)
        max_date = max(dates)

        if min_date == max_date:
            fm.write(b"date", b"(at %s)", fm.formatdate(min_date), label=b"evolve.date")
        else:
            fm.write(b"date", b"(between %s and %s)", fm.formatdate(min_date),
                     fm.formatdate(max_date), label=b"evolve.date")

    # initial support for showing note
    # if metadata.get('note'):
    #     fm.plain('\n    note: ')
    #     fm.write('note', "%s", metadata['note'], label="evolve.note")

    # Patch display
    if includediff is True:
        _patchavailable = patchavailable(node, repo, succnodes)

        if _patchavailable[0] is True:
            succ = _patchavailable[1]

            basectx = repo[node]
            succctx = repo[succ]
            # Description patch
            descriptionpatch = getmarkerdescriptionpatch(repo,
                                                         basectx.description(),
                                                         succctx.description())

            if descriptionpatch:
                # add the diffheader
                diffheader = b"diff -r %s -r %s changeset-description\n" %\
                             (basectx, succctx)
                descriptionpatch = diffheader + descriptionpatch

                def tolist(text):
                    return [text]

                fm.plain(b"\n")

                for chunk, label in patch.difflabel(tolist, descriptionpatch):
                    chunk = chunk.strip(b'\t')
                    if chunk and chunk != b'\n':
                        fm.plain(b'    ')
                    fm.write(b'desc-diff', b'%s', chunk, label=label)

            # Content patch
            diffopts = patch.diffallopts(repo.ui, {})
            matchfn = scmutil.matchall(repo)
            firstline = True
            linestart = True
            for chunk, label in patch.diffui(repo, node, succ, matchfn,
                                             opts=diffopts):
                if firstline:
                    fm.plain(b'\n')
                    firstline = False
                if linestart:
                    fm.plain(b'    ')
                    linestart = False
                if chunk == b'\n':
                    linestart = True
                fm.write(b'patch', b'%s', chunk, label=label)
        else:
            nopatch = b"    (No patch available, %s)" % _patchavailable[1]
            fm.plain(b"\n")
            # TODO: should be in json too
            fm.plain(nopatch)

    fm.plain(b"\n")

# logic around storing and using effect flags
DESCCHANGED = 1 << 0 # action changed the description
METACHANGED = 1 << 1 # action change the meta
PARENTCHANGED = 1 << 2 # action change the parent
DIFFCHANGED = 1 << 3 # action change diff introduced by the changeset
USERCHANGED = 1 << 4 # the user changed
DATECHANGED = 1 << 5 # the date changed
BRANCHCHANGED = 1 << 6 # the branch changed

METABLACKLIST = [
    re.compile(br'^__touch-noise__$'),
    re.compile(br'^branch$'),
    re.compile(br'^.*-source$'),
    re.compile(br'^.*_source$'),
    re.compile(br'^source$'),
]

def ismetablacklisted(metaitem):
    """ Check that the key of a meta item (extrakey, extravalue) does not
    match at least one of the blacklist pattern
    """
    metakey = metaitem[0]
    for pattern in METABLACKLIST:
        if pattern.match(metakey):
            return False

    return True

def _prepare_hunk(hunk):
    """Drop all information but the username and patch"""
    cleanunk = []
    for line in hunk.splitlines():
        if line.startswith(b'# User') or not line.startswith(b'#'):
            if line.startswith(b'@@'):
                line = b'@@\n'
            cleanunk.append(line)
    return cleanunk

def _getdifflines(iterdiff):
    """return a cleaned up lines"""
    try:
        lines = next(iterdiff)
    except StopIteration:
        return None
    return _prepare_hunk(lines)

def _getobsfate(successorssets):
    """ Compute a changeset obsolescence fate based on his successorssets.
    Successors can be the tipmost ones or the immediate ones.
    Returns one fate in the following list:
    - pruned
    - diverged
    - superseed
    - superseed_split
    """

    if len(successorssets) == 0:
        # The commit has been pruned
        return b'pruned'
    elif len(successorssets) > 1:
        return b'diverged'
    else:
        # No divergence, only one set of successors
        successors = successorssets[0]

        if len(successors) == 1:
            return b'superseed'
        else:
            return b'superseed_split'

def _getobsfateandsuccs(repo, revnode, successorssets=None):
    """ Return a tuple containing:
    - the reason a revision is obsolete (diverged, pruned or superseed)
    - the list of successors short node if the revision is neither pruned
    or has diverged
    """
    if successorssets is None:
        successorssets = obsutil.successorssets(repo, revnode)

    fate = _getobsfate(successorssets)

    # Apply node.short if we have no divergence
    if len(successorssets) == 1:
        successors = [nodemod.short(node_id) for node_id in successorssets[0]]
    else:
        successors = []
        for succset in successorssets:
            successors.append([nodemod.short(node_id) for node_id in succset])

    return (fate, successors)

def _successorsetdates(successorset, markers):
    """returns the max date and the min date of the markers list
    """

    if not markers:
        return {}

    dates = [m[4] for m in markers]

    return {
        b'min_date': min(dates),
        b'max_date': max(dates)
    }

def _successorsetusers(successorset, markers):
    """ Returns a sorted list of markers users without duplicates
    """
    if not markers:
        return {}

    # Check that user is present in meta
    markersmeta = [dict(m[3]) for m in markers]
    users = set(meta.get(b'user') for meta in markersmeta if meta.get(b'user'))

    return {b'users': sorted(users)}

VERBMAPPING = {
    DESCCHANGED: b"reworded",
    METACHANGED: b"meta-changed",
    USERCHANGED: b"reauthored",
    DATECHANGED: b"date-changed",
    BRANCHCHANGED: b"branch-changed",
    PARENTCHANGED: b"rebased",
    DIFFCHANGED: b"amended"
}

def _successorsetverb(successorset, markers):
    """ Return the verb summarizing the successorset
    """
    verb = None
    if not successorset:
        verb = b'pruned'
    elif len(successorset) == 1:
        # Check for effect flag

        metadata = [dict(marker[3]) for marker in markers]
        ef1 = [data.get(b'ef1') for data in metadata]

        if all(ef1):
            combined = 0
            for ef in ef1:
                combined |= int(ef)

            # Combined will be in VERBMAPPING only of one bit is set
            if combined in VERBMAPPING:
                verb = VERBMAPPING[combined]

        if verb is None:
            verb = b'rewritten'
    else:
        verb = b'split'
    return {b'verb': verb}

# Use a more advanced version of obsfateverb that uses effect-flag
if util.safehasattr(obsutil, 'obsfateverb'):

    @eh.wrapfunction(obsutil, 'obsfateverb')
    def obsfateverb(orig, *args, **kwargs):
        return _successorsetverb(*args, **kwargs)[b'verb']

# Hijack callers of successorsetverb
elif util.safehasattr(obsutil, 'obsfateprinter'):

    @eh.wrapfunction(obsutil, 'obsfateprinter')
    def obsfateprinter(orig, successors, markers, ui):

        def closure(successors):
            return _successorsetverb(successors, markers)[b'verb']

        if not util.safehasattr(obsutil, 'successorsetverb'):
            return orig(successors, markers, ui)

        # Save the old value
        old = obsutil.successorsetverb

        try:
            # Replace by own
            obsutil.successorsetverb = closure

            # Call the orig
            result = orig(successors, markers, ui)

            # And return result
            return result
        finally:
            # Replace the old one
            obsutil.successorsetverb = old

FORMATSSETSFUNCTIONS = [
    _successorsetdates,
    _successorsetusers,
    _successorsetverb
]

def successorsetallmarkers(successorset, pathscache):
    """compute all successors of a successorset.

    pathscache must contains all successors starting from selected nodes
    or revision. This way, iterating on each successor, we can take all
    precursors and have the subgraph of all obsmarkers between roots to
    successors.
    """

    markers = set()
    seen = set()

    for successor in successorset:
        stack = [successor]

        while stack:
            element = stack.pop()
            seen.add(element)
            for prec, mark in pathscache.get(element, []):
                if prec not in seen:
                    # Process element precursors
                    stack.append(prec)

                if mark not in markers:
                    markers.add(mark)

    return markers

def preparesuccessorset(successorset, rawmarkers):
    """ For a successor set, get all related markers, compute the set of user,
    the min date and the max date
    """
    hex = nodemod.hex

    successorset = [hex(n) for n in successorset]

    # hex the binary nodes in the markers
    markers = []
    for m in rawmarkers:
        hexprec = hex(m[0])
        hexsucs = tuple(hex(n) for n in m[1])
        hexparents = None
        if m[5] is not None:
            hexparents = tuple(hex(n) for n in m[5])
        newmarker = (hexprec, hexsucs) + m[2:5] + (hexparents,) + m[6:]
        markers.append(newmarker)

    # Format basic data
    data = {
        b"successors": sorted(successorset),
        b"markers": sorted(markers)
    }

    # Call an extensible list of functions to override or add new data
    for function in FORMATSSETSFUNCTIONS:
        data.update(function(successorset, markers))

    return data
