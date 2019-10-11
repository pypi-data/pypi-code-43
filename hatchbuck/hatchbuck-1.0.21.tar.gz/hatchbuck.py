"""
Hatchbuck.com CRM API bindings for Python
"""

import datetime
import json
import logging

import phonenumbers
import pkg_resources
import requests
from pycountry import countries

LOG = logging.getLogger(__name__)


class Hatchbuck:
    """
    Class to interact with the Hatchbuck.com API
    """

    url = "https://api.hatchbuck.com/api/v1/"
    key = None
    noop = False
    hatchbuck_countries = None

    def __init__(self, key, noop=False):
        """
        Initialize API session with settings for the whole session
        :param key: Hatchbuck API key token,
        :param noop: dry-run-mode, no not call the API
        """
        self.key = key
        self.noop = noop

    def country_lookup(self, country_id):
        """
        look up the country name by country ID, parsing and caching the table on first lookup
        :param country_id: the hatchbuck country ID to get the name for
        :return: country name
        """
        if self.hatchbuck_countries is None:
            # parse and cache the table on first call
            self.hatchbuck_countries = {}
            table = json.loads(
                pkg_resources.resource_stream(__name__, "hatchbuck_countries.json")
                .read()
                .decode()
            )
            for country in table["ApiIdentifierMaster"]["IdentifierList"]:
                self.hatchbuck_countries[country["IdentifierKey"]] = country[
                    "IdentifierName"
                ]
        # look up country name from cache
        return self.hatchbuck_countries.get(country_id, None)

    def _add_country_to_address(self, address):
        """
        Helper function to add the country name to an address dict
        :param address: dict containing 'countryId' key
        :return: the dict with an additional 'country' key
        """
        address["country"] = self.country_lookup(address.get("countryId", None))
        return address

    def add_countries(self, profile):
        """
        add the country name to all addresses in the profile
        :param profile: hatchbuck profile dict
        :return: the modified dict
        """
        profile["addresses"] = [
            self._add_country_to_address(addr) for addr in profile["addresses"]
        ]
        return profile

    def search_email(self, email):
        """
        Search for profiles, and search for email addresses within them
        :param email:The email address we're looking for
        :return:Return profile if it contains the email address or None
        """
        query = {"emails": [{"address": email}]}
        LOG.debug("searching for %s", query)
        req = requests.post(
            self.url + "contact/search" + "?api_key=" + self.key, json=query
        )
        result = None
        if req.status_code == 200:
            for profile in req.json():
                if self.profile_contains(profile, "emails", "address", email):
                    LOG.debug("found: %s", profile)
                    result = self.add_countries(profile)
                else:
                    LOG.debug("found profile without matching address: %s", profile)
                    continue
            # if none of the returned profiles actually contain
            # the email address return None
        elif req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
        else:
            LOG.debug("not found")
        return result

    def search_name(self, first, last):
        """
        Search for profile using first and last name
        :param first:The first name we're looking for
        :param last:The last name we're looking for
        :return:Return profile or None
        """
        query = {"firstName": first, "lastName": last}
        LOG.debug("searching for %s", query)
        req = requests.post(
            self.url + "contact/search" + "?api_key=" + self.key, json=query
        )
        result = None
        if req.status_code == 200:
            value = req.json()
            LOG.debug("found: %s", value[0])
            result = self.add_countries(value[0])
        elif req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
        else:
            LOG.debug("not found")
        return result

    def search_email_multi(self, emails):
        """
        Search for a contact using multiple addresses, only return the first match
        :param emails: A list of email addresses
        :return: Return the first user profile that matches
        """
        if isinstance(emails, str):
            emails = [emails]
        result = None
        for email in emails:
            if email is None:
                continue
            profile = self.search_email(email)
            if profile is not None:
                result = profile
                break
        return result

    def update(self, contact_id, profile):
        """
        Update an existing contact
        :param contact_id:The contact ID we want to update
        :param profile:The profile information we want the contactID to have
        :return:Return profile with updates if successful or None if fail
        """
        profile["contactId"] = contact_id
        LOG.debug("updating %s", profile)

        if self.noop:
            LOG.debug("skipping update")
            return profile

        req = requests.put(self.url + "contact" + "?api_key=" + self.key, json=profile)
        if req.status_code == requests.codes.ok:  # pylint: disable=no-member
            value = req.json()
            LOG.debug("success: %s", value)
            return self.add_countries(value)
        if req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
            return None
        # this happens e.g. when trying to add an email address
        # that already belongs to another contact
        LOG.debug("fail: %s", req.text)
        return None

    def create(self, profile):
        """
        Create a new profile
        :param profile:The profile we want to create
        :return:Return the new profile with the new contactID if
        successful or None if fail
        """
        LOG.debug("creating %s", profile)
        if self.noop:
            profile["contactId"] = None
            return profile
        req = requests.post(self.url + "contact" + "?api_key=" + self.key, json=profile)
        if req.status_code == 200:
            value = req.json()
            LOG.debug("success: %s", value)
            return self.add_countries(value)
        if req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
            return None
        LOG.debug("fail: %s", req.text)
        return None

    def profile_add_address(self, profile, address, addresstype):
        """
        :param profile: The profile we want to add the address to
        :param address: The address we want to add
        :param addresstype: The type of address we want to add
        :return: Return the profile after adding the address to it

        """
        # try to convert the country name from a two-letter abbreviation
        try:
            country = countries.get(alpha2=address["country"]).name
        except KeyError:
            country = address["country"]

        # convert the dict field names to hatchbuck names
        update = {
            "street": address["street"],
            "zip": address["zip_code"],
            "city": address["city"],
            "country": country,
            "type": addresstype,
        }

        # check that there is at least one field that is not empty
        notempty = False
        for key in ["street", "zip", "city", "country"]:
            if update[key] is not None and update[key] != "":
                notempty = True
        if not notempty:
            return profile

        if "addresses" not in profile:
            profile["addresses"] = []

        if not self.address_exists(profile, update):
            updated = self.update(profile["contactId"], {"addresses": [update]})
            if updated is None:
                # update failed or noope'd
                return profile
            # return the new profile including the new address
            return updated
        # the profile is complete
        return profile

    @staticmethod
    def address_exists(profile, address):
        """
        try to detect if a address is already in a profile
        :param profile: haystack
        :param address: needle
        :return: Boolean True/False
        """
        for item in profile["addresses"]:
            thisisit = True
            for key in address:
                if key == "country" and not item.get("country", False):
                    # handle hatchbuck API not returning 'country'
                    # but 'countryid' by ignoring country if it does
                    # not exist in the profile
                    continue
                if not (
                    item[key] == address[key]
                    or (item[key] == "" and address[key] is None)
                ):
                    thisisit = False
            if thisisit:
                # all fields matched
                return True
        return False

    def profile_contains(self, profile, dictname, attributename, value):
        """
        :param profile:hatchbuck contact profile
        :param dictname:the information in the profile dictionary
        :param attributename:A attribut that shows address(email, phone, ...)
        :param value:Values of attributename (email, phone, ...)
        :return:Return true when get a value matching the values
        in the dictionary, or flase In the opposite case
        """
        # check if a certain email/phone/website address is
        # already in the hatchbuck contact profile
        # the hatchbuck profile is built up like:
        # profile = {
        #   dictname: (e.g. 'emails')
        #     [
        #       {
        #         attributename: value, (e.g. 'address': 'me@example.com'),
        #         the attributename and value are used for matching
        #         ... (more attributes, e.g. 'type': 'Work', added here)
        #       },
        #     ],
        #   next dict name....
        # }
        # returns False if it's not there and the dict containing
        # the value if found
        if dictname not in profile:
            return False
        if attributename is None:
            return profile[dictname].lower() == value.lower()
        for element in profile[dictname]:
            if dictname == "phones":
                # ignore spaces in phone numbers when comparing
                return self.cleanup_phone_number(
                    element[attributename]
                ) == self.cleanup_phone_number(value)
            if element[attributename].lower() == value.lower():
                return True
        return False

    @staticmethod
    def cleanup_phone_number(value):
        """
        remove unneeded characters from phone numbers
        :param value: phone number
        :return: clean phone number
        """
        for rep in "()-\xa0 ":
            # clean up number
            value = value.replace(rep, "")
        return value

    def format_phone_number(self, number, country=None):
        """
        format phone number in international format
        :param number: phone number
        :param country: two digit country code if number is in local format
        :return: clean phone number
        """
        try:
            phonenumber = phonenumbers.parse(self.cleanup_phone_number(number), country)
            return phonenumbers.format_number(
                phonenumber, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except phonenumbers.phonenumberutil.NumberParseException:
            # the number could not be formatted, e.g. because of missing country
            return None

    def clean_all_phone_numbers(self, profile):
        """
        Format and deduplicate all phone numbers in profile
        :param profile: hatchbuck contact profile
        :return: modified profile
        """
        # check if there is consensus about the contacts country
        countrycode = self.get_countrycode(profile)

        for num in list(profile.get("phones", [])):
            # iterate through a copy of the list to be able to delete elements
            # when self.noop is True
            formatted = self.format_phone_number(num["number"])
            if formatted is None and countrycode is not None:
                formatted = self.format_phone_number(num["number"], countrycode)
            if formatted is None:
                # local number and unknown country? ignore and continue
                formatted = self.cleanup_phone_number(num["number"])
            # check if this number is a duplicate
            if any(
                [
                    other["id"] != num["id"]
                    and (
                        other["number"] == formatted  # same number
                        or (
                            formatted.startswith("0")  # local number
                            and self.cleanup_phone_number(other["number"]).endswith(
                                formatted[1:]
                            )
                        )
                    )
                    for other in profile["phones"]
                ]
            ):
                # this formatted is a duplicate or substring
                # (local version of an existing international version of the same number)
                # remove this duplicate
                logging.debug(
                    "%s: phone number %s is a duplicate, removing",
                    self.short_contact(profile),
                    num["number"],
                )
                if self.noop:
                    profile["phones"].remove(num)
                else:
                    newprofile = self.update(
                        profile["contactId"],
                        {
                            "phones": [
                                {"number": "", "id": num["id"], "type": num["type"]}
                            ]
                        },
                    )
                    if newprofile is not None:
                        # if the update was successful continue working
                        # with the new profile
                        profile = newprofile

            elif formatted != num["number"]:
                # the number was updated
                logging.debug(
                    "%s: phone number %s formatted, updating",
                    self.short_contact(profile),
                    formatted,
                )
                if self.noop:
                    num["number"] = formatted
                else:
                    newprofile = self.update(
                        profile["contactId"],
                        {
                            "phones": [
                                {
                                    "number": formatted,
                                    "id": num["id"],
                                    "type": num["type"],
                                }
                            ]
                        },
                    )
                    if newprofile is not None:
                        # if the update was successful continue working
                        # with the new profile
                        profile = newprofile
            else:
                # number was not changed
                pass
        return profile

    @staticmethod
    def get_countrycode(profile):
        """
        Extract country code from addresses
        :param profile: contact profile
        :return: two-letter country code or None if not unambiguous
        """
        countries_found = []
        for addr in profile.get("addresses", []):
            if (
                addr.get("country", False)
                and addr["country"].lower() not in countries_found
            ):
                countries_found.append(addr["country"].lower())
        logging.debug("countries found %s", countries_found)
        if len(countries_found) == 1:
            # look up the country code
            return countries.lookup(countries_found[0]).alpha_2
        return None

    @staticmethod
    def short_contact(profile):
        """
        Return a short version of an contact
        """
        text = ""
        if profile.get("firstName", False) and profile.get("lastName", False):
            text += "%s %s, " % (profile["firstName"], profile["lastName"])
        for email in profile.get("emails", []):
            text += "%s, " % email["address"]
        return "Contact(%s)" % text[:-2]

    def profile_add(
        self, profile, dictname, attributename, valuelist, moreattributes=None
    ):  # pylint: disable=too-many-arguments,too-many-branches
        """
        Add a new fields to the profile if it does not exist,
        or update the field if it exists
        :param profile: The profile we want to add or modify fields
        :param dictname: The name of the field we're looking for to add or edit
        :param attributename: The name of the attribute
        we're looking for to add or edit
        :param valuelist: The values of the attribute
        :param moreattributes: dict of attributes that we want to add or modify
        :return: Return profile after adding or editing fields
        """
        # add a certain email/phone/website field to the
        # hatchbuck contact profile if it's not there already
        # the hatchbuck profile is built up like:
        # profile = {
        #   dictname: (e.g. 'emails')
        #     [
        #       {
        #         attributename: value, (e.g. 'address': 'me@example.com'),
        #         the attributename and value are used for matching
        #         ... (more attributes, e.g. 'type': 'Work', added here)
        #       },
        #     ],
        #   next dict name....
        # }
        if not isinstance(valuelist, list):
            valuelist = [valuelist]
        for value in valuelist:
            if attributename is None:
                updateprofile = {dictname: value}
            else:
                updateprofile = {dictname: [{attributename: value}]}
            if (
                value is not None
                and value != ""
                and not self.profile_contains(profile, dictname, attributename, value)
            ):
                if dictname == "emails" and attributename == "address":
                    lookup = self.search_email(value)
                    if (
                        lookup is not None
                        and lookup["contactId"] != profile["contactId"]
                    ):
                        # uh-oh there is already another contact
                        #  with this email address, possible duplicate
                        LOG.warning(
                            "uh-oh trying to add email address %s to %s"
                            " already belonging to another contact %s,"
                            " not adding",
                            value,
                            profile,
                            lookup,
                        )
                        return profile
                elif dictname == "phones" and attributename == "number":
                    value = self.cleanup_phone_number(value)
                if moreattributes is not None:
                    for key in moreattributes:
                        updateprofile[dictname][0][key] = moreattributes[key]
                # pylint: disable=fixme
                # TODO updating the profile through the API right now instead
                # TODO  of batching them, can be optimized later if necessary
                updated = self.update(profile["contactId"], updateprofile)
                if updated is not None:
                    # update not failed or noop'ed
                    profile = updated
                else:
                    LOG.debug("update failed or nooped")
            else:
                LOG.debug(
                    "skipping update because value empty " "or there already: %s",
                    updateprofile,
                )
        return profile

    def add_tag(self, contact_id, tagname):
        """
        Add tag to contact
        :param contact_id: A contact ID to which the tag should be added
        :param tagname: Tag that we want to add to contact_id
        """
        LOG.debug("adding tag %s to contact %s", tagname, contact_id)
        profile = [{"name": tagname}]
        if self.noop:
            return None
        req = requests.post(
            self.url + "contact/" + contact_id + "/Tags?api_key=" + self.key,
            json=profile,
        )
        if req.status_code == 201:
            LOG.debug("success: %s", req.text)
        elif req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
        else:
            LOG.debug("fail: %s", req.text)
        return None

    def remove_tag(self, contact_id, tagname):
        """
        Remove tag from contact
        :param contact_id: A contact ID from which the tag should be removed
        :param tagname: Tag that we want to remove from the contact
        """
        LOG.debug("removing tag %s from contact %s", tagname, contact_id)
        profile = [{"name": tagname}]
        if self.noop:
            return None
        req = requests.delete(
            self.url + "contact/" + contact_id + "/Tags?api_key=" + self.key,
            json=profile,
        )
        if req.status_code == 201:
            LOG.debug("success: %s", req.text)
        elif req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
        else:
            LOG.debug("fail: %s", req.text)
        return None

    def profile_add_birthday(self, profile, date):
        """
        Add birthday to profile
        :param profile: A profile to which the birthday should be added
        :param date: The birthday should be added to the file
        :return:Return profile after adding the birthday
        """
        if not date.get("day", 0) or not date.get("month", 0):
            LOG.debug("no day/month in birthday %s, skipping", date)
            return profile
        if not date.get("year", 0):
            # set year 1000 for unknown year, year 0 is not
            # supported by python datetime.date
            date["year"] = 1000
        oldbirthday = ""
        for field in profile.get("customFields", []):
            if field["name"] == "Birthday":
                oldbirthday = field["value"]
                break
        if oldbirthday:
            oldbirthday = datetime.datetime.strptime(oldbirthday, "%m/%d/%Y").date()
            LOG.debug("found old birthday: %s", oldbirthday)
            if oldbirthday.year != 1000 and date["year"] == 1000:
                # if there is a proper year already lets not overwrite that
                date["year"] = oldbirthday.year
        return self.profile_add(
            profile,
            "customFields",
            "value",
            "%s/%s/%s" % (date["month"], date["day"], date["year"]),
            {"name": "Birthday"},
        )
