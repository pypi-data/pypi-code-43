#
#    Copyright (C) 2002-2018  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import AccessControl
import logging
import os
import string
import transaction
from Acquisition import aq_base, aq_inner
from AccessControl.Permissions import view, view_management_screens, access_contents_information
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.PropertySheets import PropertySheet
from Products.ZScheduler.ZScheduleEvent import ZScheduleEvent

from BLBase import PortalFolder, ProductsDictionary
from Permissions import ManageBastionLedgers, OperateBastionLedgers

from zope.interface import implementer
from interfaces.process import IProcess

logger = logging.getLogger('BLProcess')

manage_addBLProcessForm = PageTemplateFile('zpt/add_process', globals())


def manage_addBLProcess(self, id, title='', REQUEST=None):
    """
    Add a new BLProcess object with id *id*.
    """

    ob = BLProcess(id, title)
    self._setObject(id,  ob)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class BLProcessParams(PropertySheet):
    """
    base class to set/store process run-time parameters
    """
    __ac_permissions__ = PropertySheet.__ac_permissions__ + (
        (access_contents_information, ('getPropertyStr',)),
    )

    def __init__(self, md=None):
        PropertySheet.__init__(self, 'parameterMap', md)

    def getProperty(self, id, default=None):
        """
        just in case we have not 'initalised' our attributes ...
        """
        if self.hasProperty(id):
            try:
                value = getattr(aq_base(self.v_self()), id)
            except AttributeError:
                value = default
        else:
            value = default
        if self.getPropertyType(id) in ('tokens',) and value is None:
            return []
        return value

    def getPropertyStr(self, id, default=None):
        """
        return's a string suitable for an input form        
        """
        value = self.getProperty(id, default)
        if self.getPropertyType(id) in ('tokens',):
            return ' '.join(value)
        if value is None:
            return ''
        return str(value)


@implementer(IProcess)
class BLProcess(PortalFolder, ZScheduleEvent):
    '''
    An ordered container of runnable objects that collectively define a process.
    The container manages the scheduling of the process dispatch.
    '''
    meta_type = portal_type = 'BLProcess'


    # tuple of hashes of parameter values ...
    parameterMap = BLProcessParams()

    manage_options = (
        {'label':  'Components',  'action': 'manage_main',
         'help': ('BastionLedger', 'process.stx')},
        {'label':  'View',  'action': ''},
        {'label':  'Properties',  'action': 'manage_propertiesForm',
         'help': ('OFSP', 'Properties.stx')},
        {'label':  'Schedule',    'action': 'manage_scheduleForm',
         'help': ('ZScheduler', 'event.stx')},
        {'label':  'Run',         'action': 'manage_runForm'},
    ) + PortalFolder.manage_options[2:]

    manage_runForm = PageTemplateFile('zpt/process_run', globals())

    __ac_permissions__ = (
        (OperateBastionLedgers, ('manage_scheduleForm',
                                 'manage_run', 'manage_updateParams')),
        (access_contents_information, ('accountsInContext', 'reports')),
    )

    dontAllowCopyAndPaste = 0

    def __init__(self, id, title=''):
        ZScheduleEvent.__init__(self, id, title, id)

    def all_meta_types(self):
        return [
            ProductsDictionary('BLTransactionTemplate'),
            ProductsDictionary('Page Template'),
            ProductsDictionary('DTML Method'),
            ProductsDictionary('Script (Python)'),
        ]

    def Description(self):
        return self.description or self.__doc__

    def accountsInContext(self):
        """
        return accounts in the context of the process
        this is useful to apply objects defined in the BLProcess to the account using
        aqcuisition instead of having to pass parameters ...
        """
        return map(lambda x, y=self: x.__of__(y),
                   self.objectValues(self.account_types))

    def manage_updateParams(self, REQUEST):
        """
        update run-time parameters
        """
        # TODO - these changes aren't getting into ZODB (surviving reboot)
        # logger.info(self.parameterMap.__dict__)
        self.parameterMap.manage_changeProperties(REQUEST)
        # logger.info(self.parameterMap.__dict__)
        self.parameterMap._p_changed = 1
        transaction.get().savepoint(optimistic=True)
        REQUEST.set('management_view', 'Run')
        REQUEST.set('manage_tabs_message', 'Updated parameters')
        return self.manage_runForm(self, REQUEST)

    def manage_run(self, REQUEST=None, *args, **kw):
        """
        invoke the overridable run() function from ZMI
        """
        # TODO - introspect sub-class run() parameters, and bind based upon
        # parameterMap
        #self.run(*args, **kw)
        self.run(REQUEST or self.REQUEST)
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Process ran OK')
            return self.manage_runForm(self, REQUEST)

    def reportFilter(self, report):
        """
        an expression used to identify any reports in the Reports folder
        that would identify previous runs of the process
        """
        return False

    def reports(self):
        """
        return a list of reports produced by prior runs of this process
        """
        rf = getattr(self.aq_parent, 'Reports', None)
        if rf:
            return filter(lambda x: self.reportFilter(x), rf.objectValues())
        return []

AccessControl.class_init.InitializeClass(BLProcess)


class BLProcesses(PortalFolder):
    """
    Folder view for processes - this will eventually contain proxy objects
    with scheduling info about the actual process ...
    """
    meta_type = portal_type = 'BLProcesses'

    __ac_permissions__ = (
        (view_management_screens, ('manage_main',)),
    ) + PortalFolder.__ac_permissions__

    dontAllowCopyAndPaste = 0

    manage_options = (
        {'label': 'Processes', 'action': 'manage_main',
         'help': ('BastionLedger', 'processes.stx')},
    ) + PortalFolder.manage_options[1:]

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

    def all_meta_types(self):
        return (ProductsDictionary('BLProcess'), )


AccessControl.class_init.InitializeClass(BLProcesses)
