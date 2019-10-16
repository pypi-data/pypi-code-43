# coding: utf-8

"""
    assetic.OData  (odata.py)
    Tools to assist with using Assetic OData endpoint
"""
from __future__ import absolute_import
 
from ..api_client import ApiClient
from .apihelper import APIHelper
import six.moves.urllib as urllib  #tools to format url

class OData(object):
    """
    Class with generic tools to assist using OData endpoints
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger

        self.apihelper = APIHelper()

    def get_odata_data(self,entity,fields,filters=None,top=500,skip=0,orderby=None):
        """
        Get asset data from the asset endpoint.  Specify fields, filter optional
        :param entity: odata entity
        currently one of 'assets','workorder','workrequest'
        :param fields: A list or tuple of fields to return. Specify at least one
        :param filters: A list of valid odata filters that will append by 'and'
        or a single string representing a valid filter (filter not validated)
        :param top: number of records to return using top syntax. default 500
        :param skip: number of records to skip, must be > 0. Default=0
        :param orderby: fields to order results by. Can be a delimited string, or
        list or tuple
        :returns: a list of asset dictionaries matching the select fields or
        None if error.  If no results then empty list
        """

        #todo, make list of supported entities dynamic - i.e. hit odata metadata
        # could do this on initialisation of this class?
        if entity not in ("assets", "workorder", "workrequest", "component"
                          , "fairvaluation", "networkmeasure", "servicecriteria"
                          , "treatments"):
            msg = 'Entity must be one of "assets", "workorder", "workrequest",'\
                  ' "component", "fairvaluation", "networkmeasure"\
                  , "servicecriteria", "treatments"'
            self.logger.error(msg)
            return None
        
        # build the URL.
        url = "/odata/{0}?$top={1}".format(entity,top)
        if skip > 0:
            # only include skip if non zero else endpoint returns no data
            url = url + "&$skip={0}".format(skip)
        # add search fields
        if isinstance(fields, list) or isinstance(fields, tuple):
            if len(fields) == 0:
                msg = "OData asset search requires at least one search field"
                self.logger.error(msg)
                return None
            url = url + "&$select=" + ",".join(fields)
        else:
            # assume single field as string or comma delimited string
            url = url + "&$select=" + fields
        # apply filters
        if isinstance(filters,list) or isinstance(filters,tuple):
            if len(filters) > 0:
                url = url + "&$filter=" + " and ".join(filters)
        elif filters is not None:
            # assume single field as string or comma delimited string
            url = url + "&$filter=" + filters
            
        # add order by
        if isinstance(orderby,list) or isinstance(orderby,tuple):
            if len(orderby) > 0:
                url = url + "&$orderby=" + ",".join(orderby)
        elif orderby is not None:
            # assume single field as string or comma delimited string
            url = url + "&$orderby=" + orderby

        # replace spaces but keep other special characters
        url = urllib.parse.quote(url,safe="/?$&='")
        # get the data
        response = self.apihelper.generic_get(url)
        if response is None:
            return None
        if "value" in response:
            return response["value"]
        else:
            return None
