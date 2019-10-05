# Copyright 2011 Peter Arrenbrecht <peter.arrenbrecht@gmail.com>
#                Logilab SA        <contact@logilab.fr>
#                Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Patrick Mezard <patrick@mezard.eu>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

"""logic related to hg evolve command"""

import collections
import re

from mercurial import (
    bookmarks as bookmarksmod,
    cmdutil,
    commands,
    context,
    copies,
    error,
    encoding,
    hg,
    merge,
    mergeutil,
    node as nodemod,
    obsolete,
    obsutil,
    phases,
    pycompat,
    repair,
    scmutil,
    simplemerge,
    util,
)

from mercurial.i18n import _

from . import (
    cmdrewrite,
    compat,
    exthelper,
    rewriteutil,
    state,
    utility,
)

TROUBLES = compat.TROUBLES
shorttemplate = utility.shorttemplate
stacktemplate = utility.stacktemplate
_bookmarksupdater = rewriteutil.bookmarksupdater
sha1re = re.compile(br'\b[0-9a-f]{6,40}\b')

eh = exthelper.exthelper()
mergetoolopts = commands.mergetoolopts

abortmessage = _(b"see `hg help evolve.interrupted`\n")

def _solveone(ui, repo, ctx, evolvestate, dryrun, confirm,
              progresscb, category, lastsolved=None, stacktmplt=False):
    """Resolve the troubles affecting one revision

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    tr = repo.currenttransaction()
    assert tr is not None
    displayer = None
    if stacktmplt:
        displayer = compat.changesetdisplayer(ui, repo,
                                              {b'template': stacktemplate})
    else:
        displayer = compat.changesetdisplayer(ui, repo,
                                              {b'template': shorttemplate})
    if b'orphan' == category:
        result = _solveunstable(ui, repo, ctx, evolvestate, displayer,
                                dryrun, confirm, progresscb,
                                lastsolved=lastsolved)
    elif b'phasedivergent' == category:
        result = _solvephasedivergence(ui, repo, ctx, evolvestate,
                                       displayer, dryrun, confirm,
                                       progresscb)
    elif b'contentdivergent' == category:
        result = _solvedivergent(ui, repo, ctx, evolvestate, displayer,
                                 dryrun, confirm, progresscb)
    else:
        assert False, b"unknown trouble category: %s" % (category)
    return result

def _solveunstable(ui, repo, orig, evolvestate, displayer, dryrun=False,
                   confirm=False, progresscb=None, lastsolved=None):
    """ Tries to stabilize the changeset orig which is orphan.

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    pctx = orig.p1()
    keepbranch = orig.p1().branch() != orig.branch()
    if len(orig.parents()) == 2:
        p1obs = orig.p1().obsolete()
        p2obs = orig.p2().obsolete()
        if not p1obs and p2obs:
            pctx = orig.p2()  # second parent is obsolete ?
            keepbranch = orig.p2().branch() != orig.branch()
        elif not p2obs and p1obs:
            pass
        else:
            # store that we are resolving an orphan merge with both parents
            # obsolete and proceed with first parent
            evolvestate[b'orphanmerge'] = True
            # we should process the second parent first, so that in case of
            # no-conflicts the first parent is processed later and preserved as
            # first parent
            pctx = orig.p2()
            keepbranch = orig.p2().branch() != orig.branch()

    if not pctx.obsolete():
        ui.warn(_(b"cannot solve instability of %s, skipping\n") % orig)
        return (False, b".")
    obs = pctx
    newer = obsutil.successorssets(repo, obs.node())
    # search of a parent which is not killed, but also isn't the orig
    while not newer or newer == [()] or newer[0][0] == orig.node():
        ui.debug(b"stabilize target %s is plain dead,"
                 b" trying to stabilize on its parent\n" %
                 obs)
        obs = obs.parents()[0]
        newer = obsutil.successorssets(repo, obs.node())
    if len(newer) > 1:
        msg = _(b"skipping %s: divergent rewriting. can't choose "
                b"destination\n") % obs
        ui.write_err(msg)
        return (False, b".")
    targets = newer[0]
    assert targets
    if len(targets) > 1:
        # split target, figure out which one to pick, are they all in line?
        targetrevs = [repo[r].rev() for r in targets]
        roots = repo.revs(b'roots(%ld)', targetrevs)
        heads = repo.revs(b'heads(%ld)', targetrevs)
        if len(roots) > 1 or len(heads) > 1:
            cheader = _(b"ancestor '%s' split over multiple topological"
                        b" branches.\nchoose an evolve destination:") % orig
            selectedrev = utility.revselectionprompt(ui, repo, list(heads),
                                                     cheader)
            if selectedrev is None:
                msg = _(b"could not solve instability, "
                        b"ambiguous destination: "
                        b"parent split across two branches\n")
                ui.write_err(msg)
                return (False, b".")
            target = repo[selectedrev]
        else:
            target = repo[heads.first()]
    else:
        target = targets[0]
    target = repo[target]
    if not ui.quiet or confirm:
        repo.ui.write(_(b'move:'), label=b'evolve.operation')
        displayer.show(orig)
        if lastsolved is None or target != repo[lastsolved]:
            repo.ui.write(_(b'atop:'))
            displayer.show(target)
    if confirm and ui.prompt(b'perform evolve? [Ny]', b'n') != b'y':
        raise error.Abort(_(b'evolve aborted by user'))
    todo = b'hg rebase -r %s -d %s\n' % (orig, target)
    if dryrun:
        if progresscb:
            progresscb()
        repo.ui.write(todo)
        return (False, b".")
    else:
        repo.ui.note(todo)
        if progresscb:
            progresscb()
        with state.saver(evolvestate, {b'current': orig.node()}):
            newid = relocate(repo, orig, target, evolvestate, pctx,
                             keepbranch, b'orphan')
            return (True, newid)

def _solvephasedivergence(ui, repo, bumped, evolvestate, displayer,
                          dryrun=False, confirm=False, progresscb=None):
    """Stabilize a phase divergent changeset

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    repo = repo.unfiltered()
    bumped = repo[bumped.rev()]
    # For now we deny bumped merge
    if len(bumped.parents()) > 1:
        msg = _(b'skipping %s : we do not handle merge yet\n') % bumped
        ui.write_err(msg)
        return (False, b".")
    prec = next(repo.set(b'last(allpredecessors(%d) and public())', bumped.rev()))
    # For now we deny target merge
    if len(prec.parents()) > 1:
        msg = _(b'skipping: %s: public version is a merge, '
                b'this is not handled yet\n') % prec
        ui.write_err(msg)
        return (False, b".")

    if not ui.quiet or confirm:
        repo.ui.write(_(b'recreate:'), label=b'evolve.operation')
        displayer.show(bumped)
        repo.ui.write(_(b'atop:'))
        displayer.show(prec)
    if confirm and ui.prompt(_(b'perform evolve? [Ny]'), b'n') != b'y':
        raise error.Abort(_(b'evolve aborted by user'))
    if dryrun:
        todo = b'hg rebase --rev %s --dest %s;\n' % (bumped, prec.p1())
        repo.ui.write(todo)
        repo.ui.write((b'hg update %s;\n' % prec))
        repo.ui.write((b'hg revert --all --rev %s;\n' % bumped))
        repo.ui.write((b'hg commit --msg "%s update to %s"\n' %
                       (TROUBLES['PHASEDIVERGENT'], bumped)))
        return (False, b".")
    if progresscb:
        progresscb()

    # Checking for whether the phase-divergent changeset has common parents as
    # it's precursors. Phase-divergent changeset and precursor having different
    # parents is a result of when the changeset is rebased, picked, histedit or
    # evolved or any other operation which can change parent. In such cases,
    # when parents are not same, we first rebase the divergent changeset onto
    # parent or precursor and then perform later steps
    if not list(repo.set(b'parents(%d) and parents(%d)', bumped.rev(), prec.rev())):
        # Need to rebase the changeset at the right place
        repo.ui.status(
            _(b'rebasing to destination parent: %s\n') % prec.p1())
        with state.saver(evolvestate, {b'current': bumped.hex(),
                                       b'precursor': prec.hex()}):
            newnode = relocate(repo, bumped, prec.p1(), evolvestate,
                               category=b'phasedivergent')
            if newnode is not None:
                new = repo[newnode]
                obsolete.createmarkers(repo, [(bumped, (new,))],
                                       operation=b'evolve')
                bumped = new
                evolvestate[b'temprevs'].append(newnode)

    return _resolvephasedivergent(ui, repo, prec, bumped)

def _resolvephasedivergent(ui, repo, prec, bumped):
    """final step of a phase divergence resolution

    This will create a new changesets (or nothing when applicable), the two
    changesets needs to be on the same parents.
    """
    tr = repo.currenttransaction()
    assert tr is not None

    cl = repo.changelog
    prec_parent = cl.parentrevs(prec.rev())
    bump_parent = cl.parentrevs(bumped.rev())
    assert prec_parent == bump_parent, (prec_parent, bump_parent)

    bmupdate = _bookmarksupdater(repo, bumped.node(), tr)
    newid = None
    replacementnode = None

    # Create the new commit context. This is done by applying the changes from
    # the precursor to the bumped node onto the precursor. This is effectively
    # like reverting to the bumped node.
    wctx = context.overlayworkingctx(repo)
    wctx.setbase(prec)
    merge.update(repo, bumped.node(), ancestor=prec, mergeancestor=True,
                 branchmerge=True, force=False, wc=wctx)
    if not wctx.isempty():
        text = b'%s update to %s:\n\n' % (TROUBLES['PHASEDIVERGENT'], prec)
        text += bumped.description()
        memctx = wctx.tomemctx(text,
                               parents=(prec.node(), nodemod.nullid),
                               date=bumped.date(),
                               extra=bumped.extra(),
                               user=bumped.user())
        newid = repo.commitctx(memctx)
        replacementnode = newid
    if newid is None:
        repo.ui.status(_(b'no changes to commit\n'))
        obsolete.createmarkers(repo, [(bumped, ())], operation=b'evolve')
        newid = prec.node()
    else:
        repo.ui.status(_(b'committed as %s\n') % nodemod.short(newid))
        phases.retractboundary(repo, tr, bumped.phase(), [newid])
        obsolete.createmarkers(repo, [(bumped, (repo[newid],))],
                               flag=obsolete.bumpedfix, operation=b'evolve')
    bmupdate(newid)
    # reroute the working copy parent to the new changeset
    with repo.dirstate.parentchange():
        repo.dirstate.setparents(newid, nodemod.nullid)
    return (True, replacementnode)

def _solvedivergent(ui, repo, divergent, evolvestate, displayer, dryrun=False,
                    confirm=False, progresscb=None):
    """tries to solve content-divergence of a changeset

    returns a tuple (bool, newnode) where,
        bool: a boolean value indicating whether the instability was solved
        newnode: if bool is True, then the newnode of the resultant commit
                 formed. newnode can be node, when resolution led to no new
                 commit. If bool is False, this is ".".
    """
    repo = repo.unfiltered()
    divergent = repo[divergent.rev()]
    evolvestate[b'divergent'] = divergent.node()
    evolvestate[b'orig-divergent'] = divergent.node()
    # sometimes we will relocate a node in case of different parents and we can
    # encounter conflicts after relocation is done while solving
    # content-divergence and if the user calls `hg evolve --stop`, we need to
    # strip that relocated commit. However if `--all` is passed, we need to
    # reset this value for each content-divergence resolution which we are doing
    # below.
    evolvestate[b'relocated'] = None
    evolvestate[b'relocating'] = False
    # in case or relocation we get a new other node, we need to store the old
    # other for purposes like `--abort` or `--stop`
    evolvestate[b'old-other'] = None
    base, others = divergentdata(divergent)

    # we don't handle split in content-divergence yet
    if len(others) > 1:
        othersstr = b"[%s]" % (b','.join([bytes(i) for i in others]))
        msg = _(b"skipping %s: %s with a changeset that got split"
                b" into multiple ones:\n"
                b"|[%s]\n"
                b"| This is not handled by automatic evolution yet\n"
                b"| You have to fallback to manual handling with commands "
                b"such as:\n"
                b"| - hg touch -D\n"
                b"| - hg prune\n"
                b"| \n"
                b"| You should contact your local evolution Guru for help.\n"
                ) % (divergent, TROUBLES['CONTENTDIVERGENT'], othersstr)
        ui.write_err(msg)
        return (False, b".")
    other = others[0]
    evolvestate[b'other-divergent'] = other.node()
    evolvestate[b'base'] = base.node()

    def swapnodes(div, other):
        div, other = other, div
        evolvestate[b'divergent'] = div.node()
        evolvestate[b'other-divergent'] = other.node()
        return div, other
    # haspubdiv: to keep track if we are solving public content-divergence
    haspubdiv = False
    if not (divergent.mutable() and other.mutable()):
        haspubdiv = True
        # for simplicity, we keep public one to local side while merging
        # (as divergent is kept at local side, pinning public -> divergent)
        if divergent.mutable():
            publicdiv = other
            divergent, other = swapnodes(divergent, other)
        else:
            publicdiv = divergent
        evolvestate[b'public-divergent'] = publicdiv.node()
    # we don't handle merge content-divergent changesets yet
    if len(other.parents()) > 1:
        msg = _(b"skipping %s: %s changeset can't be "
                b"a merge (yet)\n") % (divergent, TROUBLES['CONTENTDIVERGENT'])
        ui.write_err(msg)
        hint = _(b"You have to fallback to solving this by hand...\n"
                 b"| This probably means redoing the merge and using \n"
                 b"| `hg prune` to kill older version.\n")
        ui.write_err(hint)
        return (False, b".")

    otherp1 = other.p1().rev()
    divp1 = divergent.p1().rev()

    # finding single successors of otherp1 and divp1
    try:
        otherp1 = utility._singlesuccessor(repo, other.p1())
    except utility.MultipleSuccessorsError:
        pass

    try:
        divp1 = utility._singlesuccessor(repo, divergent.p1())
    except utility.MultipleSuccessorsError:
        pass

    # the changeset on which resolution changeset will be based on
    resolutionparent = repo[divp1].node()

    gca = repo.revs(b"ancestor(%d, %d)" % (otherp1, divp1))
    # divonly: non-obsolete csets which are topological ancestor of "divergent"
    # but not "other"
    divonly = repo.revs(b"only(%d, %d) - obsolete()" % (divergent.rev(),
                                                        other.rev()))
    # otheronly: non-obsolete csets which are topological ancestor of "other"
    # but not "div"
    otheronly = repo.revs(b"only(%d, %d) - obsolete()" % (other.rev(),
                                                          divergent.rev()))
    # make it exclusive set
    divonly = set(divonly) - {divergent.rev()}
    otheronly = set(otheronly) - {other.rev()}
    # is relocation of one of the changeset required
    relocatereq = False

    # testing how both the divergent changesets are arranged, there can be 4
    # possible cases here:
    #
    # 1) both have the same parents
    # 2) both have different parents but greatest common anscestor of them is
    #    parent of one of them
    # 3) both have different parents and gca is not parent of any of them
    # 4) one of them is parent of other
    #
    # we are handling 1) very good now.
    # for 2) we will relocate one which is behind to the parent of ahead one and
    # then solve the content-divergence the way we solve 1)
    # for 3) and 4), we still have to decide
    if otherp1 in gca and divp1 in gca:
        if otherp1 == other.p1().rev() and divp1 == divergent.p1().rev():
            # both are on the same parents
            pass
        else:
            # both are not on the same parent but have same parents's succs.
            if otheronly and divonly:
                # case: we have visible csets on both side diverging from
                # tca of "divergent" and "other". We still need to decide what
                # to do in this case
                pass
            if otheronly:
                relocatereq = True
                if not haspubdiv:
                    # can't swap when public divergence, as public can't move
                    divergent, other = swapnodes(divergent, other)
                    resolutionparent = repo[otherp1].node()
            elif divonly:
                relocatereq = True
            else:
                # no extra cset on either side; so not considering relocation
                pass
    elif otherp1 in gca and divp1 not in gca:
        relocatereq = True
        pass
    elif divp1 in gca and otherp1 not in gca:
        relocatereq = True

        # When public branch is behind to the mutable branch, for now we
        # relocate mutable cset to public one's side in every case.
        #
        # This behaviour might be sub optimal when ancestors of mutable
        # cset has changes its relocated descendant rely on.
        #
        # Otherwise, we are going to rebase the "behind" branch up to the new
        # brancmap level.
        if not haspubdiv:
            divergent, other = swapnodes(divergent, other)
            resolutionparent = divergent.p1().node()
    else:
        msg = _(b"skipping %s: have a different parent than %s "
                b"(not handled yet)\n") % (divergent, other)
        hint = _(b"| %(d)s, %(o)s are not based on the same changeset.\n"
                 b"| With the current state of its implementation, \n"
                 b"| evolve does not work in that case.\n"
                 b"| rebase one of them next to the other and run \n"
                 b"| this command again.\n"
                 b"| - either: hg rebase --dest 'p1(%(d)s)' -r %(o)s\n"
                 b"| - or:     hg rebase --dest 'p1(%(o)s)' -r %(d)s\n"
                 ) % {b'd': divergent, b'o': other}
        ui.write_err(msg)
        ui.write_err(hint)
        return (False, b".")

    if not ui.quiet or confirm:
        ui.write(_(b'merge:'), label=b'evolve.operation')
        displayer.show(divergent)
        ui.write(_(b'with: '))
        displayer.show(other)
        ui.write(_(b'base: '))
        displayer.show(base)
    if confirm and ui.prompt(_(b'perform evolve? [Ny]'), b'n') != b'y':
        raise error.Abort(_(b'evolve aborted by user'))
    if dryrun:
        ui.write((b'hg update -c %s &&\n' % divergent))
        ui.write((b'hg merge %s &&\n' % other))
        ui.write((b'hg commit -m "auto merge resolving conflict between '
                  b'%s and %s"&&\n' % (divergent, other)))
        ui.write((b'hg up -C %s &&\n' % base))
        ui.write((b'hg revert --all --rev tip &&\n'))
        ui.write((b'hg commit -m "`hg log -r %s --template={desc}`";\n'
                  % divergent))
        return (False, b".")

    # Sometimes we already have the other cset where we want it
    if relocatereq and other == divergent.p1():
        relocatereq = False

    evolvestate[b'resolutionparent'] = resolutionparent
    # relocate the other divergent if required
    if relocatereq:
        # relocating will help us understand during the time of conflicts that
        # whether conflicts occur at reloacting or they occured at merging
        # content divergent changesets
        evolvestate[b'relocating'] = True
        ui.status(_(b'rebasing "other" content-divergent changeset %s on'
                    b' %s\n' % (other, divergent.p1())))
        with state.saver(evolvestate, {b'current': other.node()}):
            newother = relocate(repo, other, divergent.p1(), evolvestate,
                                keepbranch=True)
        evolvestate[b'old-other'] = other.node()
        other = repo[newother]
        evolvestate[b'relocating'] = False
        evolvestate[b'relocated'] = other.node()
        evolvestate[b'temprevs'].append(other.node())
        evolvestate[b'other-divergent'] = other.node()

    _mergecontentdivergents(repo, progresscb, divergent, other, base,
                            evolvestate)
    res, newnode = _completecontentdivergent(ui, repo, progresscb, divergent,
                                             other, base, evolvestate)
    if not haspubdiv:
        return (res, newnode)
    else:
        # we have content-divergence with a public cset:
        # after performing content divergence resolution steps, possbile cases:
        # 1) merging results in a new node:
        #       we need to perform phase divergence resolution
        # 2) merging leads to same content as public cset:
        #       divergence has been resolved by creating markers
        if not res:
            # resolution was not successful, return
            return (res, newnode)
        if newnode == publicdiv.node():
            # case 2)
            pubstr = bytes(publicdiv)
            othstr = bytes(other)
            msg = _(b'content divergence resolution between %s '
                    b'(public) and %s has same content as %s, '
                    b'discarding %s\n')
            msg %= (pubstr, othstr, pubstr, othstr)
            repo.ui.status(msg)
            return (res, newnode)
        # case 1)
        prec = publicdiv
        bumped = repo[newnode]
        return _resolvephasedivergent(ui, repo, prec=prec, bumped=bumped)

def _mergecontentdivergents(repo, progresscb, divergent, other, base,
                            evolvestate):
    if divergent not in repo[None].parents():
        repo.ui.note(_(b"updating to \"local\" side of the conflict: %s\n") %
                     divergent.hex()[:12])
        hg.updaterepo(repo, divergent.node(), False)
    # merging the two content-divergent changesets
    repo.ui.note(_(b"merging \"other\" %s changeset '%s'\n") %
                 (TROUBLES['CONTENTDIVERGENT'], other.hex()[:12]))
    if progresscb:
        progresscb()
    with state.saver(evolvestate):
        mergeancestor = repo.changelog.isancestor(divergent.node(),
                                                  other.node())
        stats = merge.update(repo,
                             other.node(),
                             branchmerge=True,
                             force=False,
                             ancestor=base.node(),
                             mergeancestor=mergeancestor)
        hg._showstats(repo, stats)

        # conflicts while merging content-divergent changesets
        if compat.hasconflict(stats):
            hint = _(b"see 'hg help evolve.interrupted'")
            raise error.InterventionRequired(_(b"unresolved merge conflicts"),
                                             hint=hint)

def _completecontentdivergent(ui, repo, progresscb, divergent, other,
                              base, evolvestate):
    """completes the content-divergence resolution"""
    # no conflicts were there in merging content divergent changesets, let's
    # resume resolution
    if progresscb:
        progresscb()
    emtpycommitallowed = repo.ui.backupconfig(b'ui', b'allowemptycommit')
    tr = repo.currenttransaction()
    assert tr is not None
    # whether to store the obsmarker in the evolvestate
    storemarker = False
    resparent = evolvestate[b'resolutionparent']

    # whether we are solving public divergence
    haspubdiv = False
    if evolvestate.get(b'public-divergent'):
        haspubdiv = True
        publicnode = evolvestate[b'public-divergent']
        publicdiv = repo[publicnode]
        othernode = evolvestate[b'other-divergent']
        otherdiv = repo[othernode]

        with repo.dirstate.parentchange():
            repo.dirstate.setparents(publicnode, nodemod.nullid)
            dirstatedance(repo, divergent, publicnode, None)
        # check if node to be committed has changes same as public one
        s = publicdiv.status()
        if not (s.added or s.removed or s.deleted or s.modified):
            # warn user if metadata is being lost
            warnmetadataloss(repo, publicdiv, otherdiv)
            # no changes, create markers to resolve divergence
            obsolete.createmarkers(repo, [(otherdiv, (publicdiv,))],
                                   operation=b'evolve')
            return (True, publicnode)
    try:
        with repo.dirstate.parentchange():
            repo.dirstate.setparents(resparent, nodemod.nullid)

        dirstatedance(repo, divergent, resparent, None)

        # merge the branches
        mergebranches(repo, divergent, other, base)
        # merge the commit messages
        desc = mergecommitmessages(ui, base.description(),
                                   divergent.description(),
                                   other.description())
        user = utility.mergeusers(ui, base, divergent, other)

        # new node if any formed as the replacement
        newnode = None

        mergehook(repo, base, divergent, other)

        newnode = repo.commit(text=desc, user=user)
        if newnode == divergent.node() or newnode is None:
            # no changes
            new = divergent
            storemarker = True
            repo.ui.status(_(b"nothing changed\n"))
            hg.updaterepo(repo, divergent.rev(), False)
        else:
            new = repo[newnode]
            newnode = new.node()
            hg.updaterepo(repo, new.rev(), False)
            if haspubdiv and publicdiv == divergent:
                bypassphase(repo, (divergent, new), operation=b'evolve')
            else:
                obsolete.createmarkers(repo, [(divergent, (new,))],
                                       operation=b'evolve')

        # creating markers and moving phases post-resolution
        if haspubdiv and publicdiv == other:
            bypassphase(repo, (other, new), operation=b'evolve')
        else:
            obsolete.createmarkers(repo, [(other, (new,))], operation=b'evolve')
        if storemarker:
            # storing the marker in the evolvestate
            # we just store the precursors and successor pair for now, we might
            # want to store more data and serialize obsmarker in a better way in
            # future
            evolvestate[b'obsmarkers'].append((other.node(), new.node()))

        phases.retractboundary(repo, tr, other.phase(), [new.node()])
        return (True, newnode)
    finally:
        repo.ui.restoreconfig(emtpycommitallowed)

def warnmetadataloss(repo, local, other):
    """warn the user for the metadata being lost while resolving
    public content-divergence"""

    # needtowarn: aspects where we need to warn user
    needtowarn = [b'branch', b'topic', b'close']
    aspects = set()
    localextra = local.extra()
    otherextra = other.extra()

    for asp in needtowarn:
        otherasp = otherextra.get(asp)
        localasp = localextra.get(asp)
        if otherasp and otherasp != localasp:
            aspects.add(asp)

    if other.description() != local.description():
        aspects.add(b'description')

    if aspects:
        # warn user
        locstr = bytes(local)
        othstr = bytes(other)
        if b'close' in aspects:
            filteredasp = aspects - {b'close'}
            if filteredasp:
                msg = _(b'other divergent changeset %s is a closed branch head '
                        b'and differs from local %s by "%s" only,' %
                        (othstr, locstr, b', '.join(sorted(filteredasp))))
            else:
                msg = _(b'other divergent changeset %s is a closed branch head '
                        b'and has same content as local %s,' % (othstr, locstr))
        else:
            msg = _(b'other divergent changeset %s has same content as local %s'
                    b' and differs by "%s" only,' %
                    (othstr, locstr, b', '.join(sorted(aspects))))
        msg += _(b' discarding %s\n' % othstr)
        repo.ui.warn(msg)

def bypassphase(repo, relation, flag=0, metadata=None, operation=b'evolve'):
    """function to create a single obsmarker relation even for public csets
    where relation should be a single pair (prec, succ)"""

    # prepare metadata
    if metadata is None:
        metadata = {}
    if b'user' not in metadata:
        luser = repo.ui.config(b'devel', b'user.obsmarker') or repo.ui.username()
        metadata[b'user'] = encoding.fromlocal(luser)
    # Operation metadata handling
    useoperation = repo.ui.configbool(b'experimental',
                                      b'evolution.track-operation')
    if useoperation and operation:
        metadata[b'operation'] = operation

    # Effect flag metadata handling
    saveeffectflag = repo.ui.configbool(b'experimental',
                                        b'evolution.effect-flags')
    with repo.transaction(b'add-obsolescence-marker') as tr:
        prec, succ = relation
        nprec = prec.node()
        npare = None
        nsucs = [succ.node()]
        if not nsucs:
            npare = tuple(p.node() for p in prec.parents())
        if nprec in nsucs:
            raise error.Abort(_(b"changeset %s cannot obsolete itself") % prec)

        if saveeffectflag:
            # The effect flag is saved in a versioned field name for
            # future evolution
            try:
                effectflag = obsutil.geteffectflag(prec, (succ,))
            except TypeError:
                # hg <= 4.7
                effectflag = obsutil.geteffectflag((prec, (succ,)))
            metadata[obsutil.EFFECTFLAGFIELD] = b"%d" % effectflag

        # create markers
        repo.obsstore.create(tr, nprec, nsucs, flag, parents=npare,
                             metadata=metadata, ui=repo.ui)
        repo.filteredrevcache.clear()

def dirstatedance(repo, oldparent, newparent, match):
    """utility function to fix the dirstate when we change parents from
    oldparent to newparent with a dirty working directory using
    repo.dirstate.setparents()

    Lets refer oldparent as Pold
               newparent as Pnew

    Now when we are on oldparent with a dirty working directory, there are three
    types of files which we are concerned about. They are files having modified,
    added and removed status.

    Lets refer modified files as Fm
               added files as Fa
               removed files as Fr

    Now, between Pold and Pnew, files can be modified, files can be added, files
    can be removed.

    Lets refer modification of a file between Pold to Pnew as Cm
               addition of a file between Pold to Pnew as Ca
               removal of a file between Pold to Pnew as Cr

    Now let's play combinations and permutations:

    |---------------------------------------------------------------|
    | Type of file |  Changes between |   End status with Pnew as   |
    |   in wdir    |    Pold -> Pnew  |       wdir parent           |
    |--------------|------------------|-----------------------------|
    |              |                  |                             |
    |   Fm         |      Cm          |       Modified or clean     |
    |--------------|------------------|-----------------------------|
    |   Fm         |      Cr          |           Added             |
    |--------------|------------------|-----------------------------|
    |   Fm         |      Ca          |       Not possible (1)      |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Ca          |       Modified or clean     |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Cm          |       Not possible (2)      |
    |--------------|------------------|-----------------------------|
    |   Fa         |      Cr          |       Not possible (2)      |
    |--------------|------------------|-----------------------------|
    |   Fr         |      Cr          | File should be untracked (3)|
    |--------------|------------------|-----------------------------|
    |   Fr         |      Ca          |       Not possible (4)      |
    |--------------|------------------|-----------------------------|
    |   Fr         |      Cm          |           Removed           |
    |--------------|------------------|-----------------------------|

    (1): File is modified in wdir, it means file was present in Pold, so
         addition of that file between Pold to Pnew is not possible

    (2): File was added in wdir, it means file was not present in Pold, so
         deletion or modification of that file from Pold to Pnew is not possible

    (3): File should be dropped from the dirstate, Pnew has it removed, so no
         need to mark that removed again

    (4): File was removed in wdir, it means file was present in Pold, so
         addition of that file between Pold to Pnew is not possible

    """

    # falling back to an existing function, in future we should have logic in
    # this function only
    cmdrewrite._uncommitdirstate(repo, oldparent, match, True)

def mergehook(repo, base, divergent, other):
    """function which extensions can wrap and merge data introduced by them
    while resolving content-divergence"""
    pass

def mergebranches(repo, divergent, other, base):
    """merges the branch information for content-divergent changesets and sets
    the dirstate branch accordingly
    If unable to merge, prompts user to select a branch

    If the branch name is different from the branch of divergent changeset, it
    sets the current branch using repo.dirstate.setbranch()
    """
    divbranch = divergent.branch()
    basebranch = base.branch()
    othbranch = other.branch()
    # content divergent changes were on different branches, ask user to
    # select one
    if divbranch != othbranch:

        if basebranch == othbranch and basebranch != divbranch:
            # we will be amending the divergent changeset so branch will be
            # preserved
            pass
        elif basebranch == divbranch and basebranch != othbranch:
            repo.dirstate.setbranch(othbranch)
        else:
            # all the three branches are different
            index = repo.ui.promptchoice(_(b"content divergent changesets on "
                                           b"different branches.\nchoose branch"
                                           b" for the resolution changeset. (a) "
                                           b"%s or (b) %s or (c) %s? $$ &a $$ &b"
                                           b" $$ &c") %
                                         (basebranch, divbranch, othbranch), 0)

            if index == 0:
                repo.dirstate.setbranch(basebranch)
            elif index == 1:
                pass
            elif index == 2:
                repo.dirstate.setbranch(othbranch)

def mergecommitmessages(ui, basedesc, divdesc, othdesc):
    """merges the commit messages and return the new merged message and whether
    there were conflicts or not while merging the messages"""

    merger = simplemerge.Merge3Text(basedesc, divdesc, othdesc)
    mdesc = []
    kwargs = {}
    kwargs['name_base'] = b'base'
    kwargs['base_marker'] = b'|||||||'
    for line in merger.merge_lines(name_a=b'divergent', name_b=b'other',
                                   **kwargs):
        mdesc.append(line)

    desc = b''.join(mdesc)
    if merger.conflicts:

        prefixes = (b"HG: Conflicts while merging changeset description of"
                    b" content-divergent changesets.\nHG: Resolve conflicts"
                    b" in commit messages to continue.\n\n")

        resolveddesc = ui.edit(prefixes + desc, ui.username(), action=b'desc')
        # make sure we remove the prefixes part from final commit message
        if prefixes in resolveddesc:
            # hack, we should find something better
            resolveddesc = resolveddesc[len(prefixes):]
        desc = resolveddesc

    return desc

def _orderrevs(repo, revs):
    """Compute an ordering to solve instability for the given revs

    revs is a list of unstable revisions.

    Returns the same revisions ordered to solve their instability from the
    bottom to the top of the stack that the stabilization process will produce
    eventually.

    This ensures the minimal number of stabilizations, as we can stabilize each
    revision on its final stabilized destination.
    """
    # Step 1: Build the dependency graph
    dependencies, rdependencies = utility.builddependencies(repo, revs)
    # Step 2: Build the ordering
    # Remove the revisions with no dependency(A) and add them to the ordering.
    # Removing these revisions leads to new revisions with no dependency (the
    # one depending on A) that we can remove from the dependency graph and add
    # to the ordering. We progress in a similar fashion until the ordering is
    # built
    solvablerevs = collections.deque([r for r in sorted(dependencies.keys())
                                      if not dependencies[r]])
    ordering = []
    while solvablerevs:
        rev = solvablerevs.popleft()
        for dependent in rdependencies[rev]:
            dependencies[dependent].remove(rev)
            if not dependencies[dependent]:
                solvablerevs.append(dependent)
        del dependencies[rev]
        ordering.append(rev)

    ordering.extend(sorted(dependencies))
    return ordering

def relocate(repo, orig, dest, evolvestate, pctx=None, keepbranch=False,
             category=None):
    """rewrites the orig rev on dest rev

    returns the node of new commit which is formed
    """
    if orig.rev() == dest.rev():
        msg = _(b'tried to relocate a node on top of itself')
        hint = _(b"This shouldn't happen. If you still need to move changesets, "
                 b"please do so manually with nothing to rebase - working "
                 b"directory parent is also destination")
        raise error.ProgrammingError(msg, hint=hint)

    if pctx is None:
        if len(orig.parents()) == 2:
            msg = _(b"tried to relocate a merge commit without specifying which "
                    b"parent should be moved")
            hint = _(b"Specify the parent by passing in pctx")
            raise error.ProgrammingError(msg, hint)
        pctx = orig.p1()

    commitmsg = orig.description()

    cache = {}
    sha1s = re.findall(sha1re, commitmsg)
    unfi = repo.unfiltered()
    for sha1 in sha1s:
        if util.safehasattr(scmutil, 'resolvehexnodeidprefix'): # > hg-4.6
            fullnode = scmutil.resolvehexnodeidprefix(unfi, sha1)
        else:
            fullnode = unfi.changelog.index.partialmatch(sha1)
        if fullnode is None:
            continue
        ctx = unfi[fullnode]
        if not ctx.obsolete():
            continue

        successors = obsutil.successorssets(repo, ctx.node(), cache)

        # We can't make any assumptions about how to update the hash if the
        # cset in question was split or diverged.
        if len(successors) == 1 and len(successors[0]) == 1:
            newsha1 = nodemod.hex(successors[0][0])
            commitmsg = commitmsg.replace(sha1, newsha1[:len(sha1)])
        else:
            repo.ui.note(_(b'The stale commit message reference to %s could '
                           b'not be updated\n') % sha1)

    tr = repo.currenttransaction()
    assert tr is not None
    r = _evolvemerge(repo, orig, dest, pctx, keepbranch)
    if compat.hasconflict(r): # some conflict
        with repo.dirstate.parentchange():
            repo.setparents(dest.node(), orig.node())
            repo.dirstate.write(tr)
            # fix up dirstate for copies and renames
            copies.duplicatecopies(repo, repo[None], dest.rev(),
                                   orig.p1().rev())
            dirstatedance(repo, dest, orig.node(), None)
        hint = _(b"see 'hg help evolve.interrupted'")
        raise error.InterventionRequired(_(b"unresolved merge conflicts"),
                                         hint=hint)
    nodenew = _relocatecommit(repo, orig, commitmsg)
    _finalizerelocate(repo, orig, dest, nodenew, tr, category, evolvestate)
    return nodenew

def _relocatecommit(repo, orig, commitmsg):
    if commitmsg is None:
        commitmsg = orig.description()
    extra = dict(orig.extra())
    if b'branch' in extra:
        del extra[b'branch']
    extra[b'rebase_source'] = orig.hex()

    backup = repo.ui.backupconfig(b'phases', b'new-commit')
    try:
        targetphase = max(orig.phase(), phases.draft)
        repo.ui.setconfig(b'phases', b'new-commit', targetphase, b'evolve')
        # Commit might fail if unresolved files exist
        nodenew = repo.commit(text=commitmsg, user=orig.user(),
                              date=orig.date(), extra=extra)
    finally:
        repo.ui.restoreconfig(backup)
    return nodenew

def _finalizerelocate(repo, orig, dest, nodenew, tr, category, evolvestate):
    destbookmarks = repo.nodebookmarks(dest.node())
    nodesrc = orig.node()
    oldbookmarks = repo.nodebookmarks(nodesrc)
    bmchanges = []

    if nodenew is not None:
        obsolete.createmarkers(repo, [(repo[nodesrc], (repo[nodenew],))],
                               operation=b'evolve')
        for book in oldbookmarks:
            bmchanges.append((book, nodenew))
            evolvestate[b'bookmarkchanges'].append((book, nodesrc))
    else:
        if category == b'orphan':
            repo.ui.status(_(b"evolution of %d:%s created no changes "
                             b"to commit\n") % (orig.rev(), orig))
        obsolete.createmarkers(repo, [(repo[nodesrc], ())], operation=b'evolve')
        # Behave like rebase, move bookmarks to dest
        for book in oldbookmarks:
            evolvestate[b'bookmarkchanges'].append((book, nodesrc))
            bmchanges.append((book, dest.node()))
    for book in destbookmarks: # restore bookmark that rebase move
        bmchanges.append((book, dest.node()))
    if bmchanges:
        repo._bookmarks.applychanges(repo, tr, bmchanges)

def _evolvemerge(repo, orig, dest, pctx, keepbranch):
    """Used by the evolve function to merge dest on top of pctx.
    return the same tuple as merge.graft"""
    if repo[b'.'].rev() != dest.rev():
        merge.update(repo,
                     dest,
                     branchmerge=False,
                     force=True)
    if repo._activebookmark:
        repo.ui.status(_(b"(leaving bookmark %s)\n") % repo._activebookmark)
    bookmarksmod.deactivate(repo)
    if keepbranch:
        repo.dirstate.setbranch(orig.branch())
    if util.safehasattr(repo, 'currenttopic'):
        # uurrgs
        # there no other topic setter yet
        if not orig.topic() and repo.vfs.exists(b'topic'):
            repo.vfs.unlink(b'topic')
        else:
            with repo.vfs.open(b'topic', b'w') as f:
                f.write(orig.topic())

    return merge.graft(repo, orig, pctx, [b'destination', b'evolving'], True)

instabilities_map = {
    b'contentdivergent': b"content-divergent",
    b'phasedivergent': b"phase-divergent"
}

def _selectrevs(repo, allopt, revopt, anyopt, targetcat):
    """select troubles in repo matching according to given options"""
    revs = set()
    if allopt or revopt:
        revs = repo.revs(b"%s()" % targetcat)
        if revopt:
            revs = scmutil.revrange(repo, revopt) & revs
        elif not anyopt:
            topic = getattr(repo, 'currenttopic', b'')
            if topic:
                revs = repo.revs(b'topic(%s)', topic) & revs
            elif targetcat == b'orphan':
                revs = _aspiringdescendant(repo,
                                           repo.revs(b'(.::) - obsolete()::'))
                revs = set(revs)
        if targetcat == b'contentdivergent':
            # Pick one divergent per group of divergents
            revs = _dedupedivergents(repo, revs)
    elif anyopt:
        revs = repo.revs(b'first(%s())' % (targetcat))
    elif targetcat == b'orphan':
        revs = set(_aspiringchildren(repo, repo.revs(b'(.::) - obsolete()::')))
        if 1 < len(revs):
            msg = b"multiple evolve candidates"
            hint = (_(b"select one of %s with --rev")
                    % b', '.join([bytes(repo[r]) for r in sorted(revs)]))
            raise error.Abort(msg, hint=hint)
    elif instabilities_map.get(targetcat, targetcat) in repo[b'.'].instabilities():
        revs = set([repo[b'.'].rev()])
    return revs

def _dedupedivergents(repo, revs):
    """Dedupe the divergents revs in revs to get one from each group with the
    lowest revision numbers
    """
    repo = repo.unfiltered()
    res = set()
    # To not reevaluate divergents of the same group once one is encountered
    discarded = set()
    for rev in revs:
        if rev in discarded:
            continue
        divergent = repo[rev]
        base, others = divergentdata(divergent)
        othersrevs = [o.rev() for o in others]
        res.add(min([divergent.rev()] + othersrevs))
        discarded.update(othersrevs)
    return res

def divergentdata(ctx):
    """return base, other part of a conflict

    This only return the first one.

    XXX this woobly function won't survive XXX
    """
    repo = ctx._repo.unfiltered()
    for base in repo.set(b'reverse(allpredecessors(%d))', ctx.rev()):
        newer = obsutil.successorssets(ctx._repo, base.node())
        # drop filter and solution including the original ctx
        newer = [n for n in newer if n and ctx.node() not in n]
        if newer:
            return base, tuple(ctx._repo[o] for o in newer[0])
    raise error.Abort(_(b"base of divergent changeset %s not found") % ctx,
                      hint=_(b'this case is not yet handled'))

def _aspiringdescendant(repo, revs):
    """Return a list of changectx which can be stabilized on top of pctx or
    one of its descendants recursively. Empty list if none can be found."""
    target = set(revs)
    result = set(target)
    paths = collections.defaultdict(set)
    for r in repo.revs(b'orphan() - %ld', revs):
        for d in _possibledestination(repo, r):
            paths[d].add(r)

    result = set(target)
    tovisit = list(revs)
    while tovisit:
        base = tovisit.pop()
        for unstable in paths[base]:
            if unstable not in result:
                tovisit.append(unstable)
                result.add(unstable)
    return sorted(result - target)

def _aspiringchildren(repo, revs):
    """Return a list of changectx which can be stabilized on top of pctx or
    one of its descendants. Empty list if none can be found."""
    target = set(revs)
    result = []
    for r in repo.revs(b'orphan() - %ld', revs):
        dest = _possibledestination(repo, r)
        if target & dest:
            result.append(r)
    return result

def _possibledestination(repo, rev):
    """return all changesets that may be a new parent for REV"""
    tonode = repo.changelog.node
    parents = repo.changelog.parentrevs
    torev = repo.changelog.rev
    dest = set()
    tovisit = list(parents(rev))
    while tovisit:
        r = tovisit.pop()
        if r == -1:
            continue
        succsets = obsutil.successorssets(repo, tonode(r))
        if not succsets:
            tovisit.extend(parents(r))
        else:
            # We should probably pick only one destination from split
            # (case where '1 < len(ss)'), This could be the currently tipmost
            # but logic is less clear when result of the split are now on
            # multiple branches.
            for ss in succsets:
                for n in ss:
                    dest.add(torev(n))
    return dest

def _handlenotrouble(ui, repo, allopt, revopt, anyopt, targetcat):
    """Used by the evolve function to display an error message when
    no troubles can be resolved"""
    troublecategories = [b'phasedivergent', b'contentdivergent', b'orphan']
    unselectedcategories = [c for c in troublecategories if c != targetcat]
    msg = None
    hint = None
    retoverride = None

    troubled = {
        b"orphan": repo.revs(b"orphan()"),
        b"contentdivergent": repo.revs(b"contentdivergent()"),
        b"phasedivergent": repo.revs(b"phasedivergent()"),
        b"all": repo.revs(b"unstable()"),
    }

    hintmap = {
        b'phasedivergent': _(b"do you want to use --phase-divergent"),
        b'phasedivergent+contentdivergent': _(b"do you want to use "
                                              b"--phase-divergent or"
                                              b" --content-divergent"),
        b'phasedivergent+orphan': _(b"do you want to use --phase-divergent"
                                    b" or --orphan"),
        b'contentdivergent': _(b"do you want to use --content-divergent"),
        b'contentdivergent+orphan': _(b"do you want to use --content-divergent"
                                      b" or --orphan"),
        b'orphan': _(b"do you want to use --orphan"),
        b'any+phasedivergent': _(b"do you want to use --any (or --rev) and"
                                 b" --phase-divergent"),
        b'any+phasedivergent+contentdivergent': _(b"do you want to use --any"
                                                  b" (or --rev) and"
                                                  b" --phase-divergent or"
                                                  b" --content-divergent"),
        b'any+phasedivergent+orphan': _(b"do you want to use --any (or --rev)"
                                        b" and --phase-divergent or --orphan"),
        b'any+contentdivergent': _(b"do you want to use --any (or --rev) and"
                                   b" --content-divergent"),
        b'any+contentdivergent+orphan': _(b"do you want to use --any (or --rev)"
                                          b" and --content-divergent or "
                                          b"--orphan"),
        b'any+orphan': _(b"do you want to use --any (or --rev)"
                         b"and --orphan"),
    }

    if revopt:
        revs = scmutil.revrange(repo, revopt)
        if not revs:
            msg = _(b"set of specified revisions is empty")
        else:
            msg = _(b"no %s changesets in specified revisions") % targetcat
            othertroubles = []
            for cat in unselectedcategories:
                if revs & troubled[cat]:
                    othertroubles.append(cat)
            if othertroubles:
                hint = hintmap[b'+'.join(othertroubles)]

    elif anyopt:
        msg = _(b"no %s changesets to evolve") % targetcat
        othertroubles = []
        for cat in unselectedcategories:
            if troubled[cat]:
                othertroubles.append(cat)
        if othertroubles:
            hint = hintmap[b'+'.join(othertroubles)]

    else:
        # evolve without any option = relative to the current wdir
        if targetcat == b'orphan':
            msg = _(b"nothing to evolve on current working copy parent")
        else:
            msg = _(b"current working copy parent is not %s") % targetcat

        p1 = repo[b'.'].rev()
        othertroubles = []
        for cat in unselectedcategories:
            if p1 in troubled[cat]:
                othertroubles.append(cat)
        if othertroubles:
            hint = hintmap[b'+'.join(othertroubles)]
        else:
            length = len(troubled[targetcat])
            if length:
                hint = _(b"%d other %s in the repository, do you want --any "
                         b"or --rev") % (length, targetcat)
            else:
                othertroubles = []
                for cat in unselectedcategories:
                    if troubled[cat]:
                        othertroubles.append(cat)
                if othertroubles:
                    hint = hintmap[b'any+' + (b'+'.join(othertroubles))]
                else:
                    msg = _(b"no troubled changesets")
                    # Exit with a 0 (success) status in this case.
                    retoverride = 0

    assert msg is not None
    ui.write_err(b"%s\n" % msg)
    if hint:
        ui.write_err(b"(%s)\n" % hint)
        ret = 2
    else:
        ret = 1

    if retoverride is not None:
        return retoverride
    return ret

def _preparelistctxs(items, condition):
    return [item.hex() for item in items if condition(item)]

def _formatctx(fm, ctx):
    fm.data(node=ctx.hex())
    fm.data(desc=ctx.description())
    fm.data(date=ctx.date())
    fm.data(user=ctx.user())

def listtroubles(ui, repo, troublecategories, **opts):
    """Print all the troubles for the repo (or given revset)"""
    troublecategories = troublecategories or [b'contentdivergent', b'orphan', b'phasedivergent']
    showunstable = b'orphan' in troublecategories
    showbumped = b'phasedivergent' in troublecategories
    showdivergent = b'contentdivergent' in troublecategories

    revs = repo.revs(b'+'.join(b"%s()" % t for t in troublecategories))
    if opts.get('rev'):
        revs = scmutil.revrange(repo, opts.get('rev'))

    fm = ui.formatter(b'evolvelist', pycompat.byteskwargs(opts))
    for rev in revs:
        ctx = repo[rev]
        unpars = _preparelistctxs(ctx.parents(), lambda p: p.orphan())
        obspars = _preparelistctxs(ctx.parents(), lambda p: p.obsolete())
        imprecs = _preparelistctxs(repo.set(b"allpredecessors(%n)", ctx.node()),
                                   lambda p: not p.mutable())
        dsets = divergentsets(repo, ctx)

        fm.startitem()
        # plain formatter section
        hashlen, desclen = 12, 60
        desc = ctx.description()
        if desc:
            desc = desc.splitlines()[0]
        desc = (desc[:desclen] + b'...') if len(desc) > desclen else desc
        fm.plain(b'%s: ' % ctx.hex()[:hashlen])
        fm.plain(b'%s\n' % desc)
        fm.data(node=ctx.hex(), rev=ctx.rev(), desc=desc, phase=ctx.phasestr())

        for unpar in unpars if showunstable else []:
            fm.plain(b'  %s: %s (%s parent)\n' % (TROUBLES['ORPHAN'],
                                                  unpar[:hashlen],
                                                  TROUBLES['ORPHAN']))
        for obspar in obspars if showunstable else []:
            fm.plain(b'  %s: %s (obsolete parent)\n' % (TROUBLES['ORPHAN'],
                                                        obspar[:hashlen]))
        for imprec in imprecs if showbumped else []:
            fm.plain(b'  %s: %s (immutable precursor)\n' %
                     (TROUBLES['PHASEDIVERGENT'], imprec[:hashlen]))

        if dsets and showdivergent:
            for dset in dsets:
                fm.plain(b'  %s: ' % TROUBLES['CONTENTDIVERGENT'])
                first = True
                for n in dset[b'divergentnodes']:
                    t = b"%s (%s)" if first else b" %s (%s)"
                    first = False
                    fm.plain(t % (nodemod.hex(n)[:hashlen], repo[n].phasestr()))
                comprec = nodemod.hex(dset[b'commonprecursor'])[:hashlen]
                fm.plain(b" (precursor %s)\n" % comprec)
        fm.plain(b"\n")

        # templater-friendly section
        _formatctx(fm, ctx)
        troubles = []
        for unpar in unpars:
            troubles.append({b'troubletype': TROUBLES['ORPHAN'],
                             b'sourcenode': unpar, b'sourcetype': b'orphanparent'})
        for obspar in obspars:
            troubles.append({b'troubletype': TROUBLES['ORPHAN'],
                             b'sourcenode': obspar,
                             b'sourcetype': b'obsoleteparent'})
        for imprec in imprecs:
            troubles.append({b'troubletype': TROUBLES['PHASEDIVERGENT'],
                             b'sourcenode': imprec,
                             b'sourcetype': b'immutableprecursor'})
        for dset in dsets:
            divnodes = [{b'node': nodemod.hex(n),
                         b'phase': repo[n].phasestr(),
                         } for n in dset[b'divergentnodes']]
            troubles.append({b'troubletype': TROUBLES['CONTENTDIVERGENT'],
                             b'commonprecursor': nodemod.hex(dset[b'commonprecursor']),
                             b'divergentnodes': divnodes})
        fm.data(troubles=troubles)

    fm.end()

def _checkevolveopts(repo, opts):
    """ check the options passed to `hg evolve` and warn for deprecation warning
    if any """

    if opts['continue']:
        if opts['any']:
            raise error.Abort(_(b'cannot specify both "--any" and "--continue"'))
        if opts['all']:
            raise error.Abort(_(b'cannot specify both "--all" and "--continue"'))
        if opts['rev']:
            raise error.Abort(_(b'cannot specify both "--rev" and "--continue"'))
        if opts['stop']:
            raise error.Abort(_(b'cannot specify both "--stop" and'
                                b' "--continue"'))
        if opts['abort']:
            raise error.Abort(_(b'cannot specify both "--abort" and'
                                b' "--continue"'))

    if opts['stop']:
        if opts['any']:
            raise error.Abort(_(b'cannot specify both "--any" and "--stop"'))
        if opts['all']:
            raise error.Abort(_(b'cannot specify both "--all" and "--stop"'))
        if opts['rev']:
            raise error.Abort(_(b'cannot specify both "--rev" and "--stop"'))
        if opts['abort']:
            raise error.Abort(_(b'cannot specify both "--abort" and "--stop"'))

    if opts['abort']:
        if opts['any']:
            raise error.Abort(_(b'cannot specify both "--any" and "--abort"'))
        if opts['all']:
            raise error.Abort(_(b'cannot specify both "--all" and "--abort"'))
        if opts['rev']:
            raise error.Abort(_(b'cannot specify both "--rev" and "--abort"'))

    if opts['rev']:
        if opts['any']:
            raise error.Abort(_(b'cannot specify both "--rev" and "--any"'))
        if opts['all']:
            raise error.Abort(_(b'cannot specify both "--rev" and "--all"'))

    # Backward compatibility
    if opts['unstable']:
        msg = (b"'evolve --unstable' is deprecated, "
               b"use 'evolve --orphan'")
        repo.ui.deprecwarn(msg, b'4.4')

        opts['orphan'] = opts['divergent']

    if opts['divergent']:
        msg = (b"'evolve --divergent' is deprecated, "
               b"use 'evolve --content-divergent'")
        repo.ui.deprecwarn(msg, b'4.4')

        opts['content_divergent'] = opts['divergent']

    if opts['bumped']:
        msg = (b"'evolve --bumped' is deprecated, "
               b"use 'evolve --phase-divergent'")
        repo.ui.deprecwarn(msg, b'4.4')

        opts['phase_divergent'] = opts['bumped']

    return opts

def _cleanup(ui, repo, startnode, shouldupdate):
    if not shouldupdate:
        # Move back to startnode, or to its successor if the start node is
        # obsolete (perhaps made obsolete by the current `hg evolve`)
        unfi = repo.unfiltered()
        succ = utility._singlesuccessor(repo, unfi[startnode])
        hg.updaterepo(repo, repo[succ].node(), False)
    if repo[b'.'].node() != startnode:
        ui.status(_(b'working directory is now at %s\n') % repo[b'.'])

def divergentsets(repo, ctx):
    """Compute sets of commits divergent with a given one"""
    cache = {}
    base = {}
    for n in obsutil.allpredecessors(repo.obsstore, [ctx.node()]):
        if n == ctx.node():
            # a node can't be a base for divergence with itself
            continue
        nsuccsets = obsutil.successorssets(repo, n, cache)
        for nsuccset in nsuccsets:
            if ctx.node() in nsuccset:
                # we are only interested in *other* successor sets
                continue
            if tuple(nsuccset) in base:
                # we already know the latest base for this divergency
                continue
            base[tuple(nsuccset)] = n
    divergence = []
    for divset, b in base.items():
        divergence.append({
            b'divergentnodes': divset,
            b'commonprecursor': b
        })

    return divergence

@eh.command(
    b'evolve|stabilize|solve',
    [(b'n', b'dry-run', False,
      _(b'do not perform actions, just print what would be done')),
     (b'', b'confirm', False,
      _(b'ask for confirmation before performing the action')),
     (b'A', b'any', False,
      _(b'also consider troubled changesets unrelated to current working '
        b'directory')),
     (b'r', b'rev', [], _(b'solves troubles of these revisions'), _(b'REV')),
     (b'', b'bumped', False, _(b'solves only bumped changesets (DEPRECATED)')),
     (b'', b'phase-divergent', False, _(b'solves only phase-divergent changesets')),
     (b'', b'divergent', False, _(b'solves only divergent changesets (DEPRECATED)')),
     (b'', b'content-divergent', False, _(b'solves only content-divergent changesets')),
     (b'', b'unstable', False, _(b'solves only unstable changesets (DEPRECATED)')),
     (b'', b'orphan', False, _(b'solves only orphan changesets (default)')),
     (b'a', b'all', None, _(b'evolve all troubled changesets related to the current'
                            b' working directory and its descendants (default)')),
     (b'', b'update', False, _(b'update to the head of evolved changesets')),
     (b'c', b'continue', False, _(b'continue an interrupted evolution')),
     (b'', b'stop', False, _(b'stop the interrupted evolution')),
     (b'', b'abort', False, _(b'abort the interrupted evolution')),
     (b'l', b'list', False, _(b'provide details on troubled changesets'
                              b' in the repo')),
     ] + mergetoolopts,
    _(b'[OPTIONS]...'),
    helpbasic=True
)
def evolve(ui, repo, **opts):
    """solve troubled changesets in your repository

    Modifying history can lead to various types of troubled changesets:
    orphan, phase-divergent, or content-divergent. The evolve command resolves
    your troubles by executing one of the following actions:

    - update working copy to a successor
    - rebase an orphan changeset
    - extract the desired changes from a phase-divergent changeset
    - fuse content-divergent changesets back together

    If you pass no arguments, evolve works in automatic mode: it will execute a
    single action to reduce instability related to your working copy. There are
    two cases for this action. First, if the parent of your working copy is
    obsolete, evolve updates to the parent's successor. Second, if the working
    copy parent is not obsolete but has obsolete predecessors, then evolve
    determines if there is an orphan changeset that can be rebased onto the
    working copy parent in order to reduce instability.
    If so, evolve rebases that changeset. If not, evolve refuses to guess your
    intention, and gives a hint about what you might want to do next.

    When ``--update`` is used, successful evolve operations update the working
    directory to the newly created changesets. Moreover, an update will always
    be performed if the current working directory parent is obsolete.

    Automatic mode only handles common use cases. For example, it avoids taking
    action in the case of ambiguity, and it ignores orphan changesets that are
    not related to your working copy.
    It also refuses to solve phase-divergent or content-divergent changesets
    unless you explicitly request such behavior (see below).

    Eliminating all instability around your working copy may require multiple
    invocations of :hg:`evolve` if you use ``--rev`` or ``--no-all``. Use
    ``--all`` (which is the default behavior) to recursively select and evolve
    all orphan changesets that can be rebased onto the working copy parent.
    This is more powerful than successive invocations, since ``--all`` handles
    ambiguous cases (e.g. orphan changesets with multiple children) by evolving
    all branches.

    When your repository cannot be handled by automatic mode, you might need to
    use ``--rev`` to specify a changeset to evolve. For example, if you have
    an orphan changeset that is not related to the working copy parent,
    you could use ``--rev`` to evolve it. Or, if some changeset has multiple
    orphan children, evolve in automatic mode refuses to guess which one to
    evolve; you have to use ``--rev`` in that case.

    Alternately, ``--any`` makes evolve search for the next evolvable changeset
    regardless of whether it is related to the working copy parent.

    You can supply multiple revisions to evolve multiple troubled changesets
    in a single invocation. In revset terms, ``--any`` is equivalent to ``--rev
    first(orphan())``. ``--rev`` and ``--all`` are mutually exclusive, as are
    ``--rev`` and ``--any``.

    ``hg evolve --any --all`` is useful for cleaning up instability across all
    branches, letting evolve figure out the appropriate order and destination.

    When you have troubled changesets that are not orphan, :hg:`evolve` refuses
    to consider them unless you specify the category of trouble you
    wish to resolve, with ``--phase-divergent`` or ``--content-divergent``.
    These options are currently mutually exclusive with each other and with
    ``--orphan`` (the default). You can combine ``--phase-divergent`` or
    ``--content-divergent`` with ``--rev``, ``--all``, or ``--any``.

    You can also use the evolve command to list the troubles affecting your
    repository by using the --list flag. You can choose to display only some
    categories of troubles with the --orphan, --content-divergent or
    --phase-divergent flags.

    Interrupted
    ===========

    The `hg evolve` command is an all purpose tool that solve all kind of
    instabilities in your repository. Sometimes, instability resolution will lead
    to merge conflict that cannot be solved without a human intervention (same as
    `hg merge`). This can lead to an "interrupted state" where human assistance is
    requested. There are three things which you can do when you face a similar
    situation:

      - `hg evolve --continue`:
         resolve all the conflicts using `hg resolve` and then run this to
         continue the interrupted evolve

      - `hg evolve --stop`:
         stops the current interrupted evolve, keeping all the successful steps,
         but delaying to resolution of the remaining step for later.

      - `hg evolve --abort`:
         aborts the interrupted evolve and undoes all the resolution which have
         happened
    """
    with repo.wlock(), repo.lock():
        return _performevolve(ui, repo, **opts)

def _performevolve(ui, repo, **opts):
    opts = _checkevolveopts(repo, opts)
    # Options
    contopt = opts['continue']
    anyopt = opts['any']
    allopt = opts['all']
    if allopt is None:
        allopt = True
    startnode = repo[b'.'].node()
    dryrunopt = opts['dry_run']
    confirmopt = opts['confirm']
    revopt = opts['rev']
    stopopt = opts['stop']
    abortopt = opts['abort']
    shouldupdate = opts['update']

    troublecategories = {
        b'phasedivergent': r'phase_divergent',
        b'contentdivergent': r'content_divergent',
        b'orphan': r'orphan',
    }
    specifiedcategories = [k for k, v in troublecategories.items() if opts[v]]
    if opts['list']:
        ui.pager(b'evolve')
        listtroubles(ui, repo, specifiedcategories, **opts)
        return

    targetcat = b'orphan'
    if 1 < len(specifiedcategories):
        msg = _(b'cannot specify more than one trouble category to solve (yet)')
        raise error.Abort(msg)
    elif len(specifiedcategories) == 1:
        targetcat = specifiedcategories[0]

    ui.setconfig(b'ui', b'forcemerge', opts.get('tool', r''), b'evolve')

    evolvestate = state.cmdstate(repo)
    # Continuation handling
    if contopt:
        if not evolvestate:
            raise error.Abort(_(b'no interrupted evolve to continue'))
        evolvestate.load()
        continueevolve(ui, repo, evolvestate)
        if evolvestate[b'command'] != b'evolve':
            evolvestate.delete()
            return
        startnode = repo.unfiltered()[evolvestate[b'startnode']]
        if b'update' in evolvestate:
            shouldupdate = evolvestate[b'update']
        evolvestate.delete()
    elif stopopt:
        if not evolvestate:
            raise error.Abort(_(b'no interrupted evolve to stop'))
        evolvestate.load()
        stopevolve(ui, repo, evolvestate)
        evolvestate.delete()
        return
    elif abortopt:
        if not evolvestate:
            raise error.Abort(_(b'no interrupted evolve to abort'))
        evolvestate.load()
        # `hg next --evolve` in play
        if evolvestate[b'command'] != b'evolve':
            pctx = repo[b'.']
            hg.updaterepo(repo, pctx.node(), True)
            ui.status(_(b'evolve aborted\n'))
            ui.status(_(b'working directory is now at %s\n')
                      % pctx.hex()[:12])
            evolvestate.delete()
            return 0
        return abortevolve(ui, repo, evolvestate)
    else:
        cmdutil.bailifchanged(repo)

        obswdir = repo[b'.'].obsolete()
        revs = _selectrevs(repo, allopt, revopt, anyopt, targetcat)

        if not (revs or obswdir):
            return _handlenotrouble(ui, repo, allopt, revopt, anyopt, targetcat)
        obswdironly = not revs and obswdir

        if obswdir:
            result = solveobswdp(ui, repo, opts)
            if result != 0 or result is True:
                # return as solving obswdp wasn't successful
                return result
        if obswdironly:
            return 0

        # Progress handling
        seen = 1
        showprogress = allopt or revopt
        count = len(revs)

        def progresscb():
            if showprogress:
                compat.progress(ui, _(b'evolve'), seen, unit=_(b'changesets'),
                                total=count)

        # Order the revisions
        revs = _orderrevs(repo, revs)

        # cbor does not know how to serialize sets, using list for skippedrevs
        stateopts = {b'category': targetcat, b'replacements': {},
                     b'revs': list(revs), b'confirm': confirmopt,
                     b'startnode': startnode, b'skippedrevs': [],
                     b'command': b'evolve', b'orphanmerge': False,
                     b'bookmarkchanges': [], b'temprevs': [], b'obsmarkers': [],
                     b'update': shouldupdate}
        evolvestate.addopts(stateopts)
        # lastsolved: keep track of successor of last troubled cset we evolved
        # to confirm that if atop msg should be suppressed to remove redundancy
        lastsolved = None

        activetopic = getattr(repo, 'currenttopic', b'')
        tr = repo.transaction(b"evolve")
        with util.acceptintervention(tr):
            for rev in revs:
                lastsolved = _solveonerev(ui, repo, rev, evolvestate,
                                          activetopic, dryrunopt,
                                          confirmopt, progresscb,
                                          targetcat, lastsolved)
                seen += 1

        if showprogress:
            compat.progress(ui, _(b'evolve'), None)

    _cleanup(ui, repo, startnode, shouldupdate)

def _solveonerev(ui, repo, rev, evolvestate, activetopic, dryrunopt, confirmopt,
                 progresscb, targetcat, lastsolved):
    """solves one trouble, including orphan merges

    Like _solveone(), this solves one trouble. Unlike _solveone(), it
    stabilizes for both parents of orphan merges.
    """
    curctx = repo[rev]
    revtopic = getattr(curctx, 'topic', lambda: b'')()
    topicidx = getattr(curctx, 'topicidx', lambda: None)()
    stacktmplt = False
    # check if revision being evolved is in active topic to make sure
    # that we can use stack aliases s# in evolve msgs.
    if activetopic and (activetopic == revtopic) and topicidx is not None:
        stacktmplt = True
    progresscb()
    ret = _solveone(ui, repo, curctx, evolvestate, dryrunopt,
                    confirmopt, progresscb, targetcat,
                    lastsolved=lastsolved, stacktmplt=stacktmplt)
    if ret[0]:
        evolvestate[b'replacements'][curctx.node()] = ret[1]
        lastsolved = ret[1]
    else:
        evolvestate[b'skippedrevs'].append(curctx.node())

    if evolvestate[b'orphanmerge']:
        # we were processing an orphan merge with both parents obsolete,
        # stabilized for second parent, re-stabilize for the first parent
        ret = _solveone(ui, repo, repo[ret[1]], evolvestate, dryrunopt,
                        confirmopt, progresscb, targetcat,
                        stacktmplt=stacktmplt)
        if ret[0]:
            evolvestate[b'replacements'][curctx.node()] = ret[1]
            lastsolved = ret[1]
        else:
            evolvestate[b'skippedrevs'].append(curctx.node())

        evolvestate[b'orphanmerge'] = False
    return lastsolved

def solveobswdp(ui, repo, opts):
    """this function updates to the successor of obsolete wdir parent"""
    oldid = repo[b'.'].node()
    startctx = repo[b'.']
    dryrunopt = opts.get('dry_run', False)
    displayer = compat.changesetdisplayer(ui, repo,
                                          {b'template': shorttemplate})
    try:
        ctx = repo[utility._singlesuccessor(repo, repo[b'.'])]
    except utility.MultipleSuccessorsError as exc:
        repo.ui.write_err(_(b'parent is obsolete with multiple'
                            b' successors:\n'))
        for ln in exc.successorssets:
            for n in ln:
                displayer.show(repo[n])
        return 2

    ui.status(_(b'update:'))
    if not ui.quiet:
        displayer.show(ctx)

    if dryrunopt:
        return 0
    res = hg.update(repo, ctx.rev())
    newid = ctx.node()

    if ctx != startctx:
        with repo.wlock(), repo.lock(), repo.transaction(b'evolve') as tr:
            bmupdater = rewriteutil.bookmarksupdater(repo, oldid, tr)
            bmupdater(newid)
        ui.status(_(b'working directory is now at %s\n') % ctx)
    return res

def stopevolve(ui, repo, evolvestate):
    """logic for handling of `hg evolve --stop`"""
    updated = False
    pctx = None
    if (evolvestate[b'command'] == b'evolve'
        and evolvestate[b'category'] == b'contentdivergent'
        and evolvestate[b'relocated']):
        oldother = evolvestate[b'old-other']
        if oldother:
            with repo.wlock(), repo.lock():
                repo = repo.unfiltered()
                hg.updaterepo(repo, oldother, True)
                strips = [evolvestate[b'relocated']]
                repair.strip(ui, repo, strips, False)
                updated = True
                pctx = repo[oldother]
    if not updated:
        pctx = repo[b'.']
        hg.updaterepo(repo, pctx.node(), True)
    ui.status(_(b'stopped the interrupted evolve\n'))
    ui.status(_(b'working directory is now at %s\n') % pctx)

def abortevolve(ui, repo, evolvestate):
    """ logic for handling of `hg evolve --abort`"""

    with repo.wlock(), repo.lock():
        repo = repo.unfiltered()
        evolvedctx = []
        # boolean value to say whether we should strip or not
        cleanup = True
        startnode = evolvestate[b'startnode']
        for old, new in evolvestate[b'replacements'].items():
            if new:
                evolvedctx.append(repo[new])
        for temp in evolvestate[b'temprevs']:
            if temp:
                evolvedctx.append(repo[temp])
        evolvedrevs = [c.rev() for c in evolvedctx]

        # checking if phase changed of any of the evolved rev
        immutable = [c for c in evolvedctx if not c.mutable()]
        if immutable:
            repo.ui.warn(_(b"cannot clean up public changesets: %s\n")
                         % b', '.join(bytes(c) for c in immutable),
                         hint=_(b"see 'hg help phases' for details"))
            cleanup = False

    # checking no new changesets are created on evolved revs
    descendants = set()
    if evolvedrevs:
        descendants = set(repo.changelog.descendants(evolvedrevs))
    if descendants - set(evolvedrevs):
        repo.ui.warn(_(b"warning: new changesets detected on destination "
                       b"branch\n"))
        cleanup = False

    # finding the indices of the obsmarkers to be stripped and stripping
    # them
    if evolvestate[b'obsmarkers']:
        stripmarkers = set()
        for m in evolvestate[b'obsmarkers']:
            m = (m[0], m[1])
            stripmarkers.add(m)
        indices = []
        allmarkers = obsutil.getmarkers(repo)
        for i, m in enumerate(allmarkers):
            marker = (m.prednode(), m.succnodes()[0])
            if marker in stripmarkers:
                indices.append(i)

        repair.deleteobsmarkers(repo.obsstore, indices)
        repo.ui.debug(b'deleted %d obsmarkers\n' % len(indices))

    if cleanup:
        if evolvedrevs:
            strippoints = [c.node()
                           for c in repo.set(b'roots(%ld)', evolvedrevs)]

        # updating the working directory
        hg.updaterepo(repo, startnode, True)

        # Strip from the first evolved revision
        if evolvedrevs:
            # no backup of evolved cset versions needed
            repair.strip(repo.ui, repo, strippoints, False)

        with repo.transaction(b'evolve') as tr:
            # restoring bookmarks at there original place
            bmchanges = evolvestate[b'bookmarkchanges']
            if bmchanges:
                repo._bookmarks.applychanges(repo, tr, bmchanges)

        evolvestate.delete()
        ui.status(_(b'evolve aborted\n'))
        ui.status(_(b'working directory is now at %s\n')
                  % nodemod.hex(startnode)[:12])
    else:
        raise error.Abort(_(b"unable to abort interrupted evolve, use 'hg "
                            b"evolve --stop' to stop evolve"))

def hgabortevolve(ui, repo):
    """logic for aborting evolve using 'hg abort'"""
    with repo.wlock(), repo.lock():
        evolvestate = state.cmdstate(repo)
        evolvestate.load()
        if evolvestate[b'command'] != b'evolve':
            pctx = repo[b'.']
            hg.updaterepo(repo, pctx.node(), True)
            ui.status(_(b'evolve aborted\n'))
            ui.status(_(b'working directory is now at %s\n')
                      % pctx.hex()[:12])
            evolvestate.delete()
            return 0
        return abortevolve(ui, repo, evolvestate)

def continueevolve(ui, repo, evolvestate):
    """logic for handling of `hg evolve --continue`"""

    ms = merge.mergestate.read(repo)
    mergeutil.checkunresolved(ms)
    if (evolvestate[b'command'] == b'next'
        or evolvestate[b'category'] == b'orphan'):
        _completeorphan(ui, repo, evolvestate)
    elif evolvestate[b'category'] == b'phasedivergent':
        _completephasedivergent(ui, repo, evolvestate)
    elif evolvestate[b'category'] == b'contentdivergent':
        _continuecontentdivergent(ui, repo, evolvestate, None)
    else:
        repo.ui.status(_(b"continuing interrupted '%s' resolution is not yet"
                         b" supported\n") % evolvestate[b'category'])
        return

    # make sure we are continuing evolve and not `hg next --evolve`
    if evolvestate[b'command'] != b'evolve':
        return

    # Progress handling
    seen = 1
    count = len(evolvestate[b'revs'])

    def progresscb():
        compat.progress(ui, _(b'evolve'), seen, unit=_(b'changesets'),
                        total=count)

    category = evolvestate[b'category']
    confirm = evolvestate[b'confirm']
    unfi = repo.unfiltered()
    # lastsolved: keep track of successor of last troubled cset we
    # evolved to confirm that if atop msg should be suppressed to remove
    # redundancy
    lastsolved = None
    activetopic = getattr(repo, 'currenttopic', b'')
    tr = repo.transaction(b"evolve")
    with util.acceptintervention(tr):
        for rev in evolvestate[b'revs']:
            # XXX: prevent this lookup by storing nodes instead of revnums
            curctx = unfi[rev]

            # check if we can use stack template
            revtopic = getattr(curctx, 'topic', lambda: b'')()
            topicidx = getattr(curctx, 'topicidx', lambda: None)()
            stacktmplt = False
            if (activetopic and (activetopic == revtopic)
                and topicidx is not None):
                stacktmplt = True

            if (curctx.node() not in evolvestate[b'replacements']
                and curctx.node() not in evolvestate[b'skippedrevs']):
                newnode = _solveone(ui, repo, curctx, evolvestate, False,
                                    confirm, progresscb, category,
                                    lastsolved=lastsolved,
                                    stacktmplt=stacktmplt)
                if newnode[0]:
                    evolvestate[b'replacements'][curctx.node()] = newnode[1]
                    lastsolved = newnode[1]
                else:
                    evolvestate[b'skippedrevs'].append(curctx.node())
            seen += 1

def _continuecontentdivergent(ui, repo, evolvestate, progresscb):
    """function to continue the interrupted content-divergence resolution."""
    tr = repo.transaction(b'evolve')
    with util.acceptintervention(tr):
        divergent = evolvestate[b'divergent']
        base = evolvestate[b'base']
        repo = repo.unfiltered()
        if evolvestate[b'relocating']:
            newother = _completerelocation(ui, repo, evolvestate)
            current = repo[evolvestate[b'current']]
            obsolete.createmarkers(repo, [(current, (repo[newother],))],
                                   operation=b'evolve')
            evolvestate[b'relocating'] = False
            evolvestate[b'relocated'] = newother
            evolvestate[b'temprevs'].append(newother)
            evolvestate[b'other-divergent'] = newother
            # continue the resolution by merging the content-divergence
            _mergecontentdivergents(repo, progresscb,
                                    repo[divergent],
                                    repo[newother],
                                    repo[base],
                                    evolvestate)

        other = evolvestate[b'other-divergent']
        ret = _completecontentdivergent(ui, repo, progresscb,
                                        repo[divergent],
                                        repo[other],
                                        repo[base],
                                        evolvestate)
        origdivergent = evolvestate[b'orig-divergent']
        evolvestate[b'replacements'][origdivergent] = ret[1]
        # logic to continue the public content-divergent
        publicnode = evolvestate.get(b'public-divergent')
        if publicnode:
            res, newnode = ret
            if not res:
                # no need to proceed for phase divergence resolution step
                pass
            elif newnode == publicnode:
                # merging had the same changes as public changeset and
                # divergence has been resolved by creating markers
                pass
            else:
                prec = repo[publicnode]
                bumped = repo[newnode]
                ret = _resolvephasedivergent(ui, repo, prec=prec, bumped=bumped)
        return ret

def _completephasedivergent(ui, repo, evolvestate):
    """function to complete the interrupted phase-divergence resolution.

    First completes the relocation of the commit and then process resolving
    phase-divergence"""

    # need to start transaction for bookmark changes
    with repo.transaction(b'evolve'):
        node = _completerelocation(ui, repo, evolvestate)
        evolvestate[b'temprevs'].append(node)
        # resolving conflicts can lead to empty wdir and node can be None in
        # those cases
        ctx = repo[evolvestate[b'current']]
        newctx = repo[node] if node is not None else repo[b'.']
        obsolete.createmarkers(repo, [(ctx, (newctx,))], operation=b'evolve')

        # now continuing the phase-divergence resolution part
        prec = repo[evolvestate[b'precursor']]
        retvalue = _resolvephasedivergent(ui, repo, prec, newctx)
        evolvestate[b'replacements'][ctx.node()] = retvalue[1]

def _completeorphan(ui, repo, evolvestate):
    """function to complete the interrupted orphan resolution"""

    node = _completerelocation(ui, repo, evolvestate)
    # resolving conflicts can lead to empty wdir and node can be None in
    # those cases
    ctx = repo[evolvestate[b'current']]
    if node is None:
        repo.ui.status(_(b"evolution of %d:%s created no changes"
                         b" to commit\n") % (ctx.rev(), ctx))
        replacement = ()
    else:
        replacement = (repo[node],)

    obsolete.createmarkers(repo, [(ctx, replacement)], operation=b'evolve')

    # make sure we are continuing evolve and not `hg next --evolve`
    if evolvestate[b'command'] == b'evolve':
        evolvestate[b'replacements'][ctx.node()] = node
        if evolvestate[b'orphanmerge']:
            # processing a merge changeset with both parents obsoleted,
            # stabilized on second parent, insert in front of list to
            # re-process to stabilize on first parent
            evolvestate[b'revs'].insert(0, repo[node].rev())
            evolvestate[b'orphanmerge'] = False

def _completerelocation(ui, repo, evolvestate):
    """function to complete the interrupted relocation of a commit
    return the new node formed
    """

    orig = repo[evolvestate[b'current']]
    ctx = orig
    source = ctx.extra().get(b'source')
    extra = {}
    if source:
        extra[b'source'] = source
        extra[b'intermediate-source'] = ctx.hex()
    else:
        extra[b'source'] = ctx.hex()
    user = ctx.user()
    date = ctx.date()
    message = ctx.description()
    ui.status(_(b'evolving %d:%s "%s"\n') % (ctx.rev(), ctx,
                                             message.split(b'\n', 1)[0]))
    targetphase = max(ctx.phase(), phases.draft)
    overrides = {(b'phases', b'new-commit'): targetphase}

    ctxparents = orig.parents()
    if len(ctxparents) == 2:
        currentp1 = repo.dirstate.parents()[0]
        p1obs = ctxparents[0].obsolete()
        p2obs = ctxparents[1].obsolete()
        # asumming that the parent of current wdir is successor of one
        # of p1 or p2 of the original changeset
        if p1obs and not p2obs:
            # p1 is obsolete and p2 is not obsolete, current working
            # directory parent should be successor of p1, so we should
            # set dirstate parents to (succ of p1, p2)
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(currentp1,
                                         ctxparents[1].node())
        elif p2obs and not p1obs:
            # p2 is obsolete and p1 is not obsolete, current working
            # directory parent should be successor of p2, so we should
            # set dirstate parents to (succ of p2, p1)
            with repo.dirstate.parentchange():
                repo.dirstate.setparents(ctxparents[0].node(),
                                         currentp1)

        else:
            # both the parents were obsoleted, if orphanmerge is set, we
            # are processing the second parent first (to keep parent order)
            if evolvestate.get(b'orphanmerge'):
                with repo.dirstate.parentchange():
                    repo.dirstate.setparents(ctxparents[0].node(),
                                             currentp1)
            pass
    else:
        with repo.dirstate.parentchange():
            repo.dirstate.setparents(repo.dirstate.parents()[0], nodemod.nullid)

    with repo.ui.configoverride(overrides, b'evolve-continue'):
        node = repo.commit(text=message, user=user,
                           date=date, extra=extra)
    return node
