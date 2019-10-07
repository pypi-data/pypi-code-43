"""Hockey crashes API wrappers."""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import Any, Iterator, List, Optional
import urllib.parse

import deserialize

import libhockey.constants
from libhockey.derived_client import HockeyDerivedClient


@deserialize.key("identifier", "id")
@deserialize.key("crash_method", "method")
@deserialize.key("crash_file", "file")
@deserialize.key("crash_class", "class")
@deserialize.key("crash_line", "line")
class HockeyCrashGroup:
    """Represents a Hockey crash group."""

    identifier: int
    app_id: int
    created_at: str
    updated_at: str
    status: int
    reason: Optional[str]
    last_crash_at: str
    exception_type: Optional[str]
    fixed: bool
    app_version_id: int
    bundle_version: str
    bundle_short_version: str
    number_of_crashes: int
    grouping_hash: str
    grouping_type: int
    pattern: Optional[str]
    crash_method: Optional[str]
    crash_file: Optional[str]
    crash_class: Optional[str]
    crash_line: Optional[str]

    def __getattr__(self, name: str) -> Any:
        """Override to keep mypy happy.

        :param name: The name of the attribute

        :raises AttributeError: Always since this shouldn't be called
        """
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def url(self) -> str:
        """Return the access URL for the crash.

        :returns: The access URL
        """
        return f"https://rink.hockeyapp.net/manage/apps/{self.app_id}/app_versions/" + \
            f"{self.app_version_id}/crash_reasons/{self.identifier}"

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return str(
            {
                "Exception Type": self.exception_type,
                "Reason": self.reason,
                "Method": self.crash_method,
                "File": self.crash_file,
                "Class": self.crash_class,
                "Count": self.number_of_crashes,
            }
        )

    def __hash__(self) -> int:
        """Calculate the hash of the object

        :returns: The hash value of the object

        :raises Exception: If the language is not English
        """
        properties = [
            self.exception_type,
            self.reason,
            self.crash_method,
            self.crash_file,
            self.crash_class,
        ]

        return hash("-".join(map(str, properties)))

    def __eq__(self, other: object) -> bool:
        """Determine if the supplied object is equal to self

        :param other: The object to compare to self

        :returns: True if they are equal, False otherwise.
        """

        if not isinstance(other, HockeyCrashGroup):
            return False

        return self.__hash__() == other.__hash__()


class HockeyCrashGroupsResponse:
    """Represents a Hockey crash groups response."""

    crash_reasons: List[HockeyCrashGroup]
    status: str
    current_page: int
    per_page: int
    total_entries: int
    total_pages: int


@deserialize.key("identifier", "id")
class HockeyCrashInstance:
    """Represents a Hockey crash instance."""

    identifier: int
    app_id: int
    crash_reason_id: int
    created_at: str
    updated_at: str
    oem: Optional[str]
    model: Optional[str]
    os_version: Optional[str]
    jail_break: Optional[bool]
    contact_string: Optional[str]
    user_string: Optional[str]
    has_log: bool
    has_description: bool
    app_version_id: int
    bundle_version: str
    bundle_short_version: str


class HockeyCrashesResponse:
    """Represents a Hockey crashes response."""

    crash_reason: HockeyCrashGroup
    crashes: List[HockeyCrashInstance]
    status: str
    current_page: int
    per_page: int
    total_entries: int
    total_pages: int


@deserialize.key("identifier", "id")
class HockeyCrashAnnotation:
    """Represents a Hockey crash annotation."""

    identifier: int
    crash_reason_id: int
    text: str
    created_at: str
    updated_at: str

class HockeyCrashAnnotationResponse:
    """Represents Hockey annotation response."""

    status: str
    crash_annotations: Optional[List[HockeyCrashAnnotation]]


class HockeyCrashesClient(HockeyDerivedClient):
    """Wrapper around the Hockey crashes APIs.

    :param token: The authentication token
    :param parent_logger: The parent logger that we will use for our own logging
    """

    def __init__(self, token: str, parent_logger: logging.Logger) -> None:
        super().__init__("crashes", token, parent_logger)

    def group(
        self, app_id: str, crash_group_id: int
    ) -> HockeyCrashGroup:
        """Get a crash group.

        :param app_id: The ID of the app
        :param crash_group_id: The ID of the group to get

        :returns: The crash group
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/crash_reasons/{crash_group_id}"
        response = self.get(request_url, retry_count=3)

        crashes_response = deserialize.deserialize(HockeyCrashesResponse, response.json())

        return crashes_response.crash_reason

    def generate_groups_for_version(
        self,
        app_id: str,
        app_version_id: int,
        *,
        page: int = 1,
        symbolicated_only: Optional[bool] = None,
        sort_field: Optional[str] = None
    ) -> Iterator[HockeyCrashGroup]:
        """Get all crash groups for a given hockeyApp version.

        These crash groups are not guaranteed to be ordered in any particular way

        :param app_id: The ID of the app
        :param app_version_id: The version ID for the app
        :param int page: The page of crash groups to get
        :param Optional[bool] symbolicated_only: Set to True to only get symbolicated crashes
        :param Optional[str] sort_field: The field to sort by

        :returns: The list of crash groups that were found
        :rtype: HockeyCrashGroup
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/app_versions/{app_version_id}/crash_reasons?"

        parameters = {
            "per_page": 100,
            "order": "desc",
            "page": page,
        }

        if symbolicated_only:
            parameters["symbolicated"] = 1 if symbolicated_only else 0

        if sort_field:
            parameters["sort"] = sort_field

        request_url += urllib.parse.urlencode(parameters)

        self.log.info(f"Fetching page {page} of crash groups")

        response = self.get(request_url, retry_count=3)

        crash_reasons_response = deserialize.deserialize(HockeyCrashGroupsResponse, response.json())

        self.log.info(f"Fetched page {page}/{crash_reasons_response.total_pages} of crash groups")

        reasons: List[HockeyCrashGroup] = crash_reasons_response.crash_reasons

        for reason in reasons:
            yield reason

        if crash_reasons_response.total_pages > page:
            yield from self.generate_groups_for_version(
                app_id,
                app_version_id,
                page=page + 1,
                symbolicated_only=symbolicated_only,
                sort_field=sort_field
            )

    def groups_for_version(
        self,
        app_id: str,
        app_version_id: int,
        max_count: Optional[int] = None,
        symbolicated_only: Optional[bool] = None,
        sort_field: Optional[str] = None
    ) -> List[HockeyCrashGroup]:
        """Get all crash groups for a given hockeyApp version.

        :param app_id: The ID of the app
        :param app_version_id: The version ID for the app
        :param max_count: The maximum count of crash groups to fetch before stopping
        :param Optional[bool] symbolicated_only: Set to True to only get symbolicated crashes
        :param Optional[str] sort_field: The field to sort by

        :returns: The list of crash groups that were found
        """

        groups = []

        for group in self.generate_groups_for_version(
            app_id,
            app_version_id,
            symbolicated_only=symbolicated_only,
            sort_field=sort_field
        ):
            groups.append(group)

            if max_count is not None and len(groups) >= max_count:
                break

        return groups

    def generate_in_group(
        self, app_id: str, crash_group_id: int, *, app_version_id: Optional[int], page: int = 1
    ) -> Iterator[HockeyCrashInstance]:
        """Get all crash instances in a group.

        :param app_id: The ID of the app
        :param crash_group_id: The ID of the group to get the crashes
        :param Optional[int] app_version_id: The version ID for the app
        :param int page: The page of crashes to start at

        :returns: The crashes that were found in the group
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/"

        if app_version_id is not None:
            request_url += f"app_versions/{app_version_id}/"

        request_url += f"crash_reasons/{crash_group_id}?per_page=100&order=desc&page={page}"
        response = self.get(request_url, retry_count=3)

        crashes_response = deserialize.deserialize(HockeyCrashesResponse, response.json())

        crashes: List[HockeyCrashInstance] = crashes_response.crashes

        for crash in crashes:
            yield crash

        if crashes_response.total_pages > page:
            yield from self.generate_in_group(app_id, crash_group_id, app_version_id=app_version_id, page=page + 1)

    def in_group(
        self, app_id: str, app_version_id: int, crash_group_id: int
    ) -> List[HockeyCrashInstance]:
        """Get all crash instances in a group.

        :param app_id: The ID of the app
        :param app_version_id: The version ID for the app
        :param crash_group_id: The ID of the group to get the crashes

        :returns: The list of crash instances that were found
        """

        return list(self.generate_in_group(app_id, crash_group_id, app_version_id=app_version_id))

    def get_log(self, app_id: str, crash_id: int) -> str:
        """Get the log from a crash

        :param app_id: The ID of the app
        :param crash_id: The ID of the crash

        :returns: The log from the crash
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/crashes/{crash_id}?format=log"
        response = self.get(request_url, retry_count=3)
        return response.text

    def get_description(self, app_id: str, crash_id: int) -> str:
        """Get the description from a crash

        :param app_id: The ID of the app
        :param crash_id: The ID of the crash

        :returns: The description from the crash
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/crashes/{crash_id}?format=text"
        response = self.get(request_url, retry_count=3)
        return response.text

    def get_annotation(self, app_id: str, group_id: int) -> Optional[HockeyCrashAnnotation]:
        """Get the annotation from a crash

        :param app_id: The ID of the app
        :param group_id: The ID of the crash group

        :raises Exception: If we get a failure status back

        :returns: The annotation on the crash if found, None otherwise
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/crash_reasons/{group_id}/crash_annotations"
        response = self.get(request_url, retry_count=3)
        parsed_response = deserialize.deserialize(HockeyCrashAnnotationResponse, response.json())

        if parsed_response.status not in ["success", "empty"]:
            raise Exception(f"Failed to get annotations: {response.text}")

        if parsed_response.crash_annotations is None:
            return None

        if len(parsed_response.crash_annotations) == 0:
            return None

        return parsed_response.crash_annotations[0]

    def set_annotation(self, app_id: str, group_id: int, text: str) -> None:
        """Set the annotation on a crash

        :param app_id: The ID of the app
        :param group_id: The ID of the crash group
        :param text: The text to set
        """

        request_url = f"{libhockey.constants.API_BASE_URL}/{app_id}/crash_reasons/{group_id}/crash_annotations?"
        request_url += urllib.parse.urlencode({"text": text})
        self.post(request_url, data={})
