'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

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
from serialbox.rules.common import PreprocessingRule
from serialbox.rules.errors import RuleError
from quartet_capture.tasks import create_and_queue_task
from quartet_capture.models import TaskParameter


class ValidDirectoryError(RuleError):

    def __init__(self, detail=None, directory_path=""):
        self.default_detail = ('An error occurred when attempting to find/create '
                               'the directory to store numbers: %s' % directory_path)
        RuleError.__init__(self, detail=detail)


class ValidNumberDirectory(PreprocessingRule):
    '''
    Checks if the number directory exists and attempts to create it if applicable.
    '''
    def execute(self, request, pool, region, size):
        # check directory_path
        try:
            if not os.path.exists(region.directory_path):
                os.makedirs(region.directory_path)
            if not os.path.exists(region.file_path):
                with open(region.file_path, 'a'):
                    os.utime(region.file_path, None)
        except:
            raise ValidDirectoryError(directory_path=region.file_path)


class SufficientNumbersStorage(PreprocessingRule):
    '''
    This rule will check whether there is a sufficient amount of numbers for the size given,
    and if not, will make a request to the third party system to receive enough numbers.
    If an insufficient number of numbers or no number is returned, it will throw an error.
    '''

    def fetch_more_numbers(self, request, pool, region, size):
        '''
        Gets more numbers from the third-party system and writes them to the
        local file store.
        '''
        rule_name = region.rule.name
        template = region.template
        task_param = TaskParameter(name="List-based Region", value=region.machine_name)
        processing_params_dict = {item.key:item.value for item in region.processing_parameters.all()}

        processing_params_dict["authentication_info"] = region.authentication_info
        
        if region.number_replenishment_size > size:
            processing_params_dict["allocate"] = {"size": region.number_replenishment_size,
                                                  "random_event_id": str(uuid.uuid1())}
        else:
            processing_params_dict["allocate"] = {"size": size, "random_event_id": str(uuid.uuid1())}

        # template rendered
        rendered = template.render(processing_params_dict)
        task = create_and_queue_task(rendered, rule_name, task_type = "Input", run_immediately=True, task_parameters=[task_param])
        task.refresh_from_db()  # ensures we get the processed result for the task.a
        region.refresh_from_db()  # ensures we have the most udpated version (in case of parallel calls)
        if task.status != "FINISHED":
            raise RuleError(detail="An error occurred while attempting to request new numbers from third-party system. Please check the log output from task %s" % task.name)
    
    def execute(self, request, pool, region, size):
        try:
            file_size = sum((1 for i in open(region.file_path)))
        except OSError as e:
            raise RuleError(detail="An error occurred while opening attempting to "
                            "read the file to store numbers: %s" % region.file_path)
        if region.last_number_line + size >= file_size:
            currently_available = (file_size + 1) - region.last_number_line  # don't overfetch if not needed.
            self.fetch_more_numbers(request, pool, region, size - currently_available)
        else:
            # numbers are sufficient. Nothing to do.
            pass
