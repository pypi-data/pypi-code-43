from mock_base._firestore.__firestore_abstract import Client, Query, DocumentReference, DocumentSnapshot, CollectionReference
from ._fx import error_path_not_is_document, error_path_not_is_collection
from ._db import Col, Doc, _DatabaseRaw
from typing import List, Optional, Iterable
from collections import OrderedDict


class MockDocument(DocumentReference):
    
    def __init__(self, path: List[str], database: _DatabaseRaw):
        self._database = database
        self.__path: List[str] = path
    
    @property
    def path(self) -> str:
        return ".".join(self.__path)
    
    @property
    def id(self) -> str:
        return self.__path[-1]
    
    @property
    def parent(self) -> CollectionReference:
        return MockCollection(self.__path[:-2], self._database)
    
    def collection(self, collection_id) -> CollectionReference:
        e = self._database.search_path(self.__path, make=True)
        if isinstance(e, Doc):
            col = Col()
            col.name = collection_id
            e.cols.append(col)
        return MockCollection(self.__path + [collection_id], self._database)
    
    def create(self, document_data):
        if self.get().exists is True:
            raise Exception("Document already exists")
        self.set(document_data, merge=False)
    
    def set(self, document_data, merge=False):
        e = self._database.search_path(self.__path, make=True)
        if isinstance(e, Doc):
            
            if merge is False:
                e.data = document_data
            else:
                if e.data is not None:
                    e.data = OrderedDict({**e.data, **document_data})
                else:
                    e.data = document_data
        else:
            raise Exception(error_path_not_is_document(self.__path))
    
    def update(self, field_updates, option=None):
        
        if self.get().exists is False:
            self.set(field_updates, merge=True)
        else:
            raise Exception("Document not found")
    
    def delete(self, option=None):
        ref = self._database.search_path(self.__path[:-1])
        doc = self._database.search_path(self.__path)
        if isinstance(ref, Col) and isinstance(doc, Doc):
            for index, d in enumerate(ref.docs):
                if d.name == doc.name:
                    ref.docs.pop(index)
    
    def get(self, field_paths=None, transaction=None) -> DocumentSnapshot:
        return MockSnapshot(self.__path, self._database)
    
    def collections(self, page_size=None) -> List[CollectionReference]:
        e = self._database.search_path(self.__path, make=False)
        if e is None:
            return []
        if isinstance(e, Doc):
            return [MockCollection(self.__path + [i.name], self._database) for i in e.cols]
        else:
            raise Exception(error_path_not_is_document(self.__path))
    
    def on_snapshot(self, callback):
        raise Exception("Not implemented")


class MockClient(Client):
    
    def __init__(self):
        self._database = _DatabaseRaw()
    
    def collection(self, *collection_path) -> CollectionReference:
        path: List[str] = []
        
        for i in collection_path:
            path += str(i).split("/")
        return MockCollection(path, self._database)
    
    def document(self, *document_path) -> DocumentReference:
        path: List[str] = []
        for i in document_path:
            path += str(i).split("/")
        return MockDocument(path, self._database)
    
    @staticmethod
    def field_path(*field_names):
        raise Exception("Not implemented")
    
    def get_all(self, references, field_paths=None, transaction=None):
        raise Exception("Not implemented")
    
    def collections(self) -> List[CollectionReference]:
        cols: List[CollectionReference] = []
        for k in self._database.database:
            cols.append(MockCollection([k.name], self._database))
        
        return cols
    
    def transaction(self, **kwargs) -> Client:
        return self


class MockSnapshot(DocumentSnapshot):
    
    def __init__(self, path: List[str], database: _DatabaseRaw):
        assert database is not None, "database raw is None"
        self._database: _DatabaseRaw = database
        self.__path: List[str] = path
    
    @property
    def exists(self) -> bool:
        e = self._database.search_path(self.__path, make=False)
        if e is None:
            return False
        return True
    
    @property
    def id(self) -> str:
        return self.__path[-1]
    
    @property
    def reference(self) -> DocumentReference:
        return MockDocument(self.__path, self._database)
    
    def get(self, field_path):
        e = self._database.search_path(self.__path, make=False)
        if e is None:
            return None
        
        if isinstance(e, Doc):
            s = field_path.split(".")
            if e.data is not None:
                result = e.data
                for i in s:
                    result = result.get(i, {})
                return result
            else:
                return None
        else:
            raise Exception(error_path_not_is_document(self.__path))
    
    def to_dict(self) -> Optional[dict]:
        
        e = self._database.search_path(self.__path, make=False)
        
        if e is None:
            return None
        if isinstance(e, Doc):
            if e is None:
                return None
            if e.data is not None:
                return e.data
            else:
                return None
        else:
            raise Exception(error_path_not_is_document(self.__path))


class MockQuery(Query):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"
    
    def __init__(self, col: Col, path: List[str], database: _DatabaseRaw):
        self.__col = Col()
        self.__col.docs = col.docs.copy()
        self.__path = path
        self._database = database
    
    def select(self, field_paths) -> Query:
        col = Col()
        col.docs = self.__col.docs.copy()
        for doc in col.docs:
            d: OrderedDict = OrderedDict()
            for key in field_paths:
                d.update({key: doc[key]})
            doc.data = d
        
        return MockQuery(col, self.__path, self._database)

    def where(self, field_path, op_string, value) -> Query:
        col = Col()
        docs = self.__col.docs.copy()
        for doc in docs:
            if type(doc[field_path]) == type(value):
                if op_string == "<=" and doc[field_path] <= value:
                    col.docs.append(doc)
                if op_string == "==" and doc[field_path] == value:
                    col.docs.append(doc)
                if op_string == ">=" and doc[field_path] >= value:
                    col.docs.append(doc)
                if op_string == ">" and doc[field_path] > value:
                    col.docs.append(doc)
                if op_string == "<" and doc[field_path] < value:
                    col.docs.append(doc)
                if op_string == "!=" and doc[field_path] != value:
                    col.docs.append(doc)
                    
            if isinstance(doc[field_path], list):
                if op_string == "array_contains" and value in doc[field_path]:
                    col.docs.append(doc)
        return MockQuery(col, self.__path, self._database)
        
    def order_by(self, field_path, direction=ASCENDING) -> Query:
        col = Col()
        docs = self.__col.docs.copy()
        
        col.docs = sorted(docs, key=lambda x: x[field_path], reverse=direction == MockQuery.DESCENDING)
        
        return MockQuery(col, self.__path, self._database)
        
    def limit(self, count) -> Query:
        col = Col()
        col.docs = self.__col.docs.copy()
        if len(col.docs) >= count:
            col.docs = col.docs[:count]
            
        return MockQuery(col, self.__path, self._database)

    def offset(self, num_to_skip) -> Query:
        if num_to_skip >= len(self.__col.docs):
            return MockQuery(Col(), self.__path, self._database)
        else:
            col = Col()
            col.docs = self.__col.docs.copy()
            col.docs = col.docs[num_to_skip:]
            return MockQuery(col, self.__path, self._database)

    def __search_position(self, document_fields) -> int:
        docs = self.__col.docs.copy()
        init = 0
        for i in docs:
            if i.name != document_fields:
                init += 1
            else:
                break
        return init

    def start_at(self, document_fields) -> Query:
        col = Col()
        init = self.__search_position(document_fields)
        col.docs = self.__col.docs.copy()[init:]
        return MockQuery(col, self.__path, self._database)

    def start_after(self, document_fields) -> Query:
        col = Col()
        init = self.__search_position(document_fields)
        col.docs = self.__col.docs.copy()[init+1:]
        return MockQuery(col, self.__path, self._database)

    def end_before(self, document_fields) -> Query:
        col = Col()
        init = self.__search_position(document_fields)
        col.docs = self.__col.docs.copy()[:init]
        return MockQuery(col, self.__path, self._database)

    def end_at(self, document_fields) -> Query:
        col = Col()
        init = self.__search_position(document_fields)
        if len(self.__col.docs) > init:
            init += 1
        col.docs = self.__col.docs.copy()[:init]
        return MockQuery(col, self.__path, self._database)

    def get(self, transaction=None):
        """DEPRECATED"""
        return self.stream()

    def stream(self, transaction=None) -> Iterable[DocumentSnapshot]:
        for i in self.__col.docs:
            yield MockSnapshot(self.__path + [i.name], self._database)

    def on_snapshot(self, callback):
        pass


class MockCollection(MockQuery, CollectionReference):
    
    def __init__(self, path: List[str], database: _DatabaseRaw):
        assert database is not None, "database Raw is None"
        self._database = database
        e = self._database.search_path(path, make=False)
        if isinstance(e, Col):
            super().__init__(e, path, database)
        else:
            raise error_path_not_is_collection(path, message=type(e))
        self.__path: List[str] = path
        
    @property
    def id(self) -> str:
        return self.__path[-1]
    
    @property
    def parent(self) -> Optional[DocumentReference]:
        if len(self.__path) > 2:
            return MockDocument(self.__path[:-1], self._database)
        else:
            return None
    
    def document(self, document_id: Optional[str] = None) -> DocumentReference:
        if document_id is None:
            raise Exception("document id is None")
        else:
            return MockDocument(self.__path + [document_id], self._database)
    
    def add(self, document_data, document_id=None) -> DocumentReference:
        doc_id = document_id
        if doc_id is None:
            doc_id = self._database.random_id()
        
        m = MockDocument(self.__path + [doc_id], self._database)
        m.set(document_data)
        return m
    
    def list_documents(self, page_size=None) -> List[DocumentReference]:
        e = self._database.search_path(self.__path)
        if isinstance(e, Col):
            result: List[DocumentReference] = [MockDocument(self.__path + [i.name], self._database) for i in e.docs]
            
            if page_size is None:
                return result
            else:
                if len(result) < page_size:
                    return result
                else:
                    return result[:page_size]
        
        else:
            raise Exception(error_path_not_is_collection(self.__path))
