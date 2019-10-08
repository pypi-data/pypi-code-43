#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:19:05 2019

@author: admin2
"""
from arangopipe_api import ArangoPipe
from arangopipe_config import ArangoPipeConfig
from arangopipe_admin_api import ArangoPipeAdmin

def run_test():
    config = ArangoPipeConfig()
    config.set_dbconnection(hostname = "http://localhost:8529",\
                                     root_user = "root",\
                                root_user_password = "open sesame")
    admin = ArangoPipeAdmin(config = config)
    admin.delete_arangomldb()
    admin = ArangoPipeAdmin(config = config)
    ap = ArangoPipe(config = config)
    admin.add_vertex_to_arangopipe('test_vertex_11')
    admin.add_vertex_to_arangopipe('test_vertex_12')
    sd = {'name': "sample doc"}
    v1 = ap.insert_into_vertex_type('test_vertex_11', sd)
    v2 = ap.insert_into_vertex_type('test_vertex_12', sd)
    admin.add_edge_definition_to_arangopipe('test_edge', 'test_vertex_11', 'test_vertex_12')
    ei = ap.insert_into_edge_type('test_edge', v1, v2)
    print ("Edge inserted: " + str(ei))
    return