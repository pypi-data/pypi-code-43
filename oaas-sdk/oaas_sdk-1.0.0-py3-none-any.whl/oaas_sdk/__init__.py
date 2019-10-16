"""
This is a Python SDK for interfacing with OaaS. It allows one to use OaaS without interacting on the webservice layer.

A Quickstart follows, but additional documentation on expected variable and return types, etc., can be found in `oaas_sdk.sdk`.

A guide to configuration is at `oaas_sdk.util`.

.. include:: ./quickstart.md
"""

from oaas_sdk.sdk import LabelingTask

LabelingTask = LabelingTask
get_companies = sdk.get_companies
get_labeling_solutions = sdk.get_labeling_solutions
