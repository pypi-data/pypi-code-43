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

# import stuff
import AccessControl
import Acquisition
import Products
from Acquisition import aq_base
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, access_contents_information, view
from OFS.PropertyManager import PropertyManager
from DateTime import DateTime
from Products.PythonScripts.standard import newline_to_br
from BLBase import *
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from utils import assert_currency
from catalog import makeBLInventoryCatalog
from Permissions import OperateBastionLedgers
from Exceptions import MissingAssociation
from Products.CMFCore import permissions
from SyndicationSupport import SyndicationSupport
from BLTaxCodeSupport import BLTaxCodeSupport

from zope.interface import Interface, implementer
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from interfaces.tools import IBLLedgerToolMultiple
from interfaces.inventory import IPart, IDispatchable

from plone.uuid.interfaces import IAttributeUUID

manage_addBLPartFolderForm = PageTemplateFile('zpt/add_partfolder', globals())


def manage_addBLPartFolder(self, id, title, REQUEST=None):
    """ adds a parts container """
    folder = BLPartFolder(id, title)
    self._setObject(id, folder)

    if REQUEST:
        REQUEST.RESPONSE.redirect(
            "%s/%s/manage_workspace" % (REQUEST['URL3'], id))

    return self._getOb(id)


@implementer(IAttributeUUID)
class BLPartFolder(LargePortalFolder):
    """
    high performance / high volume parts folder
    """
    meta_type = portal_type = 'BLPartFolder'
    _security = ClassSecurityInfo()
    dontAllowCopyAndPaste = 0


    __ac_permissions__ = LargePortalFolder.__ac_permissions__ + (
        (access_contents_information, ('partValues',)),
    )

    manage_options = (
        {'label': 'Contents', 'action': 'manage_main'},
    ) + LargePortalFolder.manage_options[1:]

    manage_main = PageTemplateFile('zpt/view_inventory', globals())

    def __init__(self, id, title=''):
        LargePortalFolder.__init__(self, id)
        self.title = title

    _security.declareProtected(view_management_screens, 'all_meta_types')

    def all_meta_types(self):
        """  """
        return [ProductsDictionary('BLPart'),
                ProductsDictionary('BLPartFolder'),
                ProductsDictionary('Page Template')]

    def partValues(self):
        """
        recursively grab all sub-folders parts as well
        """
        results = list(self.objectValues('BLPart'))
        for folder in self.objectValues('BLPartFolder'):
            results.extend(folder.partValues())
        return results


AccessControl.class_init.InitializeClass(BLPartFolder)


class BLDispatcher(ZCatalog, PropertyManager):
    """
    Order dispatching sub-system
    """
    meta_type = portal_type = 'BLDispatcher'

    _properties = (
        {'id': 'label_rows',   'type': 'int', 'mode': 'w'},
        {'id': 'label_cols',   'type': 'int', 'mode': 'w'},
        {'id': 'label_height', 'type': 'int', 'mode': 'w'},
        {'id': 'label_width',  'type': 'int', 'mode': 'w'},
    )

    manage_options = (
        {'label': 'Dispatch',   'action': 'manage_main',
         'help': ('BastionLedger', 'dispatch.stx')},
        {'label': 'Properties', 'action': 'manage_propertiesForm',
         'help': ('BastionLedger', 'dispatch_props.stx')},
    ) + ZCatalog.manage_options[3:]

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (OperateBastionLedgers, ('manage_dispatch', 'dispatch_labels', 'dispatches_array',
                                 'manage_cancel', 'objectsForStatus')),
    ) + ZCatalog.__ac_permissions__

    manage_main = PageTemplateFile('zpt/inventory_dispatcher', globals())
    dispatch_labels = PageTemplateFile('zpt/dispatch_labels', globals())

    def __init__(self, id):
        ZCatalog.__init__(self, id)
        self.label_rows = 7
        self.label_cols = 3
        self.label_width = 227
        self.label_height = 137

    def all_meta_types(self): return []

    def manage_dispatch(self, ids, REQUEST=None):
        """ """
        map(lambda x, y=self: y._getOb(x).manage_dispatch(), ids)
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def manage_cancel(self, ids, REQUEST=None):
        """ 
        set request states to cancelled
        """
        for ob in map(lambda x, y=self: y._getOb(x), ids):
            ob._status('cancelled')
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def dispatches_array(self, shiptoaddress=[], labelpos=[], REQUEST=None):
        """
        turn form data into a sparse array of text to be printed ...
        """
        # raise AssertionError, (shiptoaddress, labelpos)
        result = []
        pos_dict = {}

        # overwrite position with last found - only good for a single page ;
        ids = filter(lambda x: x, map(
            lambda x: x.get('id', ''), shiptoaddress))
        for id, pos in map(lambda x: x.split(','), labelpos):
            if id in ids:
                pos_dict[int(pos)] = id

        for pos in range(0, self.label_rows * self.label_cols):
            if pos_dict.has_key(pos):
                rec = filter(lambda x, id=pos_dict[pos]: x.get(
                    'id', '') == id, shiptoaddress)
                if rec:
                    label = rec[0]['addr']
                else:
                    order = getattr(self, pos_dict[pos]).order()
                    label = '%s\n%s' % (order.contact, order.shiptoaddress)
                result.append(newline_to_br(label))
            else:
                result.append('')

        return result

    def objectsForStatus(self, status):
        """
        we get f**ked off with Permissions on searchResults ...
        """
        return map(lambda x, y=self: y.unrestrictedTraverse(x.getPath()),
                   self.searchResults(status=status))

    def manage_repair(self, REQUEST):
        """ """
        for attr in ('label_rows', 'label_cols', 'label_width', 'label_height'):
            if not hasattr(aq_base(self), attr):
                setattr(self, attr, 0)
        if REQUEST:
            return self.manage_main(self, REQUEST)

AccessControl.class_init.InitializeClass(BLDispatcher)


@implementer(IDispatchable)
class BLDispatchable(PropertyManager, PortalContent):
    """
    something we can dispatch ...
    """
    meta_type = portal_type = 'BLDispatchable'

    _properties = (
        {'id': 'id',         'type': 'string',   'mode': 'r'},
        {'id': 'path',       'type': 'string',   'mode': 'r'},
        {'id': 'received',   'type': 'date',     'mode': 'r'},
        {'id': 'dispatched', 'type': 'date',     'mode': 'r'},
        {'id': 'dispatcher', 'type': 'string',   'mode': 'r'},
    )

    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (OperateBastionLedgers, ('manage_dispatch',)),
        (view_management_screens, ('order',)),
    ) + PortalContent.__ac_permissions__

    manage_options = PropertyManager.manage_options + PortalContent.manage_options
    manage_main = PropertyManager.manage_propertiesForm

    def __init__(self, id, path):
        self.id = id
        self.path = path
        self.received = DateTime()
        self.dispatched = None
        self.dispatcher = ''

    def manage_dispatch(self, REQUEST=None):
        """ """
        self._status('delivering')
        self.dispatched = DateTime()
        self.dispatcher = getSecurityManager().getUser().getUserName()
        self.reindexObject()
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def order(self):
        return self.unrestrictedTraverse(self.path)

    def indexObject(self, idxs=[]):
        url = '/'.join(self.getPhysicalPath())
        # acquire catalog :)
        self.aq_parent.catalog_object(self, url, idxs=idxs)

    def unindexObject(self):
        url = '/'.join(self.getPhysicalPath())
        # acquire catalog :)
        self.aq_parent.uncatalog_object(url)

AccessControl.class_init.InitializeClass(BLDispatchable)

manage_addBLInventoryForm = PageTemplateFile('zpt/add_inventory', globals())


def manage_addBLInventory(self, id, title, REQUEST=None):
    """ adds an inventory warehouse """
    try:
        inv = BLInventory(id, title)
        self._setObject(id, inv)
    except:
        raise

    if REQUEST is not None:
        #REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))
        return self.manage_main(self, REQUEST)
    else:
        return self._getOb(id)


@implementer(IBLLedgerToolMultiple)
class BLInventory(BLPartFolder, PortalContent, SyndicationSupport):

    meta_type = portal_type = 'BLInventory'


    _reserved_names = ('catalog',)
    __ac_permissions__ = BLPartFolder.__ac_permissions__ + (
        (access_contents_information, ('blPart', 'blPartIds')),
        (view_management_screens, ('manage_tabs', 'manage_main', 'manage_workspace')),
    ) + PortalContent.__ac_permissions__

    description = ''

    manage_options = (
        {'label': 'Content', 'action': 'manage_main',
         'help': ('BastionLedger', 'inventory.stx')},
        {'label': 'View', 'action': '', },
        {'label': 'Catalog', 'action': 'catalog/manage_workspace'},
        {'label': 'Dispatch', 'action': 'manage_dispatch'},
    ) + LargePortalFolder.manage_options[2:-1]

    def __init__(self, id, title=''):
        BLPartFolder.__init__(self, id, title)
        #self.customers = BLSupermarket('customers', 'Happy Shoppers')
        self.dispatcher = BLDispatcher('dispatcher')
        cat = self.catalog = ZCatalog('catalog', 'Catalog')
        makeBLInventoryCatalog(self)

    def manage_dispatch(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect('dispatcher/manage_workspace')

    def dispatch(self, order):
        """
        place in the dispatch queue for order fulfillment/delivery by warehouse staff

        at the moment, this stuff is really simple - but in the future more complex
        mappings of orders to dispatch processing will be developed.
        """
        id = order.getId()
        self.dispatcher._setObject(
            id, BLDispatchable(id, order.absolute_url(1)))

    def blPart(self, part_id):
        """
        finds the part in the catalog and returns it

        note that this method does not do any of the standard getObject
        security checking because we're sick of returning None objects!
        """
        brainz = self.catalog.searchResults(meta_type='BLPart', id=part_id)
        if brainz:
            try:
                return brainz[0]._unrestrictedGetObject()
            except:
                pass
        return None

    def blPartIds(self):
        """
        return a list of all part ids in the inventory's catalog
        """
        return map(lambda x: x['id'], self.catalog(meta_type='BLPart'))

    def searchObjects(self, **kw):
        """
        """
        return map(lambda x: x.getObject(),
                   self.catalog.searchResults(**kw))

    def syndicationQuery(self):
        """
        """
        return {'meta_type': 'BLPart',
                'created': {'query': DateTime() - 1,
                            'range': 'min'}}

    def _repair(self):
        if not getattr(aq_base(self), 'dispatcher', None):
            self.dispatcher = BLDispatcher('dispatcher')

AccessControl.class_init.InitializeClass(BLInventory)


manage_addBLPartForm = PageTemplateFile('zpt/add_part', globals())


def manage_addBLPart(self, id, title='', taxcodes=(), REQUEST=None):
    """ a part """
    ledger = self.bastionLedger().Ledger

    try:
        defaultcurrency = ledger.defaultCurrency()

        part = BLPart(id,
                      title,
                      defaultcurrency,
                      ledger.accountValues(tags='part_inv')[0].getId(),
                      ledger.accountValues(tags='part_inc')[0].getId(),
                      ledger.accountValues(tags='part_cogs')[0].getId(),
                      taxcodes=taxcodes)

        notify(ObjectCreatedEvent(part))

        self._setObject(id, part)
    except IndexError as e:
        raise MissingAssociation("part_inv, part_inc, or part_cogs tag not set for %s: %s" % (ledger, str(e)))

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(
            "%s/%s/manage_propertiesForm" % (REQUEST['URL3'], id))

    return self._getOb(id)


@implementer(IPart)
class BLPart(PortalFolder, PropertyManager, PortalContent, BLTaxCodeSupport):

    meta_type = portal_type = 'BLPart'


    __ac_permissions__ = PortalFolder.__ac_permissions__ + (
        (view, ('inventory_account', 'expense_account', 'income_account', 'created',
                'isSpecial', 'tax',)),
        (OperateBastionLedgers, ('edit_prices', 'available_accounts')),
    ) + PropertyManager.__ac_permissions__ + PortalContent.__ac_permissions__

    #edit = Document.edit

    text_format = 'structured-text'
    properties_extensible_schema__ = 1
    sku = ''
    urls = ()  # any descriptors elsewhere on the webs
    specialprice = 0  # TODO - doesn't currency convert ...

    _properties = (
        {'id': 'title',       'type': 'string',   'mode': 'w'},
        {'id': 'description', 'type': 'text',     'mode': 'w'},
        {'id': 'sku',         'type': 'string',   'mode': 'w'},
        {'id': 'unit',        'type': 'string',   'mode': 'w'},
        {'id': 'weight',      'type': 'float',    'mode': 'w'},
        {'id': 'onhand',      'type': 'float',    'mode': 'w'},
        {'id': 'notes',       'type': 'text',     'mode': 'w'},
        {'id': 'listprice',   'type': 'currency', 'mode': 'w'},
        {'id': 'sellprice',   'type': 'currency', 'mode': 'w'},
        {'id': 'specialprice', 'type': 'currency', 'mode': 'w'},
        {'id': 'lastcost',    'type': 'currency', 'mode': 'w'},
        {'id': 'urls',        'type': 'lines',    'mode': 'w'},
    )

    manage_options = (
        {'label': 'Properties', 'action': 'manage_propertiesForm',
         'help': ('BastionLedger', 'part.stx')},
        {'label': 'Content', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
        {'label': 'Tax Codes', 'action': 'manage_taxcodes'},
    ) + PortalContent.manage_options[1:]

    #manage_propertiesForm = PageTemplateFile('zpt/edit_part', globals())

    def __init__(self, id, title, defaultcurrency, inventory_accno, income_accno,  expense_accno,
                 unit='', weight=0, onhand=0, listprice=0, sellprice=0, specialprice=0, sku='', notes='', taxcodes=()):
        super(BLPart, self).__init__(id, title)
        self.sku = sku
        self.unit = unit
        self.weight = float(weight)
        self.onhand = onhand
        self.listprice = self.lastcost = ZCurrency(defaultcurrency, listprice)
        self.sellprice = ZCurrency(defaultcurrency, sellprice)
        self.specialprice = ZCurrency(defaultcurrency, specialprice)
        self.notes = notes
        self.inventory_acct = inventory_accno
        self.income_acct = income_accno
        self.expense_acct = expense_accno
        self.tax_codes = taxcodes

    def created(self):
        """
        when the part was added to the inventory
        """
        return DateTime(self.CreationDate())

    def _updateProperty(self, name, value):
        if name in ('listprice', 'sellprice', 'lastcost', 'specialprice'):
            assert_currency(value)
        PropertyManager._updateProperty(self, name, value)

    def manage_editProperties(self, REQUEST):
        """
        hmmm - we have some complex types we haven't quite made first-class properties ...
        """
        if REQUEST.has_key('inventory_accno'):
            value = REQUEST['inventory_accno']
            assert value in map(lambda x: x.getId(),
                                self.bastionLedger().Ledger.accountValues(tags='part_inv')), \
                "Invalid Inventory Account: %s" % value
            self.inventory_acct = value

        if REQUEST.has_key('income_accno'):
            value = REQUEST['income_accno']
            assert value in map(lambda x: x.getId(),
                                self.bastionLedger().Ledger.accountValues(tags='part_inc')), \
                "Invalid Income Account: %s" % value
            self.income_acct = value

        if REQUEST.has_key('expense_accno'):
            value = REQUEST['expense_accno']
            assert value in map(lambda x: x.getId(),
                                self.bastionLedger().Ledger.accountValues(tags='part_cogs')), \
                "Invalid Expense Account: %s" % value
            self.expense_acct = value

        form = PropertyManager.manage_editProperties(self, REQUEST)
        self.indexObject()
        return form

    def inventory_account(self): return getattr(
        self.bastionLedger().Ledger, self.inventory_acct)

    def expense_account(self): return getattr(
        self.bastionLedger().Ledger, self.expense_acct)

    def income_account(self): return getattr(
        self.bastionLedger().Ledger, self.income_acct)

    def available_accounts(self, tag):
        """
        returns list of accounts selectable for tag (ie 'part_inc', 'part_inv', 'part_cogs')
        """
        if not tag in ('part_inc', 'part_inv', 'part_cogs'):
            raise ValueError(tag)
        return self.bastionLedger().Ledger.accountValues(tags=tag)

    def edit_prices(self, unit, weight, onhand, sellprice, listprice, lastcost, specialprice,
                    inventory_accno, income_accno, expense_accno):
        """
        Plone editing
        """
        self._updateProperty('unit', unit)
        self._updateProperty('weight', weight)
        self._updateProperty('onhand', onhand)
        self._updateProperty('sellprice', sellprice)
        self._updateProperty('specialprice', specialprice)
        self._updateProperty('listprice', listprice)
        self._updateProperty('lastcost', lastcost)
        self.inventory_acct = inventory_accno
        self.income_acct = income_accno
        self.expense_acct = expense_accno

    def isSpecial(self):
        """ returns whether this is a special/sales item """
        return self.specialprice < self.sellprice

    #_security.declareProtected(view_management_screens, 'all_meta_types')
    # def all_meta_types(self):
    #    return filter(lambda x: x['name'] in [ 'Page Template',
    #                                           'Script (Python)' ],
    #                  Products.meta_types)

    # TODO - pcommerce API
    def price(self):
        return self.sellprice

    def tax(effective=None, taxcodes=()):
        """
        return the tax on an indivdual part

        tax codes are taxgroup/taxcode strings
        """
        if taxcodes is ():
            taxcodes = self.tax_codes
        else:
            taxcodes = filter(lambda x: x in self.tax_codes, taxcodes)
        bt = getToolByName(self, 'portal_bastionledger')
        return operator.add(map(lambda x: bt.calculateTaxByCode(effective or DateTime(),
                                                                self.sellprice,
                                                                x[0], x[1]),
                                self.taxGroupsCodes()))

AccessControl.class_init.InitializeClass(BLPart)


def addBLInventory(self, id, title=''):
    """ plone constructor """
    inv = manage_addBLInventory(self, id=id, title=title)
    id = inv.getId()
    return id


def addBLPart(self, id, title=''):
    """ plone constructor """
    part = manage_addBLPart(self, id=id, title=title)
    id = part.getId()
    return id


def addBLPartFolder(self, id, title=''):
    """ plone constructor """
    folder = manage_addBLPartFolder(self, id=id, title=title)
    id = folder.getId()
    return id


def catalogAddPart(ob, event):
    inv = ob.superValues('BLInventory')[0]
    inv.catalog.catalog_object(ob, '/'.join(ob.getPhysicalPath()))


def catalogDelPart(ob, event):
    inv = ob.superValues('BLInventory')[0]
    inv.catalog.uncatalog_object('/'.join(ob.getPhysicalPath()))
