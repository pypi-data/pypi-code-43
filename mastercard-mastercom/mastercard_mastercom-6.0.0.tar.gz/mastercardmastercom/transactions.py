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

class Transactions(BaseObject):
    """
    
    """

    __config = {
        
        "a5ebf4e0-7017-48fc-8969-d814d46f90b0" : OperationConfig("/mastercom/v6/claims/{claim-id}/transactions/clearing/{transaction-id}", "read", [], []),
        
        "29e2180e-9b72-4be6-88e4-9e9a660f0d3a" : OperationConfig("/mastercom/v6/claims/{claim-id}/transactions/authorization/{transaction-id}", "read", [], []),
        
        "418badd5-263b-4ec3-a85a-6cfd8cff1eb0" : OperationConfig("/mastercom/v6/transactions/search", "create", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())






    @classmethod
    def retrieveClearingDetail(cls,id,criteria=None):
        """
        Returns objects of type Transactions by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of Transactions
        @raise ApiException: raised an exception from the response status
        """
        mapObj =  RequestMap()
        if id:
            mapObj.set("id", id)

        if criteria:
            if (isinstance(criteria,RequestMap)):
                mapObj.setAll(criteria.getObject())
            else:
                mapObj.setAll(criteria)

        return BaseObject.execute("a5ebf4e0-7017-48fc-8969-d814d46f90b0", Transactions(mapObj))






    @classmethod
    def retrieveAuthorizationDetail(cls,id,criteria=None):
        """
        Returns objects of type Transactions by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of Transactions
        @raise ApiException: raised an exception from the response status
        """
        mapObj =  RequestMap()
        if id:
            mapObj.set("id", id)

        if criteria:
            if (isinstance(criteria,RequestMap)):
                mapObj.setAll(criteria.getObject())
            else:
                mapObj.setAll(criteria)

        return BaseObject.execute("29e2180e-9b72-4be6-88e4-9e9a660f0d3a", Transactions(mapObj))


    @classmethod
    def searchForTransaction(cls,mapObj):
        """
        Creates object of type Transactions

        @param Dict mapObj, containing the required parameters to create a new object
        @return Transactions of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("418badd5-263b-4ec3-a85a-6cfd8cff1eb0", Transactions(mapObj))







