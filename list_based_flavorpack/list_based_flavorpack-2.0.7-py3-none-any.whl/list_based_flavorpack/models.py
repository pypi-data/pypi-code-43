'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorPack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from serialbox import models as sb_models
from quartet_output.models import EndPoint, AuthenticationInfo
from quartet_capture.models import Rule
from quartet_templates.models import Template


class ListBasedRegion(sb_models.Region):
    '''
    The List-based region defines a region that retrieves numbers from
    a third-party system/application and uses a file containing a list
    for its numbers. It is tied to an Endpoint and AuthenticationInfo
    from the QU4RTET output app.
    '''
    last_number_line = models.IntegerField(
        verbose_name=_('Last Number Line'),
        help_text=_('The line number of the last number issued '
                    'maintains the state of the list-based region.'),
        default=1)
    end_point = models.ForeignKey(
        EndPoint,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("End Point"),
        help_text=_("A protocol-specific endpoint defining where"
                    "any data will come from"),)
    rule = models.ForeignKey(
        Rule,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=("Processing Rule"),
        help_text=_("A rule that may be executed by the region processing class."))
    authentication_info = models.ForeignKey(
        AuthenticationInfo,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Authentication Info"),
        help_text=_("The Authentication Info to use."))
    template = models.ForeignKey(
        Template,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Message Template"),
        help_text=_("The Django/Jinja template to send a formatted request for number ranges")
    )
    processing_class_path = models.CharField(
        max_length=150,
        null=False,
        help_text=_('The full python path to the class that will be processing region allocations'),
        verbose_name=_('Processing Class Path'),
        default='list_based_flavorpack.processing_classes.third_party_processing.processing.ThirdPartyProcessingClass'
    )
    file_id = models.UUIDField(default=uuid.uuid1)
    directory_path = models.CharField(
        max_length=150,
        default="/var/quartet/numbers",
        null=True,
        blank=True,
        help_text=_("The full path to the directory where numbers will be stored. "
                    "Leave blank for default. Default is /var/quartet/numbers"))
    number_replenishment_size = models.IntegerField(
        verbose_name=_("Number Replenishment Size"),
        null=False,
        blank=False,
        help_text=_("The size that the outbound message will request from the third-party system, "
                    "if numbers available are low. E.g.: 500"),
        default=5000
    )

    @property
    def file_path(self):
        '''
        The full path to the file.
        '''
        return os.path.join(self.directory_path, str(self.file_id))


class ProcessingParameters(models.Model):
    '''
    A key-value pair object meant to hold parameters used for processing classes.
    '''
    list_based_region = models.ForeignKey(ListBasedRegion, null=True, on_delete=models.CASCADE,
                                          related_name="processing_parameters",
                                          verbose_name=_("Processing Class Parameter"),
                                          help_text=_("A key-value pair object meant to hold parameters "
                                                      "used for processing classes."))
    key = models.CharField(max_length=200,
                           null=False,
                           help_text=_("The key part of the key-value pair. Example: q"))
    value = models.CharField(max_length=400,
                             null=True,
                             blank=True,
                             help_text=_("The value part of the key-value pair."))

    def __str__(self):
        return "{\"%s\": \"%s\"}" % (self.key, self.value)
