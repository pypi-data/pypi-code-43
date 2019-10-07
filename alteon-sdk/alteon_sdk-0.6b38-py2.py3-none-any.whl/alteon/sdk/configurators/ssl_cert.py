#!/usr/bin/env python
# Copyright (c) 2019 Radware LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# @author: Leon Meguira, Radware


from radware.sdk.common import RadwareParametersStruct, RadwareParametersExtension
from radware.alteon.sdk.alteon_configurator import MSG_UPDATE, MSG_DELETE, AlteonConfigurator
from radware.alteon.beans.SlbNewSslCfgCertsTable import *
from typing import Optional, List, ClassVar


class CertType(RadwareParametersExtension):
    group = 'group'
    cert = 'cert'


class EnumSlbSslCertsType(BaseBeanEnum):
    serverCertificate = 3
    trustedCertificate = 4
    intermediateCertificate = 5


CERT_TYPE_IMPORT = dict(
    serverCertificate='cert',
    intermediateCertificate='inca',
    trustedCertificate='clca'
)
CERT_TYPE_EXPORT = dict(
    serverCertificate='srvcrt',
    intermediateCertificate='inca',
    trustedCertificate='trstca'
)


class SSLCertParameters(RadwareParametersStruct):
    index: str
    certificate_type: EnumSlbSslCertsType
    description: Optional[str]
    intermediate_ca_name: Optional[str]
    intermediate_ca_type: Optional[CertType]
    content: Optional[str]

    def __init__(self, index: str = None, certificate_type: EnumSlbSslCertsType = None):
        self.index = index
        self.certificate_type = certificate_type
        self.description = None
        self.intermediate_ca_name = None
        self.intermediate_ca_type = None
        self.content = None


bean_map = {
    SlbNewSslCfgCertsTable: dict(
        struct=SSLCertParameters,
        direct=True,
        attrs=dict(
            ID='index',
            Type='certificate_type',
            Name='description',
            IntermcaChainName='intermediate_ca_name',
            IntermcaChainType='intermediate_ca_type'
        )
    )
}


class SSLCertConfigurator(AlteonConfigurator):
    parameters_class: ClassVar[SSLCertParameters]

    def __init__(self, alteon_connection):
        super(SSLCertConfigurator, self).__init__(bean_map, alteon_connection)

    def _read(self, parameters: SSLCertParameters) -> SSLCertParameters:
        self._read_device_beans(parameters)
        if self._beans:
            resource = 'getcert?id=' + parameters.index + '&src=txt&type=' + \
                       CERT_TYPE_EXPORT[parameters.certificate_type.name]
            parameters.content = self._rest.read_data_object(resource)
            return parameters

    def _update(self, parameters: SSLCertParameters, dry_run: bool) -> str:
        if parameters.content:
            self._rest.update_data_object('sslcertimport?&id=' + parameters.index + '&renew=1&src=txt&type=' +
                                          CERT_TYPE_IMPORT[parameters.certificate_type.name], parameters.content,
                                          dry_run=dry_run)
        self._write_device_beans(parameters, dry_run=dry_run)
        return self._get_object_id(parameters) + MSG_UPDATE

    def _entry_bean_instance(self, parameters):
        return self._get_bean_instance(SlbNewSslCfgCertsTable, parameters)

    ##override
    def delete(self, parameters: SSLCertParameters, dry_run=False, **kw) -> str:
        log.debug(' {0}: {1}, server: {2}, params: {3}'.format(self.__class__.__name__, self.DELETE.upper(), self.id,
                                                               parameters))
        self_obj = self._entry_bean_instance(parameters)
        self._device_api.delete(self_obj, dry_run=dry_run)
        self_obj.Type = 'certificateRequest'
        self._device_api.delete(self_obj, dry_run=dry_run)
        return self._get_object_id(parameters) + MSG_DELETE

    def read_all(self, parameters: SSLCertParameters = None, **kw) -> List[RadwareParametersStruct]:
        log.debug(' {0}: {1}, server: {2}, params: {3}'.format(self.__class__.__name__, self.READ_ALL.upper(), self.id,
                                                               parameters))
        result = list()
        cert_enum_value = EnumSlbSslCertsType.value_names()
        attrs = self._bean_map[SlbNewSslCfgCertsTable]['attrs']
        instance = self._entry_bean_instance(parameters)
        beans = self._device_api.read_all(instance)
        if beans:
            for bean in beans:
                if bean.Type.name in cert_enum_value:
                    parameters = SSLCertParameters()
                    self._update_param_struct_attrs_from_object(parameters, attrs, bean)
                    result.append(self.read(parameters))
        return result
