import boto3
import uuid
from vulcan.aws.services._session import AWSSession


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
        return cert_arn
