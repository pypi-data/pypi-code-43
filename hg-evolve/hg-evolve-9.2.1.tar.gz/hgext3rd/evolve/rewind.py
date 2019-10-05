from __future__ import absolute_import

import collections
import hashlib

from mercurial import (
    cmdutil,
    error,
    hg,
    obsolete,
    obsutil,
    scmutil,
)

from mercurial.i18n import _

from . import (
    exthelper,
    rewriteutil,
    compat,
)

eh = exthelper.exthelper()

# flag in obsolescence markers to link to identical version
identicalflag = 4

@eh.command(
    b'rewind|undo',
    [(b'', b'to', [], _(b"rewind to these revisions"), _(b'REV')),
     (b'', b'as-divergence', None, _(b"preserve current latest successors")),
     (b'', b'exact', None, _(b"only rewind explicitly selected revisions")),
     (b'', b'from', [],
      _(b"rewind these revisions to their predecessors"), _(b'REV')),
     (b'k', b'keep', None,
      _(b"do not modify working directory during rewind")),
     ],
    _(b'[--as-divergence] [--exact] [--keep] [--to REV]... [--from REV]...'),
    helpbasic=True)
def rewind(ui, repo, **opts):
    """rewind a stack of changesets to a previous state

    This command can be used to restore stacks of changesets to an obsolete
    state, creating identical copies.

    There are two main ways to select the rewind target. Rewinding "from"
    changesets will restore the direct predecessors of these changesets (and
    obsolete the changeset you rewind from). Rewinding "to" will restore the
    changeset you have selected (and obsolete their latest successors).

    By default, we rewind from the working directory parents, restoring its
    predecessor.

    When we rewind to an obsolete version, we also rewind to all its obsolete
    ancestors. To only rewind to the explicitly selected changesets use the
    `--exact` flag. Using the `--exact` flag can restore some changesets as
    orphan.

    The latest successors of the obsolete changesets will be superseded by
    these new copies. This behavior can be disabled using `--as-divergence`,
    the current latest successors won't be affected and content-divergence will
    appear between them and the restored version of the obsolete changesets.

    Current rough edges:

      * fold: rewinding to only some of the initially folded changesets will be
              problematic. The fold result is marked obsolete and the part not
              rewinded to are "lost".  Please use --as-divergence when you
              need to perform such operation.

      * :hg:`rewind` might affect changesets outside the current stack. Without
              --exact, we also restore ancestors of the rewind target,
              obsoleting their latest successors (unless --as-divergent is
              provided). In some case, these latest successors will be on
              branches unrelated to the changeset you rewind from.
              (We plan to automatically detect this case in the future)

    """
    unfi = repo.unfiltered()

    successorsmap = collections.defaultdict(set)
    rewindmap = {}
    sscache = {}
    with repo.wlock(), repo.lock():
        # stay on the safe side: prevent local case in case we need to upgrade
        cmdutil.bailifchanged(repo)

        rewinded = _select_rewinded(repo, opts)

        if not opts['as_divergence']:
            for rev in rewinded:
                ctx = unfi[rev]
                ssets = obsutil.successorssets(repo, ctx.node(), sscache)
                if 1 < len(ssets):
                    msg = _(b'rewind confused by divergence on %s') % ctx
                    hint = _(b'solve divergence first or use "--as-divergence"')
                    raise error.Abort(msg, hint=hint)
                if ssets and ssets[0]:
                    for succ in ssets[0]:
                        successorsmap[succ].add(ctx.node())

        # Check that we can rewind these changesets
        with repo.transaction(b'rewind'):
            oldctx = repo[b'.']

            for rev in sorted(rewinded):
                ctx = unfi[rev]
                rewindmap[ctx.node()] = _revive_revision(unfi, rev, rewindmap)

            relationships = []
            cl = unfi.changelog
            wctxp = repo[None].p1()
            update_target = None
            for (source, dest) in sorted(successorsmap.items()):
                newdest = [rewindmap[d] for d in sorted(dest, key=cl.rev)]
                rel = (unfi[source], tuple(unfi[d] for d in newdest))
                relationships.append(rel)
                if wctxp.node() == source:
                    update_target = newdest[-1]
            obsolete.createmarkers(unfi, relationships, operation=b'rewind')
            if update_target is not None:
                if opts.get('keep'):
                    hg.updaterepo(repo, oldctx, True)

                    # This is largely the same as the implementation in
                    # strip.stripcmd() and cmdrewrite.cmdprune().

                    # only reset the dirstate for files that would actually
                    # change between the working context and the revived cset
                    newctx = repo[update_target]
                    changedfiles = []
                    for ctx in [oldctx, newctx]:
                        # blindly reset the files, regardless of what actually
                        # changed
                        changedfiles.extend(ctx.files())

                    # reset files that only changed in the dirstate too
                    dirstate = repo.dirstate
                    dirchanges = [f for f in dirstate if dirstate[f] != 'n']
                    changedfiles.extend(dirchanges)
                    repo.dirstate.rebuild(newctx.node(), newctx.manifest(),
                                          changedfiles)

                    # TODO: implement restoration of copies/renames
                    # Ideally this step should be handled by dirstate.rebuild
                    # or scmutil.movedirstate, but right now there's no copy
                    # tracing across obsolescence relation (oldctx <-> newctx).
                    revertopts = {'no_backup': True, 'all': True,
                                  'rev': oldctx.node()}
                    with ui.configoverride({(b'ui', b'quiet'): True}):
                        cmdutil.revert(repo.ui, repo, oldctx,
                                       repo.dirstate.parents(), **revertopts)
                else:
                    hg.updaterepo(repo, update_target, False)

    repo.ui.status(_(b'rewinded to %d changesets\n') % len(rewinded))
    if relationships:
        repo.ui.status(_(b'(%d changesets obsoleted)\n') % len(relationships))
    if update_target is not None and not opts.get('keep'):
        ui.status(_(b'working directory is now at %s\n') % repo[b'.'])

def _select_rewinded(repo, opts):
    """select the revision we shoudl rewind to
    """
    unfi = repo.unfiltered()
    rewinded = set()
    revsto = opts.get('to')
    revsfrom = opts.get('from')
    if not (revsto or revsfrom):
        revsfrom.append(b'.')
    if revsto:
        rewinded.update(scmutil.revrange(repo, revsto))
    if revsfrom:
        succs = scmutil.revrange(repo, revsfrom)
        rewinded.update(unfi.revs(b'predecessors(%ld)', succs))

    if not rewinded:
        raise error.Abort(b'no revision to rewind to')

    if not opts['exact']:
        rewinded = unfi.revs(b'obsolete() and ::%ld', rewinded)

    return sorted(rewinded)

def _revive_revision(unfi, rev, rewindmap):
    """rewind a single revision rev.
    """
    ctx = unfi[rev]
    extra = ctx.extra().copy()
    # rewind hash should be unique over multiple rewind.
    user = unfi.ui.config(b'devel', b'user.obsmarker')
    if not user:
        user = unfi.ui.username()
    date = unfi.ui.configdate(b'devel', b'default-date')
    if date is None:
        date = compat.makedate()
    noise = b"%s\0%s\0%d\0%d" % (ctx.node(), user, date[0], date[1])
    extra[b'__rewind-hash__'] = hashlib.sha256(noise).hexdigest()

    p1 = ctx.p1().node()
    p1 = rewindmap.get(p1, p1)
    p2 = ctx.p2().node()
    p2 = rewindmap.get(p2, p2)

    updates = []
    if len(ctx.parents()) > 1:
        updates = ctx.parents()
    extradict = {b'extra': extra}

    new, unusedvariable = rewriteutil.rewrite(unfi, ctx, updates, ctx,
                                              [p1, p2],
                                              commitopts=extradict)

    obsolete.createmarkers(unfi, [(ctx, (unfi[new],))],
                           flag=identicalflag, operation=b'rewind')

    return new
