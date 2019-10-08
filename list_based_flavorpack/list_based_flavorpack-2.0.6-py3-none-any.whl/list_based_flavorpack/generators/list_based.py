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
    along with ListBasedFlavorpack. If not, see <http://www.gnu.org/licenses/>.
'''
from serialbox.generators.common import Generator
from serialbox.rules.common import PreprocessingRule
from list_based_flavorpack import list_based_flavorpack_settings as settings

def import_processing_class(region):
    '''
    Returns the processing class dynamically.
    A processing class is entered when creating a list-based region
    and is used for all rules/generator logic.
    '''
    package_path = region.processing_class_path.split(".")
    class_path = package_path[:-1]
    class_name = package_path[-1]
    processing_module = __import__(".".join(class_path), fromlist=[class_name])
    return getattr(processing_module, class_name)


class ListBasedGenerator(Generator):
    '''
    Generates a list of numbers (or anything else located in source)
    '''
    def generate(self, request, response, region, size):
        '''
        Executes an instance of the processing class and returns a list.
        '''
        processing_class = import_processing_class(region)
        return self.set_number_list(response, processing_class().get_items(region, size))

    def get_settings_module(self):
        return settings



class ListBasedPreprocessRule(PreprocessingRule):
    '''
    Used as a proxy for all rules that are added to the Processing Class.
    This allows for dynamic injection of rules without having to hack
    settings too much (except for adding this rule)
    '''
    def execute(self, request, pool, region, size):
        '''
        This will execute all the rules that have been added to
        the processing class (which is entered dynamically when creating
        a list-based region.)
        '''
        processing_instance = import_processing_class(region)()
        for rule in processing_instance.get_pre_processing_rules():
            rule().execute(request, pool, region, size)


class ListBasedPostprocessRule(PreprocessingRule):
    '''
    Used as a proxy for all rules that are added to the Processing Class.
    This allows for dynamic injection of rules without having to hack
    settings too much (except for adding this rule)
    '''
    def execute(self, request, pool, region, size):
        '''
        This will execute all the rules that have been added to
        the processing class (which is entered dynamically when creating
        a list-based region.)
        '''
        processing_instance = import_processing_class(region)()
        for rule in processing_instance.get_post_processing_rules():
            rule().execute(request, pool, region, size)
