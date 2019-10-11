# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from quartet_masterdata.models import Company, Location, TradeItem


class DBProxy:
    """
    Performs common database operations.
    """

    def get_epcis_master_data_locations(self, sgln_list: []):
        """
        Will create a list of vocabulary elements for gs1 locations
        :return: A dictionary with the key being the sgln and a dictionary
        as the value.
        """
        db_records = {}
        for sgln in sgln_list:
            location = self._partner_by_sgln(sgln=sgln)
            if location and len(location) > 0:
                # there will only ever be one
                db_records[sgln] = location[0]
        return db_records

    def _partner_by_sgln(self, sgln: str):
        qd = Company.objects.filter(SGLN=sgln)
        partner = None
        if qd.exists():
            partner = qd.values()
        else:
            qd = Location.objects.filter(SGLN=sgln)
            if qd.exists():
                partner = qd.values()
        return partner

    def get_company_prefix_length(self, barcode: str) -> int:
        """
        Uses the GTIN 14 to look up the company prefix in the trade items
        table.
        :param gtin14: The gtin
        :return: The length of the company prefix record.
        """

        company_prefix_length = None
        if len(barcode) == 14:
            try:
                trade_item = TradeItem.objects.select_related().get(
                    GTIN14=barcode)
                if trade_item.NDC:
                    company_prefix_length = 2 + len(
                        trade_item.NDC.split('-')[0])
                else:
                    company_prefix_length = len(
                        trade_item.company.gs1_company_prefix)
            except TradeItem.DoesNotExist:
                company_prefix_length = self._get_cp_len_by_company(barcode)
        elif len(barcode) == 18:
            company_prefix_length = self._get_cp_len_by_company(barcode)
        else:
            raise self.InvalidBarcode('This class will only look up company '
                                      'prefix information based on SSCC and '
                                      'GTIN 14 barcode strings.  If your '
                                      'barcode string contains app identifiers '
                                      'this may be the cause of your exception '
                                      'please remove app identifiers prior '
                                      'to invoking this function.')
        return company_prefix_length

    def get_GLN_by_SGLN(self, SGLN: str) -> str:
        """
        If you have a SGLN but need a GLN and a Company or Location
        is configured in the database, pass in the SGLN and the configured
        GLN will be returned if one is configured.
        :param SGLN: Inboud SGLN to find the GLN with.
        :return: A GLN-13 string or None.
        """
        ret = None
        try:
            company = Company.objects.get(SGLN=SGLN)
            ret = company.GLN13
        except Company.DoesNotExist:
            try:
                location = Location.objects.get(SGLN=SGLN)
                ret = location.GLN13
            except Location.DoesNotExist:
                pass
        return ret

    def get_SGLN_by_GLN(self, GLN: str) -> str:
        """
        If you have a GLN but need a SGLN and a Company or Location
        is configured in the database, pass in the GLN and the configured
        SGLN will be returned if one is configured.
        :param GLN: Inboud GLN to find the SGLN with.
        :return: A SGLN string or None.
        """
        ret = None
        try:
            company = Company.objects.get(GLN13=GLN)
            ret = company.SGLN
        except Company.DoesNotExist:
            try:
                location = Location.objects.get(GLN13=GLN)
                ret = location.SGLN
            except Location.DoesNotExist:
                pass
        return ret

    def _get_cp_len_by_company(self, barcode):
        """
        Returns the company prefix length by trying to find a company with
        the gs1_company_prefix field defined and returning that length.
        :param barcode: The barcode value with the embedded prefix.
        :return: The company prefix length.
        """
        cp_index = 5
        while cp_index < 13:
            try:
                company = Company.objects.get(
                    gs1_company_prefix__startswith=barcode[1:cp_index]
                )
                return len(company.gs1_company_prefix)
            except (Company.DoesNotExist, Company.MultipleObjectsReturned):
                if cp_index == 12:
                    self._no_company_error()
                cp_index = cp_index + 1

    def _no_company_error(self):
        raise self.CompanyConfigurationError(
            'Neither a Company or Trade Item with the company'
            'prefix found in the barcode '
            'could not be located in the '
            'database.  Check to make sure '
            'this company is configured '
            'and has a company prefix '
            'field value. Make sure there is a valid Trade Item and/or '
            'Company configured. (Trade Item for GTINs and Company for '
            'SSCCs.'
        )

    class InvalidBarcode(Exception):

        def __init__(self, *args: object) -> None:
            super().__init__(*args)
            self.message = args[0]

    class TradeItemConfigurationError(InvalidBarcode):
        pass

    class CompanyConfigurationError(InvalidBarcode):
        pass

