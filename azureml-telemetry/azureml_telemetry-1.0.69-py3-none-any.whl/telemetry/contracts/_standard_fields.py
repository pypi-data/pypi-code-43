# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines Part B of the logging schema, optional keys that have a common meaning across telemetry data."""
from typing import Any, List
from azureml.telemetry._error_response._error_response_constants import ErrorCodes


class StandardFieldKeys:
    """Keys for standard fields."""

    ALGORITHM_TYPE_KEY = 'AlgorithmType'
    CLIENT_OS_KEY = 'ClientOS'
    COMPUTE_TYPE_KEY = 'ComputeType'
    FAILURE_REASON_KEY = 'FailureReason'
    ITERATION_KEY = 'Iteration'
    TASK_RESULT_KEY = 'TaskResult'
    PARENT_RUN_ID_KEY = 'ParentRunId'
    RUN_ID_KEY = 'RunId'
    WORKSPACE_REGION_KEY = 'WorkspaceRegion'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for standard fields."""
        return [
            StandardFieldKeys.ALGORITHM_TYPE_KEY,
            StandardFieldKeys.CLIENT_OS_KEY,
            StandardFieldKeys.COMPUTE_TYPE_KEY,
            StandardFieldKeys.FAILURE_REASON_KEY,
            StandardFieldKeys.ITERATION_KEY,
            StandardFieldKeys.TASK_RESULT_KEY,
            StandardFieldKeys.PARENT_RUN_ID_KEY,
            StandardFieldKeys.RUN_ID_KEY,
            StandardFieldKeys.WORKSPACE_REGION_KEY
        ]


class StandardFields(dict):
    """Defines Part B of the logging schema, optional keys that have a common meaning across telemetry data."""

    def __init__(self, algorithm_type=None, client_os=None, compute_type=None,
                 iteration=None, run_id=None, parent_run_id=None,
                 task_result=None, failure_reason=None, workspace_region=None,
                 *args: Any, **kwargs: Any):
        """Initialize a new instance of the StandardFields."""
        super(StandardFields, self).__init__(*args, **kwargs)
        self.algorithm_type = algorithm_type
        self.client_os = client_os
        self.compute_type = compute_type
        self.failure_reason = failure_reason
        self.iteration = iteration
        self.run_id = run_id
        self.parent_run_id = parent_run_id
        self.task_result = task_result
        self.workspace_region = workspace_region

    @property
    def algorithm_type(self):
        """Component name."""
        return self.get(StandardFieldKeys.ALGORITHM_TYPE_KEY, None)

    @algorithm_type.setter
    def algorithm_type(self, value):
        """
        Set component name.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.ALGORITHM_TYPE_KEY] = value

    @property
    def client_os(self):
        """Get the client operating system."""
        return self.get(StandardFieldKeys.CLIENT_OS_KEY, None)

    @client_os.setter
    def client_os(self, value):
        """
        Set the client operating system.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.CLIENT_OS_KEY] = value

    @property
    def compute_type(self):
        """Compute Type."""
        return self.get(StandardFieldKeys.COMPUTE_TYPE_KEY, None)

    @compute_type.setter
    def compute_type(self, value):
        """
        Set compute type.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.COMPUTE_TYPE_KEY] = value

    @property
    def failure_reason(self):
        """Get failure reason."""
        return self.get(StandardFieldKeys.FAILURE_REASON_KEY, None)

    @failure_reason.setter
    def failure_reason(self, value):
        """Set failure reason."""
        validate = (value is None or value == ErrorCodes.USER_ERROR or value == ErrorCodes.SYSTEM_ERROR)
        assert validate, "Failure reason has to be either User or System"
        self[StandardFieldKeys.FAILURE_REASON_KEY] = value

    @property
    def iteration(self):
        """ID for iteration."""
        return self.get(StandardFieldKeys.ITERATION_KEY, None)

    @iteration.setter
    def iteration(self, value):
        """
        Set iteration ID.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.ITERATION_KEY] = value

    @property
    def task_result(self):
        """Job status."""
        return self.get(StandardFieldKeys.TASK_RESULT_KEY, None)

    @task_result.setter
    def task_result(self, value):
        """
        Set job status.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.TASK_RESULT_KEY] = value

    @property
    def parent_run_id(self):
        """Parent run ID."""
        return self.get(StandardFieldKeys.PARENT_RUN_ID_KEY, None)

    @parent_run_id.setter
    def parent_run_id(self, value):
        """
        Set parent run ID.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.PARENT_RUN_ID_KEY] = value

    @property
    def run_id(self):
        """Run ID."""
        return self.get(StandardFieldKeys.RUN_ID_KEY, None)

    @run_id.setter
    def run_id(self, value):
        """
        Set run ID.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.RUN_ID_KEY] = value

    @property
    def workspace_region(self):
        """Workspace region."""
        return self.get(StandardFieldKeys.WORKSPACE_REGION_KEY, None)

    @workspace_region.setter
    def workspace_region(self, value):
        """
        Workspace region to set to.

        :param value: Value to set to.
        """
        if value is not None:
            self[StandardFieldKeys.WORKSPACE_REGION_KEY] = value
