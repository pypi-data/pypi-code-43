from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz

def getServerInfoModel(appObj):
  serverInfoServerModel = appObj.flastRestPlusAPIObject.model('mainAPI', {
    'Version': fields.String(default='DEFAULT', description='Version of container running on server'),
    'APIAPP_APIDOCSURL': fields.String(default='',description='Base endpoint for EBO docs')
  })
  return appObj.flastRestPlusAPIObject.model('ServerInfo', {
    'Server': fields.Nested(serverInfoServerModel)
  })

def registerAPI(appObj, serverinfoapiprefix):

  ns = appObj.flastRestPlusAPIObject.namespace(serverinfoapiprefix, description='Public API for displaying server info.')

  @ns.route('/serverinfo')
  class servceInfo(Resource):

    '''General Server Operations'''
    @ns.doc('getserverinfo')
    @ns.marshal_with(getServerInfoModel(appObj))
    @ns.response(200, 'Success')
    def get(self):
     '''Get general information about the server'''
     curDatetime = datetime.datetime.now(pytz.utc)
     return {
      'Server': {
        'Version': appObj.version ,
        'APIAPP_APIDOCSURL': appObj.globalParamObject.apidocsurl
      }
     }
