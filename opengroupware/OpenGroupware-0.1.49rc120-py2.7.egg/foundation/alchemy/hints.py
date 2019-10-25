# Copyright (c) 2013, 2014, 2015
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
from sqlalchemy.orm import joinedload, lazyload, subqueryload, eagerload
from task import Task
from contact import Contact
from project import Project
from enterprise import Enterprise
from doc import Document

"""
WARNING: Beware SQLAlchemy's "noload" operator.  With "noload" the data is
not loaded, which may be good, but it appears it will NEVER be loaded.  The
relation represented by an InstrumentedList will remain empty even when
accessed - and there appears to be no way to reset this behavior - no way to
subsequently make the relation load.
"""

ORMHINTS = {
    Task: {
        'zogi': (
            lazyload('info'),
            joinedload('owner'),
            lazyload('owner.notes'),
            lazyload('owner.acls'),
            lazyload('owner.locks'),
            lazyload('owner.telephones'),
            lazyload('owner.addresses'),
            lazyload('owner.company_values'),
            lazyload('creator'),
            lazyload('creator.notes'),
            lazyload('creator.acls'),
            lazyload('creator.locks'),
            lazyload('creator.telephones'),
            lazyload('creator.addresses'),
            lazyload('creator.company_values'),
            joinedload('project'),  # Disabling will break access projection!
            lazyload('project.acls'),
            lazyload('project.locks'),
            lazyload('project.tasks'),
            lazyload('project.children'),
            lazyload('project.folder'),
            # lazyload('project.notes'),
            lazyload('creator.projects'),
            lazyload('owner.projects'),
            subqueryload('acls'),
            eagerload('acls'),
            lazyload('creator.enterprises'),
            lazyload('owner.enterprises'),
            lazyload('creator.teams'),
            lazyload('owner.teams'),
            lazyload('creator.info'),
            lazyload('owner.info'),
        ),
        'webdav': (
            joinedload('info'),
            lazyload('owner'),
            lazyload('creator'),
            lazyload('project'),
            lazyload('properties'),
        ),
        0: (
            lazyload('notes'),
            lazyload('attachments'),
            joinedload('parent'),
            lazyload('parent.creator'),
            lazyload('parent.owner'),
            lazyload('parent.project'),
            lazyload('parent.properties'),
            lazyload('parent.acls'),
            lazyload('parent.children'),
            lazyload('parent.attachments'),
            lazyload('logs'),
        ),
        1: (
            subqueryload('notes'),
            eagerload('notes'),
        ),
        16: (
            subqueryload('properties'),
        ),
        32: (
            subqueryload('logs'),
            eagerload('logs'),
        ),
        128: (
            subqueryload('children'),
            eagerload('children'),
            subqueryload('children.children'),
            eagerload('children.children'),
            subqueryload('parent.children'),
        ),
    },
    Contact: {
        'zogi': (
            lazyload('company_values'),
            lazyload('notes'),
            lazyload('enterprises'),
            lazyload('teams'),
            lazyload('projects'),
            lazyload('logs'),
            lazyload('properties'),
            joinedload('info'),
            subqueryload('telephones'),
            subqueryload('addresses'),
        ),
        'webdav': (
            joinedload('info'),
            lazyload('owner'),
            lazyload('creator'),
            lazyload('project'),
            subqueryload('properties'),
        ),
        8: (
            eagerload('company_values'),
        ),
        16: (
            subqueryload('properties'),
            eagerload('properties'),
        ),
        32: (
            subqueryload('logs'),
            eagerload('logs'),
        ),
        512: (
            subqueryload('enterprises'),
            eagerload('enterprises'),
        ),
        1024: (
            subqueryload('projects'),
            eagerload('projects'),
        ),
    },
    Enterprise: {
        'zogi': (
            lazyload('company_values'),
            lazyload('notes'),
            lazyload('contacts'),
            lazyload('projects'),
            lazyload('logs'),
            lazyload('properties'),
            joinedload('info'),
            subqueryload('telephones'),
            subqueryload('addresses'),
        ),
        'webdav': (
            joinedload('info'),
            lazyload('owner'),
            lazyload('creator'),
            lazyload('project'),
            subqueryload('properties'),
        ),
        8: (
            eagerload('company_values'),
        ),
        16: (
            subqueryload('properties'),
            eagerload('properties'),
        ),
        32: (
            subqueryload('logs'),
            eagerload('logs'),
        ),
        256: (
            subqueryload('contacts'),
            eagerload('contacts'),
        ),
        1024: (
            subqueryload('projects'),
            eagerload('projects'),
        ),
    },
    Document: {
        'zogi': (),
        16: (subqueryload('properties'), ),
        32: (subqueryload('logs'), ),
        32768: (subqueryload('acls'), ),
    },
    Project: {
        'zogi': (
            lazyload('tasks'),
            lazyload('properties'),
            lazyload('logs'),
            lazyload('children'),
            joinedload('_info'),
        ),
        'webdav': (
            lazyload('tasks'),
            lazyload('properties'),
            # lazyload('logs'),
            subqueryload('children'),
        ),
        16: (
            subqueryload('properties'),
            eagerload('properties'),
        ),
        32: (
            # subqueryload('logs'),
            # eagerload('logs'),
        ),
        128: (
            subqueryload('children'),
        ),
        4096: (
            subqueryload('tasks'),
        ),
        32768: (
            subqueryload('acls'),
        ),
    }
}
