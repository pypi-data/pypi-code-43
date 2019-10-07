# coding=utf-8
from alas_tools.common.clients.core import CoreClient, GeographicCoverageActiveClient


class CoreUtils(object):

    @staticmethod
    def validate_matrix(config, structure_id=None):
        return CoreClient(**config).validate_matrix(structure_id)

    @staticmethod
    def validate_commune_active(config, structure_id=None):
        result = GeographicCoverageActiveClient(**config).get_by_id(structure_id)
        if result.response.status == 200:
            return result.content

        return None

    @staticmethod
    def get_mock_rut(config, full_name=None):
        result = CoreClient(**config).get_mock_rut(full_name)
        return result
