# Code dedicated to the computation and properties of "stable ranges"
#
# These stable ranges are use for obsolescence markers discovery
#
# Copyright 2017 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
r"""stable range

General Goals and Properties
---------------------------

Stable-ranges get useful when some logic needs a recursive way to slice the
history of a repository in smaller and smaller group of revisions. Here is
example of such use cases:

* **bundle caching:**
  With an easy way to slice any subsets of history into stable-ranges, we
  can cache a small number of bundles covering these ranges and reuse them for
  other pull operations. Even if the pull operation have different boudaries.

* **metadata discovery:**
  With a simple way to recursively look at smaller and smaller ranges, an
  algorithm can do fine-grained discovery of area of history where some mutable
  metadata differ from one repository to another. Such meta data can be
  obsolescence markers, CI status, lightweight stag, etc...

To fix these use cases best, stable-ranges need some important properties:

* the total number of ranges needed to cover a full repository is well bounded.
* the minimal number of ranges to cover an arbitrary subset of the history is well bounded
* for the same section of history, the range will be the same on any
  repositories,
* the ranges are cheap to compute iteratively, each new revisions re-uses the
  ranges previous revisions uses.

Simple introduction to the Concepts
-----------------------------------

To keep things simple, let us look at the issue on a linear history::

  A -> B -> C -> D -> E -> F -> G -> H

To make sure we have range that cover each part of the history with a good
granularity we use some binary recursion. The standard stable range will be:

 [A -> B -> C -> D -> E -> F -> G -> H] size 8
 [A -> B -> C -> D]  [E -> F -> G -> H] size 4
 [A -> B]  [C -> D]  [E -> F]  [G -> H] size 2
 [A]  [B]  [C]  [D]  [E]  [F]  [G]  [H] size 1

Well bounded total number of ranges:
````````````````````````````````````

This binary slicing make sure we keep the total number of stable ranges under control.

As you can see, we have N size 1 ranges. They are trivial and we don't care
about them. Then we have: N/2 size 2 ranges + N/4 size 4 ranges + N/8 size 8
ranges, etc... So a total of about "length(repo)" standard ranges.


Well bounded number of range to cover a subset:
```````````````````````````````````````````````

Any subset of the history can be expressed with this standard ranges.

For example, [A, F] subset, can be covered with 2 ranges::

  [A ->[B -> C -> D]  [E -> F]

A less strivial example [B, F], still requires a small number of ranges (3)::

  [B]  [C -> D]  [E -> F]

In practice, any subset can be expressed in at most "2 x log2(length(subset))"
stable range, well bounded value.

Cheap incremental updates
`````````````````````````

The scheme describe above result in 2N subranges for a repository is size N. We
do not want to have to recompute these 2N stable-ranges whenever a new revision
is added to the repository. To achieve these, the stable-ranges are defined by
**fixed boundaries** that are independant from the total size of the
repository. Here is how it looks like in our example.

We start with a repository having only [A, F]. Notice how we still creates
power of two sized stable range::

  [A -> B -> C -> D]
  [A -> B]  [C -> D]  [E -> F]
  [A]  [B]  [C]  [D]  [E]  [F]

This we simply adds a new revision G, we reuse more the range we already have::

  [A -> B -> C -> D]
  [A -> B]  [C -> D]  [E -> F]
  [A]  [B]  [C]  [D]  [E]  [F]  [G]

Adding H is a bigger even as we read a new boundary.

  [A -> B -> C -> D -> E -> F -> G -> H]
  [A -> B -> C -> D]  [E -> F -> G -> H]
  [A -> B]  [C -> D]  [E -> F]  [G -> H]
  [A]  [B]  [C]  [D]  [E]  [F]  [G]  [H]

At most, adding a new revision `R` will introduces `log2(length(::R))` new
stable ranges.

More advanced elements
----------------------

Of course, the history of repository is not as simple as our linear example. So
how do we deal with the branching and merging? To do so, we leverage the
"stable sort" algorithm defined in the `stablesort.py` module. To define the
stable range that compose a set of revison `::R`, we linearize the space by
sorting it. The stable sort algorithm has two important property:

First, it give the same result on different repository. So we can use it to
algorithm involving multiple peers.

Second, in case of merge, it reuse the same order as the parents as much as possible.
This is important to keep reusing existing stable range as the repository grow.

How are ranges defined?
```````````````````````

To keep things small, and simple, a stable range always contains the final part
of a `stablesort(::R)` set of revision. It is defined by two items:

* its head revision, the R in `stablesort(::R)`
* the size of that range... well almost, for implementation reason, it uses the
  index of the first included item. Or in other word, the number of excluded
  initial item in `stablesort(::R)`.

Lets look at a practical case. In our initial example, `[A, B, C, D, E, F, G,
H]` is H-0; `[E, F, G, H]` is H-4; `[G, H]` is H-6 and `[H]` is H-7.

Let us look at a non linar graph::

 A - B - C - E
       |    /
        -D

and assume that `stablesort(::E) = [A, B, C, D, E]`. Then `[A, B, C]` is C-0,
`[A, B, D]` is D-0; `[D, E]` is E-3, `[E]` is E-4, etc...

Slicing in a non linear context
```````````````````````````````

Branching can also affect the way we slice things.

The small example above offers a simple example. For a size 5 (starting at the
root), standard slicing will want a size 4 part and size 1 part. So, in a
simple linear space `[A, B, C, D, E]` would be sliced as `[A, B, C, D] + [E]`.
However, in our non-linear case, `[A, B, C, D]` has two heads (C and D) and
cannot be expressed with a single range. As a result the range will be sliced
into more sub ranges::

    stdslice(A-0) = [A, B, C] + [D] + [E] = C-0 + D-2 + A-4

Yet, this does not mean ranges containing a merge will always result in slicing
with many revision. the sub ranges might also silently contains them. Let us
look at an exemple::

  A - B - C - D - E --- G - H
        |             /
         ---------- F

with::

  `stablesort(::H) == [A, B, C, D, E, F, G, H]`

then::

  stdslice(H-0) = [A, B, C, D] + [E, F, G, H] = D-0 + H-4

As a result the non linearity will increase the number of subranges involved,
but in practice the impact stay limited.

The total number of standard subranges stay under control with about
`O(log2(N))` new stable range introduced for each new revision. In practice the
total number of stableranges we have is about `O(length(repo))`

In addition, it is worth nothing that the head of the extra ranges we have to
use will match the destination of the "jump" cached by the stablesort
algorithm. So, all this slicing can usually be done without iterating over the
stable sorted revision.

Caching Strategy
----------------

The current caching strategy use a very space inefficient sqlite database.
testing show it often take 100x more space than what basic binary storage would
take. The sqlite storage was very useful at the proof of concept stage.

Since all new stable-ranges introduced by a revision R will be "R headed". So we
could easily store their standard subranges alongside the revision information
to reuse the existing revision index.

Subrange information can be efficiently stored, a naive approach storing all
stable ranges and their subranges would requires just 2 integer per range + 2
integer for any extra sub-ranges other than the first and last ones.

We can probably push efficiency further by taking advantage of the large
overlap in subranges for one non-merge revision to the next. This is probably a
premature optimisation until we start getting actual result for a naive binary
storage.

To use this at a large scale, it would be important to compute these data at
commit time and to exchange them alongside the revision over the network. This
is similar to what we do for other cached data.

It is also important to note that the smaller ranges can probably be computed
on the fly instead of being cached. The exact tradeoff would requires some
field testing.

Performance
-----------

The current implementation has not been especially optimized for performance.
The goal was mostly to get the order of magnitude of the algorithm complexity.
The result are convincing: medium repository get a full cache warming in a
couple of seconds and even very large and branchy repository get a fully warmed
in the order of tens of minutes. We do not observes a complexity explosion
making the algorithm unusable of large repositories.

A better cache implementation combined with an optimized version of the
algorithm should give much faster performance. Combined with commit-time
computation and exchange over the network, the overall impact of this should be
invisible to the user.

The stable range is currently successfully used in production for 2 use cases:
* obsolescence markers discovery,
* caching precomputed bundle while serving pulls

practical data
--------------

The evolve repository:

    number of revisions:          4833
    number of heads:                15
    number of merge:               612 ( 12%)
    number of range:              4826
      with   2 subranges:         4551 ( 94%)
      with   3 subranges:          255 (  5%)
      with   4 subranges:           12 (  0%)
      with   5 subranges:            7 (  0%)
      with   8 subranges:            1 (  0%)
    average range/revs:              0.99

    Estimated approximative size of a naive compact storage:
           41 056 bytes
    Current size of the sqlite cache (for comparison):
        5 312 512 bytes

The mercurial repository:

    number of revisions:         42849
    number of heads:                 2
    number of merge:              2647 (  6%)
    number of range:             41279
      with   2 subranges:        39740 ( 96%)
      with   3 subranges:         1494 (  3%)
      with   4 subranges:           39 (  0%)
      with   5 subranges:            5 (  0%)
      with   7 subranges:            1 (  0%)
    average range/revs:              0.96
    Estimated approximative size of a naive compact storage:
           342 968 bytes
    Current size of the sqlite cache (for comparison):
        62 803 968 bytes

The pypy repository (very brancy history):

    number of revisions:         97409
    number of heads:               183
    number of merge:              8371 (  8%)
    number of range:            107025
      with   2 subranges:       100166 ( 93%)
      with   3 subranges:         5839 (  5%)
      with   4 subranges:          605 (  0%)
      with   5 subranges:          189 (  0%)
      with   6 subranges:           90 (  0%)
      with   7 subranges:           38 (  0%)
      with   8 subranges:           18 (  0%)
      with   9 subranges:            9 (  0%)
      with  10 subranges:           15 (  0%)
      with  11 subranges:            4 (  0%)
      with  12 subranges:            6 (  0%)
      with  13 subranges:            7 (  0%)
      with  14 subranges:            6 (  0%)
      with  15 subranges:            1 (  0%)
      with  16 subranges:            2 (  0%)
      with  17 subranges:            2 (  0%)
      with  18 subranges:            3 (  0%)
      with  19 subranges:            2 (  0%)
      with  20 subranges:            3 (  0%)
      with  25 subranges:            1 (  0%)
      with  27 subranges:            1 (  0%)
      with  31 subranges:            3 (  0%)
      with  32 subranges:            2 (  0%)
      with  33 subranges:            1 (  0%)
      with  35 subranges:            1 (  0%)
      with  43 subranges:            1 (  0%)
      with  44 subranges:            1 (  0%)
      with  45 subranges:            2 (  0%)
      with  47 subranges:            1 (  0%)
      with  51 subranges:            1 (  0%)
      with  52 subranges:            1 (  0%)
      with  57 subranges:            1 (  0%)
      with  65 subranges:            1 (  0%)
      with  73 subranges:            1 (  0%)
      with  79 subranges:            1 (  0%)
    average range/revs:              1.10
    Estimated approximative size of a naive compact storage:
          934 176 bytes
    Current size of the sqlite cache (for comparison):
      201 236 480 bytes

A private and branchy repository:

    number of revisions:        605011
    number of heads:             14061
    number of merge:            118109 ( 19%)
    number of range:            747625
      with   2 subranges:       595985 ( 79%)
      with   3 subranges:       130196 ( 17%)
      with   4 subranges:        14093 (  1%)
      with   5 subranges:         4090 (  0%)
      with   6 subranges:          741 (  0%)
      with   7 subranges:          826 (  0%)
      with   8 subranges:         1313 (  0%)
      with   9 subranges:           83 (  0%)
      with  10 subranges:           22 (  0%)
      with  11 subranges:            9 (  0%)
      with  12 subranges:           26 (  0%)
      with  13 subranges:            5 (  0%)
      with  14 subranges:            9 (  0%)
      with  15 subranges:            3 (  0%)
      with  16 subranges:          212 (  0%)
      with  18 subranges:            6 (  0%)
      with  19 subranges:            3 (  0%)
      with  24 subranges:            1 (  0%)
      with  27 subranges:            1 (  0%)
      with  32 subranges:            1 (  0%)
    average range/revs:              1.23
    Estimated approximative size of a naive compact storage:
        7 501 928 bytes
    Current size of the sqlite cache (for comparison):
    1 950 310 400 bytes
"""

import abc
import functools
import heapq
import math
import time

from mercurial import (
    error,
    node as nodemod,
    scmutil,
    util,
)

from mercurial.i18n import _

from . import (
    compat,
    exthelper,
    firstmergecache,
    stablesort,
    utility,
)

filterparents = utility.filterparents

eh = exthelper.exthelper()


#################################
### Stable Range computation  ###
#################################

def _hlp2(i):
    """return highest power of two lower than 'i'"""
    return 2 ** int(math.log(i - 1, 2))

def subrangesclosure(repo, stablerange, heads):
    """set of all standard subrange under heads

    This is intended for debug purposes. Range are returned from largest to
    smallest in terms of number of revision it contains."""
    subranges = stablerange.subranges
    toproceed = [(r, 0, ) for r in heads]
    ranges = set(toproceed)
    while toproceed:
        entry = toproceed.pop()
        for r in subranges(repo, entry):
            if r not in ranges:
                ranges.add(r)
                toproceed.append(r)
    ranges = list(ranges)
    n = repo.changelog.node
    rangelength = stablerange.rangelength
    ranges.sort(key=lambda r: (-rangelength(repo, r), n(r[0])))
    return ranges

_stablerangemethodmap = {
    b'branchpoint': lambda repo: stablerange(),
    b'default': lambda repo: repo.stablerange,
    b'basic-branchpoint': lambda repo: stablerangebasic(),
    b'basic-mergepoint': lambda repo: stablerangedummy_mergepoint(),
    b'mergepoint': lambda repo: stablerange_mergepoint(),
}

@eh.command(
    b'debugstablerange',
    [
        (b'r', b'rev', [], b'operate on (rev, 0) ranges for rev in REVS'),
        (b'', b'subranges', False, b'recursively display data for subranges too'),
        (b'', b'verify', False, b'checks subranges content (EXPENSIVE)'),
        (b'', b'method', b'branchpoint',
         b'method to use, one of "branchpoint", "mergepoint"')
    ],
    _(b''))
def debugstablerange(ui, repo, **opts):
    """display standard stable subrange for a set of ranges

    Range as displayed as '<node>-<index> (<rev>, <depth>, <length>)', use
    --verbose to get the extra details in ().
    """
    short = nodemod.short
    revs = scmutil.revrange(repo, opts['rev'])
    if not revs:
        raise error.Abort(b'no revisions specified')
    if ui.verbose:
        template = b'%s-%d (%d, %d, %d)'

        def _rangestring(repo, rangeid):
            return template % (
                short(node(rangeid[0])),
                rangeid[1],
                rangeid[0],
                depth(unfi, rangeid[0]),
                length(unfi, rangeid)
            )
    else:
        template = b'%s-%d'

        def _rangestring(repo, rangeid):
            return template % (
                short(node(rangeid[0])),
                rangeid[1],
            )
    # prewarm depth cache
    unfi = repo.unfiltered()
    node = unfi.changelog.node

    method = opts['method']
    getstablerange = _stablerangemethodmap.get(method)
    if getstablerange is None:
        raise error.Abort(b'unknown stable sort method: "%s"' % method)

    stablerange = getstablerange(unfi)
    depth = stablerange.depthrev
    length = stablerange.rangelength
    subranges = stablerange.subranges
    stablerange.warmup(repo, max(revs))

    if opts['subranges']:
        ranges = subrangesclosure(unfi, stablerange, revs)
    else:
        ranges = [(r, 0) for r in revs]

    for r in ranges:
        subs = subranges(unfi, r)
        subsstr = b', '.join(_rangestring(unfi, s) for s in subs)
        rstr = _rangestring(unfi, r)
        if opts['verify']:
            status = b'leaf'
            if 1 < length(unfi, r):
                status = b'complete'
                revs = set(stablerange.revsfromrange(unfi, r))
                subrevs = set()
                for s in subs:
                    subrevs.update(stablerange.revsfromrange(unfi, s))
                if revs != subrevs:
                    status = b'missing'
            ui.status(b'%s [%s] - %s\n' % (rstr, status, subsstr))
        else:
            ui.status(b'%s - %s\n' % (rstr, subsstr))

class abstractstablerange(object):
    """The official API for a stablerange"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def subranges(self, repo, rangeid):
        """return the stable sub-ranges of a rangeid"""
        raise NotImplementedError()

    @abc.abstractmethod
    def revsfromrange(self, repo, rangeid):
        """return revision contained in a range"""
        raise NotImplementedError()

    @abc.abstractmethod
    def depthrev(self, repo, rev):
        """depth a revision"""
        # Exist to allow basic implementation to ignore the depthcache
        # Could be demoted to _depthrev.
        raise NotImplementedError()

    @abc.abstractmethod
    def warmup(self, repo, upto=None):
        """warmup the stable range cache"""
        raise NotImplementedError()

    @abc.abstractmethod
    def rangelength(self, repo, rangeid):
        """number of revision in <range>"""
        raise NotImplementedError()

    def _slicepoint(self, repo, rangeid):
        """find the standard slicing point for a range"""
        rangedepth = self.depthrev(repo, rangeid[0])
        step = _hlp2(rangedepth)
        standard_start = 0
        while standard_start < rangeid[1] and 0 < step:
            if standard_start + step < rangedepth:
                standard_start += step
            step //= 2
        if rangeid[1] == standard_start:
            slicesize = _hlp2(self.rangelength(repo, rangeid))
            slicepoint = rangeid[1] + slicesize
        else:
            assert standard_start < rangedepth
            slicepoint = standard_start
        return slicepoint
class stablerangebasic(abstractstablerange):
    """a very dummy implementation of stablerange

    the implementation is here to lay down the basic algorithm in the stable
    range in a inefficient but easy to read manners. It should be used by test
    to validate output."""

    __metaclass__ = abc.ABCMeta

    def _sortfunction(self, repo, headrev):
        return stablesort.stablesort_branchpoint(repo, [headrev])

    def warmup(self, repo, upto=None):
        # no cache to warm for basic implementation
        pass

    def depthrev(self, repo, rev):
        """depth a revision"""
        return len(repo.revs(b'::%d', rev))

    def revsfromrange(self, repo, rangeid):
        """return revision contained in a range

        The range `(<head>, <skip>)` contains all revisions stable-sorted from
        <head>, skipping the <index>th lower revisions.
        """
        headrev, index = rangeid[0], rangeid[1]
        revs = self._sortfunction(repo, headrev)
        return revs[index:]

    def rangelength(self, repo, rangeid):
        """number of revision in <range>"""
        return len(self.revsfromrange(repo, rangeid))

    def subranges(self, repo, rangeid):
        """return the stable sub-ranges of a rangeid"""
        headrev, index = rangeid[0], rangeid[1]
        if self.rangelength(repo, rangeid) == 1:
            return []
        slicepoint = self._slicepoint(repo, rangeid)

        # search for range defining the lower set of revision
        #
        # we walk the lower set from the top following the stable order of the
        # current "head" of the lower range.
        #
        # As soon as the revision in the lowerset diverges from the one in the
        # range being generated, we emit the range and start a new one.
        result = []
        lowerrevs = self.revsfromrange(repo, rangeid)[:(slicepoint - index)]
        head = None
        headrange = None
        skip = None
        for rev in lowerrevs[::-1]:
            if head is None:
                head = rev
                headrange = self.revsfromrange(repo, (head, 0))
                skip = self.depthrev(repo, rev) - 1
            elif rev != headrange[skip - 1]:
                result.append((head, skip))
                head = rev
                headrange = self.revsfromrange(repo, (head, 0))
                skip = self.depthrev(repo, rev) - 1
            else:
                skip -= 1
        result.append((head, skip))

        result.reverse()

        # top part is trivial
        top = (headrev, slicepoint)
        result.append(top)

        # double check the result
        initialrevs = self.revsfromrange(repo, rangeid)
        subrangerevs = sum((self.revsfromrange(repo, sub) for sub in result),
                           [])
        assert initialrevs == subrangerevs
        return result

class stablerangedummy_mergepoint(stablerangebasic):
    """a very dummy implementation of stablerange use 'mergepoint' sorting
    """

    def _sortfunction(self, repo, headrev):
        return stablesort.stablesort_mergepoint_head_basic(repo, [headrev])

class stablerangecached(abstractstablerange):
    """an implementation of stablerange using caching"""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        # cache the standard stable subranges or a range
        self._subrangescache = {}
        super(stablerangecached, self).__init__()

    def depthrev(self, repo, rev):
        return repo.depthcache.get(rev)

    def rangelength(self, repo, rangeid):
        """number of revision in <range>"""
        headrev, index = rangeid[0], rangeid[1]
        return self.depthrev(repo, headrev) - index

    def subranges(self, repo, rangeid):
        assert 0 <= rangeid[1] <= rangeid[0], rangeid
        cached = self._getsub(rangeid)
        if cached is not None:
            return cached
        value = self._subranges(repo, rangeid)
        self._setsub(rangeid, value)
        return value

    def _getsub(self, rev):
        """utility function used to access the subranges cache

        This mostly exist to help the on disk persistence"""
        return self._subrangescache.get(rev)

    def _setsub(self, rev, value):
        """utility function used to set the subranges cache

        This mostly exist to help the on disk persistence."""
        self._subrangescache[rev] = value

class stablerange_mergepoint(stablerangecached):
    """Stablerange implementation using 'mergepoint' based sorting
    """

    def __init__(self):
        super(stablerange_mergepoint, self).__init__()

    def warmup(self, repo, upto=None):
        # no cache to warm for basic implementation
        pass

    def revsfromrange(self, repo, rangeid):
        """return revision contained in a range

        The range `(<head>, <skip>)` contains all revisions stable-sorted from
        <head>, skipping the <index>th lower revisions.
        """
        limit = self.rangelength(repo, rangeid)
        return repo.stablesort.get(repo, rangeid[0], limit=limit)

    def _stableparent(self, repo, headrev):
        """The parent of the changeset with reusable subrange

        For non-merge it is simple, there is a single parent. For Mercurial we
        have to find the right one. Since the stable sort use merge-point, we
        know that one of REV parents stable sort is a subset of REV stable
        sort. In other word:

            sort(::REV) = sort(::min(parents(REV))
                          + sort(only(max(parents(REV)), min(parents(REV)))
                          + [REV]

        We are looking for that `min(parents(REV))`. Since the subrange are
        based on the sort, we can reuse its subrange as well.
        """
        ps = filterparents(repo.changelog.parentrevs(headrev))
        if not ps:
            return nodemod.nullrev
        elif len(ps) == 1:
            return ps[0]
        else:
            tiebreaker = stablesort._mergepoint_tie_breaker(repo)
            return min(ps, key=tiebreaker)

    def _parentrange(self, repo, rangeid):
        stable_parent = self._stableparent(repo, rangeid[0])
        stable_parent_depth = self.depthrev(repo, stable_parent)
        stable_parent_range = (stable_parent, rangeid[1])
        return stable_parent_depth, stable_parent_range

    def _warmcachefor(self, repo, rangeid, slicepoint):
        """warm cache with all the element necessary"""
        stack = []
        depth, current = self._parentrange(repo, rangeid)
        while current not in self._subrangescache and slicepoint < depth:
            stack.append(current)
            depth, current = self._parentrange(repo, current)
        while stack:
            current = stack.pop()
            self.subranges(repo, current)

    def _subranges(self, repo, rangeid):
        headrev, initial_index = rangeid
        # size 1 range can't be sliced
        if self.rangelength(repo, rangeid) == 1:
            return []
        # find were we need to slice
        slicepoint = self._slicepoint(repo, rangeid)

        ret = self._slicesrangeat(repo, rangeid, slicepoint)

        return ret

    def _slicesrangeat(self, repo, rangeid, slicepoint):
        headrev, initial_index = rangeid
        self._warmcachefor(repo, rangeid, slicepoint)

        stable_parent_data = self._parentrange(repo, rangeid)
        stable_parent_depth, stable_parent_range = stable_parent_data

        # top range is always the same, so we can build it early for all
        top_range = (headrev, slicepoint)

        # now find out about the lower range, if we are lucky there is only
        # one, otherwise we need to issue multiple one to cover every revision
        # on the lower set. (and cover them only once).
        if slicepoint == stable_parent_depth:
            # luckly shot, the parent is actually the head of the lower range
            subranges = [
                stable_parent_range,
                top_range,
            ]
        elif slicepoint < stable_parent_depth:
            # The parent is above the slice point,
            # it's lower subrange will be the same so we just get them,
            # (and the top range is always the same)
            subranges = self.subranges(repo, stable_parent_range)[:]
            parenttop = subranges.pop()
            lenparenttop = self.rangelength(repo, parenttop)
            skimfromparent = stable_parent_depth - slicepoint
            if lenparenttop < skimfromparent:
                # dropping the first subrange of the stable parent range is not
                # enough to skip what we need to skip, change in approach is needed
                subranges = self._slicesrangeat(repo, stable_parent_range, slicepoint)
                subranges.pop()
            elif lenparenttop > skimfromparent:
                # The first subrange of the parent is longer that what we want
                # to drop, we need to keep some of it.
                midranges = self._slicesrangeat(repo, parenttop, slicepoint)
                subranges.extend(midranges[:-1])
            subranges.append(top_range)
        elif initial_index < stable_parent_depth < slicepoint:
            # the parent is below the range we are considering, we need to
            # compute these uniques subranges
            subranges = [stable_parent_range]
            subranges.extend(self._unique_subranges(repo, headrev,
                                                    stable_parent_depth,
                                                    slicepoint))
            subranges.append(top_range)
        else:
            # we cannot reuse the parent range at all
            subranges = list(self._unique_subranges(repo, headrev,
                                                    initial_index,
                                                    slicepoint))
            subranges.append(top_range)

        ### slow code block to validated the slicing works as expected
        # toprevs = self.revsfromrange(repo, rangeid)
        # subrevs = []
        # for s in subranges:
        #     subrevs.extend(self.revsfromrange(repo, s))
        # assert toprevs == subrevs, (rangeid, slicepoint, stable_parent_range, stable_parent_depth, toprevs, subrevs)

        return subranges

    def _unique_subranges(self, repo, headrev, initial_index, slicepoint):
        """Compute subrange unique to the exclusive part of merge"""
        result = []
        depth = repo.depthcache.get
        nextmerge = repo.firstmergecache.get
        walkfrom = functools.partial(repo.stablesort.walkfrom, repo)
        getjumps = functools.partial(repo.stablesort.getjumps, repo)
        skips = depth(headrev) - slicepoint
        tomap = slicepoint - initial_index

        jumps = getjumps(headrev)
        # this function is only caled if headrev is a merge
        # and initial_index is above its lower parents
        assert jumps is not None
        jumps = iter(jumps)
        assert 0 < skips, skips
        assert 0 < tomap, (tomap, (headrev, initial_index), slicepoint)

        # utility function to find the next changeset with jump information
        # (and the distance to it)
        def nextmergedata(startrev):
            merge = nextmerge(startrev)
            depthrev = depth(startrev)
            if merge == startrev:
                return 0, startrev
            elif merge == nodemod.nullrev:
                return depthrev, None
            depthmerge = depth(merge)
            return depthrev - depthmerge, merge

        # skip over all necesary data
        mainjump = None
        jumpdest = headrev
        while 0 < skips:
            jumphead = jumpdest
            currentjump = next(jumps)
            skipped = size = currentjump[2]
            jumpdest = currentjump[1]
            if size == skips:
                jumphead = jumpdest
                mainjump = next(jumps)
                mainsize = mainjump[2]
            elif skips < size:
                revs = walkfrom(jumphead)
                next(revs)
                for i in range(skips):
                    jumphead = next(revs)
                    assert jumphead is not None
                skipped = skips
                size -= skips
                mainjump = currentjump
                mainsize = size
            skips -= skipped
        assert skips == 0, skips

        # exiting from the previous block we should have:
        # jumphead: first non-skipped revision (head of the high subrange)
        # mainjump: next jump coming jump on main iteration
        # mainsize: len(mainjump[0]::jumphead)

        # Now we need to compare walk on the main iteration with walk from the
        # current subrange head. Instead of doing a full walk, we just skim
        # over the jumps for each iteration.
        rangehead = jumphead
        refjumps = None
        size = 0
        while size < tomap:
            assert mainjump is not None
            if refjumps is None:
                dist2merge, merge = nextmergedata(jumphead)
                if (mainsize <= dist2merge) or merge is None:
                    refjumps = iter(())
                    ref = None
                else:
                    # advance counters
                    size += dist2merge
                    mainsize -= dist2merge
                    jumphead = merge
                    refjumps = iter(getjumps(merge))
                    ref = next(refjumps, None)
            elif ref is not None and mainjump[0:2] == ref[0:2]:
                # both follow the same path
                size += mainsize
                jumphead = mainjump[1]
                mainjump = next(jumps, None)
                mainsize = mainjump[2]
                ref = next(refjumps, None)
                if ref is None:
                    # we are doing with section specific to the last merge
                    # reset `refjumps` to trigger the logic that search for the
                    # next merge
                    refjumps = None
            else:
                size += mainsize
                if size < tomap:
                    subrange = (rangehead, depth(rangehead) - size)
                    assert subrange[1] < depth(subrange[0])
                    result.append(subrange)
                    tomap -= size
                    size = 0
                    jumphead = rangehead = mainjump[1]
                    mainjump = next(jumps, None)
                    mainsize = mainjump[2]
                    refjumps = None

        if tomap:
            subrange = (rangehead, depth(rangehead) - tomap)
            assert subrange[1] < depth(subrange[0]), (rangehead, depth(rangehead), tomap)
            result.append(subrange)
        result.reverse()
        return result

class stablerange(stablerangecached):

    def __init__(self, lrusize=2000):
        # The point up to which we have data in cache
        self._tiprev = None
        self._tipnode = None
        # To slices merge, we need to walk their descendant in reverse stable
        # sort order. For now we perform a full stable sort their descendant
        # and then use the relevant top most part. This order is going to be
        # the same for all ranges headed at the same merge. So we cache these
        # value to reuse them accross the same invocation.
        self._stablesortcache = util.lrucachedict(lrusize)
        # something useful to compute the above
        # mergerev -> stablesort, length
        self._stablesortprepared = util.lrucachedict(lrusize)
        # caching parent call # as we do so many of them
        self._parentscache = {}
        # The first part of the stable sorted list of revision of a merge will
        # shared with the one of others. This means we can reuse subranges
        # computed from that point to compute some of the subranges from the
        # merge.
        self._inheritancecache = {}
        super(stablerange, self).__init__()

    def warmup(self, repo, upto=None):
        """warm the cache up"""
        repo = repo.unfiltered()
        repo.depthcache.update(repo)
        cl = repo.changelog
        # subrange should be warmed from head to range to be able to benefit
        # from revsfromrange cache. otherwise each merge will trigger its own
        # stablesort.
        #
        # we use the revnumber as an approximation for depth
        ui = repo.ui
        starttime = util.timer()

        if upto is None:
            upto = len(cl) - 1
        if self._tiprev is None:
            revs = cl.revs(stop=upto)
            nbrevs = upto + 1
        else:
            assert cl.node(self._tiprev) == self._tipnode
            if upto <= self._tiprev:
                return
            revs = cl.revs(start=self._tiprev + 1, stop=upto)
            nbrevs = upto - self._tiprev
        rangeheap = []
        for idx, r in enumerate(revs):
            if not idx % 1000:
                compat.progress(ui, _(b"filling depth cache"), idx, total=nbrevs,
                                unit=_(b"changesets"))
            # warm up depth
            self.depthrev(repo, r)
            rangeheap.append((-r, (r, 0)))
        compat.progress(ui, _(b"filling depth cache"), None, total=nbrevs)

        heappop = heapq.heappop
        heappush = heapq.heappush
        heapify = heapq.heapify

        original = set(rangeheap)
        seen = 0
        # progress report is showing up in the profile for small and fast
        # repository so we build that complicated work around.
        progress_each = 100
        progress_last = time.time()
        heapify(rangeheap)
        while rangeheap:
            value = heappop(rangeheap)
            if value in original:
                if not seen % progress_each:
                    # if a lot of time passed, report more often
                    progress_new = time.time()
                    if (1 < progress_each) and (0.1 < progress_new - progress_last):
                        progress_each /= 10
                    compat.progress(ui, _(b"filling stablerange cache"), seen,
                                    total=nbrevs, unit=_(b"changesets"))
                    progress_last = progress_new
                seen += 1
                original.remove(value) # might have been added from other source
            __, rangeid = value
            if self._getsub(rangeid) is None:
                for sub in self.subranges(repo, rangeid):
                    if self._getsub(sub) is None:
                        heappush(rangeheap, (-sub[0], sub))
        compat.progress(ui, _(b"filling stablerange cache"), None, total=nbrevs)

        self._tiprev = upto
        self._tipnode = cl.node(upto)

        duration = util.timer() - starttime
        repo.ui.log(b'evoext-cache', b'updated stablerange cache in %.4f seconds\n',
                    duration)

    def subranges(self, repo, rangeid):
        cached = self._getsub(rangeid)
        if cached is not None:
            return cached
        value = self._subranges(repo, rangeid)
        self._setsub(rangeid, value)
        return value

    def revsfromrange(self, repo, rangeid):
        headrev, index = rangeid
        rangelength = self.rangelength(repo, rangeid)
        if rangelength == 1:
            revs = [headrev]
        else:
            # get all revs under heads in stable order
            #
            # note: In the general case we can just walk down and then request
            # data about the merge. But I'm not sure this function will be even
            # call for the general case.

            allrevs = self._stablesortcache.get(headrev)
            if allrevs is None:
                allrevs = self._getrevsfrommerge(repo, headrev)
                if allrevs is None:
                    mc = self._filestablesortcache
                    sorting = stablesort.stablesort_branchpoint
                    allrevs = sorting(repo, [headrev], mergecallback=mc)
                self._stablesortcache[headrev] = allrevs
            # takes from index
            revs = allrevs[index:]
        # sanity checks
        assert len(revs) == rangelength
        return revs

    def _parents(self, rev, func):
        parents = self._parentscache.get(rev)
        if parents is None:
            parents = func(rev)
            self._parentscache[rev] = parents
        return parents

    def _getsub(self, rev):
        """utility function used to access the subranges cache

        This mostly exist to help the on disk persistence"""
        return self._subrangescache.get(rev)

    def _setsub(self, rev, value):
        """utility function used to set the subranges cache

        This mostly exist to help the on disk persistence."""
        self._subrangescache[rev] = value

    def _filestablesortcache(self, sortedrevs, merge):
        if merge not in self._stablesortprepared:
            self._stablesortprepared[merge] = (sortedrevs, len(sortedrevs))

    def _getrevsfrommerge(self, repo, merge):
        prepared = self._stablesortprepared.get(merge)
        if prepared is None:
            return None

        mergedepth = self.depthrev(repo, merge)
        allrevs = prepared[0][:prepared[1]]
        nbextrarevs = prepared[1] - mergedepth
        if not nbextrarevs:
            return allrevs

        anc = repo.changelog.ancestors([merge], inclusive=True)
        top = []
        counter = nbextrarevs
        for rev in reversed(allrevs):
            if rev in anc:
                top.append(rev)
            else:
                counter -= 1
                if counter <= 0:
                    break

        bottomidx = prepared[1] - (nbextrarevs + len(top))
        revs = allrevs[:bottomidx]
        revs.extend(reversed(top))
        return revs

    def _inheritancepoint(self, repo, merge):
        """Find the inheritance point of a Merge

        The first part of the stable sorted list of revision of a merge will shared with
        the one of others. This means we can reuse subranges computed from that point to
        compute some of the subranges from the merge.

        That point is latest point in the stable sorted list where the depth of the
        revisions match its index (that means all revision earlier in the stable sorted
        list are its ancestors, no dangling unrelated branches exists).
        """
        value = self._inheritancecache.get(merge)
        if value is None:
            revs = self.revsfromrange(repo, (merge, 0))
            i = reversed(revs)
            next(i) # pop the merge
            expected = len(revs) - 1
            # Since we do warmup properly, we can expect the cache to be hot
            # for everythin under the merge we investigate
            cache = repo.depthcache
            # note: we cannot do a binary search because element under the
            # inherited point might have mismatching depth because of inner
            # branching.
            for rev in i:
                if cache.get(rev) == expected:
                    break
                expected -= 1
            value = (expected - 1, rev)
            self._inheritancecache[merge] = value
        return value

    def _subranges(self, repo, rangeid):
        if self.rangelength(repo, rangeid) == 1:
            return []
        slicepoint = self._slicepoint(repo, rangeid)

        # make sure we have cache for all relevant parent first to prevent
        # recursion (python is bad with recursion
        stack = []
        current = rangeid
        while current is not None:
            current = self._cold_reusable(repo, current, slicepoint)
            if current is not None:
                stack.append(current)
        while stack:
            # these call will directly compute the subranges
            self.subranges(repo, stack.pop())
        return self._slicesrangeat(repo, rangeid, slicepoint)

    def _cold_reusable(self, repo, rangeid, slicepoint):
        """return parent range that it would be useful to prepare to slice
        rangeid at slicepoint

        This function also have the important task to update the revscache of
        the parent rev s if possible and needed"""
        ps = filterparents(self._parents(rangeid[0], repo.changelog.parentrevs))
        if not ps:
            return None
        elif len(ps) == 1:
            # regular changesets, we pick the parent
            reusablerev = ps[0]
        else:
            # merge, we try the inheritance point
            # if it is too low, it will be ditched by the depth check anyway
            index, reusablerev = self._inheritancepoint(repo, rangeid[0])

        # if we reached the slicepoint, no need to go further
        if self.depthrev(repo, reusablerev) <= slicepoint:
            return None

        reurange = (reusablerev, rangeid[1])
        # if we have an entry for the current range, lets update the cache
        # if we already have subrange for this range, no need to prepare it.
        if self._getsub(reurange) is not None:
            return None

        # look like we found a relevent parentrange with no cache yet
        return reurange

    def _slicesrangeat(self, repo, rangeid, globalindex):
        ps = self._parents(rangeid[0], repo.changelog.parentrevs)
        if len(ps) == 1:
            reuserev = ps[0]
        else:
            index, reuserev = self._inheritancepoint(repo, rangeid[0])
            if index < globalindex:
                return self._slicesrangeatmerge(repo, rangeid, globalindex)

        assert reuserev != nodemod.nullrev

        reuserange = (reuserev, rangeid[1])
        top = (rangeid[0], globalindex)

        if rangeid[1] + self.rangelength(repo, reuserange) == globalindex:
            return [reuserange, top]
        # This will not initiate a recursion since we took appropriate
        # precaution in the caller of this method to ensure it will be so.
        # It the parent is a merge that will not be the case but computing
        # subranges from a merge will not recurse.
        reusesubranges = self.subranges(repo, reuserange)
        slices = reusesubranges[:-1] # pop the top
        slices.append(top)
        return slices

    def _slicesrangeatmerge(self, repo, rangeid, globalindex):
        localindex = globalindex - rangeid[1]

        result = []
        allrevs = self.revsfromrange(repo, rangeid)
        bottomrevs = allrevs[:localindex]

        if globalindex == self.depthrev(repo, bottomrevs[-1]):
            # simple case, top revision in the bottom set contains exactly the
            # revision we needs
            result.append((bottomrevs[-1], rangeid[1]))
        else:
            head = None
            headrange = None
            skip = None
            for rev in bottomrevs[::-1]:
                if head is None:
                    head = rev
                    headrange = self.revsfromrange(repo, (head, 0))
                    skip = self.depthrev(repo, rev) - 1
                elif rev != headrange[skip - 1]:
                    result.append((head, skip))
                    head = rev
                    headrange = self.revsfromrange(repo, (head, 0))
                    skip = self.depthrev(repo, rev) - 1
                else:
                    skip -= 1
            result.append((head, skip))

            result.reverse()

        # top part is trivial
        top = (rangeid[0], globalindex)
        result.append(top)
        return result

# merge later for outer layer wrapping
eh.merge(stablesort.eh)
eh.merge(firstmergecache.eh)
