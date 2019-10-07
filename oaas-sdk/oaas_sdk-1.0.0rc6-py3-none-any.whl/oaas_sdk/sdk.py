"""
Primary Interface with webservice. `oaas_sdk.sdk.LabelingTask` as well as the reference methods can be imported directly from the module, as:
`from oaas_sdk import LabelingTask, get_companies, get_labeling_solutions`.
"""

import json
import time
from typing import Union, Optional, Iterable, Set, List

import pandas as pd

from oaas_sdk.objects import ResultNotReady, FailedLabelingTask, PurgedLabelingTask, InvalidInputException
from oaas_sdk.util import UPDATE_FREQUENCY, MAX_DOCUMENTS
from oaas_sdk.ws import client
from oaas_sdk.ws.client import MAX_RETRIES


class LabelingTask:
    """
    Object representation of a labeling task. Can be used to check status and retrieve results. Fields on this object will automatically retrieve/update
    information from webservice.
    """
    labeling_solutions = None

    def __init__(self, task_id: str):
        """Initializes an existing or recently created labeling task."""

        self.task_id = task_id
        """Webservice assigned ID of labeling task"""

        self._last_status_update = 0
        self._status = None
        self._result = None

    @classmethod
    def history(cls, limit: int = None):
        """
        Gets a history of user-submitted labeling tasks. If run as an administrator, will return all labeling tasks; otherwise, will only return labeling tasks
        submitted by the authenticated user.
        Args:
            limit: If specified, return this number of recent labeling tasks. Otherwise, use the web service's default.

        Returns:
            DataFrame summarizing recent labeling tasks.
        """
        return client.get_labeling_tasks(limit)

    @classmethod
    def create(cls, data: pd.DataFrame, labeling_solution_category: str = 'verified',
               labeling_solution_name: str = 'label', *,
               companies: Optional[Iterable[str]] = None, output_format: str = 'arrow', tags: Optional[List[str]] = None):
        """
        Submits a new labeling task to be processed in the webservice. Input data is expected to be in the form of a DataFrame with these columns:

        - `document_id` _(optional)_: If present, will be passed through as a used provided ID. The input data's order is preserved during processing so this is entirely
          optional.
        - `product_description` _(required)_: Primary product description for this datum.
        - `from_email` _(optional)_: A domain or email address which is the source of this product description, if known.

        Args:
            labeling_solution_category: A category of labeling solution to apply to this data. Available categories can be found with `oaas_sdk.get_labeling_solutions`
            labeling_solution_name: A labeling solution name to apply to this data. Available names can be found with `oaas_sdk.get_labeling_solutions`
            data: A pandas DataFrame with the columns specified above.
            companies: If desired, search space can be restricted by specifying a list of companies here. Available companies can be found with `oaas_sdk.get_companies`
            output_format: By default, output will be retrieved through this SDK as a pandas DataFrame. If you wish to have results in another format (such as
                           json or csv) specify so here.
            tags: Optional list of strings which will "tag" this labeling task with user specified information. These tags aren't used during processing, they
                    are just helpful when referencing a previously submitted labeling task. They will show up with `LabelingTask.history` calls.

        Returns:
            A `oaas_sdk.sdk.LabelingTask` object which can be used to check status and retrieve results when finished processing.
        """

        # The service will check for this, but to avoid waiting for everything to upload before failing, check that the number of documents submitted is valid
        if len(data.index) > MAX_DOCUMENTS:
            raise InvalidInputException(
                'Labeling tasks cannot contain more than {} documents. Please split your labeling task into chunks and submit each individually.'.format(
                    MAX_DOCUMENTS))

        task_id = client.create_new_labeling_task(labeling_solution_category, labeling_solution_name, data,
                                                  companies = companies,
                                                  output_format = output_format,
                                                  tags = tags)
        return cls(task_id)

    @property
    def status(self) -> str:
        """
        Current status of labeling task.
        Returns:
            One of: [submitted, processed, failed, skipped, purged]
        """
        # update with webservice if it's been long enough
        if time.time() - self._last_status_update > UPDATE_FREQUENCY:
            self._status = client.get_labeling_task_status(self.task_id)
            self._last_status_update = time.time()

        return self._status

    @property
    def result(self) -> Union[pd.DataFrame, str]:
        """
        Retrieve result, as a DataFrame or string of json/csv depending on selected output_format, from webservice. Caches value so multiple calls
        won't requery the webservice.
        Raises:
            `oaas_sdk.objects.ResultNotReady`
            `oaas_sdk.objects.FailedLabelingTask`
            `oaas_sdk.objects.PurgedLabelingTask`
        """
        # If we've retrieved the result before, don't requery.
        if self._result is not None:
            return self._result

        # If not, check on the status of the job.
        status = self.status

        if status == 'submitted':
            raise ResultNotReady
        elif status == 'failed':
            raise FailedLabelingTask
        elif status == 'purged':
            raise PurgedLabelingTask
        else:
            self._result = client.get_labeling_task_content(self.task_id)
            return self._result

    def join(self, timeout: int = 0) -> Union[pd.DataFrame, str, None]:
        """
        Synonym for `LabelingTask.wait_for_result`, named to match the pattern of other asynchronous processing libraries such as `multiprocessing`.
        """
        return self.wait_for_result(timeout)

    def wait_for_result(self, timeout: int = 0) -> Union[pd.DataFrame, str, None]:
        """
        Blocks while waiting for labeling task to complete, and returns result.
        Args:
            timeout: If labeling task is still processing after this many seconds, raise a `TimeoutError`. 0 means to wait indefinitely.
        Returns:
            Result of labeling task. Typically a DataFrame, but could be a string representing json or csv if that output_format was specified when labeling task was created.

        Raises:
            `TimeoutError`

        """
        number_of_errors = 0
        if timeout:
            end_time = time.time() + timeout
        else:
            end_time = None
        while True:
            if end_time:
                if time.time() > end_time:
                    raise TimeoutError

            try:
                return self.result
            except KeyboardInterrupt:
                raise
            except ResultNotReady:
                pass
            except:
                # we'll retry a few times before actually bailing out. This way intermittent connection issues don't abort the whole loop
                if number_of_errors > MAX_RETRIES:
                    # Actually error.
                    raise
                else:
                    number_of_errors += 1

            # sleep so we don't use an entire core just spinning through this loop
            time.sleep(UPDATE_FREQUENCY)

    def save_logs(self, filename):
        """
        Retrieve the server debug logs for this labeling task, and save them to the specified file. This file should be sent to the OaaS team for any questions
        or issues.
        Args:
            filename: Save logs to this file.
        """
        logs = client.get_logs(self.task_id)
        with open(filename, 'w') as f:
            json.dump(logs, f)


# Other reference methods
def get_companies(labeling_solution_category: str, labeling_solution_name: str) -> Set[str]:
    """
    Get all possible companies supported by the given labeling solution. Members of this set can be used when submitting a labeling job to limit the search
    space. Also, any matches from this labeling solution are guaranteed to be a member of this set, or one of the special match types (other, generic, etc.)
    Args:
         labeling_solution_category: A category of labeling solution to apply to this data. Available categories can be found with
                                     `oaas_sdk.sdk.get_labeling_solutions`
         labeling_solution_name: A labeling solution name to apply to this data. Available names can be found with `oaas_sdk.sdk.get_labeling_solutions`
    Returns:
        List of possible company values for the specified labeling_solution_category and labeling_solution name.
     """
    return client.get_company_set(labeling_solution_category, labeling_solution_name)


def get_labeling_solutions():
    """
    Get all possible labeling solutions supported by your version of OaaS.
    Returns:
        Dictionary of available labeling "solutions". The category/name pairs are the possible arguments to the `LabelingTask.submit` method, as well as the
            `oaas_sdk.sdk.get_companies` method.
    """
    return client.get_labeling_solutions()
