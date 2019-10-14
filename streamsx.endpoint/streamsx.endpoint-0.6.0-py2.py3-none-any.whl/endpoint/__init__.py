# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

"""
Overview
++++++++

For details of implementing applications in Python
for IBM Streams including IBM Cloud Pak for Data:

  * `streamsx package documentation <https://streamsxtopology.readthedocs.io/en/stable>`_

This package exposes SPL operators in the `com.ibm.streamsx.inetserver <https://ibmstreams.github.io/streamsx.inetserver/>`_ toolkit as Python methods.


Sample
++++++

A simple example of a Streams application that provides an endpoint for json injection::

    from streamsx.topology.topology import *
    from streamsx.topology.context import submit
    import streamsx.endpoint as endpoint

    topo = Topology()

    s1 = endpoint.inject(topo)
    s1.print()

    # Use for IBM Streams including IBM Cloud Pak for Data
    submit ('DISTRIBUTED', topo)


"""

__version__='0.6.0'

__all__ = ['download_toolkit', 'inject', 'expose']
from streamsx.endpoint._endpoint import download_toolkit, inject, expose

