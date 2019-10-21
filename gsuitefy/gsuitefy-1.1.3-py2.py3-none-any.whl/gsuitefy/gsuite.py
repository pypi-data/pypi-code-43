import logging

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

log = logging.getLogger(__name__)

DEFAULT_SCOPES = ['https://www.googleapis.com/auth/admin.directory.group'
        , 'https://www.googleapis.com/auth/admin.directory.group.member']

def _create_directory_service(user_email='', service_account_email='', service_account='', scopes=[]):
    """Build and returns an Admin SDK Directory service object authorized with the service accounts
    that act on behalf of the given user.

    Args:
      user_email: The email of the user. Needs permissions to access the Admin APIs.

    Returns:
      Admin SDK directory service object.

    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account, scopes=scopes)

    credentials = credentials.create_delegated(user_email)

    return build(serviceName='admin', version='directory_v1', credentials=credentials)


class GSuiteAdmin:
    """This class defines all operations.

    Attributes:
        group_management_email: User with group management privileges
        service_account_email: The service account e-mail
        service_account: The service account path (JSON file)
        scopes: A list of scopes as string

    See:
        https://developers.google.com/resources/api-libraries/documentation/admin/directory_v1/python/latest/index.html

    """
    def __init__(self, group_management_email='', service_account_email='', service_account='', scopes=DEFAULT_SCOPES):
        self.client = _create_directory_service(user_email=group_management_email,
                                                service_account_email=service_account_email,
                                                service_account=service_account,
                                                scopes=scopes)
        self.members = self.client.members()
        self.groups = self.client.groups()
        self.users = self.client.users()

    def list_members(self, groupKey):
        """Lists all members of a given group.

        Args:
            groupKey: The group key to list all members. The value can be the group's email address, group alias, or the unique group ID.

        Returns:
            The list of membes in the group key. Members fields: id, email, type and role.

        """
        log.info('Fetching members from {}'.format(groupKey))
        result = []
        request = self.members.list(groupKey=groupKey, fields='members(id,email,type,role)')

        while request is not None:
            response = request.execute()
            result.extend(response.get('members', []))
            request = self.members.list_next(previous_request=request, previous_response=response)

        log.info('Got {} member(s)'.format(len(result)))
        return result

    def list_groups(self, query, domain):
        """Lists all group from a given domain and query.

        Args:
            query: The query to filter groups.
            domain: The GSuite domain.

        Returns:
            The list of groups in the domain.

        """
        request = self.groups.list(query=query, domain=domain)

        result = []
        while request is not None:
            response = request.execute()
            result.extend(response.get('groups', []))
            request = self.groups.list_next(previous_request=request, previous_response=response)

        return result

    def add_member_to_group(self, member, groupKey):
        """Add a member to a group.
        You can inform a member just pasing the e-mail as string ("role = MEMBER" by default) or
        an object with all the properties. Example:

            {
                'kind': "admin#directory#member",
                'role': "MANAGER / MEMBER / OWNER",
                'type': "CUSTOMER / EXTERNAL / GROUP / USER",
                'email': "foo@bar.com"
            }

        Args:
            member: Member to add in the group.
            groupKey: The group key to add the member. The value can be the group's email address, group alias, or the unique group ID.

        """
        log.info('Adding member {} to group {}'.format(member, groupKey))
        if isinstance(member, dict):
            body = {
                'kind': "admin#directory#member",
                'role': member['role'],
                'type': member['type'],
                'email': member['email']
            }
        else:
            body = {
                'kind': "admin#directory#member",
                'role': 'MEMBER',
                'email': member
            }
        req = self.members.insert(body=body, groupKey=groupKey)
        return req.execute()

    def remove_member_from_group(self, memberKey, groupKey):
        """Removes a member from a group.

        Args:
            memberKey: Member to be removed. A group member can be a user or another group. The value can be the member's (group or user) primary email address, alias, or unique ID.
            groupKey: The group key. The value can be the group's email address, group alias, or the unique group ID.

        """
        log.info('Removing member {} from group {}'.format(memberKey, groupKey))
        req = self.members.delete(memberKey=memberKey, groupKey=groupKey)
        return req.execute()