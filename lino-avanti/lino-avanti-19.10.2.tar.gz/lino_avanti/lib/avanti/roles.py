# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""User roles for this plugin."""

from lino.core.roles import UserRole

   
class ClientsNameUser(UserRole):
    """A user who can see the full name of clients but has no other access
    to client functionality.

    """

# class StatisticsUser(UserRole):
#     """A user who can see global lists of all clients, but without seeing
#     their names and other confidential data.

#     """

class ClientsUser(ClientsNameUser):
    """A user who has access to clients functionality.

    """


class ClientsStaff(ClientsUser):
    """A user who can configure clients functionality.

    """

