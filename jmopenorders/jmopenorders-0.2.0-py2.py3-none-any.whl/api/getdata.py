# -*- coding: utf-8 -*-
"""Get the Data from csv-file to generate to output."""
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


class GetData:
    """
    Get the data from csv-file.

    Auftrag Nummer,
    Hauptbereich ,
    Auftragsdatum,
    Tage offen ,
    Deb.-Nr.,
    Deb.-Name,
    Verkäufer Serviceberater,
    Arbeitswert,
    Teile ,
    Fremdleistung,
    Andere,
    Gesamt,
    Auftragswert bereit geliefert
    """

    def __init__(self, filename):
        """Init the GetData Class."""
        self.file_name = filename

    def get(self) -> list:
        """Get the data from the csv-file."""
        # global orders_file
        try:
            with open(self.file_name, "r") as orders_file:
                orders = csv.reader(orders_file, delimiter=";", quotechar='"')
                data = list(orders)

                return data

        except IOError:
            logger.debug(
                "The File with the data '" +
                self.file_name + "' does not exists",
            )
