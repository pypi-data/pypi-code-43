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

class Chargebacks(BaseObject):
    """
    
    """

    __config = {
        
        "9f354880-d03d-4812-ae4a-616fa57cf291" : OperationConfig("/mastercom/v6/chargebacks/acknowledge", "update", [], []),
        
        "24cca337-ed31-476b-9bb1-f1f44bdb7184" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks", "create", [], []),
        
        "fe6026af-5277-4b50-be31-4d9f59935a51" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/{chargeback-id}/reversal", "create", [], []),
        
        "a95d2be1-ecfa-4d6f-8b47-d2c8a6813c4d" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/{chargeback-id}/documents", "query", [], ["format"]),
        
        "ce2df25d-d2fe-465b-b062-4b7593196f75" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/loaddataforchargebacks", "create", [], []),
        
        "f8751748-bfcd-48f0-a23b-e7d2be836cb1" : OperationConfig("/mastercom/v6/chargebacks/imagestatus", "update", [], []),
        
        "e3623a3b-785c-4e0d-b42e-f9cb3b014bea" : OperationConfig("/mastercom/v6/chargebacks/status", "update", [], []),
        
        "2e5dda38-0b78-4aa7-9c5c-2a13397d5613" : OperationConfig("/mastercom/v6/claims/{claim-id}/chargebacks/{chargeback-id}", "update", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())



    def acknowledgeReceivedChargebacks(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("9f354880-d03d-4812-ae4a-616fa57cf291", self)





    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type Chargebacks

        @param Dict mapObj, containing the required parameters to create a new object
        @return Chargebacks of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("24cca337-ed31-476b-9bb1-f1f44bdb7184", Chargebacks(mapObj))






    @classmethod
    def createReversal(cls,mapObj):
        """
        Creates object of type Chargebacks

        @param Dict mapObj, containing the required parameters to create a new object
        @return Chargebacks of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("fe6026af-5277-4b50-be31-4d9f59935a51", Chargebacks(mapObj))











    @classmethod
    def retrieveDocumentation(cls,criteria):
        """
        Query objects of type Chargebacks by id and optional criteria
        @param type criteria
        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("a95d2be1-ecfa-4d6f-8b47-d2c8a6813c4d", Chargebacks(criteria))

    @classmethod
    def getPossibleValueListsForCreate(cls,mapObj):
        """
        Creates object of type Chargebacks

        @param Dict mapObj, containing the required parameters to create a new object
        @return Chargebacks of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("ce2df25d-d2fe-465b-b062-4b7593196f75", Chargebacks(mapObj))







    def chargebacksImageStatus(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("f8751748-bfcd-48f0-a23b-e7d2be836cb1", self)






    def chargebacksStatus(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("e3623a3b-785c-4e0d-b42e-f9cb3b014bea", self)






    def update(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("2e5dda38-0b78-4aa7-9c5c-2a13397d5613", self)






