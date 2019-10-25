import shutil
from CheKnife import pki
import os
from unittest import TestCase
from .aux_data import AUX_DATA_PATH
from .aux_data.aux_variables import CSR_EXAMPLE

# nosetests --with-coverage --cover-inclusive --cover-package=CheKnife --cover-html tests/test_pki.py


class TestPKI(TestCase):
    working_dir = os.path.join(AUX_DATA_PATH, 'test_pki')

    def test_gen_csr(self):

        server_dn = pki.DistinguishedName('ES', 'Madrid', 'Madrid', 'Empire', 'example.com',
                                      subject_alt_names=['www.example.com', 'web.example.com'])
        server_cert = pki.ServerCertificate(server_dn, working_dir=self.working_dir)
        server_cert.gen_key()
        server_cert.gen_csr()
        self.assertIn('Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = example.com, subjectAltName = '
                      '"DNS.1=www.example.com,DNS.2=web.example.com"', server_cert.check_csr())

    def test_create_server_certificate_from_scratch(self):
        ca = self.ca_creation()
        intermediary_ca = self.intermediary_ca_creation(ca)
        server_dn = pki.DistinguishedName('ES', 'Madrid', 'Madrid', 'Empire', 'example.com',
                                      subject_alt_names=['www.example.com', 'web.example.com'])
        server_cert = pki.ServerCertificate(server_dn, intermediary_ca, working_dir=self.working_dir)
        server_cert.gen_cert()
        self.assertIn('Issuer: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = IntermediateCA', server_cert.check_crt())
        self.assertIn('Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = example.com, subjectAltName = '
                      '"DNS.1=www.example.com,DNS.2=web.example.com"', server_cert.check_crt())

    def test_sign_csr(self):
        ca = self.ca_creation()
        intermediary_ca = self.intermediary_ca_creation(ca)
        server_cert = pki.ServerCertificate(csr=CSR_EXAMPLE, ca=intermediary_ca, working_dir=self.working_dir)
        server_cert.sign_csr()
        self.assertIn('Issuer: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = IntermediateCA', server_cert.check_crt())
        self.assertIn(
            'Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = example2.com, subjectAltName = "DNS.1=www.example2.com,DNS.2=web.example2.com"',
            server_cert.check_crt())

    def test_create_server_certificate_with_existing_intermediate_ca(self):
        ca = self.ca_creation()
        self.intermediary_ca_creation(ca)
        intermediary_ca = pki.IntermediaryCAFactory().from_file(os.path.join(
            self.working_dir, 'CA/certs/IntermediateCA.crt'))
        server_dn = pki.DistinguishedName('ES', 'Madrid', 'Madrid', 'Empire', 'example.com',
                                          subject_alt_names=['www.example.com', 'web.example.com'])
        server_cert = pki.ServerCertificate(server_dn, intermediary_ca, working_dir=self.working_dir)
        server_cert.gen_cert()
        self.assertIn('Issuer: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = IntermediateCA', server_cert.check_crt())
        self.assertIn('Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = example.com, subjectAltName = "DNS.1=www.example.com,DNS.2=web.example.com"', server_cert.check_crt())

    def intermediary_ca_creation(self, ca):
        intermediary_dn = pki.DistinguishedName('ES', 'Madrid', 'Madrid', 'Empire', 'IntermediateCA')
        intermediary_ca = pki.IntermediaryCA(intermediary_dn, ca, working_dir=self.working_dir)
        intermediary_ca.gen_ca()
        self.assertIn('Issuer: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = RootCA', intermediary_ca.check_crt())
        self.assertIn('Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = IntermediateCA',
                      intermediary_ca.check_crt())
        return intermediary_ca

    def ca_creation(self):
        dn = pki.DistinguishedName('ES', 'Madrid', 'Madrid', 'Empire', 'RootCA')
        ca = pki.CA(dn, working_dir=self.working_dir)
        ca.gen_ca()
        self.assertIn('Issuer: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = RootCA', ca.check_crt())
        self.assertIn('Subject: C = ES, ST = Madrid, L = Madrid, O = Empire, CN = RootCA', ca.check_crt())
        return ca

    def tearDown(self):
        # try:
        shutil.rmtree(self.working_dir)
        # except OSError:
        #     pass