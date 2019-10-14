#
#    Copyright (C) 2009-2018  Corporation of Balclutha. All rights Reserved.
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
import types
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from .BLBase import SimpleItem
from AccessControl.Permissions import view_management_screens, access_contents_information
from .Permissions import OverseeBastionLedgers
from .Exceptions import TaxCodeError


class BLTaxCodeSupport(SimpleItem):

    __ac_permissions__ = SimpleItem.__ac_permissions__ + (
        (view_management_screens, ('manage_taxcodes',)),
        (access_contents_information, ('allTaxGroupsCodes',
                                       'taxGroupsCodes', 'taxCodesForGroup')),
        (OverseeBastionLedgers, ('manage_editTaxGroups', 'manage_addTaxGroup')),
    )

    tax_codes = ()

    manage_taxcodes = PageTemplateFile('zpt/tax_codes', globals())

    def allTaxGroupsCodes(self):
        """
        all valid tax groups/codes
        """
        return getToolByName(self, 'portal_bastionledger').taxCodes(include_group=True)

    def manage_addTaxGroup(self, taxgroup, taxcodes=[], REQUEST=None):
        """
        add a taxgroup - with all it's codes
        """
        existing = type(self.tax_codes) == type(
            {}) and self.tax_codes.keys or self.tax_codes

        try:
            tt = getToolByName(
                self, 'portal_bastionledger').getTaxTable(taxgroup)
        except:
            raise TaxCodeError(taxgroup)
        if taxcodes:
            taxcodes = filter(lambda x: x in tt.taxCodes(), taxcodes)
        else:
            taxcodes = tt.taxCodes()
        codes = filter(lambda x: x not in existing,
                       map(lambda x: '%s/%s' % (taxgroup, x), taxcodes))
        if codes:
            self.manage_editTaxGroups(list(existing) + codes, REQUEST)

    def manage_editTaxGroups(self, taxgroups, REQUEST=None):
        """
        edit tax groups, pass in list of taxgroup/taxcode strings
        """
        self.tax_codes = tuple(
            filter(lambda x: x in self.allTaxGroupsCodes(), taxgroups))
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Edited Tax Groups/Codes')
            REQUEST.set('management_view', 'Tax Groups')
            return self.manage_taxcodes(self, REQUEST)

    def taxGroupsCodes(self, strfmt=False):
        """
        list of taxgroup/taxcode tuples
        strfmt is to produce a stringified version suitable for drop-down selections...
        """
        # these used to be a dict ....
        if type(self.tax_codes) == type({}):
            codes = self.tax_codes.keys()
        else:
            codes = self.tax_codes
        if strfmt:
            return tuple(codes)
        return tuple(map(lambda x: tuple(x.split('/')), codes))

    def taxGroups(self):
        """
        the tax groups this account ascribes to
        """
        groups = []
        for group in map(lambda x: x[0], self.taxGroupsCodes()):
            if group not in groups:
                groups.append(group)
        return tuple(groups)

    def taxCodesForGroup(self, taxgroup):
        """
        the tax group, tax codes within group assigned to this account
        """
        return filter(lambda x: x[0] == taxgroup, self.taxGroupsCodes())
