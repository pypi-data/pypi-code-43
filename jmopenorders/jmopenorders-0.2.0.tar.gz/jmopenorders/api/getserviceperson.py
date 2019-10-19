# -*- coding: utf-8 -*-
"""Get the service persion from csv-file."""
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Jürgen Mülbert. All rights reserved.
#
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#
# Lizenziert unter der EUPL, Version 1.2 oder - sobald
#  diese von der Europäischen Kommission genehmigt wurden -
# Folgeversionen der EUPL ("Lizenz");
# Sie dürfen dieses Werk ausschließlich gemäß
# dieser Lizenz nutzen.
# Eine Kopie der Lizenz finden Sie hier:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Sofern nicht durch anwendbare Rechtsvorschriften
# gefordert oder in schriftlicher Form vereinbart, wird
# die unter der Lizenz verbreitete Software "so wie sie
# ist", OHNE JEGLICHE GEWÄHRLEISTUNG ODER BEDINGUNGEN -
# ausdrücklich oder stillschweigend - verbreitet.
# Die sprachspezifischen Genehmigungen und Beschränkungen
# unter der Lizenz sind dem Lizenztext zu entnehmen.
#
import csv

from ..core.logger import logger


class GetServicePerson:
    """Handle the service person."""

    def __init__(self, filename):
        """Init the GetServicePerson Class."""
        self.file_name = filename
        self.berater = []

    def get(self) -> list:
        """
        Read the Service Person from csv-file.

        Then create a array and get this back
        """
        service_person = []
        try:
            with open(self.file_name, "r") as berater_file:
                self.berater = csv.DictReader(
                    berater_file, delimiter=";", quotechar='"',
                )

                for row in self.berater:

                    service_person.append(row["Name"])

                return service_person

        except IOError:
            logger.debug(
                "The File for the service persons %s does not exists",
                self.file_name,
            )
