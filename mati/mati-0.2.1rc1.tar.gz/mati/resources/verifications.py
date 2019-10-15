from dataclasses import dataclass
from typing import ClassVar, List

from ..types import VerificationDocument, VerificationDocumentStep
from .base import Resource


@dataclass
class Verification(Resource):
    _endpoint: ClassVar[str] = '/api/v1/verifications'
    _token_score: ClassVar[str] = 'identity'

    id: str
    expired: bool
    steps: list
    documents: List[VerificationDocument]
    hasProblem: bool
    computed: dict
    metadata: dict

    @classmethod
    def retrieve(cls, verification_id: str) -> 'Verification':
        endpoint = f'{cls._endpoint}/{verification_id}'
        resp = cls._client.get(endpoint, token_score=cls._token_score)
        docs = []
        for doc in resp['documents']:
            verification_doc = VerificationDocument(**doc)
            steps = []
            for step in doc['steps']:
                steps.append(VerificationDocumentStep(**step))
            verification_doc.steps = steps
            docs.append(verification_doc)
        resp['documents'] = docs
        return cls(**resp)
