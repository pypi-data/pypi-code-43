import typing

import pandas

from . import server, utils


class API(server.Server):

    def __init__(self, *args, fetch_batch_size=1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetch_batch_size = fetch_batch_size
        self.get('/health')
        self.get('/ready')

    def _fetch_in_batches(self, fetch, limit, offset):
        start = 0 if offset is None else offset
        end = None if limit is None else limit + start
        while True:
            # First, we determine how much data to fetch in the next request
            # If there is no end, we take the default
            if end is None:
                batch_size = self.fetch_batch_size
            # If there is an end, we continue fetching until we reach it
            elif start < end:
                batch_size = min(self.fetch_batch_size, end - start)
            # If we're past the end, we stop
            else:
                return
            # We fetch the response, and if we got anything, we repeat the loop
            response = fetch(batch_size, start)
            if response:
                start += batch_size
                yield response
            else:
                return

    def openapi_documents(self):
        '''Returns the OpenAPI documents.'''
        return self.get('/openapidocuments')

    def openapi(self):
        '''Returns the OpenAPI definition.'''
        return self.get('/openapi.json')

    def get_in_progress_datasets(self):
        '''Returns a list of all in-progress datasets.'''
        route = '/datasets/in-progress'
        return [InProgressDataset.decode(d, api=self) for d in self.get(route)]

    def get_in_progress_dataset(self, id):
        '''Returns an in-progress datasets with a given id.'''
        route = '/datasets/{}/in-progress'.format(id)
        return InProgressDataset.decode(self.get(route), api=self)

    def create_in_progress_dataset(self, name):
        '''Creates a new in-progress dataset on the server and returns it.'''
        route = '/datasets/create'
        return InProgressDataset.decode(self.post(route, {'name': name}), api=self)

    def _get_raw_datasets(self, columns=None, condition=None, include_schema=None, include_metadata=None, include_aggregations=None, aggregation_filters=None, limit=None, offset=None, order_by=None, ascending=True):
        route = '/datasets'
        request = {
            'columns': [
                {
                    'name': column[0],
                    'jsonPath': column[1],
                    'dataType': column[2] if len(column) == 3 else None
                }
                for column in columns
            ] if columns else None,
            'condition': condition.encode() if condition else None,
            'includeSchema': include_schema,
            'includeMetadata': include_metadata,
            'includeAggregations': include_aggregations,
            'aggregationFilters': utils.encode_aggregation_filters(aggregation_filters),
            'offset': offset,
            'limit': limit,
            'orderBy': utils.encode_order_by(order_by, ascending),
        }
        return self.get(route, json=request)

    def get_published_datasets(self, columns=None, condition=None, include_schema=None, include_metadata=None, aggregation_filters=None, limit=100, offset=None, order_by=None, ascending=True, dataset_column_name='dataset'):
        '''Returns a dataframe of all published datasets that match query.

        :returns: A dataframe indexed by the id and version, which in addition
          to user-specified columns, contains a column with a PublishedDataset
          object for each dataset.
        :param columns: a list of tuples describing columns in the dataframe.
          Each column is either given by a pair (column_name, json_path), or a
          triple (column_name, json_path, type).
        :param condition: a QueryExpression object limiting the fetched datasets.
        :param include_schema: a boolean specifying if the response should
          include the schema (default True)
        :param include_metadata: a boolean specifying if the response should
          include the metadata (default False)
        :param aggregation_filters: a dict limiting the fetched datasets to ones
          where column values fall into one of the selected aggregation buckets.
          For example, using the dict
            {'organ': ['liver', 'kidney'], 'species': ['mouse', 'elephant']}
          would return the datasets where both organ is either liver or kidney,
          AND species is either mouse or elephant.
        :param limit: the number of rows to return (default 100).
          Returns all rows if set to None.
        :param offset: the initial offset (default 0).
        :param order_by: a list of QueryExpression objects by which to order
          the resulting datasets.
        :param ascending: a boolean or list of booleans to select the ordering.
          If the single boolean is True (the default), the list is ascending
          according to order_by, if False, it is descending. If given as a list,
          it must be of the same length as the order_by list, and the order is
          the ascending/descending for each particular component.
        :param dataset_column_name: the name of the dataframe column in which
          the corresponding PublishedDataset objects are available.
        '''
        versions = []
        records = []
        def fetch(limit, offset):
            return self._get_raw_datasets(
                columns=columns,
                condition=condition,
                include_schema=include_schema,
                include_metadata=include_metadata,
                include_aggregations=False,
                aggregation_filters=aggregation_filters,
                limit=limit,
                offset=offset,
                order_by=order_by,
                ascending=ascending
            )['results']
        for results in self._fetch_in_batches(fetch, limit, offset):
            for result in results:
                record = result['columns']
                record[dataset_column_name] = PublishedDataset.decode(result, api=self)
                records.append(record)
                versions.append((result['id']['id'], result['id']['version']))
        index = pandas.MultiIndex.from_tuples(versions, names=['id', 'version'])
        column_names = [column[0] for column in columns] if columns else []
        if dataset_column_name is not None:
            column_names.insert(0, dataset_column_name)
        return pandas.DataFrame.from_records(records, columns=column_names, index=index)

    def get_published_dataset_aggregations(self, columns=None, condition=None, aggregation_filters=None):
        '''Returns aggregation buckets and their sizes for each column.

        :returns: aggregations as a Series with an index of buckets and terms, for example
            bucket     term
            organ      liver          10
                       kidney         20
            species    mouse           5
                       elephant       30
        :param columns: same as in self.get_published_datasets
        :param condition: same as in self.get_published_datasets
        :param aggregation_filters: same as in self.get_published_datasets
        '''
        response = self._get_raw_datasets(
            columns=columns,
            condition=condition,
            include_schema=False,
            include_metadata=False,
            include_aggregations=True,
            aggregation_filters=aggregation_filters,
            limit=0,
        )
        return utils.decode_aggregations(response['aggregations'])

    def get_published_dataset(self, id, version=None):
        '''Returns a published dataset with a given id and version.'''
        if version is None:
            version = PublishedDataset.LATEST
        route = '/datasets/{}/versions/{}'.format(id, version)
        return PublishedDataset.decode(self.get(route), api=self)

    def get_published_dataset_versions(self, id):
        '''Returns all published versions of dataset with a given id.'''
        route = '/datasets/{}'.format(id)
        response = self.get(route)
        id, versions = response['id'], response['versions']
        return [
            PublishedDataset.decode({'id': id, 'version': version['version'], 'name': version['name']}, api=self)
            for version in versions
        ]

    def create_in_progress_dataset_from_csv_file(self, name: str, file: typing.TextIO, metadata: dict = None):
        '''Creates a new in-progress dataset from a CSV file on the server.'''
        dataset = self.create_in_progress_dataset(name)
        dataset.upload_data(file)
        dataset.infer_schema()
        if metadata is not None:
            dataset.upload_metadata(metadata)
        return dataset

    def create_published_dataset_from_csv_file(self, *args, changelog='Initial version', **kwargs):
        '''Creates a new published dataset from a CSV file on the server.'''
        dataset = self.create_in_progress_dataset_from_csv_file(*args, **kwargs)
        published_dataset = dataset.publish(changelog)
        return published_dataset

    def get_dataset_permissions(self, dataset_id):
        route = '/datasets/{}/permissions'.format(dataset_id)
        return DatasetPermissions.decode(self.get(route))

    def add_dataset_user(self, dataset_id, user):
        route = '/datasets/{}/permissions/users/add'.format(dataset_id)
        return self.post(route, user.encode())

    def remove_dataset_user(self, dataset_id, email):
        route = '/datasets/{}/permissions/users/delete'.format(dataset_id)
        payload = {
            'email': email,
        }
        return self.post(route, payload)

    def add_dataset_group(self, dataset_id, group):
        route = '/datasets/{}/permissions/groups/add'.format(dataset_id)
        return self.post(route, group.encode())

    def remove_dataset_group(self, dataset_id, name):
        route = '/datasets/{}/permissions/groups/delete'.format(dataset_id)
        payload = {
            'name': name,
        }
        return self.post(route, payload)

    def change_dataset_visibility(self, dataset_id, is_public):
        route = '/datasets/{}/permissions/visibility'.format(dataset_id)
        payload = {
            'isPublic': is_public,
        }
        return self.post(route, payload)


class Schema:
    class Column:
        def __init__(self, name, description, data_type, array_value_separator, missing_value_identifiers, search, aggregation, rdf_predicate):
            self.name = name
            self.description = description
            self.data_type = data_type
            self.array_value_separator = array_value_separator
            self.missing_value_identifiers = missing_value_identifiers
            self.search = search
            self.aggregation = aggregation
            self.rdf_predicate = rdf_predicate

        def __repr__(self):
            return '<Column {}:{}>'.format(self.name, self.data_type)

        @classmethod
        def decode(cls, d):
            return cls(
                name=d['name'],
                description=d['description'],
                data_type=d['dataType'],
                array_value_separator=d['arrayValueSeparator'],
                missing_value_identifiers=d['missingValueIdentifiers'],
                search=d['search'],
                aggregation=d['aggregation'],
                rdf_predicate=d['rdfPredicate'],
            )

        def encode(self):
            return {
                'name': self.name,
                'description': self.description,
                'dataType': self.data_type,
                'arrayValueSeparator': self.array_value_separator,
                'missingValueIdentifiers': self.missing_value_identifiers,
                'search': self.search,
                'aggregation': self.aggregation,
                'rdfPredicate': self.rdf_predicate,
            }

    def __init__(self, columns):
        self.columns = columns

    def __repr__(self):
        return '<Schema>'

    @classmethod
    def decode(cls, d):
        return cls(
            columns=[
                cls.Column.decode(column) for column in d['columns']
            ]
        )

    def encode(self):
        return {
            'columns': [column.encode() for column in self.columns]
        }


class DatasetPermissions:

    class User:
        def __init__(self, email, can_write):
            self.email = email
            self.can_write = can_write

        @classmethod
        def decode(cls, u):
            return cls(email=u['email'], can_write=u['canWrite'])

        def encode(self):
            return {
                'email': self.email,
                'canWrite': self.can_write
            }

    class Group:
        def __init__(self, name, can_write):
            self.name = name
            self.can_write = can_write

        @classmethod
        def decode(cls, g):
            return cls(name=g['name'], can_write=g['canWrite'])

        def encode(self):
            return {
                'name': self.name,
                'canWrite': self.can_write
            }

    def __init__(self, id, users, groups, is_public):
        self.id = id
        self.users = users
        self.groups = groups
        self.is_public = is_public

    def __repr__(self):
        return '<DatasetPermissions {!r}>'.format(self.id)

    @classmethod
    def decode(cls, dp):
        return cls(
            id=dp['id'],
            users=list(cls.User.decode(u) for u in dp['users']),
            groups=list(cls.Group.decode(g) for g in dp['groups']),
            is_public=dp['isPublic'],
        )

    def encode(self):
        return {
            'id': self.id,
            'isPublic': self.is_public,
            'users': list(u.encode() for u in self.users),
            'groups': list(g.encode() for g in self.groups),
        }


class InProgressDataset:
    def __init__(self, id, name, schema, created, description, metadata, api):
        self.id = id
        self.name = name
        self.schema = schema
        self.created = created
        self.description = description
        self.metadata = metadata
        self.api = api

    def __repr__(self):
        return '<InProgressDataset {!r} - {}>'.format(self.id, self.name)

    @classmethod
    def decode(cls, d, api):
        return cls(
            id=d['id'],
            name=d['name'],
            schema=Schema.decode(d['schema']) if d['schema'] else None,
            created=utils.decode_utc_datetime(d['created']),
            description=d['description'],
            metadata=d['metadata'],
            api=api
        )

    def encode(self):
        return {
            'id': self.id,
            'name': self.name,
            'schema': self.schema.encode() if self.schema else None,
            'created': self.created.toisoformat(),
            'description': self.description,
            'metadata': self.metadata,
        }

    def sample(self):
        route = '/datasets/{}/in-progress/sample'.format(self.id)
        return self.api.get(route)

    def upload_schema(self, schema: Schema):
        route = '/datasets/{}/in-progress/schema/upload'.format(self.id)
        self.api.post(route, schema.encode())
        self.schema = schema

    def upload_schema_file(self, file: typing.TextIO):
        route = '/datasets/{}/in-progress/schema/upload'.format(self.id)
        schemacontent = file.read()
        updated_dataset = InProgressDataset.decode(self.api.post(route, data=schemacontent), api=self)
        self.schema = updated_dataset.schema

    def upload_metadata(self, metadata):
        route = '/datasets/{}/in-progress/metadata/upload'.format(self.id)
        self.api.post(route, metadata)
        self.metadata = metadata

    def upload_metadata_file(self, file: typing.TextIO):
        route = '/datasets/{}/in-progress/metadata/upload'.format(self.id)
        metadatacontent = file.read()
        updated_dataset = InProgressDataset.decode(self.api.post(route, data=metadatacontent), api=self)
        self.metadata = updated_dataset.metadata

    def upload_data(self, data):
        route = '/datasets/{}/in-progress/data/upload'.format(self.id)
        return self.api.upload(route, {'data': data})

    def set_description(self, description):
        route = '/datasets/{}/in-progress'.format(self.id)
        self.api.post(route, json={'description': description})
        self.description = description

    def infer_schema(self):
        route = '/datasets/{}/in-progress/schema/infer'.format(self.id)
        updated_dataset = self.api.post(route, None)
        self.schema = Schema.decode(updated_dataset['schema'])

    def delete(self):
        route = '/datasets/{}/in-progress'.format(self.id)
        return self.api.delete(route)

    def publish(self, changelog):
        route = '/datasets/{}/in-progress/publish'.format(self.id)
        return PublishedDataset.decode(self.api.post(route, {'changelog': changelog}), api=self.api)

    def copy_from(self, published_dataset):
        route = '/datasets/{}/in-progress/copy-from/{}/versions/{}'.format(
            self.id,
            published_dataset.id,
            published_dataset.version
        )
        return self.api.post(route)

    def get_permissions(self):
        return self.api.get_dataset_permissions(self.id)


class PublishedDataset:
    LATEST = 'LATEST'

    def __init__(self, id, version, name, schema, created, description, metadata, api):
        self.id = id
        self.version = version
        self.name = name
        self.schema = schema
        self.created = created
        self.description = description
        self.metadata = metadata
        self.api = api

    def __repr__(self):
        return '<PublishedDataset {!r}:{} - {}>'.format(self.id, self.version, self.name)

    @classmethod
    def decode(cls, d, api):
        return cls(
            id=d['id']['id'],
            version=d['id']['version'],
            name=d['name'],
            schema=Schema.decode(d['schema']) if ('schema' in d and d['schema']) else None,
            created=utils.decode_utc_datetime(d['created']),
            description=d['description'],
            metadata=d['metadata'] if 'metadata' in d else None,
            api=api
        )

    def encode(self):
        return {
            'id': {
                'id': self.id,
                'version': self.version,
            },
            'name': self.name,
            'schema': self.schema.encode() if self.schema else None,
            'created': self.created.toisoformat(),
            'description': self.description,
            'metadata': self.metadata
        }

    def new_version(self):
        route = '/datasets/{}/versions/{}/create-new-version'.format(self.id, self.version)
        return InProgressDataset.decode(self.api.post(route), api=self)

    def get_raw_data(self, columns=None, condition=None, include_aggregations=None, aggregation_filters=None, limit=None, offset=None, order_by=None, ascending=True):
        route = '/datasets/{}/versions/{}/data'.format(self.id, self.version)
        request = {
            'columns': columns,
            'condition': condition.encode() if condition else None,
            'includeAggregations': include_aggregations,
            'aggregationFilters': utils.encode_aggregation_filters(aggregation_filters),
            'offset': offset,
            'limit': limit,
            'orderBy': utils.encode_order_by(order_by, ascending),
        }
        return self.api.get(route, json=request)

    def get_data(self, columns=None, condition=None, aggregation_filters=None, limit=100, offset=None, order_by=None, ascending=True):
        '''
        :param columns: a list of column names that should appear in the result.
          If None, all columns are included.
        :param condition: same as in Api.get_published_datasets
        :param aggregation_filters: same as in Api.get_published_datasets
        :param limit: same as in Api.get_published_datasets
        :param offset: same as in Api.get_published_datasets
        :param order_by: same as in Api.get_published_datasets
        :param ascending: same as in Api.get_published_datasets
        '''
        ids = []
        data = []
        def fetch(limit, offset):
            return self.get_raw_data(
                columns=columns,
                condition=condition,
                include_aggregations=False,
                aggregation_filters=aggregation_filters,
                limit=limit,
                offset=offset,
                order_by=order_by,
                ascending=ascending
            )['results']
        for results in self.api._fetch_in_batches(fetch, limit, offset):
            ids += [row['id'] for row in results]
            data += [row['data'] for row in results]
        df = pandas.DataFrame.from_records(data, index=ids)
        column_names = [column.name for column in self.schema.columns]
        df = df.loc[:, column_names]  # re-order columns according to schema
        return df

    def get_data_aggregations(self, columns=None, condition=None, aggregation_filters=None):
        '''Returns aggregation buckets and their sizes for each column.

        :returns: same as in PublishedDataset.get_published_dataset_aggregations
        :param columns: same as in self.get_data
        :param condition: same as in self.get_data
        :param aggregation_filters: same as in self.get_data
        '''
        response = self.get_raw_data(
            columns=columns,
            condition=condition,
            include_aggregations=True,
            aggregation_filters=aggregation_filters,
            limit=0,
        )
        return utils.decode_aggregations(response['aggregations'])

    def openapi(self):
        route = '/datasets/{}/versions/{}/openapi.json'.format(self.id, self.version)
        return self.api.get(route)

    def get_permissions(self):
        return self.api.get_dataset_permissions.get(self.id)

    def delete_all_versions(self):
        route = '/datasets/{}'.format(self.id)
        return self.api.delete(route)


class QueryExpression:
    def __init__(self, *args):
        class_name = type(self).__name__
        if len(args) == 1:
            value = args[0]
            valid_types = [type(None), str, int, float, bool]
            if not any(isinstance(value, ty) for ty in valid_types):
                raise ValueError('Type {0} is not valid for a {1} constant'.format(type(value), class_name))
            else:
                self.is_node = False
                self.value = value
        elif len(args) == 2:
            name, arguments = args
            if not isinstance(name, str):
                raise ValueError('The first argument of a {0} node must be a string'.format(class_name))
            elif not (isinstance(arguments, list) and all(isinstance(argument, type(self)) for argument in arguments)):
                raise ValueError('The second argument of a {0} node must be a list of {0}s'.format(class_name))
            else:
                self.is_node = True
                self.name = name
                self.arguments = arguments
        else:
            raise TypeError('__init__ expected 1 (for constant) or 2 (for node) arguments, got {0}'.format(len(args)))

    def __repr__(self):
        if self.is_node:
            return '{0}({1!r}, {2!r})'.format(type(self).__name__, self.name, self.arguments)
        else:
            return '{0}({1!r})'.format(type(self).__name__, self.value)
    
    @classmethod
    def _convert_if_necessary(cls, value):
        if isinstance(value, cls):
            return value
        else:
            return cls(value)

    @classmethod
    def decode(cls, value):
        if isinstance(value, dict) and len(value) == 1:
            name, arguments = value.popitem()
            return cls(name, [cls.decode(argument) for argument in arguments])
        else:
            return cls(value)

    def encode(self):
        if self.is_node:
            return {self.name: [argument.encode() for argument in self.arguments]}
        else:
            return self.value

    @classmethod
    def search_anywhere(cls, term):
        return cls('searchAnywhere', [cls(term)])

    @classmethod
    def column(cls, column_name):
        return cls('column', [cls(column_name)])

    @classmethod
    def system_column(cls, column_name):
        return cls('systemColumn', [cls(column_name)])

    @classmethod
    def exact_search(cls, expr, string):
        return cls('exactSearch', [expr, cls(string)])

    @classmethod
    def fuzzy_search(cls, expr, string):
        return cls('fuzzySearch', [expr, cls(string)])

    @classmethod
    def json_path_query(cls, expr, json_path):
        return cls('jsonPathQuery', [expr, cls(json_path)])

    def __getitem__(self, json_path):
        return self.json_path_query(self, json_path)

    def __and__(self, other):
        return type(self)('and', [self, self._convert_if_necessary(other)])

    def __rand__(self, other):
        return type(self)('and', [self._convert_if_necessary(other), self])

    def __or__(self, other):
        return type(self)('or', [self, self._convert_if_necessary(other)])

    def __ror__(self, other):
        return type(self)('and', [self._convert_if_necessary(other), self])

    def __invert__(self):
        return type(self)('not', [self])

    def __eq__(self, other):
        return type(self)('eq', [self, self._convert_if_necessary(other)])

    def __lt__(self, other):
        return type(self)('lt', [self, self._convert_if_necessary(other)])

    def __le__(self, other):
        return type(self)('le', [self, self._convert_if_necessary(other)])

    def __gt__(self, other):
        return type(self)('gt', [self, self._convert_if_necessary(other)])

    def __ge__(self, other):
        return type(self)('ge', [self, self._convert_if_necessary(other)])
