#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
   sample state path -  /router[router-name=Base]/ospf[ospf-instance=*]/statistics/neighbor-count/
"""
""" 
    HISTORY Change Log:

    

"""

__title__   = "state"
__version__ = "0"
__status__  = "draft"
__author__  = "Harmeet Sethi"
__date__    = "2019 Oct 10th"

# Generic/Built-in Libs
import re
import sys
import os
import logging
import json
import base64
import time
import datetime
import grpc
import gnmi_pb2
from google.protobuf import json_format
from logging.handlers import RotatingFileHandler

class stateManager():
    """ Provides Mechanism to fetech state configuration Data from DUT.

    """
    class _grpcnamespacemanager:
        """namespace for setting grpc call attributes"""
        def __init__(self,**kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, _dut):
        """ initialize local attributes like dut (name or IP), state-path for getting config. manager will 
            manage grpc sessions for all duts. 
        """
        self.dut = _dut

    def _stateCallBack_getData(self, _path,):
        """ Callback function to get data for specified state hierarchy based on action performed.
                Action: Toggle
                        Configure
                        Delete
            
            filterSpecObj can be used to filter data as per implementation (either before or after grpc call)
      
        """
        data = self._getstatedata(_path)
        #TODO process received data
        data = self._deserialize(data)
        #print(data)
        return data

    def _getstatedata(self, _path):
        """ Function to perform grpc call to fetch data from router
        
        """
        #considering insercure channel fetching data
        channel = grpc.insecure_channel(self.dut)
        stub = gnmi_pb2.gNMIStub(channel)
        attributes = self._grpcnamespacemanager(mode=1, submode=0, prefix='', suppress=False, heartbeat=None, qos=0, aggregate=False, use_alias=False, encoding=0, timeout=60, intervel=60*1000000000)
        grpc_request = self._generate_request(attributes, _path)
        metadata = [('username','admin'), ('password','admin')]
        grpc_response = stub.Subscribe(grpc_request, attributes.timeout, metadata=metadata)
        json_response = []
        try:
            for response in grpc_response:
                if response.HasField('update'):
                    jsn = json_format.MessageToJson (response, preserving_proto_field_name=True)
                    #can perform some operations #TODO
                    # TODO convert json to desired format or evaluate as per requirements
                    #print(jsn)
                    json_response.append(jsn)
        except:
            # TODO exception handling
            pass  
        return json_response
                     
    def _getiterable(self, path='/'):
        ''' module to return paths in a list format
        
        '''
        if path:
            if path[0]=='/':
                if path[-1]=='/':
                    return re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1]
                else:
                    return re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:]
            else:
                if path[-1]=='/':
                    return re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1]
                else:
                    return re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)
        return []
    
    def _extractpath(self, _path='/'):
        ''' module to extract all paths from text
        
        '''
        formatedpath = []
        #iterate and add each element as per YANG tree
        for element in self._getiterable(_path):
            elementName = element.split(r"[", 1)[0]
            elementKeys = re.findall(r'\[(.*?)\]', element)
            elementItems = dict(x.split('=', 1) for x in elementKeys)
            formatedpath.append(gnmi_pb2.PathElem(name=elementName, key=elementItems))
        return gnmi_pb2.Path(elem=formatedpath)

    def _generate_request(self, attributes, _path):
        """ Function to create and return gRPC query used to verify state data

        """
        #stores grpc requests 
        requestlist = []
        #get structured grpc path from string
        grpc_path = self._extractpath(_path)
        grpc_request = gnmi_pb2.Subscription(path=grpc_path, mode=attributes.submode, suppress_redundant=attributes.suppress, sample_interval=attributes.intervel, heartbeat_interval=attributes.heartbeat)
        requestlist.append(grpc_request) 
        if attributes.prefix:
            grpc_prefix = self._extractpath(attributes.prefix)
        else:
            grpc_prefix = None
        if attributes.qos:
            grpc_qos = gnmi_pb2.QOSMarking(marking=attributes.qos)
        else:
            grpc_qos = None
        grpcsubslist = gnmi_pb2.SubscriptionList(prefix=grpc_prefix, mode=attributes.mode, allow_aggregation=attributes.aggregate, encoding=attributes.encoding, subscription=requestlist, use_aliases=attributes.use_alias, qos=grpc_qos)
        grpcrequest = gnmi_pb2.SubscribeRequest(subscribe=grpcsubslist)
        print(grpcrequest)
        yield grpcrequest 

    def _deserialize(self, _data):
        """ convert data to readable format

        """
        out = []
        new_data = {}
        #new_data['update'] = {}
        for data in _data:
            data = json.loads(data)
            #print(data)
            for item in data['update']['update']:
                new_data = {}
                # if data is in Numerical format
                try:
                    new_data[item['path']['elem'][0]['name']] = float(base64.b64decode(item['val']['json_val']).decode('utf-8').strip('\"'))
                except:
                    new_data[item['path']['elem'][0]['name']] = base64.b64decode(item['val']['json_val']).decode('utf-8').strip('\"')
                out.append(new_data)
        return out       

    # def _deserialize(self, _data):
    #     """ convert data to readable format

    #     """
    #     out = []
    #     new_data = {}
    #     new_data['update'] = {}
    #     for data in _data:
    #         data = json.loads(data)
    #         #print(data)
    #         for item in data['update']['update']:
    #             try:
    #                 new_data['update'][item['path']['elem'][0]['name']] = float(base64.b64decode(item['val']['json_val']).decode('utf-8').strip('\"'))
    #             except:
    #                 new_data['update'][item['path']['elem'][0]['name']] = base64.b64decode(item['val']['json_val']).decode('utf-8').strip('\"')
    #     out.append(new_data)
    #     return out  