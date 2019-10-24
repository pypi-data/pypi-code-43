# -*- coding: utf-8 -*-
"""
    Created on 23 mai 2014
    
    @author: renaud
    
    
    Connector Module
    ----------------    
    
    This module contains necessary stuff to be connected to
    the Agriscope API.



"""
from __future__ import print_function
from __future__ import division

from future import standard_library

standard_library.install_aliases()
from builtins import str
from builtins import object
from past.utils import old_div
import json
import urllib.request, urllib.parse, urllib.error
import time
import datetime
import pytz


class AgspError(Exception):

    """ tp rùzepùrez;s!;cd4mlksdfmlsdfksmdflk
    
        Parameter
        ~~~~~~~~~
        
        Raw connecteur to the agriscope API
        -----------------------------------
        Class grouping necessary functions to talk with the agriscope server.
        It allows to be authentification and to get information on a specific account.
        
        Possibility to get the agribase's list
        
        Posibility to downloads data for each sensor
    
    """

    def __init__(self, value):
        self.value = value

   
    def __repr__(self):
        return repr(self.value)


class AgspConnecteur(object):
    """
    Raw connector to the Agriscope web service
    
    Handle the agriscope session id, store it and use it when calls to 
    agriscope api json web service
    """

    debug = True

    def __init__(self, server=u"www.agriscope.fr"):
        self.sessionOpen = False
        self.agspSessionId = 0
        self.server = u"http://" + server
        self.application = u"/agriscope-web-reader/app"
        self.lastLogin = "undefined"
        self.lastPassword = "undefined"
        self.debug = False

    def set_debug(self, value):
        """
        Execution is verbose in debug mode
        
        :param value : True ou False
        """
        self.debug = value

    def login(self, login_p, password_p):
        """
        Allow to be authentificate in the agriscope server
        The authentification key (sessionId) received from the server is stored 
        in the AgspConneteur object
        :param login_p: User's login
        :param password_p : User's password
        
        :return: The authenfication status and the session id 
        """
        self.lastLogin = login_p
        self.lastPassword = password_p
        url = (
            self.server
            + self.application
            + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"login","parameters":{"login":"'
            + login_p
            + '","password":"'
            + password_p
            + '"}}'
        )
        obj = self.__executeJsonRequest(url, "login()")
        if obj["returnStatus"] != "RETURN_STATUS_OK":
            print("Failed to open the agriscope session for login " + login_p)
            print(obj["infoMessage"])
            self.sessionOpen = False
            self.agspSessionId = -1
        elif obj["loginOk"] == True:
            # print("Agriscope session open for login " + login_p)
            self.sessionOpen = True
            self.agspSessionId = obj["agriscopeSessionId"]
        elif obj["loginOk"] == False:
            print("Agriscope session failed for login " + login_p)
            self.sessionOpen = False
            self.agspSessionId = obj["agriscopeSessionId"]
        return (self.sessionOpen, self.agspSessionId)

    def getAgribases(self, sessionid_p=-1, showInternalSensors=False):
        """
        Return a raw dictionnary as received from the server
        By default the API is called with stored sessionId
        
        If a optionnal sessionId is specified, the function uses this one.
        
        :param: sessionid_p: sessionId 
        :param: showInternalSensors: shown internal sensors as Dbm,Rssi Sensors 
        
        :return: A raw dict as received from the server
        :rtype: dict
        """
        paramShowInternalSensors="false"
        if showInternalSensors == True :
            paramShowInternalSensors="true"
        if sessionid_p == -1:
            sessionid_p = self.agspSessionId

        url = (
            self.server
            + self.application
            + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"getAgribases","parameters":{"agriscopeSessionId":'
            + str(sessionid_p)
            +',"internalSensors":' + paramShowInternalSensors
            + "}}"
        )
        return self.__executeJsonRequest(url, "getAgribases()")

    def getSensorData(self, sensorId, from_p=None, to_p=None):
        """
        Return timeseries as an array of data and date from the the sensor id.
        
        In 
        
        Use the period specified by the from_p and the to_p parameters.
        
        If from_p AND to_p is not specified, the period is choosen automatically from
        [now - 3 days => now]
        
        If from_p is not specified and to_p is specified, the function return a range 
        between [to_p - 3 days => to_p]
        
        
        :param: sensorId: Agriscope sensor id
        :param: from_p : Datetime 
        :param: to_p : Datetime 
         
        
        :return: A tuble of two array (datesArray[], valuesArray[])
        """
        id_p = self.agspSessionId
        from_p = int(from_p * 1000)
        to_p = int(to_p * 1000)
        t0 = time.time()
        url = (
            self.server
            + self.application
            + '?service=jsonRestWebservice&arguments={"jsonWsVersion":"1.0","method":"getSensorData","parameters":{"personalKey":"DUMMY","sensorInternalId":'
            + str(sensorId)
            + ',"agriscopeSessionId":'
            + str(id_p)
            + ',"from":'
            + str(from_p)
            + ',"to":'
            + str(to_p)
            + "}}"
        )
        tmpJson = self.__executeJsonRequest(url, "getSensorData()")
        # print "      "
        # print "      "
        # print tmpJson
        now = datetime.datetime.now()

        t1 = time.time()
        nbData = len(tmpJson["atomicResults"][0]["dataValues"])
        deltams = (t1 - t0) * 1000

        # if nbData > 2 :
        #     dat0 = self.__convertUnixTimeStamp2PyDate(tmpJson['atomicResults'][0]['dataDates'][0])
        #     dat1 = self.__convertUnixTimeStamp2PyDate(tmpJson['atomicResults'][0]['dataDates'][-1])
        # print ('%s GetSensorData  get %d data en %d ms soit %.1f data/ms first %s last %s ' % (now,nbData,deltams,nbData/deltams,dat0,dat1))
        # else :
        #     print ('%s GetSensorData  get %d data en %d ms soit %.1f data/ms ' % (now,nbData,deltams,nbData/deltams))

        return (
            tmpJson["atomicResults"][0]["dataDates"],
            tmpJson["atomicResults"][0]["dataValues"],
        )

    def __convertUnixTimeStamp2PyDate(self, unixtimeStamp):
        """
        Convert a unixtime stamp (provenant du serveur agriscope) en Temps python avec une timezone UTC
        """
        #
        # Comportement bizarre de sync 1199/thermomètre(-485966252) Marsillargues Marseillais Nord(1199) T° AIR °C no user parameter
        # lors de la syncrhonination de base de l'univers
        # il y a vait:
        # unixtimestamp=1412937447499
        # unixtimestamp=1412937832500
        # unixtimestamp=1404910637499
        # unixtimestamp=-30373006607501
        # ======================================================================
        # ERROR: test_firstUnivers (tests.agspUniversTests.TestAgspUnivers)
        # ----------------------------------------------------------------------
        # Traceback (most recent call last):
        #  File "C:\Users\guillaume\Documents\Developpement\django\trunk\datatooling\pandas\tests\agspUniversTests.py", line 37, in test_firstUnivers
        # print unixtimeStamp
        if unixtimeStamp < 0:
            unixtimeStamp = 1
        # print "unixtimestamp=" + unicode(unixtimeStamp)
        returnv = pytz.utc.localize(
            datetime.datetime.utcfromtimestamp(old_div(unixtimeStamp, 1000))
        )
        # print unicode(returnv)
        # print "%s" % returnv.year
        # if (returnv.year == 1992) :

        # print "%d %s" % (unixtimeStamp, unicode(returnv))
        return returnv

    def getAgribaseIntervaleInSeconds(self, serialNumber_p):
        """
        Return the sampling intervall for an Agribase
        
        :param: serialNumber_p: Agriscope serial number
         
        
        :return: A integer, samplin in second
        """
        url = (
            "http://jsonmaint.agriscope.fr/tools/CHECK/agbs.php?sn=%d" % serialNumber_p
        )
        json = self.__executeJsonRequest(url)
        returnv = -1
        if "intervalInSec" in json:
            tmp = json["intervalInSec"]
            if tmp == "N/A":
                return 15
            returnv = int(tmp)
        return returnv

    def __executeJsonRequest(self, url, method=""):
        try:

            if self.debug == True:
                print(url)
            str_response = ""
            # RECORD MODE
            retry = 3
            i = 0
            while retry > 0:
                try:
                    response = urllib.request.urlopen(url)
                    retry = -1
                except Exception as e:
                    retry = retry - 1
                    i = i + 1
                    print(str(i) + " retry connection ")

            if retry == 0:
                print("Probleme de connexion pour aller vers " + url)
                return
            str_response = response.read().decode("utf-8")

            if self.debug == True:
                print(str_response)
            obj = json.loads(str_response, strict=False)
            infomessage = "N/A"
            if "infoMessage" in obj:
                infomessage = obj["infoMessage"]
                if "session invalide" in infomessage:
                    if len(method) > 0:
                        print(
                            u"Numero de session invalide dans l'appel de "
                            + method
                            + " par l'api."
                        )
                    else:
                        print(u"Numero de session invalide  par l'api.")
                        raise AgspError(u"Erreur de connection")
            return obj
        except Exception as e:
            print(e.__doc__)
            print(e.message)
            if len(method) > 0:
                raise AgspError(u"Erreur de connection dans " + method)
            else:
                raise AgspError(u"Erreur de connection ")
