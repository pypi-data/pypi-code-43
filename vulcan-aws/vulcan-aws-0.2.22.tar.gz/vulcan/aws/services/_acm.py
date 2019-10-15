import boto3
import uuid
from navio.aws.services._session import AWSSession


class AWSACM(AWSSession):

    def __init__(self, **kwargs):
        super(
            self.__class__,
            self
        ).__init__(kwargs['profile_name'])

    def find_cert_arn(self, **kwargs):
        cert_arn = None

        if 'domain_name' not in kwargs:
            raise Exception('Argument missing: domain_name')

        client = self.client('acm')

        paginator = client.get_paginator('list_certificates')

        page_iterator = paginator.paginate(
            CertificateStatuses=['ISSUED']
        )
        for page in page_iterator:
            if 'CertificateSummaryList' in page:
                for cert in page['CertificateSummaryList']:
                    if cert['DomainName'] == kwargs['domain_name']:
                        if cert_arn is not None:
                            raise Exception('Multiple certificates ''with same domain name.')
                        else:
                            cert_arn = cert['CertificateArn']

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
