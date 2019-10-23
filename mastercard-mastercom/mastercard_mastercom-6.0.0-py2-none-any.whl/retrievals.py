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

class Retrievals(BaseObject):
    """
    
    """

    __config = {
        
        "8b7250b7-c540-42d0-9a9b-bbac1a4d5902" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments", "create", [], []),
        
        "c8274e2b-d0f3-47df-8c57-c2b16a2f3e3f" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests", "create", [], []),
        
        "f680b481-536c-462b-9478-54b213d38458" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/loaddataforretrievalrequests", "query", [], []),
        
        "70a9426a-34a2-4fd3-848e-6b93a533fcc2" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/{request-id}/documents", "query", [], ["format"]),
        
        "e81d2ac8-c6b6-4074-bc6d-8cb9ea062301" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments/response", "create", [], []),
        
        "97edd004-e1a9-4fbb-8be5-6a793fca194c" : OperationConfig("/mastercom/v6/retrievalrequests/imagestatus", "update", [], []),
        
        "08e17720-189f-4a1e-bc7c-a116621d9cfa" : OperationConfig("/mastercom/v6/retrievalrequests/status", "update", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


    @classmethod
    def acquirerFulfillARequest(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("8b7250b7-c540-42d0-9a9b-bbac1a4d5902", Retrievals(mapObj))






    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("c8274e2b-d0f3-47df-8c57-c2b16a2f3e3f", Retrievals(mapObj))











    @classmethod
    def getPossibleValueListsForCreate(cls,criteria):
        """
        Query objects of type Retrievals by id and optional criteria
        @param type criteria
        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("f680b481-536c-462b-9478-54b213d38458", Retrievals(criteria))






    @classmethod
    def getDocumentation(cls,criteria):
        """
        Query objects of type Retrievals by id and optional criteria
        @param type criteria
        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("70a9426a-34a2-4fd3-848e-6b93a533fcc2", Retrievals(criteria))

    @classmethod
    def issuerRespondToFulfillment(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("e81d2ac8-c6b6-4074-bc6d-8cb9ea062301", Retrievals(mapObj))







    def retrievalFullfilmentImageStatus(self):
        """
        Updates an object of type Retrievals

        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("97edd004-e1a9-4fbb-8be5-6a793fca194c", self)






    def retrievalFullfilmentStatus(self):
        """
        Updates an object of type Retrievals

        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("08e17720-189f-4a1e-bc7c-a116621d9cfa", self)






