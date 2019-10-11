import boto3
import uuid
from navio.aws.services._session import AWSSession


class AWSACM(AWSSession):

    def __init__(self, **kwargs):
        super(
            self.__class__,
            self
        ).__init__(kwargs['profile_name'])

    def request_via_dns(self, **kwargs):
        if 'domain_name' not in kwargs:
            raise Exception('Argument missing: domain_name')

        if 'alternative_names' not in kwargs:
            raise Exception('Argument missing: alternative_names')

        client = self.client('acm')

        resp = client.request_certificate(
            DomainName=kwargs.get('domain_name'),
            SubjectAlternativeNames=kwargs.get('alternative_names'),
            ValidationMethod='DNS',
            IdempotencyToken=uuid.uuid4()
        )

        return resp

    def get_dns_validation_options(self, **kwargs):
        if 'certificate_arn' not in kwargs:
            raise Exception('Argument missing: certificate_arn')

        client = self.client('acm')

        resp = client.describe_certificate(
            CertificateArn=certificate_arn
        )

        return resp.get('Certificate') \
                   .get('DomainValidationOptions')[0] \
                   .get('ResourceRecord')
