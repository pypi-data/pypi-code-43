import re
import os
import subprocess
from CheKnife.paths import mktree, mv
from CheKnife.errors import PKIFileExistsError, PKIError
from CheKnife.hashing import textmd5sum


class OpenSSL(object):
    algorithm = 'sha256'

    def __init__(self, openssl='/usr/bin/openssl'):
        self.openssl = openssl

    def __call__(self, *args):

        cmdline = [self.openssl] + list(*args)
        return subprocess.check_output(cmdline, stderr=subprocess.STDOUT).decode('utf-8')

    def gen_key(self, key_path, key_size):
        self.raise_if_exists(key_path)
        cmd = ['genrsa', '-out', key_path, key_size]
        return self.__call__(cmd)

    def gen_csr(self, key_path, csr_path, DN):
        self.raise_if_exists(csr_path)
        cmd = ['req', '-new', '-' + self.algorithm, '-key', key_path, '-out', csr_path, '-subj', DN]
        return self.__call__(cmd)

    def sign_csr(self, csr_path, crt_path, days, *args):
        self.raise_if_exists(crt_path)
        cmd = ['x509', '-req', '-in', csr_path, '-out', crt_path, '-days', days] + list(args)
        return self.__call__(cmd)

    def check_key(self, key_path):
        cmd = ['rsa', '-check', '-in', key_path]
        return self.__call__(cmd)

    def check_csr(self, csr_path):
        cmd = ['req', '-text', '-noout', '-verify', '-in', csr_path]
        return self.__call__(cmd)

    def check_crt(self, crt_path):
        cmd = ['x509', '-text', '-noout', '-in', crt_path]
        return self.__call__(cmd)

    def pem2pkcs12(self, crt_path, key_path, ca_path, pfx_path):
        cmd = ['pkcs12', '-export', '-in', crt_path, '-inkey', key_path, '-certfile', ca_path, '-out', pfx_path]
        return self.__call__(cmd)

    def pkcs122pem(self, pfx_path, pem_path):
        cmd = ['pkcs12', '-in', pfx_path, '-out', pem_path, '-nodes']
        return self.__call__(cmd)

    def pem2der(self, pem_path, der_path):
        cmd = ['x509', '-outform', 'der', '-in', pem_path, '-out', der_path]
        return self.__call__(cmd)

    def der2pem(self, der_path, pem_path):
        cmd = ['x509', '-inform', 'der', '-in', der_path, '-out', pem_path]
        return self.__call__(cmd)

    def check_connect(self, host, port=443):
        cmd = [self.openssl, 's_client', '-connect', '{}:{}'.format(host, port), '-state', '-debug']
        openssl = subprocess.Popen(' '.join(cmd), shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = openssl.communicate(b'GET /')
        return stdout.decode('utf-8'), stderr.decode('utf-8')

    @staticmethod
    def raise_if_exists(file_path):
        if os.path.exists(file_path):
            raise PKIFileExistsError('Already exits {}.\nRemove it and run again.'.format(file_path))


"""
from CheKnife.pki import DistinguishedNameFactory, OpenSSL
f = DistinguishedNameFactory()
f.from_csr('/home/rafa/PycharmProjects/Misc/CheKnife/test_ca/5beebbd7b1aab791c434dd1dcd5481d6.csr')
OpenSSL()
"""
class DistinguishedNameFactory(object):
    openssl = OpenSSL()

    field_names = {
        'CN': 'common_name',
        'L': 'locality_name',
        'ST': 'state_or_province_name',
        'O': 'organization_name',
        'OU': 'organizational_unit_name',
        'C': 'country_name',
        'emailAddress': 'email',
        'subjectAltName': 'subject_alt_names'
    }

    def from_crt(self, crt_path):
        cert_info = self.openssl.check_crt(crt_path)
        subject_line = re.findall(r'Subject:.+', cert_info)[0]
        return self.from_subject_line(subject_line)

    def from_csr(self, csr_path):
        csr_info = self.openssl.check_csr(csr_path)
        subject_line = re.findall(r'Subject:.+', csr_info)[0]
        return self.from_subject_line(subject_line)

    def from_subject_line(self, subject_line):
        kwargs = self.parse_subject_line(subject_line)
        return DistinguishedName(**kwargs)

    def parse_subject_line(self, subject_line):
        parsed = {}
        items = subject_line.replace('Subject:', '').replace(' ', '').split(',')
        for item in items:
            if item.startswith('subjectAltName') or item.startswith('DNS'):
                parsed = self.subject_alt_names(item, parsed)
            else:
                item_split = item.split('=')
                parsed.update({self.field_names[item_split[0]]: item_split[1]})
        return parsed

    def subject_alt_names(self, item, parsed):
        item = item.replace('subjectAltName=', '').replace('"', '')
        alt_name = item.split('=')[1]
        parsed.setdefault(self.field_names['subjectAltName'], []).append(alt_name)
        return parsed


class DistinguishedName(object):
    def __init__(self, country_name=None, locality_name=None, state_or_province_name=None, organization_name=None,
                 common_name=None, organizational_unit_name=None, email=None, subject_alt_names=None):
        self.CN = common_name
        self.C = country_name
        self.ST = state_or_province_name
        self.L = locality_name
        self.O = organization_name
        self.OU = organizational_unit_name
        self.emailAddress = email
        self.subjectAltName = subject_alt_names
        self.DN = self.generate_dn()

    def generate_dn(self):
        attributes = ['C', 'ST', 'L', 'O', 'CN', 'emailAddress']
        dn = ''.join('/{}={}'.format(attribute, getattr(self, attribute)) for attribute in attributes
                     if getattr(self, attribute))
        dn = self.add_subject_alt_names(dn)
        return dn

    def add_subject_alt_names(self, dn):
        if isinstance(self.subjectAltName, list):
            dn += '/subjectAltName='
            count = 0
            for alt_name in self.subjectAltName:
                count += 1
                if count > 1:
                    dn += ',DNS.{}={}'.format(count, alt_name)
                else:
                    dn += 'DNS.{}={}'.format(count, alt_name)
        return dn

    def __unicode__(self):
        return self.DN

    @property
    def file_friendly_cn(self):
        # TODO: Remove non ascii chars
        return self.CN.replace(' ', '_')


class Certificate(object):
    openssl = OpenSSL()
    crt_ext = '.crt'
    key_ext = '.key'
    csr_ext = '.csr'
    srl_ext = '.srl'
    path_attrs = ['key_path', 'csr_path', 'crt_path', 'srl_path']

    def create_dirs(self):
        for attr in self.path_attrs:
            if getattr(self, attr, None):
                mktree(os.path.dirname(getattr(self, attr)))

    def check_crt(self):
        info = self.openssl.check_crt(getattr(self, 'crt_path'))
        return info

    def check_csr(self):
        info = self.openssl.check_csr(getattr(self, 'csr_path'))
        return info


class CA(Certificate):
    def __init__(self, dn, key_size=4096, days=3650, working_dir='.', **kwargs):
        self.days = str(days)
        self.key_path = kwargs.get('key_path', os.path.join(working_dir, 'CA', 'private', dn.file_friendly_cn + '.key'))
        self.csr_path = kwargs.get('csr_path', os.path.join(working_dir, 'CA', 'csr', dn.file_friendly_cn + '.csr'))
        self.crt_path = kwargs.get('crt_path', os.path.join(working_dir, 'CA', 'certs', dn.file_friendly_cn + self.crt_ext))
        self.key_size = str(key_size)
        self.dn = dn
        self.create_dirs()

    def _gen_key(self):
        self.openssl.gen_key(self.key_path, self.key_size)

    def _gen_csr(self):
        self.openssl.gen_csr(self.key_path, self.csr_path, self.dn.DN)

    def _sign_csr(self):
        args = ['-signkey', self.key_path]
        self.openssl.sign_csr(self.csr_path, self.crt_path, self.days, *args)

    def gen_ca(self):
        self._gen_key()
        self._gen_csr()
        self._sign_csr()


class IntermediaryCA(CA):
    def __init__(self, dn, ca, key_size=4096, days=3650, working_dir='.', **kwargs):
        self.ca = ca
        self.srl_path = os.path.join(working_dir, 'CA', 'srl', dn.file_friendly_cn + '.srl')
        super(IntermediaryCA, self).__init__(dn, key_size=key_size, days=days, working_dir=working_dir, **kwargs)

    def _sign_csr(self):
        args = ['-CA', self.ca.crt_path,
                '-CAkey', self.ca.key_path,
                '-CAcreateserial', '-CAserial', self.srl_path,
                '-' + self.openssl.algorithm]

        self.openssl.sign_csr(self.csr_path, self.crt_path, self.days, *args)


class CAFactory(object):
    dn_factory = DistinguishedNameFactory()
    openssl = OpenSSL()

    def from_file(self, ca_path):
        ca_dn = self.dn_factory.from_crt(ca_path)
        ca_working_dir = self.working_dir(ca_path)
        return CA(ca_dn, working_dir=ca_working_dir)

    @staticmethod
    def working_dir(ca_path):
        return os.path.dirname(os.path.dirname(os.path.dirname(ca_path)))


class IntermediaryCAFactory(object):
    dn_factory = DistinguishedNameFactory()
    openssl = OpenSSL()

    def from_file(self, intermediary_ca_path, ca_path=None):

        root_ca = self.get_root_ca(ca_path, intermediary_ca_path)
        intermediary_ca_dn = self.dn_factory.from_crt(intermediary_ca_path)
        intermediary_ca_working_dir = self.working_dir(intermediary_ca_path)

        intermediary_ca = IntermediaryCA(intermediary_ca_dn, root_ca, working_dir=intermediary_ca_working_dir)
        return intermediary_ca

    def get_root_ca(self, ca_path, intermediary_ca_path):
        if ca_path:
            return CAFactory().from_file(ca_path)
        else:
            ca_dn = self.get_root_ca_dn(ca_path, intermediary_ca_path)

            return CA(ca_dn, working_dir=self.working_dir(intermediary_ca_path))

    def get_dn(self, intermediary_ca_path):
        intermediary_ca_dn = self.dn_factory.from_crt(intermediary_ca_path)
        return intermediary_ca_dn

    def get_root_ca_dn(self, ca_path, intermediary_ca_path):
        if ca_path:
            ca_dn = self.dn_factory.from_crt(ca_path)
        else:
            ca_dn = self.ca_dn_from_intermediary_ca(intermediary_ca_path)
        return ca_dn

    def ca_dn_from_intermediary_ca(self, intermediary_ca_path):
        cert_info = self.openssl.check_crt(intermediary_ca_path)
        subject_line = re.findall(r'Issuer:.+', cert_info)[0].replace('Issuer:', '')
        ca_dn = self.dn_factory.from_subject_line(subject_line)
        return ca_dn

    @staticmethod
    def working_dir(ca_path):
        return os.path.dirname(os.path.dirname(os.path.dirname(ca_path)))


class ServerCertificate(Certificate):
    def __init__(self, dn=None, ca=None, csr=None, key_size=4096, days=3650, working_dir='.', **kwargs):
        self.working_dir = working_dir
        self.dn = self.get_dn(dn, csr)
        self.key_path = os.path.join(working_dir, 'private', self.dn.file_friendly_cn + self.key_ext)
        self.csr_path = os.path.join(working_dir, 'csr', self.dn.file_friendly_cn + self.csr_ext)
        self.crt_path = os.path.join(working_dir, 'certs', self.dn.file_friendly_cn + self.crt_ext)
        self.srl_path = os.path.join(working_dir, 'srl', self.dn.file_friendly_cn + self.srl_ext)
        self.ca = ca
        self.key_size = str(key_size)
        self.days = str(days)
        self.working_dir = working_dir
        self.kwargs = kwargs
        self.create_dirs()

    def get_dn(self, dn, csr):
        if dn is None and csr is None:
            raise PKIError('DN or CSR must be supplied.')
        elif dn is None:
            csr_path = os.path.join(self.working_dir, textmd5sum(csr) + '.csr')

            with open(csr_path, 'w') as csr_file:
                csr_file.write(csr)
            dn = DistinguishedNameFactory().from_csr(csr_path)
            csr_new_path = os.path.join(self.working_dir, 'csr', dn.file_friendly_cn + self.csr_ext)
            mktree(os.path.dirname(csr_new_path))
            os.rename(csr_path, csr_new_path)
        return dn

    def gen_key(self):
        self.openssl.gen_key(self.key_path, self.key_size)

    def gen_csr(self):
        self.openssl.gen_csr(self.key_path, self.csr_path, self.dn.DN)

    def sign_csr(self, csr=None):
        if self.ca is None:
            raise PKIError('No CA supplied, can not sign')

        if not os.path.isfile(self.csr_path) and csr is None:
            raise PKIError('You must generate a CSR first.')
        elif not os.path.isfile(self.csr_path):
            with open(self.csr_path, 'w') as csr_file:
                csr_file.write(csr)

        args = ['-CA', self.ca.crt_path,
                '-CAkey', self.ca.key_path,
                '-CAcreateserial', '-CAserial', self.srl_path,
                '-' + self.openssl.algorithm]
        self.openssl.sign_csr(self.csr_path, self.crt_path, self.days, *args)

    def get_csr(self):
        try:
            with open(self.csr_path, 'r') as csr_file:
                csr = csr_file.read()
            return csr
        except IOError:
            return

    def gen_cert(self):
        self.gen_key()
        self.gen_csr()
        self.sign_csr()

# TODO: Add Client Certificate
