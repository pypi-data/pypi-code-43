# Unofficial NonameDomain API module
# Copyright (C) 2019 Slacker

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import requests

class NonameDomain(requests.Session):
    """ Class to implement CRUD operations to the Noname Domain API """

    __LOGIN_URL = "https://www.nonamedomain.hu/api/pub/account/authentication"

    def __init__(self, domain, api_user = None, api_pw = None, token = None):
        """ Log into the API.

        Args:
            domain: the domain to manage
            api_user: API user
            api_pw: password of API user
            token: API token

        Raises:
            ValueError: if neither user+password or token provided

        Examples:
            `nnd = pynonamedomain.NonameDomain("example.com", "username", "password")`  
            `nnd = pynonamedomain.NonameDomain("example.org", token = "3e4n23y87tresnt32erstn48")`  
        """
        super(NonameDomain, self).__init__()
        self.API_URL = f"https://www.nonamedomain.hu/api/tapi/domain/{domain}"
        if token:
            self.token = token
        elif api_user and api_pw:
            self.credentials = dict()
            self.credentials["username"] = api_user
            self.credentials["password"] = api_pw
            self.token = self.__get_token()
        else:
            raise ValueError("Either username+password or token is required.")
        self.headers = dict()
        self.headers["Content-Type"] = "application/json"
        self.headers["MonsterToken"] = self.token
        self.all_subdomains = None
        self.read(cached = False)

    def __get_token(self):
        """ Get API token.

        Raises:
            requests.HTTPError: if HTTP error occurs
            requests.SSLError: if SSL error occurs

        Returns:
            API token
        """
        response = self.post(url = self.__LOGIN_URL, data = json.dumps(self.credentials))
        response.raise_for_status()
        return response.json()['result']['token']

    def create(self, **data):
        """ Create new DNS entry.

        Args:
            **data: a dictionary with all the necessary data to create a new entry

        Raises:
            SubdomainAlreadyExists: if entry already exists
            requests.HTTPError: if HTTP error occurs
            requests.SSLError: if SSL error occurs

        Returns:
            'ok' if entry created successfully

        Examples:
            `nnd.create(type = "A", host = "test", "ip" = "192.168.0.1", ttl = "600")`  
            `nnd.create(type = "TXT", text = "something", host = "sample", ttl = "60")`  
        """
        try:
            self.read(cached = False, **data)
            raise SubdomainAlreadyExists
        except SubdomainNotFound:
            response = self.put(url = self.API_URL, data = json.dumps(data))
            response.raise_for_status()
            self.read(cached = False)
            return self.read(**data)[0]["hash"]

    def read(self, cached = True, **search):
        """ Read the current entries in the zone.

        Args:
            cached: returns cached list if True, otherwise query the API
            **search: filter the entries based on their attributes

        Raises:
            SubdomainNotFound: if entry not found

        Returns:
            all subdomains if 'search' is omitted, otherwise the matching subdomains

        Examples:
            `nnd.read()`  
            `nnd.read(cached = False)`  
            `nnd.read(type = "A")`  
        """
        if not cached:
            response = self.get(url = self.API_URL)
            response.raise_for_status()
            self.all_subdomains = response.json()["result"]["records"]
        if not search:
            return self.all_subdomains
        else:
            found = list()
            for record in self.all_subdomains:
                if search.items() <= record.items():
                    found.append(record)
            if (bool(found)):
                return found
            else:
                raise SubdomainNotFound

    def remove(self, record_hash):
        """ Remove entry from the zone.

        Args:
            record_hash: hash of the entry to be deleted

        Raises:
            requests.HTTPError: if HTTP error occurs
            requests.SSLError: if SSL error occurs

        Returns:
            'ok' if entry removed successfully

        Examples:
            `nnd.remove("ab83e38eaquf86ye28e35E8c6")`  
        """
        self.read(cached = False, hash = record_hash)
        response = self.delete(f"{self.API_URL}/{record_hash}")
        response.raise_for_status()
        self.read(cached = False)
        return "ok"

    def update(self, record_hash, new_values):
        """ Update entry in the zone.

        Args:
            record hash: hash of the entry to be updated
            new_values: dictionary of the new attributes

        Raises:
            ValueError: if 'new_values' is not a dictionary

        Returns:
            'ok' if entry updated successfully

        Examples:
            `nnd.update("ab83e38eaquf86ye28e35E8c6", text = "newtext", ttl = "300")`  
            `nnd.update("ab83e38eaquf86ye28e35E8c6", type = "A", ip = "192.168.1.38")`  
        """
        if isinstance(new_values, dict):
            found = list()
            found = self.read(cached = False, hash = record_hash)
            self.remove(record_hash)
            new_values = {**found[0], **new_values}
            new_values.pop("hash", None)
            self.create(**new_values)
            return self.read(**new_values)[0]
        else:
            raise ValueError("new_values must be a dictionary")

class SubdomainNotFound(Exception):
    """ Raised if subdomain not found. """
    def __init__(self):
        super(SubdomainNotFound, self).__init__("Subdomain not found.")

class SubdomainAlreadyExists(Exception):
    """ Raised if subdomain already exists. """
    def __init__(self):
        super(SubdomainAlreadyExists, self).__init__("Subdomain already exists.")
