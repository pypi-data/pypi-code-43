#!/usr/bin/env python3
#
#
# Copyright (c) 2018, Hiroyuki Ohsaki.
# All rights reserved.
#
# $Id: cell.py,v 1.8 2019/03/10 11:49:46 ohsaki Exp $
#

import math
import os
import re
import tempfile
import time

import cellx

class Cell:
    def __init__(self,
                 width=800,
                 height=600,
                 monitor=None,
                 frame_rate=30,
                 rate_limit=30):
        self.width = width
        self.height = height
        self.monitor = monitor
        self.frame_rate = frame_rate
        self.rate_limit = rate_limit
        self.objects = {}
        self.palette = {}
        self.frame_count = 0
        self.time_started = time.time()
        self.last_display = None

    def object(self, name):
        return self.objects.get(name, None)

    def all_object_names(self):
        return self.objects.keys()

    def all_objects(self):
        return self.objects.values()

    def add(self, obj):
        self.objects[obj.name] = obj

    def delete(self, name):
        try:
            del self.objects[name]
        except KeyError:
            cellx.die("cannot delete non-existing object '%s'", name)

    def animate(self, name, x, y):
        obj = self.object(name)
        if not obj:
            cellx.die("object '%s' not found", name)
        obj.goal_x, obj.goal_y = x, y
        obj.velocity = max(obj.dist_to_goal() / self.frame_rate, 1)

    def as_dot_string(self, names):
        astr = 'graph export {\n'
        is_exported = {}
        for name in names:
            # FIXME: node size should use object width and height
            astr += '  "{}" [width="2"];\n'.format(name)
            is_exported[name] = True
        for obj in self.all_objects():
            if obj.type == 'link':
                src, dst = obj.src.name, obj.dst.name
                if is_exported.get(src, None) and is_exported.get(dst, None):
                    astr += '"{}" -- "{}";\n'.format(src, dst)
        astr += '}\n'
        return astr

    def fit_within(self, x1, y1, x2, y2, names):
        xmin = min([self.object(name).x for name in names])
        xmax = max([self.object(name).x for name in names])
        ymin = min([self.object(name).y for name in names])
        ymax = max([self.object(name).y for name in names])
        for name in names:
            obj = self.object(name)
            x, y = obj.x, obj.y
            x = x1 + (x2 - x1) * (x - xmin) / (xmax - xmin)
            y = y1 + (y2 - y1) * (y - ymin) / (ymax - ymin)
            obj.move(x, y)

    def spring(self, x1, y1, x2, y2, names, opts):
        filter = opts.get('f', 'neato')
        rotate = opts.get('r', 0)

        # export parent objects in DOT format
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        pipe = os.popen('{} >{}'.format(filter, tmpf.name), mode='w')
        names = [name for name in names \
                if not self.object(name).parent and self.object(name).type != 'link']
        pipe.write(self.as_dot_string(names))
        pipe.close()

        # parse graphviz output and extract object positions
        buf = tmpf.read().decode()
        buf = re.sub('\n', '', buf)
        for line in buf.split(']'):
            m = re.search(r'(\S+)\s*\[.*pos="([\d.-]+),([\d.-]+)",', line)
            if m:
                name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
                name = name.replace('\"', '')
                self.object(name).move(x, y)

        if rotate:
            for name in names:
                self.object(name).rotate_around(rotate,
                                                self.width() / 2,
                                                self.height() / 2)
        self.fit_within(x1, y1, x2, y2, names)

    def _display(self, objects):
        if not self.last_display:
            self.last_display = time.time()

        self.monitor.clear()
        self.monitor.render_objects(objects)
        self.monitor.display()
        self.frame_count += 1

        if self.rate_limit:
            if time.time() - self.last_display < 1 / self.rate_limit:
                delay = 1 / self.rate_limit - (time.time() - self.last_display)
                if delay > 0:
                    time.sleep(delay)
            self.last_display = time.time()

    def display(self):
        def _by_priority(obj):
            return obj.priority

        objs = [obj for obj in self.all_objects() if obj.visible]
        sorted_objs = sorted(objs, key=_by_priority)
        while True:
            nmoved = 0
            for obj in sorted_objs:
                if obj.velocity:
                    dx = obj.goal_x - obj.x
                    dy = obj.goal_y - obj.y
                    # close encough to the destination?
                    if abs(dx) < obj.velocity and abs(dy) < obj.velocity:
                        obj.velocity = None
                        continue
                    dist = math.sqrt(dx**2 + dy**2)
                    obj.shift(dx / dist * obj.velocity,
                              dy / dist * obj.velocity)
                    nmoved += 1
                if obj.fade_out:
                    obj.alpha = obj.alpha - 1 / self.frame_rate
                    if obj.alpha <= 0:
                        self.delete(obj.name)
                        sorted_objs.remove(obj)
                        continue
                    nmoved += 1
            self._display(sorted_objs)
            if nmoved == 0:
                break
        self.update_status()

    def wait(self):
        self.monitor.wait()

    def status_string(self):
        elapsed = time.time() - self.time_started
        if elapsed <= 1.0:
            return ''
        fps = self.frame_count / elapsed
        nobjs = len(self.objects)
        return 'FPS: {:.2f}, OBJ: {}'.format(fps, nobjs)

    def update_status(self):
        obj = cellx.Object(
            type='text',
            name='_status',
            text=self.status_string(),
            size=10,
            x=96,
            y=self.height - 10,
            color='white',
            priority=10,
        )
        self.add(obj)
