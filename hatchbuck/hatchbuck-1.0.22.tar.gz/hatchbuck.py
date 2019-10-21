"""
Hatchbuck.com CRM API bindings for Python
"""

import datetime
import json
import logging
import re
import copy

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

    listdictkeys = {
        "emails": ["address"],
        "addresses": ["country", "state", "city", "zip", "street"],
        # "customFields": ["value"], # custom fields are empty, not deleted
        "phones": ["number"],
        "socialNetworks": ["address"],
    }

    def __init__(self, key, noop=False):
        """
        Initialize API session with settings for the whole session
        :param key: Hatchbuck API key token,
        :param noop: dry-run-mode, no not call the API
        """
        self.key = key
        self.noop = noop

    def _country_lookup(self, country_id):
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
        address["country"] = self._country_lookup(address.get("countryId", None))
        if address.get("countryId", False):
            del address["countryId"]
        return address

    def _add_countries(self, profile):
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
                    result = self._add_countries(profile)
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
            result = self._add_countries(value[0])
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

    def silent_update(self, profile, update):
        """
        update a profile, respecting noop, and return the updated profile

        if an error happens (invalid data or api token) the _unmodified profile_
        is returned and the error message logged
        :param profile: profile dict with contactId
        :param update: the dict key(s) to update/overwrite (basically the diff)
        :return: updated profile
        """
        newprofile = self.safe_update(profile, update)
        if newprofile is None:
            return profile
        return newprofile

    def safe_update(self, profile, update):  # pylint: disable=too-many-branches
        """
        update a profile, respecting noop, and return the updated profile

        if self.noop is True no update will be done to hatchbuck.com and
        this function tries to simulate what would happen
        :param profile: profile dict with contactId
        :param update: the dict key(s) to update/overwrite (basically the diff)
        :return: updated profile
        """
        # logging.warning("safe_update %s %s", profile, update)
        if not self.noop:
            return self.update(profile["contactId"], update)

        # for these list-of-dicts: if the dict fields with these names are empty the
        # whole dict is removed

        for key in update:  # pylint: disable=too-many-branches,too-many-nested-blocks
            if isinstance(update[key], str):
                # simple field like firstName, lastName etc
                # logging.warning("str %s", update[key])
                profile[key] = update[key]
            elif isinstance(update[key], dict):
                # dict like salesRep
                # logging.warning("dict %s", update[key])
                # for subkey in update[key]:
                #    profile[key][subkey] = update[key][subkey]
                # actually replace the whole dict, since we don't know the new id
                # of the new sales rep we'll just leave it out
                profile[key] = update[key]
            elif isinstance(update[key], list):
                # list of dicts like "emails", "addresses" etc
                # logging.warning("list %s", update[key])
                for item in update[key]:
                    # logging.warning("item %s", item)
                    if item.get("id", False):
                        # if there is an existing id in the update lets use that
                        lookforfield = ["id"]
                    elif self.listdictkeys.get(key, False) and all(
                        [item.get(impkey, False) for impkey in self.listdictkeys[key]]
                    ):
                        # if the update contains all listdictkeys lets try to find this
                        lookforfield = self.listdictkeys[key]
                    else:
                        # we can't identify if this is a potential duplicate/update
                        # this is mostly a case for (incomplete) addresses
                        # as all the other types (emails, phones, etc) without the
                        # primary listdictkey information (email address, phone number,
                        # etc) would not be accepted by hatchbuck.
                        # we'll add incomplete addresses (at least one field needs to
                        # be nonempty, making sure all the fields are present)
                        # and ignore other updates (emails, phones, social)
                        # if the address is a duplicate it will be deduplicated in
                        # clean_all_addresses, which we don't call now
                        if key == "addresses" and any(
                            [item.get(field, False) for field in self.listdictkeys[key]]
                        ):
                            for field in self.listdictkeys[key]:
                                if field not in item:
                                    item[field] = ""
                            profile[key].append(item)
                        break

                    # find the corresponding id element in profile
                    found = False
                    for listitem in range(len(profile[key])):
                        # iterate over the list offset to re-use the offset for
                        # update or delete later
                        if all(
                            [
                                profile[key][listitem].get(impkey) == item.get(impkey)
                                for impkey in lookforfield
                            ]
                        ):
                            found = listitem
                            # logging.warning("found %s", found)
                            break

                    if found is not False:
                        if self.listdictkeys.get(key, False) and all(
                            [
                                item.get(impkey, "") == ""
                                for impkey in self.listdictkeys[key]
                            ]
                        ):
                            # all the "primary key" fields are empty,
                            # that means the entry should be deleted
                            # logging.warning("deleting %s", found)
                            del profile[key][found]
                        else:
                            for subkey in item:
                                # logging.warning("setting %s", subkey)
                                profile[key][found][subkey] = item[subkey]
                    else:
                        # didn't find a matching list entry -> add
                        profile[key].append(item)
            else:
                logging.warning("safe_update: unknown field type in %s", update[key])

        return profile

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
            return self._add_countries(value)
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
        :param profile:The profile we want to create, email and status required
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
            return self._add_countries(value)
        if req.status_code == 401:
            LOG.error("Hatchbuck API code wrong or expired?")
            return None
        LOG.debug("fail: %s", req.text)
        return None

    def add_address(
        self,
        profile,
        street="",
        zipcode="",
        city="",
        state="",
        country="",
        addresstype="Work",
    ):  # pylint: disable=too-many-arguments,too-many-branches
        """
        Add street address to profile and return updated profile
        :param profile: profile to add address to
        :param street: street name and number
        :param zipcode: zip code
        :param city: city
        :param state: state
        :param country: country (preferably english version)
        :param addresstype: "Work", "Home" or "Other"
        :return: updated profile
        """
        update = self._clean_address(
            {
                "street": street,
                "zip": zipcode,
                "city": city,
                "state": state,
                "country": country,
                "type": addresstype,
            }
        )
        for address in profile.get("addresses", []):
            if self._address_obsolete(update, address):
                # don't add the address if it is obsolete
                return profile
        return self.silent_update(profile, {"addresses": [update]})

    def profile_add_address(self, profile, address, addresstype):
        """
        :param profile: The profile we want to add the address to
        :param address: The address we want to add
        :param addresstype: The type of address we want to add
        :return: Return the profile after adding the address to it

        """
        return self.add_address(
            profile,
            address["street"],
            address["zip_code"],
            address["city"],
            "",
            address["country"],
            addresstype,
        )

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
                return self._cleanup_phone_number(
                    element[attributename]
                ) == self._cleanup_phone_number(value)
            if element[attributename].lower() == value.lower():
                return True
        return False

    @staticmethod
    def _cleanup_phone_number(value):
        """
        remove unneeded characters from phone numbers
        :param value: phone number
        :return: clean phone number
        """
        for rep in "()-\xa0 ":
            # clean up number
            value = value.replace(rep, "")
        return value

    def _format_phone_number(self, number, country=None):
        """
        format phone number in international format
        :param number: phone number
        :param country: two digit country code if number is in local format
        :return: clean phone number
        """
        try:
            phonenumber = phonenumbers.parse(
                self._cleanup_phone_number(number), country
            )
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
        countrycode = self._get_countrycode(profile)

        for num in list(profile.get("phones", [])):
            # iterate through a copy of the list to be able to delete elements
            # when self.noop is True
            formatted = self._format_phone_number(num["number"])
            if formatted is None and countrycode is not None:
                formatted = self._format_phone_number(num["number"], countrycode)
            if formatted is None:
                # local number and unknown country? ignore and continue
                formatted = self._cleanup_phone_number(num["number"])
            # check if this number is a duplicate
            if any(
                [
                    other["id"] != num["id"]
                    and (
                        other["number"] == formatted  # same number
                        or (
                            formatted.startswith("0")  # local number
                            and self._cleanup_phone_number(other["number"]).endswith(
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
                profile = self.silent_update(
                    profile,
                    {"phones": [{"number": "", "id": num["id"], "type": num["type"]}]},
                )

            elif formatted != num["number"]:
                # the number was updated
                logging.debug(
                    "%s: phone number %s formatted, updating",
                    self.short_contact(profile),
                    formatted,
                )
                profile = self.silent_update(
                    profile,
                    {
                        "phones": [
                            {"number": formatted, "id": num["id"], "type": num["type"]}
                        ]
                    },
                )
            else:
                # number was not changed
                pass
        return profile

    @staticmethod
    def _get_countrycode(profile):
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

    def clean_all_addresses(self, profile):
        """
        clean and deduplicate all contact addresses
        :param profile: contact profile
        :return: cleaned and deduplicated profile
        """
        for address in copy.deepcopy(profile.get("addresses", [])):
            # iterate through a copy of the list to be able to delete entries in-flight
            # clean up the address first
            new = copy.deepcopy(address)
            new = self._clean_address(new)
            logging.info("iterating old: %s, new: %s", address, new)
            if new != address:
                # there was an update
                logging.info(
                    "%s: updating address to %s", self.short_contact(profile), new
                )
                profile = self.silent_update(profile, {"addresses": [new]})
            # now check if there is a more-specific address that makes
            # this address obsolete/redundant
            for other in profile["addresses"]:
                if (
                    other.get("id", "") != new.get("id", "")
                    and other != new
                    and self._address_obsolete(new, other)
                ):
                    # we are an obsolete address
                    logging.info(
                        "%s: deleting obsolete address %s",
                        self.short_contact(profile),
                        new,
                    )
                    profile = self.silent_update(
                        profile,
                        {
                            "addresses": [
                                {
                                    "id": new["id"],
                                    "type": new["type"],
                                    "city": "",
                                    "country": "",
                                    "countryId": "",
                                    "state": "",
                                    "street": "",
                                    "zip": "",
                                }
                            ]
                        },
                    )
                    if new.get("isPrimary", False):
                        # uh-oh we deleted the the primary address
                        profile = self.silent_update(
                            profile,
                            {
                                "addresses": [
                                    {
                                        "id": other["id"],
                                        "type": other["type"],
                                        "isPrimary": True,
                                    }
                                ]
                            },
                        )
                    break  # from finding the redundant other

        return profile

    def _address_obsolete(self, this, other):
        """
        Decide if this address is redundant/less-specific/obsolete compared to other
        :param this: this address
        :param other: other address
        :return: True if this is redundant to other
        """
        for field in self.listdictkeys["addresses"]:
            if this.get(field, False) and (
                not other.get(field, False) or this[field] != other[field]
            ):
                # if this has a country/state/city/zip/street and other not or not
                # the same -> this is more specific
                logging.debug(
                    "%s has more information than %s, not obsolete", this, other
                )
                return False

        if all(
            [
                not this.get(field, False) or this[field] == other[field]
                for field in self.listdictkeys["addresses"]
            ]
        ):
            # this matches other in all non-empty fields -> this is redundant
            logging.debug(
                "%s has only empty or same fields than %s, obsolete", this, other
            )
            return True

        thisscore = 0
        otherscore = 0
        for field in self.listdictkeys["addresses"]:
            if this.get(field, False):
                thisscore = thisscore * 2 + 1
            if other.get(field, False):
                otherscore = otherscore * 2 + 1
        if thisscore > otherscore:
            logging.debug(
                "%s score %s > %s score %s, not obsolete",
                this,
                thisscore,
                other,
                otherscore,
            )
            return False
        logging.debug(
            "%s score %s <= %s score %s, obsolete", this, thisscore, other, otherscore
        )
        return True

    def _clean_address(self, address):  # pylint: disable=too-many-branches
        """
        clean up an address
        :param address: address dict
        :return: cleaned up address
        """
        if address.get("country", ""):
            # check if the country is a valid country name
            # this also fixes two letter country codes
            try:
                country = countries.search_fuzzy(
                    self._clean_country_name(address["country"])
                )[0].name
            except LookupError:
                country = False
            if country and country != address["country"]:
                address["country"] = country
        if re.match(r"^[a-zA-Z]{2}-[0-9]{4,6}$", address.get("zip", "")):
            # zipcode contains country code (e.g. CH-8005)
            countrycode, zipcode = address["zip"].split("-")
            try:
                address["country"] = countries.lookup(countrycode).name
                address["zip"] = zipcode
            except LookupError:
                pass
        if (
            not address.get("street", "")
            and not address.get("zip", "")
            and address.get("city", "")
        ):
            # there is a city but no street/zip
            # logging.warning(address["city"].split(","))
            if len(address["city"].split(",")) == 3:
                # Copenhagen Area, Capital Region, Denmark
                # Lausanne, Canton de Vaud, Suisse
                # Vienna, Vienna, Austria
                try:
                    address["country"] = countries.search_fuzzy(
                        self._clean_country_name(address["city"].split(",")[2])
                    )[0].name
                    address["city"] = self._clean_city_name(
                        address["city"].split(",")[0]
                    )
                except LookupError:
                    pass
            elif len(address["city"].split(",")) == 2:
                # Zürich und Umgebung, Schweiz
                # Currais Novos e Região, Brasil
                # München und Umgebung, Deutschland
                # Région de Genève, Suisse
                # Zürich Area, Svizzera
                try:
                    address["country"] = countries.search_fuzzy(
                        self._clean_country_name(address["city"].split(",")[1])
                    )[0].name
                    address["city"] = self._clean_city_name(
                        address["city"].split(",")[0]
                    )
                except LookupError:
                    pass
            elif len(address["city"].split(",")) == 1:
                # United States
                # Switzerland
                # Luxembourg
                try:
                    address["country"] = countries.search_fuzzy(
                        self._clean_country_name(self._clean_city_name(address["city"]))
                    )[0].name
                    # if the lookup is successful this is a country name, not city name
                    address["city"] = ""
                except LookupError:
                    pass

        if address.get("type", "") not in ["Work", "Home", "Other"]:
            address["type"] = "Other"
        # ensure all relevant fields are set
        address["street"] = self._clean_street_name(address.get("street", ""))
        address["city"] = self._clean_city_name(address.get("city", ""))
        address["zip"] = address.get("zip", "").strip()
        address["state"] = address.get("state", "").strip()
        address["country"] = self._clean_country_name(address.get("country", ""))
        return address

    @staticmethod
    def _clean_street_name(street):
        """
        clean and normalize street name
        :param street: street
        :return: clean street name
        """
        if street.strip() == "geolocation":
            # magic word from website geolocation
            street = ""
        if street.strip() == "False":
            # bug in odoo2hatchbuck
            street = ""
        street = street.replace("str. ", "strasse ")
        street = street.replace("str ", "strasse ")
        return street.strip()

    @staticmethod
    def _clean_country_name(country):
        """
        look up country names not covered by pycountry
        :param country: country
        :return: clean country name
        """
        if country is None:
            country = ""
        country = country.strip()
        mapping = {
            "suisse": "Switzerland",
            "svizzera": "Switzerland",
            "schweiz": "Switzerland",
            "deutschland": "Germany",
            "brasil": "Brazil",
        }
        return mapping.get(country.lower(), country)

    @staticmethod
    def _clean_city_name(city):
        """
        remove "area", "region" words from city names
        :param city: city name
        :return: clean city name
        """
        for word in [
            " Bay Area",
            " area",
            " Area",
            "Greater ",
            "und Umgebung",
            "e Região",
            "Région de",
        ]:
            city = city.replace(word, "")

        mapping = {"zurich": "Zürich"}

        return mapping.get(city.strip().lower(), city.strip())

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
                    value = self._cleanup_phone_number(value)
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
