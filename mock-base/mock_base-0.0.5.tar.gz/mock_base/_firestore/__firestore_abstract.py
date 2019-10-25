from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Iterable, Any, Optional


class Client:
    
    @abstractmethod
    def collection(self, *collection_path) -> CollectionReference:
            """Get a reference to a collection.

            For a top-level collection:

            .. code-block:: python

                >>> client.collection('top')

            For a sub-collection:

            .. code-block:: python

                >>> client.collection('mydocs/doc/subcol')
                >>> # is the same as
                >>> client.collection('mydocs', 'doc', 'subcol')

            Sub-collections can be nested deeper in a similar fashion.

            Args:
                collection_path (Tuple[str, ...]): Can either be

                    * A single ``/``-delimited path to a collection
                    * A tuple of collection path segments

            Returns:
                ~.firestore_v1.collection.CollectionReference: A reference
                to a collection in the Firestore database.
            """
            pass

    @abstractmethod
    def document(self, *document_path) -> DocumentReference:
            """Get a reference to a document in a collection.

            For a top-level document:

            .. code-block:: python

                >>> client.document('collek/shun')
                >>> # is the same as
                >>> client.document('collek', 'shun')

            For a document in a sub-collection:

            .. code-block:: python

                >>> client.document('mydocs/doc/subcol/child')
                >>> # is the same as
                >>> client.document('mydocs', 'doc', 'subcol', 'child')

            Documents in sub-collections can be nested deeper in a similar fashion.

            Args:
                document_path (Tuple[str, ...]): Can either be

                    * A single ``/``-delimited path to a document
                    * A tuple of document path segments

            Returns:
                ~.firestore_v1.document.DocumentReference: A reference
                to a document in a collection.
            """

    @staticmethod
    @abstractmethod
    def field_path(*field_names):
            """Create a **field path** from a list of nested field names.

            A **field path** is a ``.``-delimited concatenation of the field
            names. It is used to represent a nested field. For example,
            in the data

            .. code-block:: python

               data = {
                  'aa': {
                      'bb': {
                          'cc': 10,
                      },
                  },
               }

            the field path ``'aa.bb.cc'`` represents the data stored in
            ``data['aa']['bb']['cc']``.

            Args:
                field_names (Tuple[str, ...]): The list of field names.

            Returns:
                str: The ``.``-delimited field path.
            """
            
    # @staticmethod
    # @abstractmethod
    # def write_option(**kwargs):
    #         """Create a write option for write operations.
    #
    #         Write operations include :meth:`~.DocumentReference.set`,
    #         :meth:`~.DocumentReference.update` and
    #         :meth:`~.DocumentReference.delete`.
    #
    #         One of the following keyword arguments must be provided:
    #
    #         * ``last_update_time`` (:class:`google.protobuf.timestamp_pb2.\
    #                Timestamp`): A timestamp. When set, the target document must
    #                exist and have been last updated at that time. Protobuf
    #                ``update_time`` timestamps are typically returned from methods
    #                that perform write operations as part of a "write result"
    #                protobuf or directly.
    #         * ``exists`` (:class:`bool`): Indicates if the document being modified
    #               should already exist.
    #
    #         Providing no argument would make the option have no effect (so
    #         it is not allowed). Providing multiple would be an apparent
    #         contradiction, since ``last_update_time`` assumes that the
    #         document **was** updated (it can't have been updated if it
    #         doesn't exist) and ``exists`` indicate that it is unknown if the
    #         document exists or not.
    #
    #         Args:
    #             kwargs (Dict[str, Any]): The keyword arguments described above.
    #
    #         Raises:
    #             TypeError: If anything other than exactly one argument is
    #                 provided by the caller.
    #         """
    #
   
    @abstractmethod
    def get_all(self, references, field_paths=None, transaction=None):
            """Retrieve a batch of documents.

            .. note::

               Documents returned by this method are not guaranteed to be
               returned in the same order that they are given in ``references``.

            .. note::

               If multiple ``references`` refer to the same document, the server
               will only return one result.

            See :meth:`~.firestore_v1.client.Client.field_path` for
            more information on **field paths**.

            If a ``transaction`` is used and it already has write operations
            added, this method cannot be used (i.e. read-after-write is not
            allowed).

            Args:
                references (List[.DocumentReference, ...]): Iterable of document
                    references to be retrieved.
                field_paths (Optional[Iterable[str, ...]]): An iterable of field
                    paths (``.``-delimited list of field names) to use as a
                    projection of document fields in the returned results. If
                    no value is provided, all fields will be returned.
                transaction (Optional[~.firestore_v1.transaction.\
                    Transaction]): An existing transaction that these
                    ``references`` will be retrieved in.

            Yields:
                .DocumentSnapshot: The next document snapshot that fulfills the
                query, or :data:`None` if the document does not exist.
            """

    @abstractmethod
    def collections(self) -> List[CollectionReference]:
        """List top-level collections of the client's database.

            Returns:
                Sequence[~.firestore_v1.collection.CollectionReference]:
                    iterator of subcollections of the current document.
            """

    @abstractmethod
    def batch(self):
        """Get a batch instance from this client.

            Returns:
                ~.firestore_v1.batch.WriteBatch: A "write" batch to be
                used for accumulating document changes and sending the changes
                all at once.
            """

    @abstractmethod
    def transaction(self, **kwargs) -> Client:
        """Get a transaction that uses this client.

            See :class:`~.firestore_v1.transaction.Transaction` for
            more information on transactions and the constructor arguments.

            Args:
                kwargs (Dict[str, Any]): The keyword arguments (other than
                    ``client``) to pass along to the
                    :class:`~.firestore_v1.transaction.Transaction`
                    constructor.

            Returns:
                ~.firestore_v1.transaction.Transaction: A transaction
                attached to this client.
            """
        
  
class DocumentReference(ABC):
    
    @property
    @abstractmethod
    def path(self) -> str:
        """Database-relative for this document.

        Returns:
            str: The document's relative path.
        """

    @property
    @abstractmethod
    def id(self) -> str:
        """The document identifier (within its collection).

        Returns:
            str: The last component of the path.
        """

    @property
    @abstractmethod
    def parent(self) -> CollectionReference:
        """Collection that owns the current document.

        Returns:
            ~.firestore_v1.collection.CollectionReference: The
            parent collection.
        """
        parent_path = self._path[:-1]
        return self._client.collection(*parent_path)

    @abstractmethod
    def collection(self, collection_id) -> CollectionReference:
        """Create a sub-collection underneath the current document.

        Args:
            collection_id (str): The sub-collection identifier (sometimes
                referred to as the "kind").

        Returns:
            ~.firestore_v1.collection.CollectionReference: The
            child collection.
        """

    @abstractmethod
    def create(self, document_data):
        """Create the current document in the Firestore database.

        Args:
            document_data (dict): Property names and values to use for
                creating a document.

        Returns:
            google.cloud.firestore_v1.types.WriteResult: The
            write result corresponding to the committed document. A write
            result contains an ``update_time`` field.

        Raises:
            ~google.cloud.exceptions.Conflict: If the document already exists.
        """

    @abstractmethod
    def set(self, document_data, merge=False):
        """Replace the current document in the Firestore database.

        A write ``option`` can be specified to indicate preconditions of
        the "set" operation. If no ``option`` is specified and this document
        doesn't exist yet, this method will create it.

        Overwrites all content for the document with the fields in
        ``document_data``. This method performs almost the same functionality
        as :meth:`create`. The only difference is that this method doesn't
        make any requirements on the existence of the document (unless
        ``option`` is used), whereas as :meth:`create` will fail if the
        document already exists.

        Args:
            document_data (dict): Property names and values to use for
                replacing a document.
            merge (Optional[bool] or Optional[List<apispec>]):
                If True, apply merging instead of overwriting the state
                of the document.

        Returns:
            google.cloud.firestore_v1.types.WriteResult: The
            write result corresponding to the committed document. A write
            result contains an ``update_time`` field.
        """
        pass

    @abstractmethod
    def update(self, field_updates, option=None):
        """Update an existing document in the Firestore database.

        By default, this method verifies that the document exists on the
        server before making updates. A write ``option`` can be specified to
        override these preconditions.

        Each key in ``field_updates`` can either be a field name or a
        **field path** (For more information on **field paths**, see
        :meth:`~.firestore_v1.client.Client.field_path`.) To
        illustrate this, consider a document with

        .. code-block:: python

           >>> snapshot = document.get()
           >>> snapshot.to_dict()
           {
               'foo': {
                   'bar': 'baz',
               },
               'other': True,
           }

        stored on the server. If the field name is used in the update:

        .. code-block:: python

           >>> field_updates = {
           ...     'foo': {
           ...         'quux': 800,
           ...     },
           ... }
           >>> document.update(field_updates)

        then all of ``foo`` will be overwritten on the server and the new
        value will be

        .. code-block:: python

           >>> snapshot = document.get()
           >>> snapshot.to_dict()
           {
               'foo': {
                   'quux': 800,
               },
               'other': True,
           }

        On the other hand, if a ``.``-delimited **field path** is used in the
        update:

        .. code-block:: python

           >>> field_updates = {
           ...     'foo.quux': 800,
           ... }
           >>> document.update(field_updates)

        then only ``foo.quux`` will be updated on the server and the
        field ``foo.bar`` will remain intact:

        .. code-block:: python

           >>> snapshot = document.get()
           >>> snapshot.to_dict()
           {
               'foo': {
                   'bar': 'baz',
                   'quux': 800,
               },
               'other': True,
           }

        .. warning::

           A **field path** can only be used as a top-level key in
           ``field_updates``.

        To delete / remove a field from an existing document, use the
        :attr:`~.firestore_v1.transforms.DELETE_FIELD` sentinel. So
        with the example above, sending

        .. code-block:: python

           >>> field_updates = {
           ...     'other': firestore.DELETE_FIELD,
           ... }
           >>> document.update(field_updates)

        would update the value on the server to:

        .. code-block:: python

           >>> snapshot = document.get()
           >>> snapshot.to_dict()
           {
               'foo': {
                   'bar': 'baz',
               },
           }

        To set a field to the current time on the server when the
        update is received, use the
        :attr:`~.firestore_v1.transforms.SERVER_TIMESTAMP` sentinel.
        Sending

        .. code-block:: python

           >>> field_updates = {
           ...     'foo.now': firestore.SERVER_TIMESTAMP,
           ... }
           >>> document.update(field_updates)

        would update the value on the server to:

        .. code-block:: python

           >>> snapshot = document.get()
           >>> snapshot.to_dict()
           {
               'foo': {
                   'bar': 'baz',
                   'now': datetime.datetime(2012, ...),
               },
               'other': True,
           }

        Args:
            field_updates (dict): Field names or paths to update and values
                to update with.
            option (Optional[~.firestore_v1.client.WriteOption]): A
               write option to make assertions / preconditions on the server
               state of the document before applying changes.

        Returns:
            google.cloud.firestore_v1.types.WriteResult: The
            write result corresponding to the updated document. A write
            result contains an ``update_time`` field.

        Raises:
            ~google.cloud.exceptions.NotFound: If the document does not exist.
        """

    @abstractmethod
    def delete(self, option=None):
        pass

    @abstractmethod
    def get(self, field_paths=None, transaction=None) -> DocumentSnapshot:
        """Retrieve a snapshot of the current document.

        See :meth:`~.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Args:
            field_paths (Optional[Iterable[str, ...]]): An iterable of field
                paths (``.``-delimited list of field names) to use as a
                projection of document fields in the returned results. If
                no value is provided, all fields will be returned.
            transaction (Optional[~.firestore_v1.transaction.\
                Transaction]): An existing transaction that this reference
                will be retrieved in.

        Returns:
            ~.firestore_v1.document.DocumentSnapshot: A snapshot of
                the current document. If the document does not exist at
                the time of `snapshot`, the snapshot `reference`, `data`,
                `update_time`, and `create_time` attributes will all be
                `None` and `exists` will be `False`.
        """

    @abstractmethod
    def collections(self, page_size=None) -> List[CollectionReference]:
        """List subcollections of the current document.

        Args:
            page_size (Optional[int]]): The maximum number of collections
            in each page of results from this request. Non-positive values
            are ignored. Defaults to a sensible value set by the API.

        Returns:
            Sequence[~.firestore_v1.collection.CollectionReference]:
                iterator of subcollections of the current document. If the
                document does not exist at the time of `snapshot`, the
                iterator will be empty
        """
        pass

    @abstractmethod
    def on_snapshot(self, callback):
        pass


class Query(ABC):
    
    @abstractmethod
    def select(self, field_paths) -> Query:
        """Project documents matching query to a limited set of fields.

        See :meth:`~.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        If the current query already has a projection set (i.e. has already
        called :meth:`~.firestore_v1.query.Query.select`), this
        will overwrite it.

        Args:
            field_paths (Iterable[str, ...]): An iterable of field paths
                (``.``-delimited list of field names) to use as a projection
                of document fields in the query results.

        Returns:
            ~.firestore_v1.query.Query: A "projected" query. Acts as
            a copy of the current query, modified with the newly added
            projection.
        Raises:
            ValueError: If any ``field_path`` is invalid.
        """
    
    @abstractmethod
    def where(self, field_path, op_string, value) -> Query:
        """Filter the query on a field.

        See :meth:`~.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        Returns a new :class:`~.firestore_v1.query.Query` that
        filters on a specific field path, according to an operation (e.g.
        ``==`` or "equals") and a particular value to be paired with that
        operation.

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names) for the field to filter on.
            op_string (str): A comparison operation in the form of a string.
                Acceptable values are ``<``, ``<=``, ``==``, ``>=``
                and ``>``.
            value (Any): The value to compare the field against in the filter.
                If ``value`` is :data:`None` or a NaN, then ``==`` is the only
                allowed operation.

        Returns:
            ~.firestore_v1.query.Query: A filtered query. Acts as a
            copy of the current query, modified with the newly added filter.

        Raises:
            ValueError: If ``field_path`` is invalid.
            ValueError: If ``value`` is a NaN or :data:`None` and
                ``op_string`` is not ``==``.
        """
    
    @abstractmethod
    def order_by(self, field_path, direction="ASCENDING") -> Query:
        """Modify the query to add an order clause on a specific field.

        See :meth:`~.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        Successive :meth:`~.firestore_v1.query.Query.order_by` calls
        will further refine the ordering of results returned by the query
        (i.e. the new "order by" fields will be added to existing ones).

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names) on which to order the query results.
            direction (Optional[str]): The direction to order by. Must be one
                of :attr:`ASCENDING` or :attr:`DESCENDING`, defaults to
                :attr:`ASCENDING`.

        Returns:
            ~.firestore_v1.query.Query: An ordered query. Acts as a
            copy of the current query, modified with the newly added
            "order by" constraint.

        Raises:
            ValueError: If ``field_path`` is invalid.
            ValueError: If ``direction`` is not one of :attr:`ASCENDING` or
                :attr:`DESCENDING`.
        """
    
    @abstractmethod
    def limit(self, count) -> Query:
        """Limit a query to return a fixed number of results.

        If the current query already has a limit set, this will overwrite it.

        Args:
            count (int): Maximum number of documents to return that match
                the query.

        Returns:
            ~.firestore_v1.query.Query: A limited query. Acts as a
            copy of the current query, modified with the newly added
            "limit" filter.
        """
    
    @abstractmethod
    def offset(self, num_to_skip) -> Query:
        """Skip to an offset in a query.

        If the current query already has specified an offset, this will
        overwrite it.

        Args:
            num_to_skip (int): The number of results to skip at the beginning
                of query results. (Must be non-negative.)

        Returns:
            ~.firestore_v1.query.Query: An offset query. Acts as a
            copy of the current query, modified with the newly added
            "offset" field.
        """
    
    @abstractmethod
    def start_at(self, document_fields) -> Query:
        """Start query results at a particular document value.

        The result set will **include** the document specified by
        ``document_fields``.

        If the current query already has specified a start cursor -- either
        via this method or
        :meth:`~.firestore_v1.query.Query.start_after` -- this will
        overwrite it.

        When the query is sent to the server, the ``document_fields`` will
        be used in the order given by fields set by
        :meth:`~.firestore_v1.query.Query.order_by`.

        Args:
            document_fields (Union[~.firestore_v1.\
                document.DocumentSnapshot, dict, list, tuple]): a document
                snapshot or a dictionary/list/tuple of fields representing a
                query results cursor. A cursor is a collection of values that
                represent a position in a query result set.

        Returns:
            ~.firestore_v1.query.Query: A query with cursor. Acts as
            a copy of the current query, modified with the newly added
            "start at" cursor.
        """
    
    @abstractmethod
    def start_after(self, document_fields) -> Query:
        """Start query results after a particular document value.

        The result set will **exclude** the document specified by
        ``document_fields``.

        If the current query already has specified a start cursor -- either
        via this method or
        :meth:`~.firestore_v1.query.Query.start_at` -- this will
        overwrite it.

        When the query is sent to the server, the ``document_fields`` will
        be used in the order given by fields set by
        :meth:`~.firestore_v1.query.Query.order_by`.

        Args:
            document_fields (Union[~.firestore_v1.\
                document.DocumentSnapshot, dict, list, tuple]): a document
                snapshot or a dictionary/list/tuple of fields representing a
                query results cursor. A cursor is a collection of values that
                represent a position in a query result set.

        Returns:
            ~.firestore_v1.query.Query: A query with cursor. Acts as
            a copy of the current query, modified with the newly added
            "start after" cursor.
        """
    
    @abstractmethod
    def end_before(self, document_fields) -> Query:
        """End query results before a particular document value.

        The result set will **exclude** the document specified by
        ``document_fields``.

        If the current query already has specified an end cursor -- either
        via this method or
        :meth:`~.firestore_v1.query.Query.end_at` -- this will
        overwrite it.

        When the query is sent to the server, the ``document_fields`` will
        be used in the order given by fields set by
        :meth:`~.firestore_v1.query.Query.order_by`.

        Args:
            document_fields (Union[~.firestore_v1.\
                document.DocumentSnapshot, dict, list, tuple]): a document
                snapshot or a dictionary/list/tuple of fields representing a
                query results cursor. A cursor is a collection of values that
                represent a position in a query result set.

        Returns:
            ~.firestore_v1.query.Query: A query with cursor. Acts as
            a copy of the current query, modified with the newly added
            "end before" cursor.
        """
    
    @abstractmethod
    def end_at(self, document_fields) -> Query:
        """End query results at a particular document value.

        The result set will **include** the document specified by
        ``document_fields``.

        If the current query already has specified an end cursor -- either
        via this method or
        :meth:`~.firestore_v1.query.Query.end_before` -- this will
        overwrite it.

        When the query is sent to the server, the ``document_fields`` will
        be used in the order given by fields set by
        :meth:`~.firestore_v1.query.Query.order_by`.

        Args:
            document_fields (Union[~.firestore_v1.\
                document.DocumentSnapshot, dict, list, tuple]): a document
                snapshot or a dictionary/list/tuple of fields representing a
                query results cursor. A cursor is a collection of values that
                represent a position in a query result set.

        Returns:
            ~.firestore_v1.query.Query: A query with cursor. Acts as
            a copy of the current query, modified with the newly added
            "end at" cursor.
        """
    
    @abstractmethod
    def get(self, transaction=None):
        """Deprecated alias for :meth:`stream`."""
    
    @abstractmethod
    def stream(self, transaction=None) -> Iterable[DocumentSnapshot]:
        """Read the documents in the collection that match this query.

        This sends a ``RunQuery`` RPC and then returns an iterator which
        consumes each document returned in the stream of ``RunQueryResponse``
        messages.

        .. note::

           The underlying stream of responses will time out after
           the ``max_rpc_timeout_millis`` value set in the GAPIC
           client configuration for the ``RunQuery`` API.  Snapshots
           not consumed from the iterator before that point will be lost.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Args:
            transaction (Optional[~.firestore_v1.transaction.\
                Transaction]): An existing transaction that this query will
                run in.

        Yields:
            ~.firestore_v1.document.DocumentSnapshot: The next
            document that fulfills the query.
        """
    
    @abstractmethod
    def on_snapshot(self, callback):
        """Monitor the documents in this collection that match this query.

        This starts a watch on this query using a background thread. The
        provided callback is run on the snapshot of the documents.

        Args:
            callback(~.firestore.query.QuerySnapshot): a callback to run when
                a change occurs.

        Example:
            from google.cloud import firestore_v1

            db = firestore_v1.Client()
            query_ref = db.collection(u'users').where("user", "==", u'Ada')

            def on_snapshot(docs, changes, read_time):
                for doc in docs:
                    print(u'{} => {}'.format(doc.id, doc.to_dict()))

            # Watch this query
            query_watch = query_ref.on_snapshot(on_snapshot)

            # Terminate this watch
            query_watch.unsubscribe()
        """


class CollectionReference(Query, ABC):
    
    @property
    @abstractmethod
    def id(self) -> str:
        """The collection identifier.

        Returns:
            str: The last component of the path.
        """
        return self._path[-1]
    
    @property
    @abstractmethod
    def parent(self) -> Optional[DocumentReference]:
        """Document that owns the current collection.

        Returns:
            Optional[~.firestore_v1.document.DocumentReference]: The
            parent document, if the current collection is not a
            top-level collection.
        """
    
    @abstractmethod
    def document(self, document_id: Optional[str] = None) -> DocumentReference:
        """Create a sub-document underneath the current collection.

        Args:
            document_id (Optional[str]): The document identifier
                within the current collection. If not provided, will default
                to a random 20 character string composed of digits,
                uppercase and lowercase and letters.

        Returns:
            ~.firestore_v1.document.DocumentReference: The child
            document.
        """
    
    @abstractmethod
    def add(self, document_data, document_id=None) -> DocumentReference:
        """Create a document in the Firestore database with the provided data.

        Args:
            document_data (dict): Property names and values to use for
                creating the document.
            document_id (Optional[str]): The document identifier within the
                current collection. If not provided, an ID will be
                automatically assigned by the server (the assigned ID will be
                a random 20 character string composed of digits,
                uppercase and lowercase letters).

        Returns:
            Tuple[google.protobuf.timestamp_pb2.Timestamp, \
                ~.firestore_v1.document.DocumentReference]: Pair of

            * The ``update_time`` when the document was created (or
              overwritten).
            * A document reference for the created document.

        Raises:
            ~google.cloud.exceptions.Conflict: If ``document_id`` is provided
                and the document already exists.
        """
    
    @abstractmethod
    def list_documents(self, page_size=None) -> List[DocumentReference]:
        """List all subdocuments of the current collection.

        Args:
            page_size (Optional[int]]): The maximum number of documents
            in each page of results from this request. Non-positive values
            are ignored. Defaults to a sensible value set by the API.

        Returns:
            Sequence[~.firestore_v1.collection.DocumentReference]:
                iterator of subdocuments of the current collection. If the
                collection does not exist at the time of `snapshot`, the
                iterator will be empty
        """
    

class DocumentSnapshot(ABC):
    @property
    @abstractmethod
    def exists(self) -> bool:
        """Existence flag.

        Indicates if the document existed at the time this snapshot
        was retrieved.

        Returns:
            bool: The existence flag.
        """
      
    @property
    @abstractmethod
    def id(self) -> str:
        """The document identifier (within its collection).

        Returns:
            str: The last component of the path of the document.
        """
    
    @property
    @abstractmethod
    def reference(self) -> DocumentReference:
        """Document reference corresponding to document that owns this data.

        Returns:
            ~.firestore_v1.document.DocumentReference: A document
            reference corresponding to this document.
        """
    
    @abstractmethod
    def get(self, field_path) -> Any:
        """Get a value from the snapshot data.

        If the data is nested, for example:

        .. code-block:: python

           >>> snapshot.to_dict()
           {
               'top1': {
                   'middle2': {
                       'bottom3': 20,
                       'bottom4': 22,
                   },
                   'middle5': True,
               },
               'top6': b'\x00\x01 foo',
           }

        a **field path** can be used to access the nested data. For
        example:

        .. code-block:: python

           >>> snapshot.get('top1')
           {
               'middle2': {
                   'bottom3': 20,
                   'bottom4': 22,
               },
               'middle5': True,
           }
           >>> snapshot.get('top1.middle2')
           {
               'bottom3': 20,
               'bottom4': 22,
           }
           >>> snapshot.get('top1.middle2.bottom3')
           20

        See :meth:`~.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        A copy is returned since the data may contain mutable values,
        but the data stored in the snapshot must remain immutable.

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names).

        Returns:
            Any or None:
                (A copy of) the value stored for the ``field_path`` or
                None if snapshot document does not exist.

        Raises:
            KeyError: If the ``field_path`` does not match nested data
                in the snapshot.
        """
    
    @abstractmethod
    def to_dict(self) -> Optional[dict]:
        """Retrieve the data contained in this snapshot.

        A copy is returned since the data may contain mutable values,
        but the data stored in the snapshot must remain immutable.

        Returns:
            Dict[str, Any] or None:
                The data in the snapshot.  Returns None if reference
                does not exist.
        """


