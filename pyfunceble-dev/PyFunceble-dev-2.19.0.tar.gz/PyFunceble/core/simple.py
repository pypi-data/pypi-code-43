# pylint:disable=line-too-long
"""
The tool to check the availability or syntax of domains, IPv4, IPv6 or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provide the logic for a simple test from the CLI.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/special-thanks.html

Contributors:
    https://pyfunceble.github.io/contributors.html

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://pyfunceble.github.io/

License:
::


    MIT License

    Copyright (c) 2017, 2018, 2019 Nissar Chababy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
# pylint:enable=line-too-long

from domain2idna import get as domain2idna

import PyFunceble
from PyFunceble.file_core import FileCore
from PyFunceble.mysql import MySQL
from PyFunceble.status import Status, SyntaxStatus, URLStatus
from PyFunceble.whois_db import WhoisDB

from .cli import CLICore


class SimpleCore(CLICore):
    """
    Brain of PyFunceble for simple test.

    :param str subject: The subject we are testing.
    """

    def __init__(self, subject):
        self.preset = PyFunceble.Preset()

        if PyFunceble.CONFIGURATION.idna_conversion:
            self.subject = domain2idna(subject)
        else:
            self.subject = subject

        self.mysql_db = MySQL()
        self.whois_db = WhoisDB(mysql_db=self.mysql_db)

    @classmethod
    def test(cls, subject, subject_type, whois_db=None):
        """
        Process a test of the given subject and return the result.
        """

        if PyFunceble.CONFIGURATION.syntax:
            return SyntaxStatus(subject, subject_type=subject_type).get()

        if subject_type in ["url"]:
            return URLStatus(subject, subject_type=subject_type).get()

        return Status(subject, subject_type=subject_type, whois_db=whois_db).get()

    @classmethod
    def save_into_database(cls, output, filename, mysql_db):
        """
        Saves the current status inside the database.
        """

        if PyFunceble.CONFIGURATION.db_type in ["mariadb", "mysql"]:
            table_name = mysql_db.tables["tested"]

            if not filename:
                filename = "simple"

            to_insert = (
                "INSERT INTO {0} "
                "(tested, file_path, _status, status, _status_source, status_source, "
                "domain_syntax_validation, expiration_date, http_status_code, "
                "ipv4_range_syntax_validation, ipv4_syntax_validation, "
                "ipv6_range_syntax_validation, ipv6_syntax_validation, "
                "subdomain_syntax_validation, url_syntax_validation, whois_server, digest) "
                "VALUES (%(tested)s, %(file_path)s, %(_status)s, %(status)s, %(_status_source)s, "
                "%(status_source)s, %(domain_syntax_validation)s, "
                "%(expiration_date)s, %(http_status_code)s, "
                "%(ipv4_range_syntax_validation)s, %(ipv4_syntax_validation)s, "
                "%(ipv6_range_syntax_validation)s, %(ipv6_syntax_validation)s, "
                "%(subdomain_syntax_validation)s, "
                "%(url_syntax_validation)s, %(whois_server)s, %(digest)s)"
            ).format(table_name)

            to_update = (
                "UPDATE {0} SET _status = %(_status)s, status = %(status)s, "
                "_status_source = %(_status_source)s, status_source = %(status_source)s, "
                "domain_syntax_validation = %(domain_syntax_validation)s, "
                "expiration_date = %(expiration_date)s, http_status_code = %(http_status_code)s, "
                "ipv4_range_syntax_validation = %(ipv4_range_syntax_validation)s, "
                "ipv4_syntax_validation = %(ipv4_syntax_validation)s, "
                "ipv6_range_syntax_validation = %(ipv6_range_syntax_validation)s, "
                "ipv6_syntax_validation = %(ipv6_syntax_validation)s, "
                "subdomain_syntax_validation = %(subdomain_syntax_validation)s, "
                "url_syntax_validation = %(url_syntax_validation)s, "
                "whois_server = %(whois_server)s "
                "WHERE digest = %(digest)s"
            ).format(table_name)

            with mysql_db.get_connection() as cursor:
                to_set = Merge({"file_path": filename}).into(output)

                to_set["digest"] = sha256(
                    bytes(to_set["file_path"] + to_set["tested"], "utf-8")
                ).hexdigest()

                if (
                    isinstance(to_set["http_status_code"], str)
                    and not to_set["http_status_code"].isdigit()
                ):
                    to_set["http_status_code"] = None

                try:
                    cursor.execute(to_insert, to_set)
                except mysql_db.errors:
                    cursor.execute(to_update, to_set)

                PyFunceble.LOGGER.debug(
                    f"Saved into the {repr(table_name)} table:\n{to_set}"
                )

    def domain(self):
        """
        Handle the simple domain testing.
        """

        # We run the preset specific to this method.
        self.preset.simple_domain()
        # We print the header if it was not done yet.
        PyFunceble.CLICore.print_header()

        if self.subject:
            data = self.test(self.subject, "domain", self.whois_db)

            if PyFunceble.CONFIGURATION.simple:
                # The simple mode is activated.

                # We print the domain and the status.
                print(
                    "{0} {1}".format(
                        self.get_simple_coloration(data["status"]) + data["tested"],
                        data["status"],
                    )
                )

            self.save_into_database(data, None, self.mysql_db)
        else:
            PyFunceble.CLICore.print_nothing_to_test()

    def url(self):
        """
        Handle the simple URL testing.
        """

        # We run the preset specific to this method.
        self.preset.simple_url()
        # We print the header if it was not done yet.
        PyFunceble.CLICore.print_header()

        if self.subject:
            data = self.test(self.subject, "url", self.whois_db)

            if PyFunceble.CONFIGURATION.simple:
                # The simple mode is activated.

                # We print the domain and the status.
                print(
                    "{0} {1}".format(
                        self.get_simple_coloration(data["status"]) + data["tested"],
                        data["status"],
                    )
                )

            self.save_into_database(data, None, self.mysql_db)
        else:
            PyFunceble.CLICore.print_nothing_to_test()
