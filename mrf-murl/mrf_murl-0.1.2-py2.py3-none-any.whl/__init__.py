#!/usr/bin/env python3
"""
Murl
====
The URI object class.
"""
from . import urlsec, urlende
import re
import pkg_resources


class Murl(object):
    """Initialize an instance of Murl with the following optional params:

        - url: String with URI, default: empty string.
        - queryDelim: char to separate key=value pairs, default: &,
            recommended: & or ;.

        Initialization can raise a *ValueError* if:

        - There is an '@' in an existing Authority without there being both a
            username:password pair.
        - There is no host specified in an existing Authority.
        - Host has imbalanced IPv6 brackets.
        - Port number is not between 1 and 65535 inclusive.
        - There is more than one colon in Authority outside username:password
            and without the host being IPv6.

        The entire assembled URI, as a str, is available through the standard
            str() function.

        All properties, if not already set, will return/be None on get.
    """

    def __init__(self, url="", queryDelim="&"):
        self._attrs = urlsec.divideURL(url, queryDelim)
        self._queryDelim = queryDelim

    def __str__(self):
        return urlsec.assembleURL(self._attrs, self.queryDelim)

    @property
    def queryDelim(self):
        """Get or set the current query delimeter."""
        return self._queryDelim

    @queryDelim.setter
    def queryDelim(self, val):
        self._queryDelim = val

    @property
    def scheme(self):
        """Get or set the current scheme. Raises a *ValueError* on set if:

            - Scheme doesn't comply with standard format
                (letter that can be followed by letters, digits, +, ., or -).
        """
        val = self._attrs["scheme"]
        return val if not val == "" else None

    @scheme.setter
    def scheme(self, val):
        val = val.lower()
        if re.match(r"^([a-z]+)([a-z]|\d|\+|\.|\-)*$", val) is None:
            raise ValueError(
                "Scheme has to start with a letter, followed by "
                + "letters, digits, +, ., or -."
            )
        else:
            self._attrs["scheme"] = val

    def _getAuthProperty(self, prop):
        return (
            None
            if self._attrs["authority"] == ""
            or self._attrs["authority"][prop] == ""
            else urlende.decode(self._attrs["authority"][prop])
        )

    def _setAuthProperty(self, prop, val):
        other = "password" if prop == "username" else "username"
        if self._attrs["authority"] == "":
            raise ValueError(
                "This URI has no host specified. Add one using the"
                + " 'host' property."
            )
        elif prop != "port" and self._attrs["authority"][other] == "":
            raise ValueError(
                "This URI has no "
                + other
                + " already set. To set"
                + " both, use  the 'auth' property."
            )
        elif prop == "port" and (
                type(val) is not int or val < 1 or val > 65535):
            raise ValueError(
                "Port number has to be an int between 1 and 65535 inclusive."
            )
        else:
            valEncoded = urlende.isEncoded(val, safe="")
            self._attrs["authority"][prop] = (
                val if valEncoded else urlende.encode(val, safe="")
            )

    @property
    def host(self):
        """Get or set host. Raises a *ValueError* on set if:

            - Value has imbalanced IPv6 brackets ('[' but no following ']',
            or vice versa)
        """
        return self._getAuthProperty("host")

    @host.setter
    def host(self, val):
        if ("[" in val and "]" not in val[val.index("["):]) or (
            "]" in val and "[" not in val[: val.index("]")]
        ):
            raise ValueError("Host has imbalanced IPv6 brackets.")
        if self._attrs["authority"] == "":
            username = password = port = ""
            self._attrs["authority"] = dict(
                username=username, password=password,
                port=port, host=val.lower()
            )
        else:
            self._attrs["authority"]["host"] = val.lower()

    @property
    def domain(self):
        """Get domain only of the URI.
        If IPv4/6 or no registered public suffix is found, domain = host.
        This assumes the longest matching public suffix is the host's public
        suffix. For example:
       ::
            amazon.com.mx
        would match .mx, and .com.mx. The longer is .com.mx, therefore it's
        assumed as the public suffix.
        """
        IPv4 = (
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            + r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        if (
            self.host is None
            or "[" in self.host
            or re.match(IPv4, self.host) is not None
        ):
            return self.host
        else:  # not None, IPv6 or IPv4
            # We want to extract the domain + public suffix
            LOC = "data/public_suffix_list.dat"
            DATA_PATH = pkg_resources.resource_filename(__name__, LOC)
            with open(DATA_PATH) as content:
                public_suffix = ""
                for i, line in enumerate(content):
                    if not line.startswith("//") and not line.startswith("\n"):
                        suffix = "." + line.split("\n")[0]
                        if (
                            suffix in self.host
                            and self.host.rfind(suffix) + len(suffix)
                            == len(self.host)
                            and len(public_suffix) < len(suffix)
                        ):
                            public_suffix = suffix
            if public_suffix != "":
                beginSuffix = self.host.rfind(public_suffix)
                beginDomain = self.host.rfind(".", 0, beginSuffix)
                return self.host[beginDomain + 1:]
            else:  # if no public suffix available, return entire host
                return self.host

    @property
    def auth(self):
        """Get or set authentication part as a dict with the keys 'username'
        and 'password'.
        Raises *ValueError* on set if:

        - Value is not a dict with the keys 'username' and 'password'.

        On set, detects if username/password are already percent-encoded.
        """
        notFound = (
            self._attrs["authority"] == ""
            or self._attrs["authority"]["username"] == ""
        )
        return (
            None
            if notFound
            else dict(
                username=urlende.decode(self._attrs["authority"]["username"]),
                password=urlende.decode(self._attrs["authority"]["password"]),
            )
        )

    @auth.setter
    def auth(self, authdict):
        if self._attrs["authority"] == "":
            raise ValueError(
                "Cannot add authentication without host. "
                + "Add host using the 'host' property."
            )
        elif (
            type(authdict) is dict
            and "username" in authdict and "password" in authdict
        ):
            u, p = authdict["username"], authdict["password"]
            uEncoded, pEncoded = (
                urlende.isEncoded(u, safe=""),
                urlende.isEncoded(p, safe=""),
            )
            self._attrs["authority"]["username"] = (
                u if uEncoded else urlende.encode(u, safe="")
            )
            self._attrs["authority"]["password"] = (
                p if pEncoded else urlende.encode(p, safe="")
            )
        else:
            raise ValueError(
                "Auth value must be a dict with the keys "
                + "'username' and 'password'."
            )

    @property
    def username(self):
        """Get or set username individually. Raises a *ValueError* on set if:

        - Host has not yet been set.
        - Password is not already set.

        On set, detects if username is already percent-encoded.
        """
        return self._getAuthProperty("username")

    @username.setter
    def username(self, val):
        self._setAuthProperty("username", val)

    @property
    def password(self):
        """Get or set password individually. Raises a *ValueError* on set if:

        - Host has not yet been set.
        - Username is not already set.

        On set, detects if password is already percent-encoded.
        """
        return self._getAuthProperty("password")

    @password.setter
    def password(self, val):
        self._setAuthProperty("password", val)

    @property
    def port(self):
        """Get or set port number. Raises a *ValueError* on set if:

        - Host has not yet been set.
        - Port is not an int between 1 and 65535, inclusive.
        """
        return self._getAuthProperty("port")

    @port.setter
    def port(self, val):
        self._setAuthProperty("port", val)

    @property
    def path(self):
        """Get or set path. Returns *ValueError* on set if:

        - Path starts with two forward slashes.

        On set, detects if path is already percent-encoded.
        On get, unlike other components, the encoded path is returned.
        """
        return None if self._attrs["path"] == "" else self._attrs["path"]

    @path.setter
    def path(self, val):
        if val.startswith("//"):
            raise ValueError("Path cannot start with two forward slashes.")
        self._attrs["path"] = val if urlende.isEncoded(val) \
            else urlende.encode(val)

    def addQuery(self, key, val, spaceIsPlus=True):
        """Add a single key=value pair to the Query part.
        Function will detect if key/value is already encoded.
        Params:
            - key (str): key for this pair. Can be existing key to add to its
                values.
            - val (str): value for this pair.
            - spaceIsPlus (bool): Optional. True if space should be encoded as
                + instead of %20.
        """
        keyEncoded = urlende.isEncoded(key, plus=spaceIsPlus, safe="")
        valEncoded = urlende.isEncoded(val, plus=spaceIsPlus, safe="")
        oldQ = self._attrs["query"]
        key = key if keyEncoded else urlende.encode_query(key, spaceIsPlus)
        val = val if valEncoded else urlende.encode_query(val, spaceIsPlus)
        if oldQ == "":  # empty
            temp = {}
            temp[key.lower()] = [val]
            self._attrs["query"] = temp
        elif key.lower() in self._attrs["query"]:
            self._attrs["query"][key.lower()].append(val)
        else:
            self._attrs["query"][key.lower()] = [val]

    def getQuery(self, key, decodeVal=True, spaceIsPlus=True):
        """Get list of values for a given key. Raises a *KeyError* if:
            - Key does not exist in this URI's Query.
        Function will detect if key is already encoded.
        Params:
            - key (str): key whose values you want as a list.
            - decodeVal (bool): Optional. True if values are to be returned
                decoded.
            - spaceIsPlus (bool): Optional. True if space should be encoded as
                + instead of %20.
        """
        keyEncoded = urlende.isEncoded(key, plus=spaceIsPlus, safe="")
        if self._attrs["query"] != "":
            key = key if keyEncoded else urlende.encode_query(key, spaceIsPlus)
            arr = self._attrs["query"][key.lower()]
            res = [] if decodeVal else arr
            if decodeVal:
                for val in arr:
                    enc = urlende.decode_query(val, spaceIsPlus)
                    res.append(enc)
            return res
        else:
            raise KeyError("Key does not exist.")

    def changeQuery(self, key, newVal, val=None, spaceIsPlus=True):
        """Change one or all values for a specific key. Raises a *KeyError* if:
            - Key does not exist in the URI's Query.
        And a *ValueError* if:
            - A value is specified but it does not exist for this key.
        Function detects if key/values are already encoded.
        Params:
            - key (str): key whose value(s) you want to change.
            - newVal (str): new value instead of the pre-existing value(s).
            - val (str): Old value if only one value is to be changed instead
                of all.
            - spaceIsPlus (bool): Optional. True if space should be encoded as
                + instead of %20.
        """
        # 1. Remove current query
        self.removeQuery(key, val, spaceIsPlus)
        # 2. Add the new query
        self.addQuery(key, newVal, spaceIsPlus)

    def removeQuery(self, key, val=None, spaceIsPlus=True):
        """Remove one or all values for a specific key. Raises a *KeyError* if:
            - Key does not exist in the URI's Query.
        And a *ValueError* if:
            - A value is specified but it does not exist for this key.
        Function detects if key/value are already encoded.
        Params:
            - key (str): key whose value(s) you want to delete.
            - val (str): Optional. Current value if only one value is to be
                deleted instead of all.
            - spaceIsPlus (bool): Optional. True if space should be encoded
                as + instead of %20.
        """
        keyEncoded = urlende.isEncoded(key, plus=spaceIsPlus, safe="")
        key = key if keyEncoded else urlende.encode_query(key, spaceIsPlus)
        if self._attrs["query"] != "" and key in self._attrs["query"]:
            if val is None:
                del self._attrs["query"][key.lower()]
            else:
                valEncoded = urlende.isEncoded(val)
                val = val if valEncoded else urlende.encode_query(
                    val, spaceIsPlus)
                arr = self._attrs["query"][key.lower()]
                if val in arr:
                    self._attrs["query"][key.lower()] = [
                        x for x in arr if x != val]
                else:
                    raise ValueError("This value for this key does not exist.")
                if len(self._attrs["query"][key.lower()]) == 0:
                    del self._attrs["query"][key.lower()]
            if len(self._attrs["query"]) == 0:
                self._attrs["query"] = ""
        else:
            raise KeyError("This key does not exist.")

    @property
    def queryString(self):
        """Get assembled querystring for the URI."""
        return "?" + urlsec._assembleQuery(
            self._attrs["query"], self.queryDelim)

    @property
    def fragment(self):
        """Get or set the fragment of the URI.
        Returns a decoded fragment on get.
        On set, detects if fragment is already percent encoded.
        """
        return (
            None
            if self._attrs["fragment"] == ""
            else urlende.decode(self._attrs["fragment"])
        )

    @fragment.setter
    def fragment(self, val):
        fragEncoded = urlende.isEncoded(val, safe="")
        self._attrs["fragment"] = val if fragEncoded else urlende.encode(
            val, safe="")
