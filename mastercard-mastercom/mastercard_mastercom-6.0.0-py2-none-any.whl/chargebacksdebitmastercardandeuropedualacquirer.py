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

class ChargebacksDebitMasterCardAndEuropeDualAcquirer(BaseObject):
    """
    
    """

    __config = {
        
        "2e0f6ff9-6aa9-4603-a3aa-b1bda210c5ad" : OperationConfig("/mastercom/v6/chargebacks/debitmc/acknowledge", "update", [], []),
        
        "309b1ef2-f657-4e61-974c-7b9a2953e84a" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/debitmc", "create", [], []),
        
        "f5264d5a-01cc-437b-b17e-e94049b3def6" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/debitmc/{chargeback-id}/reversal", "create", [], []),
        
        "1aa7b90c-3bcb-44ed-a5de-082fea727c39" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/debitmc/{chargeback-id}/documents", "query", [], ["format"]),
        
        "849e1f47-2f31-433f-bb4f-574f02f4e675" : OperationConfig("/mastercom/v6/chargebacks/debitmc/imagestatus", "update", [], []),
        
        "3ade515b-1dc8-47c9-a02e-6df92be8ad8d" : OperationConfig("/mastercom/v6/chargebacks/debitmc/status", "update", [], []),
        
        "7bb75b5d-6a2b-4819-a1cc-419f79df963a" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/debitmc/{chargeback-id}", "update", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())



    def acknowledgeReceivedChargebacks(self):
        """
        Updates an object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("2e0f6ff9-6aa9-4603-a3aa-b1bda210c5ad", self)





    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @param Dict mapObj, containing the required parameters to create a new object
        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("309b1ef2-f657-4e61-974c-7b9a2953e84a", ChargebacksDebitMasterCardAndEuropeDualAcquirer(mapObj))






    @classmethod
    def createReversal(cls,mapObj):
        """
        Creates object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @param Dict mapObj, containing the required parameters to create a new object
        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("f5264d5a-01cc-437b-b17e-e94049b3def6", ChargebacksDebitMasterCardAndEuropeDualAcquirer(mapObj))











    @classmethod
    def retrieveDocumentation(cls,criteria):
        """
        Query objects of type ChargebacksDebitMasterCardAndEuropeDualAcquirer by id and optional criteria
        @param type criteria
        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("1aa7b90c-3bcb-44ed-a5de-082fea727c39", ChargebacksDebitMasterCardAndEuropeDualAcquirer(criteria))


    def chargebacksImageStatus(self):
        """
        Updates an object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("849e1f47-2f31-433f-bb4f-574f02f4e675", self)






    def chargebacksStatus(self):
        """
        Updates an object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("3ade515b-1dc8-47c9-a02e-6df92be8ad8d", self)






    def update(self):
        """
        Updates an object of type ChargebacksDebitMasterCardAndEuropeDualAcquirer

        @return ChargebacksDebitMasterCardAndEuropeDualAcquirer object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("7bb75b5d-6a2b-4819-a1cc-419f79df963a", self)






