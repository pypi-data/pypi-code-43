# coding=utf-8

from alas_tools.common.clients.client_base import ApiClientBase, EntityClientBase


class CoreClient(ApiClientBase):
    entity_endpoint_base_url = '/core'

    def get_mock_rut(self, full_name):
        params = {
            'full_name': full_name,
        }
        result= self.http_post_json(self.entity_endpoint_base_url + '/mock/get-rut', params)
        if result.response.status == 200:
            return result.content["rut"]

        return None

    def validate_matrix(self, structure_id):
        params = {
            'structure_id': structure_id,
        }
        result = self.http_post_json(self.entity_endpoint_base_url + '/comune/validate-matrix', params)
        if result.response.status == 200:
            return result.content["result"]

        return None


class GeographicCoverageActiveClient(EntityClientBase):
    entity_endpoint_base_url = '/management/geographic-coverages-active/'

    def __init__(self, country_code='cl', **kwargs):
        super(GeographicCoverageActiveClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'

    def validate_commune_active(self, structure_id=None):
        result = self.get_by_id(structure_id)
        if result.response.status == 200:
            return result.content

        return None


def normalize_str(s):
    replacements = (
        ("  ", " "),
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ü", "u"),
        ("ñ", "n"),
        ("Á", "A"),
        ("É", "E"),
        ("Í", "I"),
        ("Ó", "O"),
        ("Ú", "U"),
        ("Ü", "U"),
        ("Ñ", "N"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return str(s.lower())
