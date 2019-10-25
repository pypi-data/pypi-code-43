#
# Copyright (c) 2009, 2013, 2015, 2016
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
COILS_ROUTE_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'groupid':              ['group_id', 'int', 0],
    'group_id':             ['group_id', 'int', 0],
    'routegroupid':         ['group_id', 'int', 0],
    'comment':              ['comment', ],
    'routegroupobjectid':   ['group_id', 'int', 0],
    'is_singleton':         ['is_singleton', 'int', 0],
    'issingleton':          ['is_singleton', 'int', 0],
    'singleton':            ['is_singleton', 'int', 0],
    'runcontrol':           ['runcontrol', 'int', 0],
    'runcontrolmask':       ['runcontrol', 'int', 0],
    'routegroupname':       None,
    'created':              None,
    'modified':             None,
    'lastmodified':         None,
    'last_modified':        None,
    }

COILS_ROUTEGROUP_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'routegroupid':         ['group_id', 'int', 0],
    'route_group_id':       ['group_id', 'int', 0],
    'name':                 ['name', 'str'],
    'comment':              ['comment', 'str'],
    }

COILS_PROCESS_KEYMAP = {
    'objectid':              ['object_id', 'int', 0],
    'object_id':             ['object_id', 'int', 0],
    'routeid':               ['route_id', 'int'],
    'route_id':              ['route_id', 'int'],
    'routeobjectid':         ['route_id', 'int'],
    'parentprocessid':       ['parent_id', 'int'],
    'parent_id':             ['parent_id', 'int'],
    'parentid':              ['parent_id', 'int'],
    'parentprocessobjectid': ['parent_id', 'int'],
    'priority':              ['priority', 'int', 201],
    'data':                  None,
    'filename':              None,
    'state':                 None,
    }
