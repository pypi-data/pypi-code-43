import json
import time
import uuid
import logging
import hashlib
from abc import ABCMeta, abstractmethod

from v_bootstrap.utils.security import PubKeys
from v_bootstrap.utils.errors import BoardError, ConfigValidationError
from v_bootstrap.utils.connectors import SerialConnector, SSHConnector

logger = logging.getLogger(__name__)


class BoardBase(object):
    __metaclass__ = ABCMeta

    PATH_MODEL_NAME = '/etc/aos/model_name.txt'

    def __init__(self):
        self._connector = None

    @abstractmethod
    def init_connector(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        self._connector = self.init_connector()

    def disconnect(self):
        if self._connector:
            self._connector.close()
            self._connector = None

    @property
    def connector(self):
        return self._connector

    @abstractmethod
    def _generate_pair(self, pair_type):
        pass

    @abstractmethod
    def get_hw_id(self):
        pass

    @abstractmethod
    def get_vin(self):
        pass

    @abstractmethod
    def get_model_name(self):
        pass

    def generate_pkeys(self):
        """ Generates a key pair. Returns object with public ones. """
        logger.info("Generating security keys ...")

        pkeys = PubKeys()
        for t in PubKeys.TYPES:
            logger.debug("Generating %s key pairs ...", t)

            public = self._generate_pair(t)

            if t == PubKeys.TYPE_ONLINE:
                pkeys.online = public
            elif t == PubKeys.TYPE_OFFLINE:
                pkeys.offline = public

        return pkeys

    @abstractmethod
    def configure(self, cfg):
        pass

    @abstractmethod
    def perform_deprovisioning(self):
        pass


_key_offline_pri = b''
_key_online_pri = b''


class Board(BoardBase):
    PATH_VIN = '/var/aos/vin'

    def __init__(self, port, cred):
        super(Board, self).__init__()
        self._port = port
        self._cred = cred

    def init_connector(self):
        serial = SerialConnector(self._port, self._cred)
        serial.connect()

        return serial

    def get_hw_id(self):
        logger.info("Obtaining hardware ID ...")
        hw_id = self._read_hw_id()
        return hw_id

    def get_vin(self):
        logger.info("Obtaining vin ...")
        if not self._is_vin_defined():
            logger.info("VIN not found.... Initializing board ")
            if not self._is_file_exist("/var/aos"):
                self.connector.execute_script("mkdir /var/aos")
            self.connector.execute_script("/xt/scripts/aos-provisioning.step2.sh get_vin")
            logger.info("Script done")
        if self._is_vin_defined():
            return self._cat_file(self.PATH_VIN, 17, True)
        else:
            logger.error("VIN not defined")
            return None

    def _is_vin_defined(self):
        ret = self.connector.execute("test -e {}".format(Board.PATH_VIN))
        return not ret.exit_code

    def _is_file_exist(self, filename):
        ret = self.connector.execute("test -e {}".format(filename))
        return not ret.exit_code

    def _is_model_name_file_present(self):
        """ Checks presence if model name file. """
        ret = self.connector.execute(
            "test -e {}".format(BoardVirtual.PATH_MODEL_NAME))
        if ret.exit_code:
            return False

        return True

    def _validate_content_upload(self, content, target_file_name, add_new_line=False):
        target_checksum = self._read_checksum(target_file_name)
        if not target_checksum:
            return False

        m = hashlib.sha1()
        m.update(content.encode('utf-8'))
        if add_new_line:
            m.update('\n'.encode('utf-8'))

        logger.debug("Content digest is {}, Board file digest is {}".format(m.hexdigest(), target_checksum))

        return m.hexdigest() == target_checksum

    def _read_checksum(self, filename):
        """ Calculate file checksum on board. """
        ret = self.connector.execute("sha1sum {}".format(filename))
        if ret.exit_code:
            return False

        splitted = list(filter(None, ret.data.split(" ")))
        if len(splitted) == 2 and splitted[1] == filename:
            logger.debug("received checksum: {}".format(splitted[0]))
            return splitted[0]

        return False

    def _cat_file(self, filename,  file_len, allow_empty=False):
        while True:
            try:
                ret = self.connector.execute("cat {}".format(filename))
                if ret.exit_code:
                    logger.error('Failed to get {} from the board'.format(filename))
                    raise AssertionError
                result = ret.data
                if len(result) != file_len:
                    if not len(result) and allow_empty:
                        return ""
                    time.sleep(0.5)
                else:
                    return result
            except ValueError:
                pass

    def _echo_to_file(self, filename, content, retry_count=5):
        cmd = "echo '{}' > {}".format(content, filename)
        try:
            logger.info("Uploading file {}.".format(filename))
            retry_count -= 1
            self.connector.execute(cmd, debug=False)
            while retry_count > 0 and not self._validate_content_upload(content, filename, True):
                logger.info("Upload file {} failed. Retry count left {}".format(filename, retry_count))
                self.connector.execute(cmd, debug=False)
                retry_count -= 1
        except ValueError:
            pass

    def _read_hw_id(self):
        tmp_guid = str(uuid.uuid4())

        logger.debug("Running AOS provisioning script STEP1")
        while True:
            try:
                ret = self.connector.execute_script("/xt/scripts/aos-provisioning.step1.sh")
                if ret.exit_code:
                    logger.error("Failed to run AOS provisioning script STEP1")
                    raise AssertionError
                break
            except ValueError:
                pass
        logger.debug("AOS provisioning script STEP1 successful finished")

        result = self._cat_file("/var/aos/hwid", len(tmp_guid)-4)
        return result

    def _generate_pair(self, pair_type):
        result = self._cat_file("/var/aos/{}.pub.pem".format(pair_type), 450)
        return result

    def _save_cert_to_file(self, file_name, file_content):
        logger.info("Upload cert {} to board".format(file_name))
        _CERT_END = "-----END CERTIFICATE-----\n"
        _CERT_END_NOT_NL = "-----END CERTIFICATE-----"

        chunks = file_content.split(_CERT_END)

        while True:
            try:
                self.connector.execute("rm -f {}".format(file_name), debug=False)
            except ValueError:
                pass

            for chunk in chunks:
                if chunk not in [_CERT_END, _CERT_END_NOT_NL, ""]:
                    cmd = "echo '{}' >> {}".format(chunk + _CERT_END_NOT_NL, file_name)
                    self.connector.send(cmd)
            time.sleep(1.5)
            self.connector.send("\x03")
            time.sleep(1)
            self.connector.execute('clear')
            self.connector.clear()

            resp = self.connector.execute("test -e {}".format(file_name))
            if resp.exit_code:
                logger.error("Uploaded file not found. Retrying upload...")
                continue

            if not self._validate_content_upload(file_content, file_name):
                logger.error("Uploaded file checksum is wrong. Retrying upload...")
                continue
            else:
                logger.info("File {} uploaded successfully.".format(file_name))
                break

    def configure(self, cfg):
        logger.info("Configuring the board ...")
        logger.debug("Putting certificates...")
        self._save_cert_to_file("/var/aos/online.crt.pem", cfg.online_certificate)
        self._save_cert_to_file("/var/aos/offline.crt.pem", cfg.offline_certificate)
        time.sleep(1)
        logger.debug("Putting info...")
        self._echo_to_file("/var/aos/vin", cfg.vin)
        self._echo_to_file("/var/aos/claim", cfg.user_claim)
        self._echo_to_file("/var/aos/sm_service_discovery", cfg.service_discovery_uri)

        logger.debug("Running AOS provisioning script STEP2")
        while True:
            try:
                ret = self.connector.execute_script("/xt/scripts/aos-provisioning.step2.sh")
                if ret.exit_code:
                    logger.error("Failed to run AOS provisioning script STEP2")
                    raise AssertionError
                break
            except ValueError:
                pass
        logger.debug("AOS provisioning script STEP2 successful finished")

    def perform_deprovisioning(self):
        logger.debug("Running AOS deprovisioning script")
        while True:
            try:
                ret = self.connector.execute_script("/xt/scripts/aos-provisioning.step2.sh deprovisioning")
                if ret.exit_code:
                    logger.error("Failed to run AOS deprovisioning script")
                    raise AssertionError
                break
            except ValueError:
                pass
        logger.debug("AOS deprovisioning script successful finished")

    def get_model_name(self):
        """ Obtains model name and version"""
        logger.info("Obtaining model name ...")

        if self._is_model_name_file_present():
            model_name = self.connector.execute("cat %s" % self.PATH_MODEL_NAME).data
        else:
            model_name = "Dev board; 1.0"

        if isinstance(model_name, bytes):
            model_name = model_name.decode()

        if not model_name:
            logger.info(" .. model name is absent. Please update you VM image with a fresh copy!")
            return "VM test", "0.1"

        model_name_chunks = model_name.strip().split(";")
        model_name_name_chunk = model_name_chunks[0].strip()
        if len(model_name_chunks) > 1:
            model_name_version_chunk = model_name_chunks[1].strip()
        else:
            model_name_version_chunk = "0.1"

        logger.info(" .. model name: '{}' version: '{}'".format(model_name_name_chunk, model_name_version_chunk))
        return model_name_name_chunk, model_name_version_chunk


class BoardVirtual(BoardBase):
    PATH_HW_ID = '/etc/guid'
    PATH_SM_CERTS = '/var/aos/servicemanager/data/fcrypt'
    PATH_VIS_CFG = '/var/aos/vis/visconfig.json'
    PATH_SERVICE_MANAGER_CFG = '/var/aos/servicemanager/aos_servicemanager.cfg'

    def __init__(self, address, port=22, cred=None):
        super(BoardVirtual, self).__init__()
        self._address = address
        self._port = port
        self._cred = cred

    def init_connector(self):
        ssh = SSHConnector(self._address, self._port, self._cred)
        ssh.connect()

        return ssh

    def _generate_pair(self, p_type):
        self._create_certs_dir()

        pkeys_prefix = '{}/vehicle_{}.key.pem'.format(BoardVirtual.PATH_SM_CERTS, p_type)
        # generate private
        cmd = "openssl genrsa -out {} {}".format(pkeys_prefix, 2048)
        resp = self.connector.execute(cmd)
        if resp.exit_code:
            logger.error('Failed to generate key.')
            raise BoardError("Failed to generate key.")

        # generate public
        public_name = '.'.join((pkeys_prefix, 'pub'))
        cmd = "openssl rsa -in {} -outform " \
              "PEM -pubout -out {}".format(pkeys_prefix, public_name)
        resp = self.connector.execute(cmd)
        if resp.exit_code:
            logger.error('Failed to generate public key.')
            raise BoardError("Failed to generate public key.")

        cmd = "cat {}".format(public_name)
        pub_key = self.connector.execute(cmd).data

        return pub_key

    def _define_hw_id(self):
        """ Generates a HWID for the board. """
        guid = str(uuid.uuid4())
        cmd = "echo {} > {}".format(guid, BoardVirtual.PATH_HW_ID)
        ret = self.connector.execute(cmd)

        if ret.exit_code:
            logger.debug('Failed to set HW ID.')
            return

        return guid

    def _is_hw_id(self):
        """ Checks a HWID. """
        ret = self.connector.execute(
            "test -e {}".format(BoardVirtual.PATH_HW_ID))
        if ret.exit_code:
            return False

        return True

    def _is_model_name_file_present(self):
        """ Checks presence if model name file. """
        ret = self.connector.execute(
            "test -e {}".format(BoardVirtual.PATH_MODEL_NAME))
        if ret.exit_code:
            return False

        return True

    def _create_certs_dir(self):
        """ Creates a certificates directory. """
        cmd = "mkdir -p {}".format(BoardVirtual.PATH_SM_CERTS)
        resp = self.connector.execute(cmd)
        if resp.exit_code:
            logger.error("Failed to create certificates dir")
            raise BoardError("Failed to create certificates dir")

    def _set_certificates(self, online_cert_cont, offline_cert_cont):
        """ Saves certificates on board. """
        logger.debug("Setting the certificates to %s ...",
                     BoardVirtual.PATH_SM_CERTS)

        self._create_certs_dir()

        cert_file = "{}/{}".format(BoardVirtual.PATH_SM_CERTS, 'vehicle_offline.crt.pem')
        cmd = "echo '{}' > {}".format(offline_cert_cont, cert_file)
        ret_offline = self.connector.execute(cmd, debug=False)

        cert_file = "{}/{}".format(BoardVirtual.PATH_SM_CERTS, 'vehicle_online.crt.pem')
        cmd = "echo '{}' > {}".format(online_cert_cont, cert_file)
        ret_online = self.connector.execute(cmd, debug=False)

        if ret_offline.exit_code or ret_online.exit_code:
            raise BoardError("Failed to set certificates.")

    _STORAGE_ADAPTER = 'storageadapter'
    _KEY_VIN = 'Attribute.Vehicle.VehicleIdentification.VIN'
    _KEY_CLAIM = 'Attribute.Vehicle.UserIdentification.Users'

    def _update_vis_config(self, vin, claim):
        logger.debug("Updating VIS configuration ...")

        ret = self.connector.execute(
            "cat {}".format(BoardVirtual.PATH_VIS_CFG)).data
        try:
            config = json.loads(ret)
        except ValueError as e:
            logger.debug(e)
            raise BoardError("Failed to set VIS configuration.")

        try:
            for pos, a in enumerate(config['Adapters']):
                if BoardVirtual._STORAGE_ADAPTER in a['Plugin']:
                    data = a['Params']['Data']
                    data[BoardVirtual._KEY_VIN]['Value'] = vin
                    data[BoardVirtual._KEY_CLAIM]['Value'] = [claim]
        except KeyError as e:
            logger.debug(e)
            raise BoardError("Failed to set VIS configuration")

        vis_cfg = json.dumps(config, indent=4)

        cmd = "echo '{}' > {}".format(vis_cfg, BoardVirtual.PATH_VIS_CFG)
        self.connector.execute(cmd)

    def _update_service_manager_config(self, service_discovery_url):
        logger.debug("Updating service manager configuration ...")

        ret = self.connector.execute(
            "cat {}".format(BoardVirtual.PATH_SERVICE_MANAGER_CFG)).data
        try:
            config = json.loads(ret)
        except ValueError as e:
            logger.debug(e)
            raise BoardError("Failed to update service manager configuration.")
        try:
            if config["serviceDiscovery"] != service_discovery_url:
                logger.debug("Service discovery url: {} changing to: {}".format(
                    config["serviceDiscovery"],
                    service_discovery_url))
                config["serviceDiscovery"] = service_discovery_url
        except KeyError as e:
            logger.debug(e)
            raise BoardError("Failed to set service manager configuration")

        sm_cfg = json.dumps(config, indent=4)

        cmd = "echo '{conf_data}' > {conf_file_name}".format(
            conf_file_name=BoardVirtual.PATH_SERVICE_MANAGER_CFG,
            conf_data=sm_cfg)
        self.connector.execute(cmd)

    def _restart_aos_services(self):
        logger.debug("Restarting services ...")

        for s in ("aos-vis", "aos-servicemanager"):
            logger.debug("Enabling %s ...", s)
            self.connector.execute("systemctl enable {}".format(s))
            logger.debug("Restarting %s ...", s)
            self.connector.execute("systemctl restart {}".format(s))

    def get_hw_id(self):
        """ Obtains a board HWID"""
        logger.info("Obtaining hardware ID ...")

        if self._is_hw_id():
            hw_id = self.connector.execute(
                "cat {}".format(BoardVirtual.PATH_HW_ID)).data
        else:
            # make a random UUID
            hw_id = self._define_hw_id()

        if isinstance(hw_id, bytes):
            hw_id = hw_id.decode()

        return hw_id.strip()

    def get_vin(self):
        """ Obtains VIN. """
        logger.info("Obtaining VIN ...")
        vis_config = self.connector.execute("cat {}".format(BoardVirtual.PATH_VIS_CFG)).data
        if not vis_config:
            return None

        vin = None
        try:
            vis_data = json.loads(vis_config)
            for pos, a in enumerate(vis_data["Adapters"]):
                if BoardVirtual._STORAGE_ADAPTER in a["Plugin"]:
                    data = a["Params"]["Data"]
                    vin = data[BoardVirtual._KEY_VIN]["Value"]
                    if vin is not None and vin == "TestVIN":
                        vin = None
                    break
        except Exception:
            logger.warning("Can't read VIN for virtual board.")

        return vin

    def get_model_name(self):
        """ Obtains model name and version"""
        logger.info("Obtaining model name ...")

        if self._is_model_name_file_present():
            model_name = self.connector.execute("cat %s" % self.PATH_MODEL_NAME).data
        else:
            model_name = "dev VM; 1.1"

        if isinstance(model_name, bytes):
            model_name = model_name.decode()

        if not model_name:
            logger.info(" .. model name is absent. Please update you VM image with a fresh copy!")
            return "VM test", "0.1"

        model_name_chunks = model_name.strip().split(";")
        model_name_name_chunk = model_name_chunks[0].strip()
        if len(model_name_chunks) > 1:
            model_name_version_chunk = model_name_chunks[1].strip()
        else:
            model_name_version_chunk = "0.1"

        logger.info(" .. model name: '{}' version: '{}'".format(model_name_name_chunk, model_name_version_chunk))
        return model_name_name_chunk, model_name_version_chunk

    def configure(self, cfg):
        logger.info("Configuring the board ...")
        self._set_certificates(cfg.online_certificate, cfg.offline_certificate)
        self._update_vis_config(cfg.vin, cfg.user_claim)
        self._update_service_manager_config(cfg.service_discovery_uri)
        self._restart_aos_services()

    def perform_deprovisioning(self):
        logger.info("Disabling service manager...")
        self.connector.execute("systemctl stop aos-servicemanager")
        self.connector.execute("systemctl disable aos-servicemanager")
        self.connector.execute("cd /var/aos/servicemanager && /usr/bin/aos_servicemanager -reset")


class Config(object):
    """ Contains a board configuration. """

    def __init__(self):
        self._hw_id = None
        self._vin = None
        self._keys = None
        self._model = None
        self._manufacturer = None
        self._online_cert = None
        self._offline_cert = None
        self._user_claim = None
        self._discovery_uri = None

    @property
    def hw_id(self):
        return self._hw_id

    @hw_id.setter
    def hw_id(self, value):
        self._hw_id = value

    @property
    def vin(self):
        return self._vin

    @vin.setter
    def vin(self, value):
        self._vin = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def offline_certificate(self):
        return self._offline_cert

    @offline_certificate.setter
    def offline_certificate(self, value):
        self._offline_cert = value

    @property
    def online_certificate(self):
        return self._online_cert

    @online_certificate.setter
    def online_certificate(self, value):
        self._online_cert = value

    @property
    def user_claim(self):
        return self._user_claim

    @user_claim.setter
    def user_claim(self, value):
        self._user_claim = value

    def set_keys(self, keys):
        self._keys = keys

    def get_public_online(self):
        return self._keys.online

    def get_public_offline(self):
        return self._keys.offline

    @property
    def service_discovery_uri(self):
        return self._discovery_uri

    @service_discovery_uri.setter
    def service_discovery_uri(self, value):
        self._discovery_uri = value

    def validate(self):
        if self.vin is None:
            raise ConfigValidationError("VIN code is not set.")

        if self.offline_certificate is None:
            raise ConfigValidationError("Offline certificate is not defined.")

        if self.online_certificate is None:
            raise ConfigValidationError("Online certificate is not defined.")

        if self.user_claim is None:
            raise ConfigValidationError("User claim is not defined.")
