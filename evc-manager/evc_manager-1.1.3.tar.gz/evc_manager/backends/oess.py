""" OESS backend module. """


import sys
import time
import copy
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # pylint: disable=E1101
from ..libs.core.cli import CliOptions
from ..libs.core.log import info
from ..libs.core.log import warn
from ..libs.core.log import debug
from ..libs.models.evc import EthernetVirtualCircuit
from ..libs.models.nni import NNI
from ..libs.models.uni import UNI
from ..libs.models.metrics import Metrics
from ..libs.models.current_config import CurrentConfig
from ..libs.models.mac_address import MacAddress
from .generic_backend import Backend


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint: disable=E1101


class Oess(Backend):
    """ OESS backend class. """

    get_existing_circuits = 'services/data.cgi?action=get_existing_circuits'
    get_workgroups = 'services/data.cgi?action=get_workgroups'
    get_nodes = 'services/data.cgi?action=get_nodes'
    get_device_interfaces = 'services/data.cgi?action=get_node_interfaces'
    query_vlan_availability = 'services/data.cgi?action=is_vlan_tag_available'
    get_path = 'services/data.cgi?action=get_shortest_path'
    provision_circuit = 'services/provisioning.cgi?action=provision_circuit'
    remove_circuit = "services/provisioning.cgi?action=remove_circuit"

    def authenticate(self):
        """

        :param: use_input_file: if provided, operates offline
        """
        self.user = CliOptions().user
        self.password = CliOptions().password
        self.url = CliOptions().backend_url
        self.tenant = CliOptions().tenant
        self.tenant_id = None  # pylint: disable=W0201
        self._send_get()
        self.get_workgroup()

    def _send_get(self, query=None, payload=None):
        """ Send HTTP Request to OESS """
        if CliOptions().verbose in ['warning', 'debug']:
            return self._send_get_final(query, payload)
        else:
            try:
                return self._send_get_final(query, payload)
            except requests.exceptions.ConnectTimeout as error:
                info(error)
                sys.exit(1)  # Error Code 1 - Connection Timeout.
            except Exception as error:  # pylint: disable=W0703
                info(error)
                sys.exit(2)  # Error Code 2 - Unknown

    def _send_get_final(self, query=None, payload=None):
        """ Send HTTP Request to OESS """

        if not self.session_request:
            # Confirm if authenticated
            self.session_request = requests.Session()
            self.session_request.auth = (self.user, self.password)
            debug("URL: %s" % self.url)
            try:
                request = self.session_request.get(self.url, verify=False, timeout=4)

            except requests.exceptions.ConnectTimeout:
                msg = "ERROR: Not possible to connect to OESS. "
                msg += "Confirm OESS is running."
                raise requests.exceptions.ConnectTimeout(msg)

            except Exception as error:
                raise Exception(error)

            debug("Query result is %s" % request)
            if request.status_code == 200:
                return True
            else:
                raise Exception("Error: OESS Authentication Failed!")

        url = self.url + query
        if payload is not None:
            url_ext = ""
            for item in payload:
                url_ext = url_ext + '&' + item + '=' + payload[item]
            url = url + url_ext

        debug("URL: %s" % url)

        request = self.session_request.get(url, verify=False)

        if request.status_code != 200:
            raise Exception("Error on query: %s\nStatus Code: %s" % (url, request.status_code))

        results = json.loads(request.text)
        debug("Query result is %s" % results)

        if 'results' not in results:
            raise Exception(results['error'])

        return results['results']

    def get_evcs(self):
        """ Returns a list of all EVCs """
        query = self.get_existing_circuits
        payload = {'workgroup_id': self.tenant_id}

        return self.process_oess_circuits(self._send_get(query, payload))

    def get_workgroup(self):
        """ Get OESS's workgroup/tenant ID using the name provided """
        query = self.get_workgroups
        groups = self._send_get(query)

        for group in groups:
            if group['name'] == self.tenant:
                self.tenant_id = group['workgroup_id']  # pylint: disable=W0201

        if not self.tenant_id:
            raise Exception("OESS workgroup not found!")

    @staticmethod
    def get_unis(endpoints):
        """

        :param endpoints:
        :return:
        """
        unis = list()
        for endpoint in endpoints:
            uni = UNI()
            uni.device = endpoint['node']
            uni.interface_name = endpoint['interface']
            uni.interface_description = endpoint['interface_description']
            uni.tag.type = 'vlan'
            uni.tag.value = endpoint['tag']
            for mac_addr in endpoint['mac_addrs']:
                uni.mac_addresses.append(MacAddress(mac_addr['mac_address']))
            unis.append(copy.deepcopy(uni))
            del uni
        return unis

    @staticmethod
    def process_link(links):
        """

        :param links:
        :return:
        """
        path = list()
        for span in links:
            link = NNI()
            link.device_a = span['node_a']
            link.interface_a = span['interface_a']
            link.device_z = span['node_z']
            link.interface_z = span['interface_z']
            link.name = span['name']
            path.append(link)
            del link
        return path

    def get_requested_paths(self, circuit):
        """

        :param circuit:
        :return:
        """
        requested_paths = list()
        requested_paths.append(self.process_link(circuit['links']))
        if len(circuit['backup_links']) > 0:
            requested_paths.append(self.process_link(circuit['backup_links']))
        return requested_paths

    @staticmethod
    def get_metrics(bandwidth):
        """

        :param bandwidth:
        :return:
        """
        metrics = Metrics()
        metrics.min_bw = bandwidth
        return metrics

    @staticmethod
    def is_up(circuit):
        """

        :param circuit:
        :return:
        """
        if circuit['operational_state'] == 'up':
            return True
        return False

    def get_current_config(self, oess_circuit, evc):
        """

        :param oess_circuit:
        :param evc
        :return:
        """
        current_config = CurrentConfig()
        current_config.backend = 'oess'
        current_config.backend_evc_id = oess_circuit['circuit_id']
        current_config.is_active = oess_circuit['state']
        current_config.is_optimized = True
        current_config.is_up = self.is_up(oess_circuit)

        if oess_circuit['active_path'] == 'primary':
            current_config.current_path = evc.paths[0]
        else:
            current_config.is_backup = True
            current_config.current_path = evc.paths[1]
        return current_config

    @staticmethod
    def get_time_timestamp(circuit, action='created_on'):
        """

        :param circuit:
        :param action:
        :return:
        """
        p_time = circuit[action] if action in circuit else 0
        if isinstance(p_time, str):
            oess_pattern = '%m/%d/%Y %H:%M:%S'
            p_time = int(time.mktime(time.strptime(p_time, oess_pattern)))
        return p_time

    @staticmethod
    def get_external_identifier(oess_circuit):
        """

        :param oess_circuit:
        :return:
        """
        idx = 'external_identifier'
        ext_id = oess_circuit[idx] if idx in oess_circuit else 0
        if not ext_id:
            return 0
        return ext_id

    def process_oess_circuits(self, oess_circuits):
        """

        :param oess_circuits:
        """
        evcs = list()
        for oess_circuit in oess_circuits:
            evcs.append(copy.deepcopy(self.process_oess_circuit(oess_circuit)))

        return evcs

    def process_oess_circuit(self, circuit):
        """

        :param circuit:
        :return:
        """
        evc = EthernetVirtualCircuit()
        evc.name = circuit['description']
        evc.unis = self.get_unis(circuit['endpoints'])
        evc.paths = self.get_requested_paths(circuit)
        evc.provisioning_time = self.get_time_timestamp(circuit)
        evc.decommissioning_time = 0
        evc.tenant = circuit['workgroup']['name']
        evc.metrics = self.get_metrics(circuit['bandwidth'])
        evc.external_id = self.get_external_identifier(circuit)
        evc.current_config = self.get_current_config(circuit, evc)
        return evc

    def add_evc(self, new_evc):
        """ Add or Update EVC based on the provided EVC(s) name(s)

        Args:
            EVC class
        Returns:

        """
        backup_path = None

        msg = self.evaluate_nodes(new_evc)
        if msg['result'] == 'error':
            info("Error: %s" % msg["msg"])
            return msg

        msg = self.evaluate_unis(new_evc)
        if msg['result'] == 'error':
            info("Error: %s" % msg["msg"])
            return msg

        debug("Requesting Paths...")
        if new_evc.paths:
            primary_path = self.oess_get_path(new_evc.unis,
                                              requested=new_evc.path[0])

            if len(new_evc.paths) >= 2:
                backup_path = self.oess_get_path(new_evc.unis,
                                                 requested=new_evc.path[1])

        else:
            primary_path = self.oess_get_path(new_evc.unis)
            backup_path = self.oess_get_path(new_evc.unis, primary=primary_path)

        debug('Primary Path: %s' % primary_path)
        debug('Backup Path: %s' % backup_path)

        warn("Provisioning circuit...")

        if self.oess_provision_circuit(new_evc, primary_path, backup_path):
            msg = {'result': 'created',
                   'msg': 'EVC %s provisioned.' % new_evc.name}
            return msg

        return {'result': 'error',
                'msg': 'Error provisioning EVC %s' % new_evc.name}

    def evaluate_nodes(self, new_evc):
        """ Evaluate if the OESS's switch is up. Otherwise, UNIs are not
        recognized. """

        for uni in new_evc.unis:
            debug("Evaluating each node provided")
            msg = self.oess_evaluate_device(uni.device)
            if msg['result'] == 'error':
                return msg

        return {'result': 'ok'}

    def evaluate_unis(self, new_evc):
        """ Evaluate if the EVC's params are correct and if the VLANs
        are available.

        Args:
            new_evc: EVC class
        Returns:
            True if ok
            False if not ok
        """
        for uni in new_evc.unis:
            debug("Evaluating each UNI provided")
            msg = self.oess_evaluate_device_interfaces(uni)
            if msg['result'] == 'error':
                return msg

            debug("Verifying if VLANs provided are available")
            msg = self.oess_evaluate_vlans_availability(uni)
            if msg['result'] == 'error':
                return msg

        return {'result': 'ok'}

    def oess_evaluate_device(self, device):
        """ Get existing and UP devices """
        query = self.get_nodes
        devices = self._send_get(query)

        for found_device in devices:
            if found_device["name"] == device:
                if found_device["operational_state"] == "up":
                    if found_device["in_maint"] == "no":
                        return {'result': 'ok'}
        msg = {'result': 'error',
               'msg': 'Device %s not found, DOWN or in maintenance' %
                      device}
        return msg

    def oess_evaluate_device_interfaces(self, uni):
        """ Get existing interfaces for device """
        query = self.get_device_interfaces
        payload = {'node': uni.device}
        device_interfaces = self._send_get(query, payload)

        for device_interface in device_interfaces:
            if device_interface["name"] == uni.interface_name:
                return {'result': 'ok'}

        msg = {'result': 'error',
               'msg': 'Incorrect UNI provided %s:%s' %
                      (uni.device, uni.interface_name)}
        return msg

    def oess_evaluate_vlans_availability(self, uni):
        """ Check if VLAN is available for device and interface provided"""
        query = self.query_vlan_availability
        payload = {'node': uni.device,
                   'interface': uni.interface_name,
                   'vlan': str(uni.tag.value)}
        if self._send_get(query, payload)[0]["available"] in [1]:
            return {'result': 'ok'}

        msg = {'result': 'error',
               'msg': 'VLAN %s not available on device %s interface %s' %
                      (uni.tag.value, uni.device, uni.interface_name)}
        return msg

    def oess_get_path(self, unis, requested=None, primary=None):
        """ Process path """
        query = self.get_path

        # First, try the paths

        for uni in unis:
            query += "&node=%s" % uni.device

        if requested:
            for link in requested:
                query += "&link=%s" % link.name

        elif primary:
            for link in primary:
                query += "&link=%s" % link

        final_path = self._send_get(query)

        path = []
        for link in final_path:
            path.append(link['link'])

        return path

    def oess_provision_circuit(self, new_evc, primary_path, backup_path):
        """ Create OESS Provisioning Query """

        query = self.provision_circuit
        query += '&workgroup_id=%s' % self.tenant_id

        try:

            for uni in new_evc.unis:
                query += '&node=%s&interface=%s&tag=%s' % \
                         (uni.device, uni.interface_name, uni.tag.value)

            for link in primary_path:
                query += "&link=" + link

            for link in backup_path:
                query += "&backup_link=" + link

            if not new_evc.provisioning_time:
                query += '&provision_time=-1'
            else:
                query += '&provision_time=%s' % new_evc.provisioning_time

            if not new_evc.decommissioning_time:
                query += '&remove_time=-1'
            else:
                query += '&remove_time=%s' % new_evc.decommissioning_time

            query += '&description=%s' % new_evc.name

            result = self._send_get(query)

            if result["success"] == 1:
                return {'result': 'created',
                        'msg': 'EVC %s created.' % new_evc.name}

        except (KeyError, TypeError):
            return {'result': 'error',
                    'msg': 'EVC %s NOT created.' % new_evc.name}

    def delete_evc(self, evc_to_delete):
        """ Delete EVC with the provided EVC(s) name(s) """
        info('Deleting EVC %s:' % evc_to_delete.name)
        for uni in evc_to_delete.unis:
            info('\tUNI device %s' % uni.device)
            info('\tUNI interface %s' % uni.interface_name)
            info('\tUNI vlan %s' % uni.tag.value)

        try:
            query = self.remove_circuit
            query += "&remove_time=-1"
            query += "&workgroup_id=%s" % self.tenant_id
            query += "&circuit_id=%s" % evc_to_delete.current_config.backend_evc_id

            result = self._send_get(query)

            if result[0]["success"] == 1:
                return {'result': 'deleted',
                        'msg': 'EVC %s deleted.' % evc_to_delete.name}

            return {'result': 'error',
                    'msg': 'EVC %s NOT deleted.' % evc_to_delete.name}

        except (KeyError, AttributeError, TypeError):
            return {'result': 'error',
                    'msg': 'EVC %s NOT deleted.' % evc_to_delete.name}
