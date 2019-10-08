# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
import uuid
import requests
from lxml import etree
from urllib.parse import urlparse
from django.utils.translation import gettext as _
from requests.auth import HTTPBasicAuth, HTTPProxyAuth
from quartet_capture.rules import RuleContext
from quartet_output import errors
from quartet_output.transport.http import HttpTransportMixin, user_agent
from quartet_output.models import EndPoint
from quartet_capture import models, rules, errors as capture_errors
from list_based_flavorpack.models import ListBasedRegion


class NumberRequestTransportStep(rules.Step, HttpTransportMixin):
    '''
    Uses the transport information within the `region`.
    '''

    def execute(self, data, rule_context: RuleContext):
        # get the task parameters that we rely on
        try:
            self.info(_('Looking for the task parameter with the target Region. '
                        'Output Name.'))
            param = models.TaskParameter.objects.get(
                task__name=rule_context.task_name,
                name='List-based Region'
            )
            # now see if we can get the output critieria based on the param
            # value
            self.info(_('Found the region param, now looking up the '
                        'Region instance with name %s.'),
                      param.value
                      )
        except models.TaskParameter.DoesNotExist:
            raise capture_errors.ExpectedTaskParameterError(
                _('The task parameter with name List-based Region '
                  'could not be found.  This task parameter is required by '
                  'the NumberRequestTransportStep to function correctly.')
            )
        try:
            region = ListBasedRegion.objects.get(machine_name=param.value)
            # check the url/urn to see if we support the protocol
            protocol = self._supports_protocol(region.end_point)
            self.info('Protocol supported.  Sending message to %s.' %
                      region.end_point.urn)
            response = self._send_message(data, protocol, rule_context, region)
            # Pass response for downstream processing.
            rule_context.context['NUMBER_RESPONSE'] = response.content
        except Exception as e:
            self.error(_("An error occurred while sending request to third party: %s"), str(e))
            raise

    def get_auth(self, region):
        """
        Get's the authentication method and credentials from the
        region record.
        :param region: A ListBasedModel model instance.
        :return: A `requests.auth.HTTPBasicAuth` or `HTTPProxyAuth`
        """
        auth_info = region.authentication_info
        auth = None
        if auth_info:
            auth_type = auth_info.type or ''
            if 'digest' in auth_type.lower():
                auth = HTTPBasicAuth
            elif 'proxy' in auth_type.lower():
                auth = HTTPProxyAuth
            else:
                auth = HTTPBasicAuth
            auth = auth(auth_info.username, auth_info.password)
        return auth
        
    def post_data(self, data: str, rule_context: RuleContext,
                  region: ListBasedRegion,
                  content_type='application/xml',
                  file_extension='xml',
                  http_put=False):
        '''
        :param data_context_key: The key within the rule_context that contains
         the data to post.  If being invoked from the internals of this
         module this is usually the OUTBOUND_EPCIS_MESSSAGE_KEY value of the
         `quartet_output.steps.ContextKeys` Enum.
        :param output_criteria: The output criteria containing the connection
        info.
        :return: The response.
        '''
        if not http_put:
            func = requests.post
        else:
            func = requests.put
        response = func(
            region.end_point.urn,
            data,
            auth=self.get_auth(region),
            headers={'content-type': content_type, 'user-agent': user_agent}
        )
        return response

    def _send_message(
        self,
        data: str,
        protocol: str,
        rule_context: RuleContext,
        region: ListBasedRegion
    ):
        '''
        Sends a message using the protocol specified.
        :param protocol: The scheme of the urn in the output_criteria endpoint.
        :param rule_context: The RuleContext contains the data in the
        OUTBOUND_EPCIS_MESSAGE_KEY value from the `ContextKey` class.
        :param region: The originating region.
        :return: None.
        '''
        content_type = self.get_parameter('content-type', 'application/xml')
        file_extension = self.get_parameter('file-extension', 'xml')
        put_data = self.get_boolean_parameter('put-data')
        if protocol.lower() in ['http', 'https']:
            if not put_data:
                func = self.post_data
            else:
                func = self.put_data
            self.info("request sent %s", data)
            response = func(
                data,
                rule_context,
                region,
                content_type,
                file_extension
            )
            try:
                response.raise_for_status()
            except:
                if response.content:
                    self.info("Error occurred with following response %s", response.content)
                raise
            self.info("Response Received %s", response.content[0:5000])
            return response

    def _supports_protocol(self, endpoint: EndPoint):
        '''
        Inspects the output settings and determines if this step can support
        the protocol or not. Override this to support another or more
        protocols.
        :param EndPoint: the endpoint to inspect
        :return: Returns the supported scheme if the protocol is supported or
        None.
        '''
        parse_result = urlparse(
            endpoint.urn
        )
        if parse_result.scheme.lower() in ['http', 'https']:
            return parse_result.scheme
        else:
            raise errors.ProtocolNotSupportedError(_(
                'The protocol specified in urn %s is not supported by this '
                'step or module.'
            ), endpoint.urn)

    def on_failure(self):
        super().on_failure()

    @property
    def declared_parameters(self):
        return {
            'content-type': 'The content-type to add to the header during any '
                            'http posts, puts, etc. Default is application/'
                            'xml',
            'file-extension': 'The file extension to specify when posting and '
                              'putting data via http. Default is xml'
        }


class UUIDRequestStep(rules.Step):
    '''
    Returns UUIDs.
    Excepts a request data as follows:
    <?xml version="1.0" encoding="UTF-8"?>
    <NumberRequest>
        <Type>UUID</Type>
        <Size>10</Size>
    </NumberRequest>
    '''
    def execute(self, data, rule_context: RuleContext):
        # get the task parameters that we rely on
        try:
            self.info(_('Looking for the task parameter with the target Region. '
                        'Output Name.'))
            param = models.TaskParameter.objects.get(
                task__name=rule_context.task_name,
                name='List-based Region'
            )
            # now see if we can get the output critieria based on the param
            # value
            self.info(_('Found the region param, now looking up the '
                        'Region instance with name %s.'),
                      param.value
                      )
        except models.TaskParameter.DoesNotExist:
            raise capture_errors.ExpectedTaskParameterError(
                _('The task parameter with name List-based Region '
                  'could not be found.  This task parameter is required by '
                  'the NumberRequestTransportStep to function correctly.')
            )
        try:
            region = ListBasedRegion.objects.get(machine_name=param.value)
            # check the url/urn to see if we support the protocol
            root = etree.fromstring(data)
            size = int(root.find('.//Size').text)
            with open(region.file_path, "a") as f:
                for i in range (size):
                    f.write("%s\n" % uuid.uuid1())
        except Exception as e:
            self.info(_("An error occurred while sending request to third party: %s"), str(e))
            self.info(_("Inbound data %s", str(data)))
            raise

    def on_failure(self):
        super().on_failure()

    @property
    def declared_parameters(self):
        return {
            'content-type': 'The content-type to add to the header during any '
                            'http posts, puts, etc. Default is application/'
                            'xml',
            'file-extension': 'The file extension to specify when posting and '
                              'putting data via http. Default is xml'
        }
