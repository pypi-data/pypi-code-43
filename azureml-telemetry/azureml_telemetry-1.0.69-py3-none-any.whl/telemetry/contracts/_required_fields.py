# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines Part A of the logging schema, keys that have a common meaning across telemetry data."""
from typing import Any, List


class RequiredFieldKeys:
    """Keys for required fields."""

    SESSION_ID_KEY = 'SessionId'
    CLIENT_TYPE_KEY = 'ClientType'
    CLIENT_VERSION_KEY = 'ClientVersion'
    COMPONENT_NAME_KEY = 'ComponentName'
    CORRELATION_ID_KEY = 'CorrelationId'
    EVENT_ID_KEY = 'EventId'
    EVENT_TIME_KEY = 'EventTime'
    SUBSCRIPTION_ID_KEY = 'SubscriptionId'
    WORKSPACE_ID_KEY = 'WorkspaceId'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for required fields."""
        return [
            RequiredFieldKeys.SESSION_ID_KEY,
            RequiredFieldKeys.CLIENT_TYPE_KEY,
            RequiredFieldKeys.CLIENT_VERSION_KEY,
            RequiredFieldKeys.COMPONENT_NAME_KEY,
            RequiredFieldKeys.CORRELATION_ID_KEY,
            RequiredFieldKeys.EVENT_ID_KEY,
            RequiredFieldKeys.EVENT_TIME_KEY,
            RequiredFieldKeys.SUBSCRIPTION_ID_KEY,
            RequiredFieldKeys.WORKSPACE_ID_KEY
        ]


class RequiredFields(dict):
    """Defines Part A of the logging schema, keys that have a common meaning across telemetry data."""

    def __init__(self, session_id=None, client_type=None, client_version=None, component_name=None,
                 correlation_id=None, subscription_id=None, workspace_id=None,
                 *args: Any, **kwargs: Any) -> None:
        """Initialize a new instance of the RequiredFields."""
        super(RequiredFields, self).__init__(*args, **kwargs)
        self.client_type = client_type
        self.client_version = client_version
        self.component_name = component_name
        self.correlation_id = correlation_id
        self.subscription_id = subscription_id
        self.workspace_id = workspace_id
        self[RequiredFieldKeys.SESSION_ID_KEY] = session_id

    @property
    def session_id(self):
        """Client session ID."""
        return self.get(RequiredFieldKeys.SESSION_ID_KEY, None)

    @session_id.setter
    def session_id(self, value):
        """Set client session ID."""
        if value is not None:
            self[RequiredFieldKeys.SESSION_ID_KEY] = value

    @property
    def client_type(self):
        """Type of client, e.g. SDK."""
        return self.get(RequiredFieldKeys.CLIENT_TYPE_KEY, None)

    @client_type.setter
    def client_type(self, value):
        """Set type of client."""
        if value is not None:
            self[RequiredFieldKeys.CLIENT_TYPE_KEY] = value

    @property
    def client_version(self):
        """Client version."""
        return self.get(RequiredFieldKeys.CLIENT_VERSION_KEY, None)

    @client_version.setter
    def client_version(self, value):
        """Set client version."""
        if value is not None:
            self[RequiredFieldKeys.CLIENT_VERSION_KEY] = value

    @property
    def component_name(self):
        """Client component name."""
        return self.get(RequiredFieldKeys.COMPONENT_NAME_KEY, None)

    @component_name.setter
    def component_name(self, value):
        """Set component name."""
        if value is not None:
            self[RequiredFieldKeys.COMPONENT_NAME_KEY] = value

    @property
    def correlation_id(self):
        """Correlation ID."""
        return self.get(RequiredFieldKeys.CORRELATION_ID_KEY, None)

    @correlation_id.setter
    def correlation_id(self, value):
        """Set correlation ID."""
        if value is not None:
            self[RequiredFieldKeys.CORRELATION_ID_KEY] = value

    @property
    def event_id(self):
        """Event ID."""
        return self.get(RequiredFieldKeys.EVENT_ID_KEY, None)

    @property
    def event_time(self):
        """Event time."""
        return self.get(RequiredFieldKeys.EVENT_TIME_KEY, None)

    @property
    def subscription_id(self):
        """Subscription ID."""
        return self.get(RequiredFieldKeys.SUBSCRIPTION_ID_KEY, None)

    @subscription_id.setter
    def subscription_id(self, value):
        """Set subscription ID."""
        if value is not None:
            self[RequiredFieldKeys.SUBSCRIPTION_ID_KEY] = value

    @property
    def workspace_id(self):
        """Workspace ID."""
        return self.get(RequiredFieldKeys.WORKSPACE_ID_KEY, None)

    @workspace_id.setter
    def workspace_id(self, value):
        """Set workspace ID."""
        if value is not None:
            self[RequiredFieldKeys.WORKSPACE_ID_KEY] = value
