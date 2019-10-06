#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
***
Module:
***

#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
"""
import base64
import datetime
import hashlib
# import binascii
# import logging
import os
import pickle
import time
from traceback import print_exc
import sys
import pem

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.backends.openssl import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.asymmetric import padding
# noinspection PyProtectedMember
from cryptography.x509 import ExtensionOID, Certificate, CertificateSigningRequestBuilder, Name, NameAttribute

from foxyproxy.constant import Constant
from foxyproxy.csp import TokenRecord
from foxyproxy.csp import CertificateRecord
from foxyproxy.csp import ReaderRecord
from foxyproxy.csp import BaseCryptoService
from foxyproxy.upstream import RegisterUpstream
from foxyproxy.create_csr import *
if sys.version_info[0] >= 3:
    # noinspection PyCompatibility
    from builtins import str

# If this is Python 2, use raw_input()
if sys.version_info[:2] <= (2, 7):
    # noinspection PyUnresolvedReferences
    get_input = raw_input
else:
    get_input = input

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# logger.addHandler(ch)


class CryptoPGP(BaseCryptoService):
    """
    This class implements signing with eIDAS smart cards of a Czech trust provider I.CA.
    """

    def __init__(self, cmd_params):

        server = RegisterUpstream.get_service(cmd_params['upstream'], cmd_params['token'])
        if server is None:
            logging.error("No upstream server configuration created")
            exit(-1)

        if cmd_params['register']:
            self.create_csr = True
        else:
            self.create_csr = False

        # we call the super() constructor to initialize the 'self.signer' object
        super(CryptoPGP, self).__init__(server)

        # and we try to read known tokens and certificates from disk

        self.pgp_token_file = os.path.join(self.token_dir, 'pgp')
        self.known_tokens = dict()

        if os.path.isfile(self.pgp_token_file):
            f = open(self.pgp_token_file, 'rb')
            self.known_tokens = pickle.load(f)
            f.close()
            # somehow check the integrity
            for item in self.known_tokens.keys():
                if (self.known_tokens[item]['date'] is None) or (self.known_tokens[item]['request'] is None) \
                        or (self.known_tokens[item]['fingerprint'] is None):
                    logging.error("The pgp token configuration file seems corrupted: %s" % self.pgp_token_file)

        # let's try to read certificates now
        self.pgp_cert_file = os.path.join(self.cert_dir, 'all')
        self.known_certs = dict()

        if os.path.isfile(self.pgp_cert_file):
            f = open(self.pgp_cert_file, 'rb')
            self.known_certs = pickle.load(f)
            f.close()
            # somehow check the integrity
            for item in self.known_certs.keys():
                if (self.known_certs[item]['date'] is None) or (self.known_certs[item]['key'] is None) \
                        or (self.known_certs[item]['subject'] is None) or (self.known_certs[item]['issuer'] is None) \
                        or (self.known_certs[item]['subject_cn'] is None) or (self.known_certs[item]['ca'] is None):
                    logging.error("The pgp token configuration file seems corrupted: %s" % self.pgp_cert_file)

        # let's see if user has added some new certificates
        # first we read certificates from the user's home folder
        cert_files = [f for f in os.listdir(self.cert_dir) if os.path.isfile(os.path.join(self.cert_dir, f))]

        for cert_file in cert_files:
            # noinspection PyBroadException
            certs = None
            # noinspection PyBroadException
            try:
                certs = pem.parse_file(cert_file)
            except Exception:
                try:
                    # let's try to open it as a der file
                    with open(cert_file, "rb") as f:
                        certs = [Certificate.load(f.read())]
                except Exception as ex_in:
                    template = "An exception when parsing a file {0} for certificates. Error {1}, arguments:\n{2!r}"
                    logging.error(cert_file, template.format(type(ex_in).__name__, ex_in.args))
                    if cert_file.endswith('.pem'):
                        logging.debug(print_exc())
            if certs is not None:
                for cert in certs:  # type: Certificate
                    ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
                    digest = hashlib.sha256(cert.public_key()).hexdigest()
                    logging.debug("New certificate %s - %s" % (cert.subject, digest))
                    if ext and ext.value and ext.value.ca:
                        # this is a CA, we store it as a CA cert
                        self.known_certs[digest] = {'date': time.time(),
                                                    'ca': True,
                                                    'subject_cn': "dan",
                                                    'subject': "hash_subject",
                                                    'issuer': "hash_issuer"}
                    else:
                        # this is enduser, we store it as an end-user cert
                        self.known_certs[digest] = {'date': time.time(),
                                                    'ca': False,
                                                    'subject_cn': "dan",
                                                    'subject': "hash_subject",
                                                    'issuer': "hash_issuer"}

        if os.path.isfile(self.pgp_token_file):
            f = open(self.pgp_token_file, 'rb')
            known_tokens = pickle.load(f)
            f.close()
            # somehow check the integrity
            for item in known_tokens.keys():
                if (known_tokens[item]['date'] is None) or (known_tokens[item]['pkcs10'] is None):
                    logging.error("The pgp token configuration file seems corrupted: %s" % self.pgp_token_file)

    def init(self, session, config=None):
        """
        Initilize crypto token
        :param session:
        :param config:
        :return:
        """
        was_down = self.server.downtime(session)

        if was_down:
            # we refresh the crypto storage
            self.storage.initialize()
            self._read_certificates(session)
            self.server.set_uptime()
        pass

    def aliases(self):
        """
        Get aliases
        :return:
        """
        pass

    def chain(self, alias, sign_alg=0):
        """
        Get the certificate chain
        :param alias:
        :param sign_alg:
        :return:
        """
        reader = self.get_token(alias)
        if len(reader) != 1:
            if len(reader) == 0:
                # we haven't found the name
                response_data = Constant.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = Constant.CMD_VAGUE_NAME
        else:
            # and we need to get the certificate chain
            response_data = self.get_certs(reader.reader)
        return response_data

    def sign(self, session, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        signing consists of the following APDUs
        '00A4040006D2760001240100' - PGP applet select
        '0020008106313233343536' - PIN verify
        '002a9e9a14000000000000000000000000000000000000000000' - sending data over

        :param session:
        :param alias:
        :param fingerprint:
        :param password:
        :param hash_alg:
        :param sign_alg:
        :return:
        """

        readers = self.get_token(alias)
        if len(readers) != 1:
            if len(readers) == 0:
                # we haven't found the name
                response_data = Constant.CMD_READER_NOT_FOUND
            else:
                # the name is not unique
                response_data = Constant.CMD_VAGUE_NAME
            return response_data

        reader = readers[0]
        # we have a reader, let's do the signing
        if len(fingerprint) == 40:
            sha_id = "10"
        elif len(fingerprint) == 64:
            sha_id = "30"
        else:
            response_data = Constant.CMD_READER_WRONG_DATA
            return response_data

        self.server.cmd(session, '00A4000C023F00', reader.reader, 1)
        response_all = self.server.cmd(session, '00A4010C020604', reader.reader)
        # PIN
        # if the password is set
        pin_ok = True
        if password is not None:
            pin_update = None
            encoded_password = binascii.b2a_hex(password.encode('ascii')).decode('ascii')  # 3287195
            if (reader.pin is not None) and (reader.pin == encoded_password):
                logging.error("Blocked repeated use of incorrect PIN to reader %s, remaining tries %s"
                             % (reader.reader, response_all[-1:]))
                pin_ok = False
            else:
                response_all = self.server.cmd(session, '00200081%02X%s' % (len(password), encoded_password),
                                               reader.reader)
                if (response_all is not None) and (len(response_all) > 0) \
                        and response_all[0][-4:-1] == "63C":
                    # there is a problem with PIN - the counter was decreased
                    logging.error("Incorrect PIN to reader %s, remaining tries %s" %
                                 (reader.reader, response_all[0][-1:]))
                    pin_update = {'type': 'pin', 'alias': alias, 'value': encoded_password}
                    reader.pin = encoded_password
                elif (response_all is not None) and (len(response_all) > 0) \
                        and response_all[0][-4:] == "9000":
                    reader.pin = None
                    pin_update = {'type': 'pin', 'alias': alias, 'value': encoded_password}
                elif (response_all is None) or len(response_all) < 1:
                    logging.error("Error with PIN verification at reader %s - no details available" %
                                 reader.reader)
                    pin_ok = False
                else:
                    logging.error("Error with PIN verification at reader %s, the error code is %s" %
                                 (reader.reader, response_all[0]))
                    pin_ok = False

                if pin_update:
                    self.process_queue.put(pin_update, True, 1.0)  # we can give it a second
        if not pin_ok:
            response_data = Constant.CMD_READER_WRONG_PIN
        else:
            # let's do signing - we may try a few times if 'file_id' is not set
            keep_trying = True
            response_data = None
            temp_file_id = reader.file_id

            key_id_limit = 15
            if temp_file_id == 0:
                temp_file_id = key_id_limit
            while keep_trying:
                # h MSE:Set sha-256
                self.server.cmd(session, '002241AA04890214%s' % sha_id, reader.reader)
                # h MSE:Set DST
                response_all = self.server.cmd(session, '002241B60A 840380%02X00 89031323%s' % (temp_file_id, sha_id),
                                               reader.reader)
                if (response_all is not None) and (len(response_all) > 0) \
                        and (response_all[0][-4:] != "9000" or len(response_all[0]) < 4):
                    logging.error("Error setting MSE DST reader %s - code: %s" %
                                  (reader.reader, response_all[0]))

                # send the hash to the card
                sha_length = int(len(fingerprint) / 2)
                response_all = self.server.cmd(session,
                                               '002a90a0%02X90%02X%s' % (sha_length + 2, sha_length, fingerprint),
                                               reader.reader)
                if (response_all is not None) \
                        and (len(response_all) > 0) \
                        and (response_all[0][-4:] != "9000" or len(response_all[0]) < 4):
                    logging.error("Error sending hash for signing reader %s - code %s" %
                                  (reader.reader, response_all[0]))

                # finally, request signing and collect the signature
                response_all = self.server.cmd(session, "002A9E9A00", reader.reader)
                if response_all[0][-4:] != "9000":
                    logging.error("Signing unsuccessful reader %s, error code %s" %
                                  (reader.reader, response_all[0][-4:]))
                    response_data = response_all[0][-4:]
                    # let's see if we should try again
                    if reader.file_id == 0 and key_id_limit > 0:
                        key_id_limit -= 1
                        temp_file_id -= 1
                    else:
                        keep_trying = False
                else:
                    if reader.file_id == 0:
                        self._update_file_id(reader, temp_file_id)
                    response_data = response_all[0][0:-4]
                    keep_trying = False
        return response_data

    def apdu(self, session, token, command):
        """
        A native command provided by the cryptographic token
        :param session: upsteram TCP/HTTP connection or None
        :param token: identification of the cryptographic token, e.g., smartcard
        :type token: str
        :param command: the actual command - hex encoded
        :type command: str
        :return:
        """

        response_all = self.server.cmd(session, command, token)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = Constant.CMD_INTERNAL_ERROR
        return response_data

    def reset(self, session, token):
        """
        As described in the abstract class
        :param session:
        :param token:
        :return:
        """
        response_all = self.server.cmd(session, None, token, 1)
        if len(response_all) > 0:
            response_data = response_all[0]
        else:
            response_data = Constant.CMD_INTERNAL_ERROR

        return response_data

    # #########################################################################
    #  Internal methods
    # #########################################################################

    def _read_certificates(self, session):

        # let's now get a list of card readers and ATRs
        response_data = self.server.inventory(session)

        for reader in response_data:
            logging.info("Found a new token %s" % reader)

            # let's get the token's ID
            response_all = self.server.cmd(session, ['00A4040006D2760001240100', '00ca004f00'], reader)
            if (len(response_all) == 2) and (response_all[0][-4:] == "9000") and (response_all[1][-4:] == "9000"):
                # according to the PGP specs, the manufacturer and card serial number are bytes 9-14
                # but we can use the whole string
                token_sn = response_all[1][:-4]
                # let's get the token's public key
                response_all = self.server.cmd(session, ['00A4040006D2760001240100', '0047810002b60000'], reader)
                if (len(response_all) == 2) and (response_all[0][-4:] == "9000") and (response_all[1][-4:] == "9000") \
                        and len(response_all[1]) > 64:
                    public_key = response_all[1][4:-4]  # skip first 2 bytes - a PGP tag, and 9000 at the end
                    self.storage.certificates[reader] = ReaderRecord()
                    self.storage.certificates[reader].token = token_sn
                    self.storage.certificates[reader].key = public_key
                    #     # we need to get the certificates from files
                else:
                    logging.info("Token '%s' doesn't return a valid signing key." % reader)
            else:
                logging.info("Token '%s' is not recognized as a PGP token" % reader)

        # now we have a dictionary of connected tokens, we need to find certificates and reconstruct chains
        for reader in self.storage.certificates.keys():
            finger_key = hashlib.sha256(self.storage.certificates[reader].key).hexdigest()
            if finger_key in self.known_certs:  # TODO check upper/lower case
                # here we do something
                pass
            else:
                if self.create_csr:
                    # we create a pkcs10 so we can request a certificate

                    # first we need to ask for user data:
                    print("We need some personal information, which will be included in the certificate, if you"
                          "don't wish to use any of the items, just press Enter to skip to the next one.")
                    print("You have to provide either 'Name' or 'Email address'.")
                    not_right = True
                    dn = []
                    while not_right:
                        name = get_input("Name: ")
                        email = get_input("Email address: ")
                        if (len(name) < 3) and ((len(email) < 5) or ('@' not in email)):
                            print("\nYou have to enter name or an email address.\n\n")
                            continue
                        org = get_input("Company / organization: ")
                        country = get_input(
                            "Country as a 2 letter code (see a list at https://www.ssl.com/csrs/country_codes/): ")
                        print("")
                        dn = []
                        if len(name) > 1:
                            dn.append(NameAttribute(NameOID.COMMON_NAME, str(name)))
                        if len(email) > 1:
                            dn.append(NameAttribute(NameOID.EMAIL_ADDRESS, str(email)))
                        if len(org) > 1:
                            dn.append(NameAttribute(NameOID.ORGANIZATION_NAME, str(org)))
                        if len(country) == 2:
                            dn.append(NameAttribute(NameOID.COUNTRY_NAME, str(country)))
                        print('Your information is encoded as: %s' % dn)
                        ok = get_input("Is the information correct? (type 'yes' to continue) ")
                        if ok == 'yes':
                            not_right = False
                        pass

                    # create a key from the hex value

                    # ignore the initial SeqOf tag
                    source_key = self.storage.certificates[reader].key
                    if source_key[0] == '8':
                        offset = 2 + int(source_key[1]) * 2
                    else:
                        offset = 2
                    offset += 2  # there's a tag '81' we need to skip - 81 = modulus
                    # get modulus
                    if source_key[offset] == '8':  # get the length of modules -> this means it's extended length
                        l_l = 2 * int(source_key[offset + 1])  # get the number of bytes/characters encoding the length
                        len_str = int(source_key[offset + 2: offset + 2 + l_l], 16) * 2  # get the encoded length
                        modulus = "00" + source_key[offset + 6: offset + len_str + 2 + l_l]  # get the modulus itself
                        offset += 2 + l_l + len_str
                    else:
                        len_str = int(source_key[offset: offset + 2], 16) * 2  # length of the encoded modulus value
                        modulus = source_key[offset + 2: offset + len_str + 2]  # simple - modulus only value
                        offset += 2 + len_str  # now it points at the beginning of th next item = exponent

                    # recompute modulus length
                    mod_len = "%X" % (len(modulus) // 2)
                    if len(mod_len) % 2 == 1:
                        mod_len = "0" + mod_len  # make sure we get whole bytes = even number of hex chars
                    if (len(modulus) // 2) > 127:
                        l_l = "8%X" % (len(mod_len) // 2)  # extended length encoding
                        modulus = l_l + mod_len + modulus  # correctly encoded TLV for modulus
                    else:
                        modulus = mod_len + modulus  # simple - modulus with length

                    offset += 2  # skip the tag '82'
                    # get exponent - it's always simple length
                    len_str = int(source_key[offset:offset + 2], 16) * 2
                    exponent = source_key[offset:offset + 2 + len_str]

                    # first put modulus and exponent together
                    clean_key = "02" + modulus + "02" + exponent

                    # wrap it in a sequence
                    clean_key_len = len(clean_key) // 2
                    len_str = "%X" % clean_key_len
                    if len(len_str) % 2 == 1:
                        len_str = "0" + len_str
                    if clean_key_len > 127:
                        l_l = "8%X" % (len(len_str)//2)
                        len_str = l_l + len_str
                    clean_key = '30' + len_str + clean_key

                    # but last step is to wrap it in a BIT STRING
                    clean_key_len = len(clean_key) // 2 + 1  # an extra 1B for bit string bit length
                    len_str = "%X" % clean_key_len
                    if len(len_str) % 2 == 1:
                        len_str = "0" + len_str
                    if clean_key_len > 127:
                        l_l = "8%X" % (len(len_str)//2)
                        len_str = l_l + len_str
                    clean_key = '03' + len_str + "00" + clean_key

                    # and we add the algorithm
                    clean_key = "300D06092A864886F70D0101010500" + clean_key
                    clean_key_len = len(clean_key) // 2
                    len_str = "%X" % clean_key_len
                    if len(len_str) % 2 == 1:
                        len_str = "0" + len_str
                    if clean_key_len > 127:
                        l_l = "8%X" % (1 + clean_key_len // 256)
                        len_str = l_l + len_str
                    clean_key = '30' + len_str + clean_key

                    # clean_key = '-----BEGIN PUBLIC KEY-----\n' + clean_key +'\n-----END PUBLIC KEY-----'
                    public_key = load_der_public_key(
                        binascii.unhexlify(clean_key),
                        default_backend())  # # type: rsa._RSAPublicKey

                    # private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                    #                                        backend=default_backend())
                    # csrtest = CertificateSigningRequestBuilder().subject_name(Name(dn)).sign(private_key,
                    #                                                                          hashes.SHA256(),
                    #                                                                          default_backend())
                    # mybytes = binascii.hexlify(csrtest.public_bytes(serialization.Encoding.DER))
                    csr = CertificateSigningRequestBuilder().subject_name(Name(dn))
                    csr = create_csr_info(csr, public_key, hashes.SHA256, default_backend())

                    # we now need to request a PIN and do the signing
                    pin2 = ''
                    counter = 0
                    pin = None
                    while (pin2 != 'yes') and counter < 3:
                        counter += 1
                        pin = get_input("Please enter your PIN so we can sign the certificate request: ")
                        pin2 = get_input("The PIN is %d characters long, is it correct? (yes/n) " % len(pin))
                    pass
                    # convert pin
                    clean_pin = binascii.hexlify(pin)
                    clean_hash = hashlib.sha256(csr.tbs_certrequest_bytes).hexdigest()
                    clean_hash = "3031300d060960864801650304020105000420" + clean_hash
                    response_all = self.server.cmd(session,
                                                   ['00A4040006D2760001240100',
                                                    '00200081%02X%s' % (len(pin), clean_pin),
                                                    '002a9e9a%02X%s00' % (len(clean_hash) // 2, clean_hash)], reader)
                    if len(response_all) < 3:
                        logging.error("Signing request for a CSR resulted in an error - the submitted data was %s" %
                                      clean_hash)
                        print("Please check the token is properly plugged in as it doesn't respond.")
                    elif response_all[0][-4:] != "9000":
                        logging.error("Applet select for unsuccessful - code: %s" % response_all[0])
                        print("Please check the token is properly plugged in as it doesn't respond.")
                    elif (len(response_all) == 3) and (response_all[0][-4:] == "9000") and \
                            (response_all[1][-4:] != "9000"):
                        print("Error when verifying your PIN - you entered: %s" % pin)
                        exit(6)
                    elif response_all[2][-4:] != "9000":
                        logging.error("Signing request for a CSR resulted in a signing error"
                                      " - the submitted data was %s" % clean_hash)
                        print("Please check the token is properly plugged in as it doesn't respond.")
                    elif (response_all[0][-4:] != "9000") or (response_all[1][-4:] != "9000") \
                            or (response_all[2][-4:] != "9000"):
                        logging.error("Some other error when creating a CSR signature: %s" % ' '.join(response_all))
                    else:
                        # all good - we have a signature and
                        logging.info("Signature result was %s" % response_all[2])
                        signature = response_all[2][0:-4]

                        # first test if the signature is OK
                        # https://www.entrust.net/ssl-technical/csr-viewer.cfm - signature / CSR tester - or
                        # openssl req -text -noout -verify -in <filename>
                        # noinspection PyPep8,PyBroadException
                        try:
                            public_key.verify(
                                binascii.unhexlify(signature),
                                binascii.unhexlify(clean_hash),
                                padding.PKCS1v15(),
                                # padding.PSS(
                                #    mgf=padding.MGF1(hashes.SHA256()),
                                #    salt_length=padding.PSS.MAX_LENGTH),
                                hashes.SHA256())
                        except Exception:
                            logging.error("CSR signature is invalid")

                        # we can finish the CSR
                        data = create_csr_signed(csr, signature)
                        filename = datetime.datetime.now().strftime("%I_%M%p_%d_%B_%Y")
                        fout = open(os.path.join(self.user_dir, filename) + '.csr', 'w')
                        data = base64.b64encode(binascii.unhexlify(data))
                        data_out = '\n'.join([data[i:i + 60] for i in range(0, len(data), 60)])
                        fout.write('-----BEGIN CERTIFICATE REQUEST-----\n' +
                                   data_out +
                                   '\n-----END CERTIFICATE REQUEST-----')
                        fout.close()

                        print("You can copy and paste this text to request a certificate")
                        print(data)
                        print("\nWe have also stored the request in a file: %s" % os.path.join(self.user_dir, filename))
                else:
                    logging.error("Connected token '%s' doesn't have any certificates, you can initiate certificate"
                                  "request with 'foxyproxy -r -c pgp'" % 'reader')

            # we can also add this token to a list of known tokens -> we've seen them before
            if self.storage.certificates[reader].token not in self.known_tokens:
                # we will add it
                pass
            else:
                # we check the key and certificate are the same
                pass

        # self.known_certs
        # self.known_tokens
        # self.storage.cert_names
        # self.storage.certificates

        # a better source -
        #   https://github.com/ANSSI-FR/SmartPGP/blob/64c280aecc22642980a2e39d2b47b84c76f27e33/bin/smartpgp/commands.py
        # according to the following source code -
        # https://github.com/Yubico/ykneo-openpgp/blob/master/applet/src/openpgpcard/OpenPGPApplet.java

        # CLA - any, let's try 0x00
        # INS - 0xF1 - get version
        #      0xCA - get data
        # get data:
        #   0x004F - AID
        #   0x005E - login data
        #   0x5F50 - URL
        #   0x5F52 - historical data
        #   0x0065 - cardholder data
        #   0x006E - app related data
        #   0x007A - sec support template
        #   0x7F21 - cardholder certificate
        #   0x00C4 - PW status
        #   0x0101 - 0x0104 - private use
        #

        for reader in self.storage.certificates.keys():

            ##########################
            # a new approach to derive the file ID for the private key
            ##########################
            error = False
            response_all = self.server.cmd(session, '00A4040006D2760001240100', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd(session, '00A4010C023F50', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd(session, '00A4010C023F10', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True
            response_all = self.server.cmd(session, '00A4020C025660', reader)
            if len(response_all) < 1 or response_all[0][-4:] != "9000":
                error = True

            cert_file_id = 1
            not_found = True
            while not_found and not error:
                response_all = self.server.cmd(session, '00B2%02X0400' % cert_file_id, reader)  # a folder
                # print(response_all[0])
                if len(response_all) < 1 or response_all[0][-4:] != "9000":
                    cert_file_id -= 1  # the previous one was the last good
                    not_found = False
                else:
                    cert_file_id += 1

            ##########################
            ##########################

            latest_cert_time = 0
            self.storage.card_cas[reader] = []
            self.server.cmd(session, '00A40004023F0000', reader, 1)

            new_item = True
            certificate_id = 1
            end_subject = ""
            end_issuer = ""

            subject_cn = None
            while new_item:
                self.server.cmd(session, '00A4000C023F00', reader)  # switch to the app
                self.server.cmd(session, '00A4010C023F50', reader)  # select files with objects
                self.server.cmd(session, '00A4010C023F10', reader)  # we need a directory structure
                response_all = self.server.cmd(session, '00A4020C025630', reader)  # and a list of certificates
                if response_all[0][-4:] != "9000":
                    logging.error("00A4020C025630 command returned an error (reader %s) - %s" %
                                  (reader, response_all[0][-4:]))
                    break

                # select 1..n-th certificate record
                apdu = '00B2%02X0400' % certificate_id
                certificate_id += 1
                response_all = self.server.cmd(session, apdu, reader)
                if len(response_all) < 1:
                    logging.error("00B2%02X0400 command didn't return any response" % certificate_id)
                    break
                if response_all[0][-4:] != "9000":
                    logging.info("00B2%02X0400 command returned an error - %s" %
                                 (certificate_id, response_all[0][-4:]))
                    break
                # keep the first line without the last 4 characters
                raw_response = bytearray.fromhex(response_all[0][:-4])  # remove the first ASN.1 tag
                if raw_response[1] <= 0x81:
                    raw_response = raw_response[2:]  # ... and its length
                else:
                    offset = (raw_response[1] - 128) + 2  # ... and its length, we only keep the value
                    raw_response = raw_response[offset:]  # the long length encoding 01 82 xx xx
                file_id = None
                cert_len = 0
                while (len(raw_response) > 2) and ((file_id is None) or (cert_len == 0)):
                    if raw_response[0] == 0x10:  # this is 2 file descriptors to select a certificate
                        file_id = raw_response[2:6]
                    if raw_response[0] == 0x12:  # this is the length of the certificate we expect
                        cert_len = ((raw_response[2] * 256 + raw_response[3]) * 256 + raw_response[4]) * 256 + \
                                   raw_response[5]
                    raw_response = raw_response[(2 + raw_response[1]):]
                # let's get a certificate now - first select one
                self.server.cmd(session, '00A4000C023F00', reader)
                self.server.cmd(session, '00A4010C023F50', reader)
                apdu = "00A4010C02%s" % binascii.b2a_hex(file_id[0:2]).decode('ascii')  # select cert folder /3f20
                self.server.cmd(session, apdu, reader)
                apdu = "00 a4 020C02%s" % binascii.b2a_hex(file_id[2:4]).decode('ascii')  # and the cert we want
                response_all = self.server.cmd(session, apdu, reader)
                if len(response_all) > 0 and response_all[0][-4:] == '9000':
                    counter = 0
                    new_cert = ""
                    while cert_len > 0:  # reading the cert - multiple APDUs
                        response_all = self.server.cmd(session, '00B0%02X0000' % counter, reader)
                        if len(response_all) < 1 or response_all[0][-4:] != "9000":
                            break
                        new_cert += response_all[0][:-4]
                        cert_len -= (len(response_all[0]) / 2 - 2)
                        counter += 1

                    if cert_len <= 0:  # it should end up in cert_len == 0
                        # we got a cert
                        cert = x509.load_der_x509_certificate(binascii.a2b_hex(new_cert), default_backend())
                        subject_list = []
                        subject_cn = ""
                        for attribute in cert.subject:
                            oid_in = attribute.oid
                            # dot = oid_in.dotted_string
                            # noinspection PyProtectedMember
                            oid_name = oid_in._name
                            val = attribute.value
                            subject_list.append('%s: %s' % (oid_name, val))
                            if oid_name.lower() == "commonname":
                                subject_cn = val
                        subject_list.sort()
                        subject = ', '.join(subject_list)
                        issuer_list = []
                        for attribute in cert.issuer:
                            oid_in = attribute.oid
                            # dot = oid_in.dotted_string
                            # noinspection PyProtectedMember
                            oid_name = oid_in._name
                            val = attribute.value
                            issuer_list.append('%s: %s' % (oid_name, val))
                        issuer_list.sort()
                        issuer = ', '.join(issuer_list)
                        ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
                        if ext and ext.value and ext.value.ca:
                            logging.debug("New CA certificate from reader %s: %s" % (reader, subject_cn))
                            # this is a CA, we store it in card CA list
                            _cas = CertificateRecord()
                            _cas.name = subject
                            _cas.issuer = issuer
                            _cas.cert = base64.standard_b64encode(binascii.a2b_hex(new_cert))
                            self.storage.card_cas[reader].append(_cas)
                        else:
                            logging.info("New user certificate from reader %s: %s" % (reader, subject_cn))
                            # it's an end-user certificate
                            issued_at = Constant.unix_time(cert.not_valid_before)
                            if issued_at > latest_cert_time:
                                self.storage.certificates[reader].cert = \
                                    base64.standard_b64encode(binascii.a2b_hex(new_cert))
                                end_issuer = issuer
                                end_subject = subject
                            else:
                                # we will only take the latest certificate - if there are more end-user certs
                                pass
                    else:
                        logging.error("Error reading a certificate from smart card, selector: %s" % apdu)

                else:
                    # cert file selection returned error
                    if len(response_all) > 0:
                        logging.error("Certificate file selection returned error: %s" % response_all[0])
                    else:
                        logging.error("Certificate file selection returned no response")

            # this is the end of reading certificates from smart card - we now need to create a chain
            # and extract the subject from the end-user cert
            if end_subject == "" or end_issuer == "":
                logging.warning("No end-user certificate found on this smart card %s" % reader)
            else:
                # create a link from name to smart card
                _token = TokenRecord()
                _token.name = end_subject
                _token.short_name = subject_cn
                _token.reader = reader
                self.cert_names.append(_token)
                # we will try to find it with the first signature ...  end_cert_id})
                # let's create a chain
                root = False
                chain = []
                while not root:
                    next_found = False
                    for ca_cert in self.storage.card_cas[reader]:  # type: CertificateRecord
                        if ca_cert.name == end_issuer:
                            next_found = True
                            chain.append(ca_cert)
                            end_issuer = ca_cert.issuer
                            if ca_cert.name == ca_cert.issuer:
                                root = True
                            break
                    if not next_found:
                        break
                if len(chain) < 1:
                    logging.error("No certificate found for %s" % end_subject)
                else:
                    self.storage.certificates[reader].chain = chain

        pass

    def _update_file_id(self, reader, file_id):
        """
        If we find a correct file_id for the user's private key, we set it in the cert_names list
        :param reader: a copy of one of the items retrieved from cert_names
        :type reader: TokenRecord
        :param file_id: an integer - the new file_id
        :return: None
        """
        new_cert_names = []
        for one_name in self.cert_names:  # type: TokenRecord
            if reader.name == one_name.name:
                one_name.file_id = file_id
            new_cert_names.append(one_name)
        self.cert_names = new_cert_names
