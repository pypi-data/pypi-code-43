"""
Shared, static objects/exceptions/etc.
"""
from requests import HTTPError


class UnknownLabelingTask(Exception):
    """
    Labeling task with specified ID not found.
    """
    pass


class PurgedLabelingTask(Exception):
    """
    Results of labeling task with specified ID are no longer available. You'll need to resubmit this task.
    """


class FailedLabelingTask(Exception):
    """
    Labeling task failed to process. See webservice logs for more information.
    """


class ResultNotReady(Exception):
    """
    LabelingTask is still processing, result is not ready yet.
    """


class ConfigurationException(Exception):
    """
    Invalid or missing configuration; cannot use SDK without a valid configuration present.
    """


class InvalidInputException(Exception):
    """
    Invalid input; failed pre-validation within the SDK before submitting to OaaS.
    """


class WebServiceException(Exception):
    def __init__(self, *args, **kwargs):
        # add title and description as returned by the webservice
        self.message = kwargs.pop('message', "Unknown message")
        self.title = kwargs.pop('title', "Unknown title")
        self.description = kwargs.pop('description', "Unknown Description")
        super(WebServiceException, self).__init__(*args)

    def __str__(self) -> str:
        return "{}: {}\n({})".format(self.title, self.description, self.message)
