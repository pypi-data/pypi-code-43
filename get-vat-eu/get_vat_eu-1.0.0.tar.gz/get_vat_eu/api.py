#
# api.py
#
# Copyright (c) 2019 CityCommerce srl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""The main file."""

import re
import zeep
import string
from .constants import (common_defaults, urls, vat, countries)
from .exceptions import (
    VIESServiceError, ResponseIOError, ResponseVatNumberNotConforming,
    CannotGetTraderName, CannotGetTraderAddress, VatNotValid,
    AddressStringNotCorrespondingToExpectedFormat, CountryCodeNotImplemented)


def request_vat_information(vat_number: str,
                            country_code: str = countries['code']['default']
                            ) -> dict:
    r"""Make a SOAP request and expect a response.

    :param vat_number: the vat number identifier.
    :param country_code: a two letter uppercase country identifier.
    :type vat_number: str
    :type country_code: str
    :returns: a data structure containing the SOAP response.
    :rtype: dict
    :raises: VIESServiceError or a built-in exception.
    """
    try:
        client = zeep.Client(urls['ec_check_vat_api'])
        response = client.service.checkVatApprox(country_code, vat_number)
    except zeep.exceptions.Fault:
        raise VIESServiceError

    return response


def parse_address_string(address_string: str,
                         country_code: str = countries['code']['default']
                         ) -> dict:
    r"""Get relevant information from the address string.

    :param address_string: a string containing all the address information.
    :param country_code: a two letter uppercase country identifier.
    :type address_string: str
    :type country_code: str
    :returns: a data structure with keys differing from country code to country code.
    :rtype: dict
    :raises: AddressStringNotCorrespondingToExpectedFormat or a built-in exception.
    """
    assert len(country_code) == 2

    trader_information = dict()

    if country_code == 'IT':
        if (address_string.endswith(
                countries['IT']['address_string']['separator'])
                and countries['IT']['address_string']['separator'] in
                address_string[0:-1]):

            # Divide the original string in two parts. Ignore the final empty string.
            buf = address_string.split(
                countries['IT']['address_string']['separator'])[:-1]

            # The address part is the first substring. Remove spaces around the string borders.
            address_substring = buf[0].strip(
                countries['IT']['address_string']['delimiter'])

            # Postal code, city, province.
            pc_cty_prv_substring = buf[1]

            # Get the other substring into its various components.
            # Always be tolerant with the delimiters on the borders.
            # Remove empty substrings in case of unexpected address string formats.
            buf = list(
                filter(
                    None,
                    pc_cty_prv_substring.strip(
                        countries['IT']['address_string']['delimiter']).split(
                            countries['IT']['address_string']['delimiter'])))

            # We expect at least 3 elements: postal code, province and city.
            if len(buf) < 3:
                raise AddressStringNotCorrespondingToExpectedFormat

            # We know that province and postal code are not composed by delimiters.
            postal_code = buf[0]
            province = buf[-1]
            # A city might contain spaces (delimiters).
            # Always be tolerant with the delimiters on the borders.
            city = countries['IT']['address_string']['delimiter'].join(
                buf[1:-1]).strip(
                    countries['IT']['address_string']['delimiter'])

            # Check that the province is composed of 2 uppercase letter characters.
            # Check that the postal code correponds to the standard.
            if (not re.match(countries['IT']['post_code']['regex'],
                             postal_code)
                    or not re.match(countries['IT']['province']['regex'],
                                    province)):
                raise AddressStringNotCorrespondingToExpectedFormat

            trader_information['address'] = address_substring
            trader_information['post_code'] = postal_code
            trader_information['province'] = province
            trader_information['city'] = city
        else:
            raise AddressStringNotCorrespondingToExpectedFormat

    return trader_information


def vat_adheres_to_specifications(
        vat_number: str,
        country_code: str = countries['code']['default']) -> bool:
    r"""Check that the VAT number corresponds to the specifications.

    :param vat_number: the vat number identifier.
    :param country_code: a two letter uppercase country identifier.
    :type vat_number: str
    :type country_code: str
    :returns: ``True`` if the VAT number adheres to the specifications, ``False`` otherwise.
    :rtype: bool
    :raises: a built-in exception.
    """
    assert len(country_code) == 2

    vat_conforming = False
    if re.match(vat['regex'], country_code + vat_number):
        vat_conforming = True

    return vat_conforming


def parse_response(response: dict,
                   vat_number: str,
                   country_code: str = countries['code']['default']) -> dict:
    r"""Parses the response and get the relevant fields.

    :param response: a data structure containing the SOAP response.
    :param vat_number: the vat number identifier.
    :param country_code: a two letter uppercase country identifier.
    :type response: dict
    :type vat_number: str
    :type country_code: str
    :returns: a data structure with keys differing from country code to country code.
    :rtype: dict
    :raises: ResponseIOError, ResponseVatNumberNotConforming, CannotGetTraderName,
        CannotGetTraderAddress, CountryCodeNotImplemented, VatNotValid, or a built-in exception.
    """
    assert 'countryCode' in response
    assert 'vatNumber' in response
    assert 'requestDate' in response
    assert 'valid' in response
    assert 'traderName' in response
    assert 'traderCompanyType' in response
    assert 'traderAddress' in response
    assert 'traderStreet' in response
    assert 'traderPostcode' in response
    assert 'traderCity' in response
    assert 'traderNameMatch' in response
    assert 'traderCompanyTypeMatch' in response
    assert 'traderStreetMatch' in response
    assert 'traderPostcodeMatch' in response
    assert 'traderCityMatch' in response
    assert 'requestIdentifier' in response
    # The following variables must be defined.
    assert response['countryCode'] is not None
    assert response['vatNumber'] is not None
    assert response['requestDate'] is not None
    assert response['valid'] is not None
    assert isinstance(response['valid'], bool)
    assert isinstance(response['countryCode'], str)
    assert isinstance(response['vatNumber'], str)

    if response['countryCode'] != country_code:
        raise ResponseIOError
    if response['vatNumber'] != vat_number:
        raise ResponseIOError

    trader_information = dict()

    # 'valid' is compulsory.
    if response['valid']:
        if not vat_adheres_to_specifications(response['vatNumber']):
            raise ResponseVatNumberNotConforming

        # 'contryCode' is compulsory.
        if response['countryCode'] == 'IT':

            if response['traderName'] is None:
                raise CannotGetTraderName
            else:
                trader_information['name'] = response['traderName']

            if (response['traderStreet'] is None
                    or response['traderCity'] is None
                    or response['traderPostcode'] is None):
                if response['traderAddress'] is None:
                    raise CannotGetTraderAddress
                else:
                    trader = parse_address_string(response['traderAddress'],
                                                  response['countryCode'])
                    trader_information['address'] = trader['address']
                    trader_information['city'] = trader['city']
                    trader_information['province'] = trader['province']
                    trader_information['post_code'] = trader['post_code']
            else:
                trader_information['address'] = trader['address']
                trader_information['city'] = response['traderCity']
                trader_information['province'] = response['traderCity']
                trader_information['post_code'] = response['traderPostCode']
        else:
            # A generic country.
            raise CountryCodeNotImplemented
    else:
        raise VatNotValid

    return trader_information


def prettify_trader_information(
        information: dict, country_code: str = countries['code']['default']):
    r"""Capitalize the first letter of each word in the fields.

    :param information: a data structure containing the trader information.
    :param country_code: a two letter uppercase country identifier.
    :type information: dict
    :type country_code: str
    :returns: None
    :rtype: None
    :raises: a built-in exception.
    """
    assert len(country_code) == 2
    if country_code == 'IT':
        assert 'address' in information
        assert 'city' in information
        assert isinstance(information['address'], str)
        assert isinstance(information['city'], str)

    if country_code == 'IT':
        information['address'] = string.capwords(information['address'])
        information['city'] = string.capwords(information['city'])


def pipeline(vat_number: str,
             country_code: str = countries['code']['default'],
             trader_information_pretty=True,
             show_input=True) -> str:
    r"""Execute the pipeline.

    :param vat_number: the vat number identifier.
    :param country_code: a two letter uppercase country identifier.
    :param trader_information_pretty: change the capitalization
        of the elements to something more human readable.
    :param show_input: return the country code and the
        vat number along with the normal output.
    :type vat_number: str
    :type country_code: str
    :type trader_information_pretty: bool
    :type show_input: bool
    :returns: a data structure with all the relevant fields.
    :rtype: dict
    :raises: a built-in exception.
    """
    response = request_vat_information(vat_number, country_code)
    trader_information = parse_response(response, vat_number, country_code)
    if trader_information_pretty:
        prettify_trader_information(trader_information, country_code)
    if show_input:
        trader_information['vat_number'] = vat_number
        trader_information['country_code'] = country_code
    return trader_information
