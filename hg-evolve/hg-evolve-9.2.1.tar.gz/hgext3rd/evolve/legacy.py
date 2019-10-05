# Copyright 2011 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#                Logilab SA        <contact@logilab.fr>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""Deprecated extension that formerly introduced "Changeset Obsolescence".

This concept is now partially in Mercurial core (starting with Mercurial 2.3).
The remaining logic has been grouped with the evolve extension.

Some code remains in this extensions to detect and convert prehistoric format
of obsolete marker than early user may have create. Keep it enabled if you
were such user.
"""

from mercurial import error

import sys
import json

from mercurial.i18n import _
from mercurial import lock as lockmod
from mercurial.node import bin, nullid
from mercurial import registrar
from mercurial import util

try:
    from mercurial.utils.dateutil import makedate
except ImportError:
    # compat with hg < 4.6
    from mercurial.util import makedate

commandfunc = registrar.command

#####################################################################
### Older format management                                       ###
#####################################################################

# Code related to detection and management of older legacy format never
# handled by core


def reposetup(ui, repo):
    """Detect that a repo still contains some old obsolete format
    """
    if not repo.local():
        return
    evolveopts = ui.configlist(b'experimental', b'evolution')
    if not evolveopts:
        evolveopts = b'all'
        ui.setconfig(b'experimental', b'evolution', evolveopts)
    for arg in sys.argv:
        if r'debugc' in arg:
            break
    else:
        data = repo.vfs.tryread(b'obsolete-relations')
        if not data:
            data = repo.svfs.tryread(b'obsoletemarkers')
        if data:
            raise error.Abort(b'old format of obsolete marker detected!\n'
                              b'run `hg debugconvertobsolete` once.')

def _obsdeserialize(flike):
    """read a file like object serialized with _obsserialize

    this deserialize into a {subject -> objects} mapping

    this was the very first format ever."""
    rels = {}
    for line in flike:
        subhex, objhex = line.split()
        subnode = bin(subhex)
        if subnode == nullid:
            subnode = None
        rels.setdefault(subnode, set()).add(bin(objhex))
    return rels

cmdtable = {}
command = commandfunc(cmdtable)
@command(b'debugconvertobsolete', [], b'')
def cmddebugconvertobsolete(ui, repo):
    """import markers from an .hg/obsolete-relations file"""
    cnt = 0
    err = 0
    lock = repo.lock()
    some = False
    try:
        unlink = []
        tr = repo.transaction(b'convert-obsolete')
        try:
            repo._importoldobsolete = True
            store = repo.obsstore
            ### very first format
            try:
                f = repo.vfs(b'obsolete-relations')
                try:
                    some = True
                    for line in f:
                        subhex, objhex = line.split()
                        suc = bin(subhex)
                        prec = bin(objhex)
                        sucs = (suc == nullid) and [] or [suc]
                        meta = {
                            b'date': b'%i %i' % makedate(),
                            b'user': ui.username(),
                            }
                        try:
                            store.create(tr, prec, sucs, 0, metadata=meta)
                            cnt += 1
                        except ValueError:
                            repo.ui.write_err(b"invalid old marker line: %s"
                                              % (line))
                            err += 1
                finally:
                    f.close()
                unlink.append(repo.vfs.join(b'obsolete-relations'))
            except IOError:
                pass
            ### second (json) format
            data = repo.svfs.tryread(b'obsoletemarkers')
            if data:
                some = True
                for oldmark in json.loads(data):
                    del oldmark[r'id']  # dropped for now
                    del oldmark[r'reason']  # unused until then
                    oldobject = str(oldmark.pop(r'object'))
                    oldsubjects = [str(s) for s in oldmark.pop(r'subjects', [])]
                    lookup_errors = (error.RepoLookupError, error.LookupError)
                    if len(oldobject) != 40:
                        try:
                            oldobject = repo[oldobject].node()
                        except lookup_errors:
                            pass
                    if any(len(s) != 40 for s in oldsubjects):
                        try:
                            oldsubjects = [repo[s].node() for s in oldsubjects]
                        except lookup_errors:
                            pass

                    oldmark[r'date'] = r'%i %i' % tuple(oldmark[r'date'])
                    meta = dict((k.encode('utf-8'), v.encode('utf-8'))
                                for k, v in oldmark.items())
                    try:
                        succs = [bin(n) for n in oldsubjects]
                        succs = [n for n in succs if n != nullid]
                        store.create(tr, bin(oldobject), succs,
                                     0, metadata=meta)
                        cnt += 1
                    except ValueError:
                        msg = b"invalid marker %s -> %s\n"
                        msg %= (oldobject, oldsubjects)
                        repo.ui.write_err(msg)
                        err += 1
                unlink.append(repo.svfs.join(b'obsoletemarkers'))
            tr.close()
            for path in unlink:
                util.unlink(path)
        finally:
            tr.release()
    finally:
        del repo._importoldobsolete
        lock.release()
    if not some:
        ui.warn(_(b'nothing to do\n'))
    ui.status(b'%i obsolete marker converted\n' % cnt)
    if err:
        ui.write_err(b'%i conversion failed. check you graph!\n' % err)

@command(b'debugrecordpruneparents', [], b'')
def cmddebugrecordpruneparents(ui, repo):
    """add parent data to prune markers when possible

    This command searches the repo for prune markers without parent information.
    If the pruned node is locally known, it creates a new marker with parent
    data.
    """
    pgop = b'reading markers'

    # lock from the beginning to prevent race
    wlock = lock = tr = None
    try:
        wlock = repo.wlock()
        lock = repo.lock()
        tr = repo.transaction(b'recordpruneparents')
        unfi = repo.unfiltered()
        nm = unfi.changelog.nodemap
        store = repo.obsstore
        pgtotal = len(store._all)
        for idx, mark in enumerate(list(store._all)):
            if not mark[1]:
                rev = nm.get(mark[0])
                if rev is not None:
                    ctx = unfi[rev]
                    parents = tuple(p.node() for p in ctx.parents())
                    before = len(store._all)
                    store.create(tr, prec=mark[0], succs=mark[1], flag=mark[2],
                                 metadata=dict(mark[3]), parents=parents)
                    if len(store._all) - before:
                        ui.write(_(b'created new markers for %i\n') % rev)
            ui.progress(pgop, idx, total=pgtotal)
        tr.close()
        ui.progress(pgop, None)
    finally:
        lockmod.release(tr, lock, wlock)
