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


class RadwareError(Exception):
    def __init__(self):
        self.message = None

    def __str__(self):
        return self.message


class GeneralError(RadwareError):
    def __init__(self, message):
        self.message = message


class DeviceError(RadwareError):
    def __init__(self, device_type, details=None):
        self.device_type = device_type
        self.message = '\nDevice Error:\n' \
                       'Details: {0}\n'.format(details)


class FunctionError(RadwareError):
    def __init__(self, func, reason=None, status=None):
        self.func = func
        self.reason = reason
        self.status = status
        self.message = '\nFunction Error:\n' \
                       'Function: {0}\n' \
                       'Status: {1}\n' \
                       'Reason: {2}'.format(func, status, reason)


class DeviceFunctionError(FunctionError):
    def __init__(self, func, device_type, reason=None, status=None):
        super(DeviceFunctionError, self).__init__(func, reason, status)
        self.message = '\n{3} Function Error:\n' \
                       'Function: {0}\n' \
                       'Status: {1}\n' \
                       'Reason: {2}'.format(func, status, reason, device_type.name)


class DeviceConfiguratorError(RadwareError):
    def __init__(self, configurator, reason):
        self.configurator = configurator
        self.reason = reason
        self.message = '\nConfigurator: {0}\nReason: {1}'.format(configurator, reason)


class ArgumentTypeError(RadwareError):
    def __init__(self, expected, argument):
        self.expected_class = expected
        self.arg_class = type(argument)
        self.message = '\nArgument Type Error:\n' \
                       'Reason: invalid argument class {0}\n' \
                       'Details: expect argument class {1}.'.format(self.arg_class, expected)


class ArgumentNotExpectedTypeError(RadwareError):
    def __init__(self, argument, details=None):
        self.arg_class = type(argument)
        self.message = '\nArgument Not Expected Type Error:\n' \
                       'Reason: invalid argument class {0}\n' \
                       'Details: {1}.'.format(self.arg_class, details)


class ArgumentNotExpectedError(RadwareError):
    def __init__(self, argument, details=None):
        self.argument = argument
        self.message = '\nArgument Not Expected Error:\n' \
                       'Details: {0}.'.format(details)


class ArgumentMissingError(RadwareError):
    def __init__(self, class_name, arg_name):
        self.class_name = class_name
        self.arg_name = arg_name
        self.message = '\nMissing Argument Error:\n' \
                       'Reason: missing argument {0} on class {1}\n' \
                       'Details: expect argument class {1}.'.format(arg_name, class_name)


class RestRequestError(RadwareError):
    def __init__(self, response):
        self.response = response
        self.message = '\nRest Request Error:\n' \
                       'Status: {0}\n' \
                       'Reason: {1}\n' \
                       'url= {2}\n' \
                       'method= {3}\n' \
                       'body= {4}\n' \
                       'Details: {5}.'.format(response.status, response.reason, response.request.url,
                                              response.request.method, response.request.body, response.content)


class DeviceRestRequestError(DeviceError, RestRequestError):
    def __init__(self, response, device_type):
        DeviceError.__init__(self, device_type)
        RestRequestError.__init__(self, response)
        self.response = response
        self.message = self.message + '\n{0}'.format(device_type.name)
