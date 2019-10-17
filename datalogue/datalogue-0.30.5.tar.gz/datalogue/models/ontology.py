from typing import Dict, List, Optional, Union
from uuid import UUID
import itertools

from datalogue.errors import _enum_parse_error, DtlError
from datalogue.models.permission import Permission
from datalogue.utils import _parse_list, SerializableStringEnum


class ShareTarget(SerializableStringEnum):
    User = "User"
    Group = "Group"
    Organization = "Organization"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("share target", s))

    @staticmethod
    def share_target_from_str(string: str) -> Union[DtlError, 'ShareTarget']:
        return SerializableStringEnum.from_str(ShareTarget)(string)


class OntologyNode:
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 children: List['OntologyNode'] = [],
                 id: Optional[UUID] = None):

        if not isinstance(name, str):
            raise DtlError("name should be string in OntologyNode")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in OntologyNode")

        if not isinstance(children, List):
            raise DtlError("children should be list in OntologyNode")

        if id is not None and not isinstance(id, UUID):
            raise DtlError("id should be uuid in OntologyNode")

        self.name = name
        self.description = description
        self.children = children
        self.id = id

    def __eq__(self, other: 'OntologyNode'):
        if isinstance(self, other.__class__):
            return (self.name == other.name and
                    self.description == other.description and
                    self.children == other.children and
                    self.id == other.id)
        return False


    def __repr__(self):
        return f'{self.__class__.__name__}(id: {self.id}, name: {self.name!r})'

    @staticmethod
    def as_payload(ontology_node: 'OntologyNode') -> Union[DtlError, dict]:
        payload = {
            "name": ontology_node.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology_node.children))
        }

        if ontology_node.id is not None:
            payload["node_id"] = str(ontology_node.id)

        if ontology_node.description is not None:
            payload["description"] = ontology_node.description

        return payload

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, 'OntologyNode']:
        id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        children = payload.get("children")
        if children is None:
            children = []
        else:
            children = _parse_list(OntologyNode.from_payload)(children)
        return OntologyNode(name, description, children, id=id)


class Ontology:
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 tree: List[OntologyNode] = [],
                 id: Optional[UUID] = None):

        if not isinstance(name, str):
            raise DtlError("name should be string in Ontology")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in Ontology")

        if not isinstance(tree, List):
            raise DtlError("tree should be list in Ontology")

        if id is not None and not isinstance(id, UUID):
            raise DtlError("id should be uuid in Ontology")

        self.name = name
        self.description = description
        self.tree = tree
        self.id = id



    def __eq__(self, other: 'Ontology'):
        if isinstance(self, other.__class__):
            return (self.name == other.name and
                    self.description == other.description and
                    self.tree == other.tree and
                    self.id == other.id)
        return False

    def __repr__(self):
        def print_nodes(tree, output=[], level=0):
            for n in tree:
                padding = '   ' * level
                if level == 0:
                    output.append(padding + n.name)
                else:
                    output.append(padding + '|___' + n.name)
                for c in n.children:
                    print_nodes([c], output, level=level+1)
            return output

        first_line = f'Ontology(id: {self.id}, name: {self.name!r}, description: {self.description!r})' + '\n'
        return '\n'.join(print_nodes(self.tree, [first_line]))

    def leaves(self) -> List[OntologyNode]:
        def iterate(node: OntologyNode) -> List[OntologyNode]:
            if not node.children:
                return [ node ]
            else:
                return list(itertools.chain(*map(lambda n: iterate(n), node.children)))

        return list(itertools.chain(*map(lambda n: iterate(n), self.tree)))

    @staticmethod
    def as_payload(ontology: 'Ontology') -> Union[DtlError, dict]:
        payload = {
            "name": ontology.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology.tree))
        }

        if ontology.description is not None:
            payload["description"] = ontology.description

        return payload

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, 'Ontology']:
        id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        tree = payload.get("tree")
        if tree is None:
            tree = []
        else:
            tree = _parse_list(OntologyNode.from_payload)(payload["tree"])
        return Ontology(name, description, tree, id=id)

    @staticmethod
    def create_body_for_sharing(target_id: UUID, target_type: ShareTarget, permission: Permission) -> Dict:

        if not isinstance(target_type, ShareTarget):
             return DtlError(f"'{target_type}' should be a type of '{ShareTarget.__name__}' and must be in: {list(map(str, ShareTarget))}")

        if not isinstance(permission, Permission):
            return DtlError(f"'{permission}' should be a type of '{Permission.__name__}' and must be in: {list(map(str, Permission))}")

        body = {}

        body["organizations"] = None
        body["groups"] = None
        body["users"] = None

        if target_type == ShareTarget.User:
            body["users"] = {str(target_id): permission.value}
        elif target_type == ShareTarget.Group:
            body["groups"] = {str(target_id): permission.value}
        elif target_type == ShareTarget.Organization:
            body["organizations"] = {str(target_id): permission.value}
        return body


    @staticmethod
    def create_body_for_sharing(target_id: UUID, target_type: ShareTarget, permission: Permission) -> Union[Dict,
                                                                                                            DtlError]:

        if not isinstance(target_type, ShareTarget):
            return DtlError(
                f"'{target_type}' should be a type of '{ShareTarget.__name__}' and must be in: {list(map(str, ShareTarget))}")

        if not isinstance(permission, Permission):
            return DtlError(
                f"'{permission}' should be a type of '{Permission.__name__}' and must be in: {list(map(str, Permission))}")

        body = {}

        body["organizations"] = None
        body["groups"] = None
        body["users"] = None

        if target_type == ShareTarget.User:
            body["users"] = {str(target_id): permission.value}
        elif target_type == ShareTarget.Group:
            body["groups"] = {str(target_id): permission.value}
        elif target_type == ShareTarget.Organization:
            body["organizations"] = {str(target_id): permission.value}
        return body


class DataRef:
    def __init__(self, node: OntologyNode, path_list: List[List[str]]):
        self.node = node
        self.path_list = path_list
