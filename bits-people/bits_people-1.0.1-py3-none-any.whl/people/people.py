# -*- coding: utf-8 -*-
"""People class file."""

from bits.mysql import MySQL
from bits.people.person import Person


class People(MySQL):
    """People class."""

    def __init__(
        self,
        server,
        port,
        user,
        password,
        db,
        verbose=False,
    ):
        """Initialize a class instance."""
        MySQL.__init__(self, server, port, user, password, db, verbose)

    #
    # Assets
    #
    def delete_asset(self, asset_id):
        """Delete an asset by id."""

    def get_assets(self):
        """Return a list of assets."""

    def get_assets_by_type(self, asset_type='welcome email'):
        """Get all assets of a certain type."""

    #
    # Desks
    #
    def get_desks(self):
        """Return a list of people desk records."""

    #
    # Institutions
    #
    def get_institutions(self):
        """Return a list of institutions."""

    def get_institutions_dict(self):
        """Return a dict of institutions."""

    #
    # People
    #
    def get_emails_dict(self):
        """Return a dict of emails."""

    def get_emplids(self):
        """Return a list of emplid to pid mappings."""

    def get_emplids_dict(self):
        """Return a dict of emplid to pid."""

    def get_people(self):
        """Return a list of people records."""
        return self.get_table('people')

    def get_people_dict(self, key='id'):
        """Return a dict of people records."""
        return self.get_table_dict('people', key)

    def get_people_objects(self):
        """Return a list of people objects."""
        people = []
        for record in self.get_table('people'):
            people.append(Person(record))
        return people

    def get_person_by_username(self, username):
        """Return the person with the given username, if exists."""

    def get_person_types(self):
        """Return a list of person types."""

    def get_person_types_dict(self):
        """Return a dict of person types."""

    #
    # Phones and Telephones?
    #
    def get_phones(self):
        """Return a list of person phones."""

    def get_phones_dict(self):
        """Return a dict of person phones."""

    def get_telephones_dict(self):
        """Return a dict of telephones."""

    #
    # Usernames
    #
    def get_usernames_dict(self):
        """Return a dict of all usernames."""

    #
    # People Users
    #
    def get_users(self):
        """Return a list of users."""

    def get_users_dict(self):
        """Return a dict of users."""

    #
    # Vendor Data
    #
    def add_vendor_value(self, vendor, pid, key, value):
        """Add a key=value pair to a vendor for a person."""

    def delete_vendor_value(self, vendor, pid, key, value):
        """Delete vendor data for a person."""

    def get_vendor_data(self, vendor):
        """Return a list of records for a vendor."""

    def get_vendor_data_dict(self, vendor):
        """Return a dict of records for a vendor."""

    def get_vendors(self):
        """Return a list of vendors in vendor data."""

    def update_person_vendor_value(self, vendor, pid, key, value):
        """Delete vendor data for a person."""

    # Vendor - Github
    def add_github_value(self):
        """Comment"""

    def delete_github_value(self):
        """Comment"""

    def delete_person_github_data(self):
        """Comment"""

    def get_github_data(self):
        """Comment"""

    def update_github_value(self):
        """Comment"""

    # Vendor - Google
    def add_google_value(self):
        """Comment"""

    def delete_google_value(self):
        """Comment"""

    def delete_person_google_data(self):
        """Comment"""

    def get_google_data(self):
        """Comment"""

    def update_google_value(self):
        """Comment"""

    #
    # Report Functions
    #
    def display_hires(self):
        """Comment"""

    def display_terms(self):
        """Comment"""

    def get_hires_terms(self):
        """Return information about new hires and terminations"""

    def sort_hires_terms(self):
        """Sort for hires and terms reports."""

    #
    # Update Functions
    #
    def update_account_statuses(self):
        """Update accounts status for all people."""

    def update_desks(self):
        """Update desk information for all people."""
