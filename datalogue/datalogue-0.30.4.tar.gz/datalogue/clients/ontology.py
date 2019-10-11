from typing import Optional, Union, List
from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.ontology import Ontology, ShareTarget
from datalogue.models.permission import Permission
from datalogue.utils import _parse_list
from datalogue.errors import DtlError
from uuid import UUID


class _OntologyClient:
    """
    Client to interact with the ontology
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/yggy"

    def create(self, ontology: Ontology) -> Union[DtlError, Ontology]:
        """
        Create :class:`Ontology` object given ontology object
        :return: :class:`Ontology` object, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + '/ontology/import', HttpMethod.POST, body=Ontology.as_payload(ontology))

        if isinstance(res, DtlError):
            return res
            
        return Ontology.from_payload(res)

    def get(self, ontology_id: UUID) -> Union[DtlError, Ontology]:
        """
        Get :class:`Ontology` object given ontology_id
        :return: :class:`Ontology` object, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}', HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Ontology.from_payload(res)

    def update(self, ontology_id: UUID, updated_ontology: Ontology) -> Union[DtlError, Ontology]:
        """
        Update :class:`Ontology` method that will replace the existing ontology.
        The structure of this ontology will replace the existing structure. Please make sure you include a full
        ontological structure and not just the changes/modifications
        :param ontology_id: UUID is the id of the ontology that you want to replace/modify/update.
        :param updated_ontology: Ontology object that will replace the existing ontology.
        :return: The updated Ontology if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}', HttpMethod.PUT, body=Ontology.as_payload(updated_ontology))

        if isinstance(res, DtlError):
            return res

        return Ontology.from_payload(res)

    def delete(self, ontology_id: UUID) -> Union[DtlError, bool]:
        """
        Delete :class:`Ontology` based on the given ontology_id
        :return: True if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}', HttpMethod.DELETE)
        if isinstance(res, DtlError):
            return res
        else:
            return True


    def share(self, ontology_id: UUID, target_id: UUID, target_type: ShareTarget, permission: Permission) -> Union[DtlError, bool]:
        """
        Share the given ontology with an specific user or group with the desired permission (Write or Read)

        :param ontology_id: UUID is the id of the ontology that you want to share
        :param target_id: UUID is the id of the User, the Group or Organization you want to share with (depending on the target_type param)
        :param target_type: String (`Group` or `User`) with whom you want to share the ontology. It can be a User, Group or Organization.
        :param permission: String (`Write` or `Read`) the permission you want to grant
        :return: True if successful, else returns :class:`DtlError`
        """

        body = Ontology.create_body_for_sharing(target_id, target_type, permission)
        if isinstance(body, DtlError):
            return body

        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}/share', HttpMethod.POST, body)
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def unshare(self, ontology_id: UUID, target_id: UUID, target_type: ShareTarget) -> Union[DtlError, bool]:
        """
        Unshare the given ontology from an specific user or group. That User/Group won't be able to access that ontology
        any more.

        :param ontology_id: UUID is the id of the ontology that you want to unshare
        :param target_id: UUID is the id of the User, the Group or Organization you want to unshare from (depending on the target_type param)
        :param target_type: String (`Group` or `User`) with whom you want to unshare the ontology. It can be a User, Group or Organization.
        :return: True if successful, else returns :class:`DtlError`
        """
        body = Ontology.create_body_for_sharing(target_id, target_type, Permission.NoPermission)

        if isinstance(body, DtlError):
            return body

        res = self.http_client.make_authed_request(self.service_uri + f'/ontology/{str(ontology_id)}/share',
                                                   HttpMethod.POST, body)
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Ontology]]:
        """
        List the ontologies

        TODO Pagination

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available Ontologies or an error message as a string

        """
        res = self.http_client.make_authed_request(self.service_uri + f'/ontologies', HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return _parse_list(Ontology.from_payload)(res)

