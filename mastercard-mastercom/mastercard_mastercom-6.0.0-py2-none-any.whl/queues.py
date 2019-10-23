#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardmastercom import ResourceConfig

class Queues(BaseObject):
    """
    
    """

    __config = {
        
        "85fae546-17e6-49a6-9cf8-06b7f62b6cae" : OperationConfig("/mastercom/v6/queues", "list", [], ["queue-name"]),
        
        "f5b9c8ec-b095-440e-843b-1dfbbd8a24b0" : OperationConfig("/mastercom/v6/queues", "create", [], []),
        
        "528fe816-ae01-434b-945b-f6e8d3aa7f45" : OperationConfig("/mastercom/v6/queues/names", "list", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())




    @classmethod
    def retrieveClaimsFromQueue(cls,criteria=None):
        """
        List objects of type Queues

        @param Dict criteria
        @return Array of Queues object matching the criteria.
        @raise ApiException: raised an exception from the response status
        """

        if not criteria :
            return BaseObject.execute("85fae546-17e6-49a6-9cf8-06b7f62b6cae", Queues())
        else:
            return BaseObject.execute("85fae546-17e6-49a6-9cf8-06b7f62b6cae", Queues(criteria))




    @classmethod
    def retrieveClaimsFromQueueWithDateInterval(cls,mapObj):
        """
        Creates object of type Queues

        @param Dict mapObj, containing the required parameters to create a new object
        @return Queues of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("f5b9c8ec-b095-440e-843b-1dfbbd8a24b0", Queues(mapObj))








    @classmethod
    def retrieveQueueNames(cls,criteria=None):
        """
        List objects of type Queues

        @param Dict criteria
        @return Array of Queues object matching the criteria.
        @raise ApiException: raised an exception from the response status
        """

        if not criteria :
            return BaseObject.execute("528fe816-ae01-434b-945b-f6e8d3aa7f45", Queues())
        else:
            return BaseObject.execute("528fe816-ae01-434b-945b-f6e8d3aa7f45", Queues(criteria))





