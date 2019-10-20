from __future__ import print_function
from blessed import Terminal
from .block import Block, Grid, SizePref, DEFAULT_SIZE_PREF, QueueEntry
from math import floor, ceil
from threading import Event, Thread, RLock, current_thread
from werkzeug import local
from queue import Queue, Empty
from time import sleep
import sys
from io import StringIO
import signal
import logging
from collections import namedtuple
from tempfile import NamedTemporaryFile

# A Plot is an object-oriented realization of the information contained in
# the Grid object inside the Runner's Block object (attribute). We don't
# force the Block developer to handle this complexity.
#
# Instead, the Block developer is responsible only for the Grid: a map of numbers
# to blocks, and a layout containing some or all of the (number) keys in the map.
# The layout is a recursive structure containing only Python lists, tuples, and
# numbers. (For example: [1, [(2,3), [4, 5]]] ). The digits signify leaf blocks
# (those not containing a Grid of blocks embedded within it). _Lists_ inside the
# layout signify horizontal orientation of the blocks it contains, and _tuples_,
# horizontal orientation. The problem with this simple specification of a layout --
# just lists, tuple, and digits for the convenience of the Block developer --
# is that it's not possible (without subclassing, which doesn't work well here)
# to hang metadata on the lists and tuples. We need that metadata to know how to
# divvy up the space available to each of the leaf blocks within the list or tuple,
# given the space available to the list or tuple as a whole. This metadata is the
# SizePrefs each Block declares.
#
# We use Plots to objectify the Grid as follows. A leaf Block gets wrapped
# in a Plot object together with the block's own SizePrefs, or the default ones
# if it doesn't have any specified. A list or tuple in a layout is built into a
# Plot object using the Blocks it contains, but its SizePref's arg is calculated
# by the merging of the SizePrefs of those blocks. This is the metadata referred
# to above.
#
# So, building a Plot requires a recursive procedure. On the way down from the
# outermost block, we build a tree of Plots as we go down. It's _on the way back
# up_, though, that we calcuate SizePrefs for the Plots that represent lists
# or tuples.
#
# Once the plot tree is fully built, the x and y coordinates and width and height
# of each block have been produced, and each block can be passed that information,
# which it uses to display itself.

# Uncomment to debug deadlock problems
#import stacktracer
#stacktracer.trace_start("/tmp/trace.html",interval=2,auto=True)

Lifeline = namedtuple('Lifeline', 'stderr msg_queue')


class Plot(object):
    def __init__(self,
                 w_sizepref=None,
                 h_sizepref=None,
                 horizontal=True,
                 subplots=None,
                 block = None):
        self.w_sizepref = w_sizepref
        self.h_sizepref = h_sizepref
        self.subplots = subplots
        self.horizontal = horizontal
        self.block = block

    def __repr__(self):
        me ='[ z={} chld={} wsp={}, hsp={}'.format(self.horizontal,
                                                   len(self.subplots) if self.subplots else 0,
                                                   self.w_sizepref,
                                                   self.h_sizepref)

        if self.subplots:
            for subplot in self.subplots:
                me = me + '\n\t' + repr(subplot)
        me = me + ' ]'
        return me

class Runner(object):

    def __init__(self, grid, stop_event=None, stderr_filename=None):

        self._grid = grid
        self._plot = Plot()
        self._done = Event()
        self._term = Terminal()
        self._lock = RLock()
        self._stop_event = stop_event if stop_event else Event()
        self._root_plot = None
        self.rebuild_plot_q = Queue()
        self._stderr = StdErrRedirector(stderr_filename)
        self.init_grid(self._grid)
        self.load()
        self._grid.runner = self

    def __repr__(self):
        return 'runner'

    def term_width(self):
        return self._term.width

    def term_height(self):
        return self._term.height

    def _on_kill(self, *args):
        #if self._grid._cmds and 'input' in self._grid._names:
        if 'input' in self._grid._names:
            self._grid._names['input'].status = 'KeyboardInterrupt (Control-D to exit)'
            self._grid._names['input'].text = ''
        else:
            #if self._grid._cmds:
            self.rebuild_plot_q.put(QueueEntry('stop', None, None))

    def update_all(self):
        if self.rebuild_plot_q.empty():
            self.rebuild_plot_q.put(QueueEntry('', None, None))  # '' is empty cmd

    def _on_resize(self, *args):
        self.update_all()

    def start(self):

        self._thread = Thread(
            name='runner',
            target=self._run,
            args=()
        )

        #if self._grid._cmds:
        self._io_thread = Thread(name='io', target=self._read_cmd, args=())

        signal.signal(signal.SIGWINCH, self._on_resize)
        signal.signal(signal.SIGINT, self._on_kill)

        #if self._grid._cmds:
        self._io_thread.start()
        self._thread.start()

    def stop(self, *args):
        self._term.clear()
        if not self._done.is_set():
            self._done.set()
            self.rebuild_plot_q.put(QueueEntry('', None, None))  # '' is empty cmd

            if (self._thread and self._thread.isAlive() and
                self._thread.name != current_thread().name):
                self._thread.join()
            if (self._io_thread and self._io_thread.isAlive() and
                self._io_thread.name != current_thread().name):
                self._io_thread.join()
            self._stop_event.set()        # app waits on this event

    def done(self):
        return not self._thread.isAlive() or self._done.is_set()

    def _read_cmd(self):
        self._stderr.redirect()
        PROMPT = ''
        with self._term.cbreak():
            if 'input' not in self._grid._names:
                return
            input_block = self._grid._names['input']
            input_block.text = PROMPT
            while True:
                val = self._term.inkey(timeout=.5)
                if not val:  # timeout
                    if self._done.is_set():
                        break
                    continue
                else:
                    input_block.status = input_block.default_status
                if val.is_sequence:
                    if val.name == 'KEY_ENTER':
                        # if not cmd: ??? maybe refresh something? or redo previous?
                        cmd, *args = input_block.text.strip().split(Block.MIDDLE_DOT)
                        if cmd == 'stop' or cmd in self._grid._cmds:
                            self.rebuild_plot_q.put(QueueEntry(cmd, args, None))
                        elif input_block.text:
                            input_block.status = 'Unknown command: {}'.format(cmd)
                        input_block.text = PROMPT
                    elif val.name == 'KEY_DELETE':
                        input_block.text = input_block.text[:-1]
                    elif val.name == 'KEY_ESCAPE':
                        pass  # hmmmm
                    else:
                        # TODO ignore?
                        input_block.text = PROMPT
                else:
                    if not val.isalnum():
                        if ord(val) == 4:  # ctl-d
                            input_block.status = 'Exiting'
                            self.rebuild_plot_q.put(QueueEntry('stop', None, None))
                            self.stop()
                        if ord(val) == 32: # space
                            input_block.text += Block.MIDDLE_DOT
                    elif not input_block.text and val in self._grid._cmds:
                        # Handles one-char-no-return commands
                        self.rebuild_plot_q.put(QueueEntry(val, None, None))
                    else:
                        input_block.text += val

    def _run(self):
        self._stderr._enable_proxy()
        self._stderr.redirect()
        self.rebuild_plot_q.put(QueueEntry('', None, None))  # show at start once
        with self._term.fullscreen():
            with self._term.hidden_cursor():
                try:
                    while True:
                        if self._done.is_set() and self.rebuild_plot_q.empty():
                            break
                        try:
                            entry = self.rebuild_plot_q.get(timeout=10)
                            if entry and entry.cmd:  # requeue it, we don't process it here
                                self.rebuild_plot_q.put(entry)
                                if entry.cmd == 'stop':
                                    self.stop()
                        except Empty:
                            pass

                        with self._lock:
                            self.load()
                            self.display_plot(self._root_plot,
                                              0, 0,                                 # x, y
                                              self._term.width, self._term.height,  # w, h
                                              self._term)
                except Exception as e:
                    debug = True
                    print(str(e))

                    if debug:
                        logging.exception("10 seconds to view exception")
                        sleep(10)
                    self.stop()

    def update(self):
        if self.rebuild_plot_q.empty():
            self.rebuild_plot_q.put(QueueEntry(''))  # '' is empty cmd

    def init_grid(self, grid):
        with self._lock:
            self._grid = grid
            self._grid.lifeline = Lifeline(self._stderr, self.rebuild_plot_q)
            self.rebuild_plot_q.put(QueueEntry('start', None, None))

    def load(self):
        with self._lock:
            layout = self._grid._layout
            blocks = self._grid._slots
            self._root_plot = self.build_plot(layout, blocks)


    # Gets called at Runner creation, when the terminal is resized, or any
    # part of any block is changed. When any of those happen, we need to rebuild
    # the plot tree. Starting from the root Block, we recurse down all its
    # embedded Blocks, creating a Plot to represent each level on the way.
    # As we undo the recursion and travel back up the tree, at each level
    # we merge the SizePrefs of all the blocks at that level and store the
    # result in the Plot containing the blocks. When this completes, we can use the
    # resulting plot tree to display the top-most block, the Runner's Block.
    def build_plot(self, layout, blocks, horizontal=True):
        def merge_sizeprefs(plots, horizontal):
            # m_ stands for "main", s_ stands for "secondary"
            # main is the width sizepref is the plot is horizontal, and
            # the height size pref if it's vertical.
            # The main sizepref is summed, the secondary maxed
            # TODO document hard_max and the infinities values
            m_hard_min, m_hard_max, s_hard_min, s_hard_max = [0], [], [0], []
            for plot in subplots:
                # Just combine arrays
                m_sizepref = plot.w_sizepref if horizontal else plot.h_sizepref
                m_hard_min += m_sizepref.hard_min
                if m_sizepref.hard_max != float('-inf'):
                    m_hard_max += m_sizepref.hard_max

                s_sizepref = plot.h_sizepref if horizontal else plot.w_sizepref
                s_hard_min += s_sizepref.hard_min
                if s_sizepref.hard_max != float('-inf'):
                    s_hard_max += s_sizepref.hard_max

            # sum the main sizeprefs
            m_hard_max = [sum(m_hard_max) if m_hard_max else None]
            m_hard_min = [sum(m_hard_min)]
            # max the secondary sizeprefs
            s_hard_max = [max(s_hard_max) if s_hard_max else None]
            s_hard_min = [max(s_hard_min)]

            m_sizepref = SizePref(hard_min=m_hard_min, hard_max=m_hard_max) if m_hard_max else None
            s_sizepref = SizePref(hard_min=s_hard_min, hard_max=s_hard_max) if s_hard_max else None

            return (m_sizepref, s_sizepref) if horizontal else (s_sizepref, m_sizepref)

        while not self.rebuild_plot_q.empty():
            entry = self.rebuild_plot_q.get()
            if entry.cmd:
                # Pass the cmd to the grid
                self._grid.handler(self._grid, entry.cmd, entry.args, entry.kwargs)

        subplots = []
        if not layout:
            for _, block in blocks.items():
                # If there's no layout there's only one block.

                # If the blocks contains SizePrefs we use those. In other words,
                # specified SizePrefs override those being calculated as we move
                # up the Plot tree.

                # handle w_sizepref
                if not block.w_sizepref:
                    w_sizepref = DEFAULT_SIZE_PREF

                # merge its sizeprefs (which contain numbers) into
                # new sizeprefs containing lists. hard_max'es can
                # contain either the string 'text' meaning 'the
                # size of the amount of text you can fit in the
                # plot', or they can contain a float, which is treated
                # as an int, but using float allows for infinity.
                else:
                    hard_min, hard_max = [block.w_sizepref.hard_min], [block.w_sizepref.hard_max]
                    if block.w_sizepref.hard_min == 'text': hard_min = [block.num_text_cols]
                    if block.w_sizepref.hard_max == 'text': hard_max = [block.num_text_cols]
                    w_sizepref = SizePref(hard_min=hard_min, hard_max=hard_max)

                # handle h_sizepref
                if not block.h_sizepref:
                    h_sizepref = DEFAULT_SIZE_PREF
                else:
                    hard_min, hard_max = [block.h_sizepref.hard_min], [block.h_sizepref.hard_max]
                    if block.h_sizepref.hard_min == 'text': hard_min = [block.num_text_rows]
                    if block.h_sizepref.hard_max == 'text': hard_max = [block.num_text_rows]
                    h_sizepref = SizePref(hard_min=hard_min, hard_max=hard_max)

                # This return is purposely *inside* the loop because
                # there's only one block, so we have all we need to
                # build the plot.
                return Plot(w_sizepref, h_sizepref, block=block)
        for element in layout:
            if type(element) == int:
                block = blocks[element]
                if block.grid:
                    if block.w_sizepref or block.h_sizepref:

                        temp = self.build_plot(None, {element: block})
                    subplot = self.build_plot(block.grid._layout,
                                              block.grid._slots)
                    if block.w_sizepref:
                        subplot.w_sizepref = temp.w_sizepref
                    if block.h_sizepref:
                        subplot.h_sizepref = temp.h_sizepref

                else:  # it's a leaf block
                    subplot = self.build_plot(None, {element: block})

            else:  # it's list or tuple
               orientation = type(element) == list
               subplot = self.build_plot(element, blocks, orientation)
            subplots.append(subplot)
        w_sizepref, h_sizepref = merge_sizeprefs(subplots, horizontal)
        return Plot(w_sizepref, h_sizepref, horizontal=horizontal, subplots=subplots)

    # Display the plot by recursing down the plot tree built by
    # build_plot() and determine the coordinates for the plots embedded in
    # each plot by using the SizePrefs of the plots
    def display_plot(self, plot, x, y, w, h, term=None):
        if plot.block:
            plot.block.display(w, h, x, y, term)
        else:
            for subplot, new_x, new_y, new_w, new_h in Runner.divvy(plot.subplots, x, y, w, h, plot.horizontal):
                self.display_plot(subplot, new_x, new_y, new_w, new_h, term)

    # Divvy up the space available to a series of plots among them
    # by referring to SizePrefs for each.
    def divvy(plots, x, y, w, h, horizontal):
        def calc_block_size(total_size, num_blocks, block_index):
            base, rem = divmod(total_size, num_blocks)
            return base + int(block_index < rem)

        num_plots = len(plots)
        memo = [[]] * num_plots
        for i in range(num_plots):
            memo[i] = {'x':0, 'y':0, 'w':0, 'h':0}

        # The main complications in divvying up the available space for the
        # plots are in satisfying the hard_min and hard_max preferences for
        # each plot.

        # handle hard_min first, but save off hard_maxes
        rem = w if horizontal else h  # remaining space to divvy
        hard_maxes = []  # tuple: (remaining_allowed, plot_index)
        unmet_hard_maxes_indexes = set()  # ??? TODO
        free_indexes = set()  # we can assign unlimited space to these blocks

        for i, plot in enumerate(plots):
            if horizontal:
                prefs, xy, wh = plot.w_sizepref, 'x', 'w'
            else:
                prefs, xy, wh = plot.h_sizepref, 'y', 'h'

            if rem > 0:
                # Reserve only the minimum space required
                amount = min(rem, sum(prefs.hard_min))
                rem -= amount
                memo[i][wh] += amount
            if prefs.hard_max:
                total_hard_max = sum(prefs.hard_max)
                # hard_maxes is a tuple: (remaining_allowed, plot_index)
                hard_maxes.append((max(0, (total_hard_max - memo[i][wh])), i))
                if memo[i][wh] < total_hard_max:
                    #hard_maxes.append((total_hard_max,i))
                    unmet_hard_maxes_indexes.add(i)
            else:
                free_indexes.add(i)

        if rem > 0:  # if rem == 0, we're done
            # Now deal with hard_max

            # The watermark max chars we can allocate to *every* plot without
            # exceeding the largest hard_max
            watermark = 0
            for i, (hmax_num, hmax_index) in enumerate(sorted(hard_maxes)):
                # if this hard max has been satisfied already, move passed it
                if hmax_num <= watermark:
                    continue

                unsatisfied_hard_maxes = len(hard_maxes) - i
                satisfied_hard_maxes = len(hard_maxes) - unsatisfied_hard_maxes
                new_amount = hmax_num - watermark
                # Is rem large enough that everyone can take on the new amount?
                if (rem // (num_plots - satisfied_hard_maxes)) < new_amount:
                    # no. we're done. just split the remaining space fairly
                    break
                else:
                    watermark = hmax_num

            # All max(watermark/hard_max) to every plot.
            for i, plot in enumerate(plots):
                if horizontal:
                    prefs, xy, wh = plot.w_sizepref, 'x', 'w'
                else:
                    prefs, xy, wh = plot.h_sizepref, 'y', 'h'
                if not prefs.hard_max:
                    alloc = watermark
                else:
                    hard_max_target = sum(prefs.hard_max) - memo[i][wh]
                    alloc = min(watermark, hard_max_target)
                    if alloc > 0:
                        if alloc == hard_max_target:
                            unmet_hard_maxes_indexes.remove(i)  # hard_max has been met for this plot
                memo[i][wh] += max(0, alloc)
                rem -= alloc

            if rem:  # rem can't be < 0
                # mins and maxes have all been accounted for
                rem_copy = rem
                total_unmet = num_plots - (len(hard_maxes) - len(unmet_hard_maxes_indexes))
                unmet_count = 0
                for i in range(num_plots):
                    if i not in unmet_hard_maxes_indexes and i not in free_indexes:
                        continue
                    add = calc_block_size(rem_copy, total_unmet, unmet_count)
                    unmet_count +=1
                    memo[i]['w' if horizontal else 'h'] += add
                    rem -= add
            #assert(rem == 0), rem

        # Calculate x,y and bundle for return
        out = []
        count_x, count_y = x, y
        for i, plot in enumerate(plots):
            m = memo[i]
            if horizontal:
                m['x'] = count_x
                count_x += m['w']
                m['y'] = y
                m['h'] = h
            else:
                m['y'] = count_y
                count_y += m['h']
                m['x'] = x
                m['w'] = w
            out.append((plot, m['x'], m['y'], m['w'], m['h']))
        return out

# https://stackoverflow.com/questions/14890997/redirect-stdout-to-a-file-only-for-a-specific-thread
class StdErrRedirector(object):
    def __init__(self, filename):
        self._orig_stderr = sys.stderr
        self._orig__stderr__ = sys.__stderr__
        self._thread_proxies = {}
        self._lock = RLock()
        self._fp = None
        if filename:
            self._fp = open(filename, 'w+')

    def redirect(self):
        ident = current_thread().name
        with self._lock:
            self._thread_proxies[ident] = StringIO()
            return self._thread_proxies[ident]

    def stop_redirect(self):
        ident = current_thread().name
        with self._lock:
            if ident not in self._thread_proxies:
                return
            retval = self._thread_proxies[ident].getvalue()
            self._thread_proxies[ident].close()
            del self._thread_proxies[ident]
            return retval

    def _get_stream(self, original):
        def proxy():
            ident = current_thread().name
            return self._thread_proxies.get(ident, original)
        return proxy

    def _enable_proxy(self):
        with self._lock:
            sys.__stderr__ = local.LocalProxy(self._get_stream(sys.__stderr__))
            sys.stderr = local.LocalProxy(self._get_stream(sys.stderr))


    def _disable_proxy(self):
        with self._lock:
            sys.__stderr__ = self._orig___stderr__
            sys.stderr = self._orig_stderr

    def dump(self):
        with self._lock:
            from datetime import datetime
            now = datetime.now().strftime('%H:%M:%S')
            for name, out in self._thread_proxies.items():
                val = out.getvalue()
                if val:
                    if self._fp:
                        header = '{} ({}) '.format(now, name)
                        lines = val.split('\n')
                        for i in range(len(lines) - 1):  # there's extra \n at the end
                            self._fp.write(header + lines[i] + '\n')
                self._thread_proxies[name] = StringIO()
            if self._fp:
                self._fp.flush()

if __name__ == '__main__':
    blocks = {}
    blocks[1] = Block('blx')
    blocks[2] = Block('bly')
    blocks[3] = Block('blz')
    g = Grid([1, (2,3)], blocks)
    top = BareBlock(grid=g)
    runner = Runner(top)
    plot = runner.build_plot(a._layout, a._slots)
    print(plot)

