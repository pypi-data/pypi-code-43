# Copyright 2011 Peter Arrenbrecht <peter.arrenbrecht@gmail.com>
#                Logilab SA        <contact@logilab.fr>
#                Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Patrick Mezard <patrick@mezard.eu>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""evolve templates
"""

from . import (
    error,
    exthelper,
    obshistory
)

from mercurial import (
    templatekw,
    util
)

eh = exthelper.exthelper()

### template keywords

if util.safehasattr(templatekw, 'compatlist'):
    @eh.templatekeyword(b'instabilities', requires=set([b'ctx', b'templ']))
    def showinstabilities(context, mapping):
        """List of strings. Evolution instabilities affecting the changeset
        (zero or more of "orphan", "content-divergent" or "phase-divergent")."""
        ctx = context.resource(mapping, b'ctx')
        return templatekw.compatlist(context, mapping, b'instability',
                                     ctx.instabilities(),
                                     plural=b'instabilities')

    @eh.templatekeyword(b'troubles', requires=set([b'ctx', b'templ']))
    def showtroubles(context, mapping):   # legacy name for instabilities
        ctx = context.resource(mapping, b'ctx')
        return templatekw.compatlist(context, mapping, b'trouble',
                                     ctx.instabilities(), plural=b'troubles')
else:
    # older template API in hg < 4.6
    @eh.templatekeyword(b'instabilities')
    def showinstabilities(**args):
        """List of strings. Evolution instabilities affecting the changeset
        (zero or more of "orphan", "content-divergent" or "phase-divergent")."""
        ctx = args[b'ctx']
        return templatekw.showlist(b'instability', ctx.instabilities(), args,
                                   plural=b'instabilities')

    @eh.templatekeyword(b'troubles')
    def showtroubles(**args):
        ctx = args[b'ctx']
        return templatekw.showlist(b'trouble', ctx.instabilities(), args,
                                   plural=b'troubles')

_sp = templatekw.showpredecessors
if util.safehasattr(_sp, '_requires'):
    def showprecursors(context, mapping):
        return _sp(context, mapping)
    showprecursors.__doc__ = _sp._origdoc
    _tk = templatekw.templatekeyword(b"precursors", requires=_sp._requires)
    _tk(showprecursors)
else:
    templatekw.keywords[b"precursors"] = _sp


def closestsuccessors(repo, nodeid):
    """ returns the closest visible successors sets instead.
    """
    return directsuccessorssets(repo, nodeid)

_ss = templatekw.showsuccessorssets
if util.safehasattr(_ss, '_requires'):
    def showsuccessors(context, mapping):
        return _ss(context, mapping)
    showsuccessors.__doc__ = _ss._origdoc
    _tk = templatekw.templatekeyword(b"successors", requires=_ss._requires)
    _tk(showsuccessors)
else:
    templatekw.keywords[b"successors"] = _ss

def _getusername(ui):
    """the default username in the config or None"""
    try:
        return ui.username()
    except error.Abort: # no easy way to avoid ui raising Abort here :-/
        return None

def obsfatedefaulttempl(ui):
    """ Returns a dict with the default templates for obs fate
    """
    # Prepare templates
    verbtempl = b'{verb}'
    usertempl = b'{if(users, " by {join(users, ", ")}")}'
    succtempl = b'{if(successors, " as ")}{successors}' # Bypass if limitation
    datetempleq = b' (at {min_date|isodate})'
    datetemplnoteq = b' (between {min_date|isodate} and {max_date|isodate})'
    datetempl = b'{if(max_date, "{ifeq(min_date, max_date, "%s", "%s")}")}' % (datetempleq, datetemplnoteq)

    optionalusertempl = usertempl
    username = _getusername(ui)
    if username is not None:
        optionalusertempl = (b'{ifeq(join(users, "\0"), "%s", "", "%s")}'
                             % (username, usertempl))

    # Assemble them
    return {
        b'obsfate_quiet': verbtempl + succtempl,
        b'obsfate': verbtempl + succtempl + optionalusertempl,
        b'obsfate_verbose': verbtempl + succtempl + usertempl + datetempl,
    }

def obsfatedata(repo, ctx):
    """compute the raw data needed for computing obsfate
    Returns a list of dict
    """
    if not ctx.obsolete():
        return None

    successorssets, pathcache = closestsuccessors(repo, ctx.node())

    # closestsuccessors returns an empty list for pruned revisions, remap it
    # into a list containing en empty list for future processing
    if successorssets == []:
        successorssets = [[]]

    succsmap = repo.obsstore.successors
    fullsuccessorsets = [] # successor set + markers
    for sset in successorssets:
        if sset:
            markers = obshistory.successorsetallmarkers(sset, pathcache)
            fullsuccessorsets.append((sset, markers))
        else:
            # XXX we do not catch all prune markers (eg rewritten then pruned)
            # (fix me later)
            foundany = False
            for mark in succsmap.get(ctx.node(), ()):
                if not mark[1]:
                    foundany = True
                    fullsuccessorsets.append((sset, [mark]))
            if not foundany:
                fullsuccessorsets.append(([], []))

    values = []
    for sset, rawmarkers in fullsuccessorsets:
        raw = obshistory.preparesuccessorset(sset, rawmarkers)
        values.append(raw)

    return values

def obsfatelineprinter(obsfateline, ui):
    quiet = ui.quiet
    verbose = ui.verbose
    normal = not verbose and not quiet

    # Build the line step by step
    line = []

    # Verb
    line.append(obsfateline[b'verb'])

    # Successors
    successors = obsfateline[b"successors"]

    if successors:
        fmtsuccessors = map(lambda s: s[:12], successors)
        line.append(b" as %s" % b", ".join(fmtsuccessors))

    # Users
    if (verbose or normal) and b'users' in obsfateline:
        users = obsfateline[b'users']

        if not verbose:
            # If current user is the only user, do not show anything if not in
            # verbose mode
            username = _getusername(ui)
            if len(users) == 1 and users[0] == username:
                users = None

        if users:
            line.append(b" by %s" % b", ".join(users))

    # Date
    if verbose:
        min_date = obsfateline[b'min_date']
        max_date = obsfateline[b'max_date']

        if min_date == max_date:
            fmtmin_date = util.datestr(min_date, b'%Y-%m-%d %H:%M %1%2')
            line.append(b" (at %s)" % fmtmin_date)
        else:
            fmtmin_date = util.datestr(min_date, b'%Y-%m-%d %H:%M %1%2')
            fmtmax_date = util.datestr(max_date, b'%Y-%m-%d %H:%M %1%2')
            line.append(b" (between %s and %s)" % (fmtmin_date, fmtmax_date))

    return b"".join(line)

def obsfateprinter(obsfate, ui, prefix=b""):
    lines = []
    for raw in obsfate:
        lines.append(obsfatelineprinter(raw, ui))

    if prefix:
        lines = [prefix + line for line in lines]

    return b"\n".join(lines)

if not util.safehasattr(templatekw, 'obsfateverb'): # <= hg-4.5
    @eh.templatekeyword(b"obsfatedata")
    def showobsfatedata(repo, ctx, **args):
        # Get the needed obsfate data
        values = obsfatedata(repo, ctx)

        if values is None:
            return templatekw.showlist(b"obsfatedata", [], args)

        return _showobsfatedata(repo, ctx, values, **args)

def _showobsfatedata(repo, ctx, values, **args):

    # Format each successorset successors list
    for raw in values:
        # As we can't do something like
        # "{join(map(nodeshort, successors), ', '}" in template, manually
        # create a correct textual representation
        gen = b', '.join(n[:12] for n in raw[b'successors'])

        makemap = lambda x: {b'successor': x}
        joinfmt = lambda d: b"%s" % d[b'successor']
        raw[b'successors'] = templatekw._hybrid(gen, raw[b'successors'], makemap,
                                                joinfmt)

    # And then format them
    # Insert default obsfate templates
    args[b'templ'].cache.update(obsfatedefaulttempl(repo.ui))

    if repo.ui.quiet:
        name = b"obsfate_quiet"
    elif repo.ui.verbose:
        name = b"obsfate_verbose"
    elif repo.ui.debugflag:
        name = b"obsfate_debug"
    else:
        name = b"obsfate"

    # Format a single value
    def fmt(d):
        nargs = args.copy()
        nargs.update(d[name])
        templ = args[b'templ']
        # HG 4.6
        if hasattr(templ, "generate"):
            return templ.generate(name, nargs)
        else:
            return args[b'templ'](name, **nargs)

    # Generate a good enough string representation using templater
    gen = []
    for d in values:
        chunk = fmt({name: d})
        chunkstr = []

        # Empty the generator
        try:
            while True:
                chunkstr.append(next(chunk))
        except StopIteration:
            pass

        gen.append(b"".join(chunkstr))
    gen = b"; ".join(gen)

    return templatekw._hybrid(gen, values, lambda x: {name: x}, fmt)

# copy from mercurial.obsolete with a small change to stop at first known changeset.

def directsuccessorssets(repo, initialnode, cache=None):
    """return set of all direct successors of initial nodes
    """

    succmarkers = repo.obsstore.successors

    # Stack of nodes we search successors sets for
    toproceed = [initialnode]
    # set version of above list for fast loop detection
    # element added to "toproceed" must be added here
    stackedset = set(toproceed)

    pathscache = {}

    if cache is None:
        cache = {}
    while toproceed:
        current = toproceed[-1]
        if current in cache:
            stackedset.remove(toproceed.pop())
        elif current != initialnode and current in repo:
            # We have a valid direct successors.
            cache[current] = [(current,)]
        elif current not in succmarkers:
            if current in repo:
                # We have a valid last successors.
                cache[current] = [(current,)]
            else:
                # Final obsolete version is unknown locally.
                # Do not count that as a valid successors
                cache[current] = []
        else:
            for mark in sorted(succmarkers[current]):
                for suc in mark[1]:
                    if suc not in cache:
                        if suc in stackedset:
                            # cycle breaking
                            cache[suc] = []
                        else:
                            # case (3) If we have not computed successors sets
                            # of one of those successors we add it to the
                            # `toproceed` stack and stop all work for this
                            # iteration.
                            pathscache.setdefault(suc, []).append((current, mark))
                            toproceed.append(suc)
                            stackedset.add(suc)
                            break
                else:
                    continue
                break
            else:
                succssets = []
                for mark in sorted(succmarkers[current]):
                    # successors sets contributed by this marker
                    markss = [[]]
                    for suc in mark[1]:
                        # cardinal product with previous successors
                        productresult = []
                        for prefix in markss:
                            for suffix in cache[suc]:
                                newss = list(prefix)
                                for part in suffix:
                                    # do not duplicated entry in successors set
                                    # first entry wins.
                                    if part not in newss:
                                        newss.append(part)
                                productresult.append(newss)
                        markss = productresult
                    succssets.extend(markss)
                # remove duplicated and subset
                seen = []
                final = []
                candidate = sorted(((set(s), s) for s in succssets if s),
                                   key=lambda x: len(x[1]), reverse=True)
                for setversion, listversion in candidate:
                    for seenset in seen:
                        if setversion.issubset(seenset):
                            break
                    else:
                        final.append(listversion)
                        seen.append(setversion)
                final.reverse() # put small successors set first
                cache[current] = final

    return cache[initialnode], pathscache
