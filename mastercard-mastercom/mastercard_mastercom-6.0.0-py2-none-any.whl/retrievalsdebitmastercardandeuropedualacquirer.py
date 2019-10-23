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

class RetrievalsDebitMasterCardAndEuropeDualAcquirer(BaseObject):
    """
    
    """

    __config = {
        
        "92819913-3d67-4387-856c-8934a789d47d" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/debitmc/{request-id}/fulfillments", "create", [], []),
        
        "b0e98a1c-a548-422b-bdaa-d5bf5bdd4ae2" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/debitmc", "create", [], []),
        
        "53a66745-6527-4471-9905-1763516027e5" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/debitmc/{request-id}/documents", "query", [], ["format"]),
        
        "30d92065-9be2-4d6f-bc58-0227ff4a3a60" : OperationConfig("/mastercom/v6/claims/{claim-id}/retrievalrequests/debitmc/{request-id}/fulfillments/response", "create", [], []),
        
        "f102bbe6-6001-438d-a4d4-aba8734f3da4" : OperationConfig("/mastercom/v6/retrievalrequests/debitmc/imagestatus", "update", [], []),
        
        "7084db2a-d1ed-47c3-abbf-a2d2b8d876a7" : OperationConfig("/mastercom/v6/retrievalrequests/debitmc/status", "update", [], []),
        
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
        Creates object of type RetrievalsDebitMasterCardAndEuropeDualAcquirer

        @param Dict mapObj, containing the required parameters to create a new object
        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("92819913-3d67-4387-856c-8934a789d47d", RetrievalsDebitMasterCardAndEuropeDualAcquirer(mapObj))






    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type RetrievalsDebitMasterCardAndEuropeDualAcquirer

        @param Dict mapObj, containing the required parameters to create a new object
        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("b0e98a1c-a548-422b-bdaa-d5bf5bdd4ae2", RetrievalsDebitMasterCardAndEuropeDualAcquirer(mapObj))











    @classmethod
    def getDocumentation(cls,criteria):
        """
        Query objects of type RetrievalsDebitMasterCardAndEuropeDualAcquirer by id and optional criteria
        @param type criteria
        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("53a66745-6527-4471-9905-1763516027e5", RetrievalsDebitMasterCardAndEuropeDualAcquirer(criteria))

    @classmethod
    def issuerRespondToFulfillment(cls,mapObj):
        """
        Creates object of type RetrievalsDebitMasterCardAndEuropeDualAcquirer

        @param Dict mapObj, containing the required parameters to create a new object
        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("30d92065-9be2-4d6f-bc58-0227ff4a3a60", RetrievalsDebitMasterCardAndEuropeDualAcquirer(mapObj))







    def retrievalFullfilmentImageStatus(self):
        """
        Updates an object of type RetrievalsDebitMasterCardAndEuropeDualAcquirer

        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("f102bbe6-6001-438d-a4d4-aba8734f3da4", self)






    def retrievalFullfilmentStatus(self):
        """
        Updates an object of type RetrievalsDebitMasterCardAndEuropeDualAcquirer

        @return RetrievalsDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("7084db2a-d1ed-47c3-abbf-a2d2b8d876a7", self)






