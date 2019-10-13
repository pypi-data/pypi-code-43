# -*- coding: utf-8 -*-
"""Init file for People."""

import base64
import datetime
import google.auth
import re

# from bits.people.people import People
from google.cloud import bigquery
from google.cloud import firestore


class People(object):
    """People Class."""

    def __init__(
        self,
        bitsdb_project='broad-bitsdb-firestore',
        people_project='broad-people-api',
        verbose=False
    ):
        """Initialize a class instance."""
        self.credentials, self.project = google.auth.default()
        self.bitsdb = firestore.Client(bitsdb_project, self.credentials)
        self.peopledb = firestore.Client(people_project, self.credentials)

    def get_all_people(self, fields=None, includeTerminated=False):
        """Return a list of all People."""
        collection = 'people_people'
        query = self.bitsdb.collection(collection)

        # handle terminated users
        if not includeTerminated:
            query = query.where(u'terminated', u'==', False)

        # handle fields
        if fields:
            query = query.select(fields)

        people = []
        for doc in query.get():
            person = doc.to_dict()
            people.append(person)
        return people

    def get_future_hires(self):
        """Return a list of future hires."""
        today = str(datetime.datetime.now().date())
        collection = 'people_people'
        query = self.bitsdb.collection(collection)
        query = query.where(u'start_date', u'>', today)
        hires = []
        for doc in query.stream():
            hires.append(doc.to_dict())
        return hires

    def get_future_terms(self):
        """Return a list of future terms."""
        today = str(datetime.datetime.now().date())
        collection = 'people_people'
        query = self.bitsdb.collection(collection)
        query = query.where(u'end_date', u'>', today)
        hires = []
        for doc in query.stream():
            hires.append(doc.to_dict())
        return hires

    def get_home_institutions(self):
        """Return a list of Home Institutions."""
        fields = [
            'emplid',
            'home_institution',
            'terminated',
        ]
        people = self.get_all_people(fields=fields)
        institutions = {}
        for p in people:
            if p['terminated']:
                continue
            name = p['home_institution']
            if name not in institutions:
                institutions[name] = 0
            institutions[name] += 1
        home_institutions = []
        for name in institutions:
            inst = {
                'name': name,
                'count': institutions[name],
            }
            home_institutions.append(inst)
        return home_institutions

    def get_job_classes(self):
        """Return a list of Job Classes."""
        fields = [
            'emplid',
            'job_class',
            'terminated',
        ]
        people = self.get_all_people(fields=fields)
        classes = {}
        for p in people:
            if p['terminated']:
                continue
            job_class = p['job_class']
            if job_class not in classes:
                classes[job_class] = 0
            classes[job_class] += 1
        job_classes = []
        for name in classes:
            c = {
                'name': name,
                'count': classes[name],
            }
            job_classes.append(c)
        return job_classes

    def get_org_units(self):
        """Return a list of Organizational Units."""
        fields = [
            'emplid',
            'org_unit',
            'terminated',
        ]
        people = self.get_all_people(fields=fields)
        ous = {}
        for p in people:
            org_unit = p['org_unit']
            if org_unit not in ous:
                ous[org_unit] = 0
            ous[org_unit] += 1
        org_units = []
        for name in ous:
            o = {
                'name': name,
                'count': ous[name],
            }
            org_units.append(o)
        return org_units

    def get_people(self, args, role):
        """Return people based on arguments."""
        collection = u'people_people'
        kind = u'people_people'
        return self.run_query(collection, kind, args)

    def get_person(self, args, role):
        """Return a person."""
        collection = u'people_people'
        coll = self.bitsdb.collection(collection)

        # get person_id
        person_id = None
        if 'id' in args and args['id']:
            person_id = args['id']

        # return if person_id is not set
        if not person_id:
            return {}

        # check if id is an emplid
        ref = coll.document(person_id)
        person = ref.get().to_dict()
        if person:
            return self.prepare_person(person, role)

        # check string keys
        for key in [
            u'person_id',
            u'username',
            u'github_id',
            u'github_login',
            u'google_id',
            u'desk',
            u'primary_work_phone',
        ]:
            query = coll.where(key, u'==', person_id)
            results = list(query.get())
            if len(results) == 1:
                person = results[0].to_dict()
                return self.prepare_person(person, role)

        # check array keys
        for key in [
            u'emails',
            u'desks',
            u'extensions',
        ]:
            query = coll.where(key, u'array_contains', person_id)
            results = list(query.get())
            if len(results) == 1:
                person = results[0].to_dict()
                return self.prepare_person(person, role)

        return {}

    def get_person_direct_reports(self, args, role):
        """Return the list of direct reports for a person."""
        person = self.get_person(args, role)

        # get emplid of the person
        emplid = person.get('emplid')
        if not emplid:
            return []

        # run query
        collection = u'people_people'
        query = self.bitsdb.collection(collection).where(
            u'manager_id', u'==', emplid
        ).order_by('last_name').get()

        # assemble and return direct reports for this person
        reports = []
        for doc in query:
            person = self.prepare_person(doc.to_dict(), role)
            if not person['terminated']:
                reports.append(person)
        return reports

    def get_user(self, sub):
        """Return a user from datastore."""
        return self.peopledb.collection('users').document(sub).get().to_dict()

    def get_user_role(self, user):
        """Return a user's role."""
        # check if user is an admin
        admin = user.get('admin', False)
        if admin:
            return 'admin'
        return 'user'

    def get_users(self):
        """Return a user from datastore."""
        query = self.peopledb.collection('users').get()
        users = []
        for doc in query:
            users.append(doc.to_dict())
        return users

    def prepare_person(self, person, role):
        """Prepare a single person."""
        # public users just sees name, email, phone
        if role == 'public':
            return {
                'kind': 'people#person',
                'first_name': person['first_name'],
                'last_name': person['last_name'],
                'full_name': person['full_name'],
                'email': person['email'],
                'primary_work_phone': person['primary_work_phone'],
            }

        # authenticated users see basic People info
        elif role in ['nobody', 'user']:
            return {
                'kind': 'people#person',
                'department_name': person['department_name'],
                'desk': person['desk'],
                'email': person['email'],
                'emplid': person['emplid'],
                'first_name': person['first_name'],
                'full_name': person['full_name'],
                'github_login': person.get('github_login'),
                'google_id': person.get('google_id'),
                'home_institution': person.get('home_institution'),
                'job_class': person['job_class'],
                'last_name': person['last_name'],
                'manager_id': person['manager_id'],
                'manager': person['manager'],
                'nicknames': person.get('nicknames', []),
                'org_unit': person['org_unit'],
                'photo_url': person.get('photo_url'),
                'primary_work_phone': person.get('primary_work_phone'),
                'slack_id': person.get('slack_id'),
                'slack_name': person.get('slack_name'),
                'terminated': person.get('terminated', False),
                'title': person['title'],
                'username': person['username'],
            }

        # named users see additional info
        # elif role == 'user':
        #     return {
        #         'kind': 'people#person',
        #         'department_name': person['department_name'],
        #         'desk': person['desk'],
        #         'email': person['email'],
        #         'emplid': person['emplid'],
        #         'first_name': person['first_name'],
        #         'full_name': person['full_name'],
        #         'github_login': person.get('github_login'),
        #         'home_institution': person['home_institution'],
        #         'job_class': person['job_class'],
        #         'last_name': person['last_name'],
        #         'manager_id': person['manager_id'],
        #         'manager': person['manager'],
        #         'nicknames': person.get('nicknames', []),
        #         'org_unit': person['org_unit'],
        #         'photo_url': person.get('photo_url'),
        #         'primary_work_phone': person['primary_work_phone'],
        #         'slack_id': person.get('slack_id'),
        #         'slack_name': person.get('slack_name'),
        #         'terminated': person.get('terminated', False),
        #         'title': person['title'],
        #         'username': person['username'],
        #     }

        # admin users see full record
        elif role == 'admin':
            person['kind'] = 'people#person'
            return person
        # no role, no data
        return None

    #
    # Run Firestore queries
    #
    def _get_max_results(self, args):
        """Return the max results."""
        maxResults = 1000
        if 'maxResults' in args and args['maxResults']:
            try:
                if int(args['maxResults']) <= int(maxResults):
                    maxResults = int(args['maxResults'])
            except Exception as e:
                print('ERROR processing maxResults: %s' % (e))
                return maxResults
        return maxResults

    def _get_order_by(self, args):
        """Return the order by."""
        orderBy = u'emplid'
        if 'orderBy' in args:
            orderBy = u'%s' % (args['orderBy'])
        return orderBy

    def _get_page_token(self, args):
        """Return the page token."""
        pageToken = None
        if 'pageToken' in args:
            pageToken = u'%s' % (args['pageToken'])
        return pageToken

    def _get_next_page_token(self, items, maxResults, orderBy, results):
        """Return the nextPageToken."""
        nextPageToken = None
        if len(results) > maxResults:
            token = (u'%s:%s' % (orderBy, items[-1][orderBy])).encode()
            nextPageToken = base64.b64encode(token).decode()
        return nextPageToken

    def _get_query(self, ref, args):
        """Return the query."""
        maxResults = self._get_max_results(args)
        orderBy = self._get_order_by(args)
        pageToken = self._get_page_token(args)

        # order results
        query = ref.order_by(orderBy)

        # limit results
        limit = maxResults + 1
        query = query.limit(limit)

        # add where clause, orderBy must be set and be non-null and non-empty
        query = query.where(orderBy, u'>', u'')

        # add start after
        if pageToken:
            token = base64.b64decode(pageToken).decode()
            key, value = token.split(':')
            if key != orderBy:
                print(u'ERROR: Invalid token: %s:%s' % (key, value))
            else:
                query = query.start_after({
                    key: value,
                })

        return query, maxResults, orderBy

    def run_query(self, collection, kind, args):
        """Run a query and return a response."""
        # collection ref
        ref = self.bitsdb.collection(collection)

        # get query
        query, maxResults, orderBy = self._get_query(ref, args)

        # get people results
        items = []
        results = list(query.get())
        for doc in results[:maxResults]:
            items.append(doc.to_dict())
        # create response
        response = {
            kind: items,
        }

        # create nextPageToken
        nextPageToken = self._get_next_page_token(items, maxResults, orderBy, results)
        if nextPageToken:
            response['nextPageToken'] = u'%s' % (nextPageToken)
        return response

    def search_people(self, args, role):
        """Return results from a people search."""
        if 'q' not in args:
            return []

        # include terminated people in search results
        includeTerminated = False
        if args.get('includeTerminated'):
            includeTerminated = True
        print('Include terminated: %s' % (includeTerminated))

        # get the full querystring
        querystring = args['q']
        print('Original Query String: %s' % (querystring))

        # find all the quoted substrings
        substrings = re.findall(r'\"(.+?)\"', querystring)

        # remove the quoted substrings from querystring
        remainder = querystring
        for string in substrings:
            remainder = remainder.replace('"%s"' % (string), '')

        # add remaining strings to substrings list
        for word in re.sub(' +', ' ', remainder).strip().split(' '):
            word = word.strip().replace('"', '')
            if word:
                substrings.append(word)
        print('Query Substrings: %s' % (sorted(substrings)))

        # get ordering from arguments
        order = 'last_name, first_name'
        if 'order' in args and args['order'].strip():
            order = args['order']

        # return no results if we have no search strings
        # if not substrings:
        #     return []

        # create search string merging several fields
        searchstring = """
            LOWER(ARRAY_TO_STRING(
                [
                    CAST(emplid AS STRING),
                    CAST(person_id AS STRING),
                    IF (desk IS NOT NULL, desk, ""),
                    IF (email IS NOT NULL, email, ""),
                    IF (full_name IS NOT NULL, full_name, ""),
                    IF (github_login IS NOT NULL, github_login, ""),
                    IF (home_institution IS NOT NULL, home_institution, ""),
                    IF (job_class IS NOT NULL, job_class, ""),
                    IF (org_unit IS NOT NULL, org_unit, ""),
                    IF (primary_work_phone IS NOT NULL, primary_work_phone, ""),
                    IF (slack_name IS NOT NULL, slack_name, ""),
                    IF (title IS NOT NULL, title, ""),
                    IF (username IS NOT NULL, username, ""),
                    ARRAY_TO_STRING(nicknames, ' ')
                ],
                ' '
            ))"""

        wheres = []

        # exclude terminated users for non admins and for includeTerminated is False
        if role != 'admin' or not includeTerminated:
            wheres.append('terminated IS FALSE')

        # create where clause from the query words
        for word in substrings:
            wherestring = '%s LIKE "%%%s%%"' % (
                searchstring,
                word.lower(),
            )
            wheres.append(wherestring)

        # create query string
        query = 'SELECT * FROM `broad-bitsdb-api.peopleapi.people`'

        # add where clauses to query
        if wheres:
            query += ' WHERE %s' % (' AND '.join(wheres))

        # add order clause to query
        query += ' ORDER BY %s' % (order)

        # add limit clause
        query += ' LIMIT 1000'

        # run query
        print('Running Query: %s' % (re.sub(' +', ' ', query.replace('\n', ' '))).strip())
        client = bigquery.Client()
        query_job = client.query(
            query,
            location="US",
        )

        # get users from search results
        results = []
        for row in query_job:  # API request - fetches results
            person = self.prepare_person(dict(row), role)
            results.append(person)
        return results
