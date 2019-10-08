'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

    ListBasedFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ListBasedFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with ListBasedFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''
import uuid
from list_based_flavorpack.processing_classes.vanilla_processing.rules import NoOddRequests


class VanillaProcessingClass:
    '''
    An example of a processing  class for a list based pool/region.
    Returns UUIDs stored in memory.
    '''
    def __init__(self):
        '''
        Sets processing rules.
        '''
        self.pre_processing_rules = [NoOddRequests,]
        self.post_processing_rules = []
    
    def get_pre_processing_rules(self):
        '''
        Returns processing rules to be executed prior to the generator running.
        '''
        return self.pre_processing_rules
    
    def get_post_processing_rules(self):
        '''
        Returns processing rules to be executed after the generator has run.
        '''
        return self.post_processing_rules
    
    def get_items(self, region, size):
        first = region.last_number_line
        max_line = first + size
        region.last_number_line =  max_line
        region.save()
        return [str(uuid.uuid1()) for i in range(first, max_line)]
