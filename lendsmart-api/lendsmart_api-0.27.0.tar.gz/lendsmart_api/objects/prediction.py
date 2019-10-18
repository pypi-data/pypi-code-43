from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class PredictionChunk(Base):

    api_endpoint = '/prediction_chunks'

    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "status": Property(),
        "mergeable": Property(),
        "location": Property(),
        "document_id": Property(),
        "inference_considered_valid": Property(),
    }

class PredictionSegment(Base):

    api_endpoint = '/prediction_segements'

    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "chunk_segments": Property(mutable=True, filterable=True),
        "status": Property(),
    }

class PredictionWorkflow(Base):
    api_endpoint = 'prediction_workflows'
    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "mergeable": Property(),
        "inference_considered_valid": Property(),
        "status": Property()
    }
