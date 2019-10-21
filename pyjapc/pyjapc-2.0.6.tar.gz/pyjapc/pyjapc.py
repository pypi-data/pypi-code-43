# -*- coding: utf-8 -*-
"""PyJapc is a Python to FESA/LSA/INCA interface via JAPC.

Copyright (c) CERN 2015-2016

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

:Authors:
  - Michael Betz <mbetz@cern.ch>
  - Tom Levens <tom.levens@cern.ch>
  - Michi Hostettler <michi.hostettler@cern.ch>
"""

import os
import threading
import traceback
import getpass
import atexit
import sys
import datetime
import logging
import pprint
import jpype as jp
import numpy as np
import cmmnbuild_dep_manager
import six
import base64

# Spyder gives trouble if this import is not the last
import pytz


class PyJapc(object):
    """Start a JVM and load up the JAPC classes.

    Args:
        selector (str): The default JAPC selector, describing the moment in
            time an operation (GET or SET) should act. See
            `here <https://wikis.cern.ch/display/JAPC/Basic+Actions#BasicActions-Selectors>`__
            for details on how to specify a selector. Examples of valid
            timingSelectors are: "SPS.USER.SFTPRO1", "LEI.USER.LIN3MEAS",
            "CPS.USER.ALL", etc.

            This is the default selector which is used if you don't specify an
            override in getParam() or setParam().

        incaAcceleratorName (str): The accelerator name provided to the
            Injector Control Architecture (INCA) framework.

            It can be any of AD, CTF3, ISOLDE, LEIR, LHC, LINAC4, NORTH, PS,
            PSB, SCT, SPS or can be even an empty string ("").

            You might need to call rbacLogin() to make full use of INCA.

            WARNING: If incaAcceleratorName is None, INCA will not be
            initialized and JAPC calls will go directly to the hardware without
            passing by the INCA servers.

        noSet (bool): Do not actually carry out SET operations.
            Only prints them to the console (safe-mode).

        timeZone (str): Report timestamps in `local` or in `utc` time.

        logLevel (int): Set the log level for the PyJapc logger.
    """

    def __init__(self, selector="LHC.USER.ALL", incaAcceleratorName="auto", noSet=False, timeZone="utc",
                 logLevel=None):
        atexit.register(self.__del__)
        self._noSet = noSet
        self._rbaLoginService = None
        # This lock ensures that only one callback is run at a time
        self._subscriptionCallbackLock = threading.Lock()

        # --------------------------------------------------------------------
        # Dictionaries for caching often used objects
        # --------------------------------------------------------------------
        # For caching all the "ParameterObjects" ever created
        self._paramDict = dict()

        # For caching all the "SubscriptionHandles" ever created
        self._subscriptionHandleDict = dict()

        # Setup logging
        logging.basicConfig()
        self.log = logging.getLogger(__package__)

        if logLevel is not None:
            self.log.setLevel(logLevel)

        # --------------------------------------------------------------------
        # Startup the JVM and the connection to Python (JPype)
        # --------------------------------------------------------------------
        mgr = cmmnbuild_dep_manager.Manager("pyjapc", logging.WARNING)
        mgr.start_jpype_jvm()

        log4j = jp.JPackage('org').apache.log4j
        if log4j.BasicConfigurator is not None and callable(log4j.BasicConfigurator.configure):
            log4j.BasicConfigurator.configure()
            if logLevel is not None:
                log4j.Logger.getRootLogger().setLevel(log4j.Level.toLevel(logLevel))
            else:
                log4j.Logger.getRootLogger().setLevel(log4j.Level.WARN)

        # Enable `*` Wildcard selectors (see https://wikis.cern.ch/display/JAPC/Wildcard+Selectors)
        jp.java.lang.System.setProperty("default.wildcard.subscription.on", "true")

        cern = jp.JPackage("cern")

        # --------------------------------------------------------------------
        # Try to initialize the INCA with an Java accelerator type
        # --------------------------------------------------------------------

        # new JAPC selector standard
        if selector is None:
            self.log.warning("The NULL selector is deprecated. Using an empty-string selector instead.")
            selector = ""

        ic = cern.japc.ext.inca.IncaConfigurator

        # User wants to configure INCA
        if incaAcceleratorName is not None:
            if incaAcceleratorName == "auto":
                if selector == "":
                    raise ValueError("Cannot infer incaAcceleratorName for an empty selector, "
                                     "please specify it manually")
                else:
                    acc = selector.split('@')[-1].split('.')[0]
                    if acc not in self._incaAccFromTiming.keys():
                        raise ValueError("Cannot infer incaAcceleratorName from selector '{0}', "
                                         "please specify it manually".format(selector))
                    incaAcceleratorName = self._incaAccFromTiming[acc]
            else:
                incaAcceleratorName = incaAcceleratorName

            if ic.isConfigured:
                if ic.clientAccelerator.getName() != incaAcceleratorName:
                    self.log.warning("INCA is already configured for {0}, cannot change it to {1}.".format(
                        ic.clientAccelerator.getName(), incaAcceleratorName
                    ))
            else:
                if incaAcceleratorName == "":
                    ic.configure()
                else:
                    self.log.info("Configuring INCA for {0}".format(incaAcceleratorName))
                    acceleratorJObj = getattr(cern.accsoft.commons.domain.CernAccelerator, incaAcceleratorName)
                    ic.configure(acceleratorJObj)
        else:
            # None has been specified. Do no initialize INCA.
            self.log.info("Will not use INCA. Falling back to pure JAPC. Descriptors will not be available.")

        # --------------------------------------------------------------------
        # Instantiate some useful JAPC (factory) classes
        # --------------------------------------------------------------------
        # Will be populated later (if needed)
        self._parameterFactory = cern.japc.core.factory.ParameterFactory.newInstance()
        self._simpleParameterValueFactory = cern.japc.core.factory.SimpleParameterValueFactory
        self._mapParameterValueFactory = cern.japc.core.factory.MapParameterValueFactory
        self._selectorFactory = cern.japc.core.factory.SelectorFactory
        self._functionFactory = cern.japc.value.factory.DomainValueFactory
        # Setup the default selector
        self._selector = self._selectorFactory.newSelector(selector)

        # --------------------------------------------------------------------
        # Store some user settings
        # --------------------------------------------------------------------
        if timeZone == "utc":
            self._selectedTimezone = pytz.utc
        elif timeZone == "local":
            self._selectedTimezone = pytz.timezone("Europe/Zurich")
        elif isinstance(timeZone, datetime.tzinfo) or timeZone is None:
            self._selectedTimezone = timeZone
        else:
            self.log.warning("Unknown timeZone argument: {0}. Falling back on UTC time.".format(timeZone))
            self._selectedTimezone = pytz.utc

        if self._noSet:
            self.log.info("No SETs will be made as noSet=True")

    # INCA accelerator name from timing domain lookup
    _incaAccFromTiming = {
        "ADE": "AD",
        "CPS": "PS",
        "FCT": "CTF",
        "ISO": "ISOLDE",
        "LEI": "LEIR",
        "LHC": "LHC",
        "LNA": "ELENA",
        "PSB": "PSB",
        "SCT": "CTF",
        "SPS": "SPS",
    }

    def __del__(self):
        self.clearSubscriptions()
        self.rbacLogout()
        self._paramDict.clear()
        self._rbaLoginService = None
        self._parameterFactory = None
        self._selectorFactory = None
        self._selector = None
        # self.log.debug("PyJapc.__del__()")
        # time.sleep(0.2)
        # jp.shutdownJVM()   # Would be nice to do but this freezes the Python kernel
        # TODO: JAPC logout

    @staticmethod
    def enableInThisThread():
        """Allows PyJapc object to be used in threads other than the main one.

        For more details please see here:
        http://jpype.readthedocs.io/en/latest/userguide.html#threading
        """
        jp.attachThreadToJVM()

    def _giveMeSelector(self, **kwargs):
        """Produce and return a JAPC selector object with certain overrides.

        Args:
            timingSelectorOverride (str): Default "LHC.USER.ALL".
            dataFilterOverride (dict): Default None

        Tries to fallback on default selector if something is not specified.

        Note that dataFilterOverride=None specifies to not use a filter.
        """
        if ("timingSelectorOverride" in kwargs) or ("dataFilterOverride" in kwargs):
            # Fallback on defaults
            timingSelector = kwargs.get("timingSelectorOverride", self._selector.id)
            dataFilter = kwargs.get("dataFilterOverride", self._selector.dataFilter)
            # Handle "ACC.USER.NAME N" type selectors provided by CCM
            if timingSelector is None:
                self.log.warning("The NULL selector is deprecated. Using an empty-string selector instead.")
                timingSelector = ""
            timingSelector = timingSelector.split(" ")[0]
            if dataFilter is None:
                s = self._selectorFactory.newSelector(timingSelector)
            else:
                dataFilter = self._convertPyToVal(dataFilter)
                s = self._selectorFactory.newSelector(timingSelector, dataFilter)
            return s
        else:
            return self._selector

    def setSelector(self, timingSelector, dataFilter=None):
        """Sets the default selector and filter used for GET/SET.

        This selector and filter is used if you don't specify an override in
        getParam() or setParam().

        Args:
            timingSelector (str): A string describing the moment in time a GET
                or SET operation should act. See
                `here <https://wikis.cern.ch/display/JAPC/Basic+Actions#BasicActions-Selectors>`__
                for details on how to specify a selector. Examples of valid
                timingSelectors are: "SPS.USER.SFTPRO1", "LEI.USER.LIN3MEAS",
                "CPS.USER.ALL", etc.

            dataFilter: Provides additional information, which is not treated
                at the level of JAPC but passed to a device (so it is
                device-specific). It is sometimes used to specify the operating
                mode (# of averaging, use-case, etc.) of a FESA device. The
                type of dataFilter can be any of the types which are also
                accepted by setParam() (a Python primitive, a numpy array, a
                Python dictionary or a JAPC ParameterValue Object). FESA will
                most likely expect a filter with a specific name / type, which
                you will have to find out yourself. The FESA navigator might
                give you a hint.

                Example for setting a filter to averaging = 1::

                    japc = PyJapc()
                    japc.setSelector('LHC.USER.ALL', {"averaging": 1})
        """
        self._selector = self._giveMeSelector(timingSelectorOverride=timingSelector, dataFilterOverride=dataFilter)

    def getSelector(self):
        """Return the timing selector"""
        return self._selector.id

    def setDataFilter(self, dataFilter):
        """Set the data filter"""
        self._selector = self._giveMeSelector(dataFilterOverride=dataFilter)

    def getDataFilter(self):
        """Return the data filter"""
        return self._convertValToPy(self._selector.dataFilter) if self._selector.dataFilter else None

    def getUsers(self, machine):
        """Get a list of user for a particular machine

        Note that you may need to set the environment variable TGM_NETWORK
        before starting JPype for some accelerators (such as LINAC4):

        https://wikis.cern.ch/display/InCA/System+properties+used+by+AscBeans#SystempropertiesusedbyAscBeans-TGM_NETWORK

        """
        cern = jp.JPackage("cern")
        TgmUtil = cern.japc.ext.tgm.TgmUtil
        users = [user for user in TgmUtil.getLinesforMachineGroup(machine, TgmUtil.USER)]
        if not users:
            users = ["ALL"]
        return list(map(lambda x: '{0}.{1}.{2}'.format(machine, TgmUtil.USER, x), users))

    def rbacLogin(self, username=None, password=None, loginDialog=False, readEnv=True):
        """Perform RBAC authentication.

        This is required to work with access-protected FESA classes.

        If the environment variable RBAC_TOKEN_SERIALIZED is set and readEnv is
        True then a login will be attempted with the RBAC token contained in
        the environment.

        If no username is provided, login by location is attempted and no
        password is needed (only works in certain locations, e.g. in the
        control room). Otherwise username/password authentication is
        performed using the username provided.

        Note that is is *strongly* discouraged to pass a password to this
        function in interactive sessions, as this will be stored in the shell
        history in plaintext. If the password is left blank, getpass will be
        used to provide a secure interactive password entry.

        Finally passing loginDialog=True shows a Tk GUI widget to allow entry
        of the username and password.

        Don't forget to call rbacLogout() at the end of your session to return
        your token.

        Args:
            username (str): The RBAC username for an "explicit" login.

            password (str): The RBAC password for an "explicit" login.

            loginDialog (bool): If true, a graphical login dialog is shown
                using pyjapc.rbac_dialog.

            readEnv (bool): Read the RBAC token from the environment variable
                "RBAC_TOKEN_SERIALIZED" if it is set.
        """
        cern = jp.JPackage("cern")

        byLoc = False

        env = os.getenv("RBAC_TOKEN_SERIALIZED", "")
        if readEnv and env:
            try:
                self.log.info("Reusing RBAC token from environment")
                token = cern.rbac.common.RbaToken(base64.b64decode(env))
                cern.rbac.util.holder.ClientTierTokenHolder.setRbaToken(token)

                if cern.rbac.util.lookup.RbaTokenLookup.findRbaToken() is None:
                    raise RuntimeError("Could not reuse RBAC token, maybe it has expired?")

                self.log.info("RBAC login successful")
                return
            except Exception as e:
                self.log.warning(e)

        if loginDialog:
            if six.PY2:
                import rbac_dialog
            else:
                import pyjapc.rbac_dialog as rbac_dialog
            if username is None:
                username = getpass.getuser()
            byLoc, username, password = rbac_dialog.getPw(username, "PyJapc")
            if not byLoc and (username is None or password is None):
                raise RuntimeError("RBAC login cancelled by user")
        else:
            if username is None:
                byLoc = True
            else:
                if password is None:
                    password = getpass.getpass("Enter RBAC Password for {0}: ".format(username))
        try:
            self._doLogin(byLoc, username, password)
        except Exception as e:
            if self._rbaLoginService is not None:
                self._rbaLoginService.close()
                self._rbaLoginService = None
            raise e

    def _doLogin(self, byLoc, username, password):
        cern = jp.JPackage("cern")
        self.rbacLogout()
        loginBuilder = cern.rbac.util.authentication.LoginServiceBuilder.newInstance()
        loginBuilder.applicationName("PyJapc")
        loginBuilder.autoRefresh(True)
        if byLoc:
            self.log.info("Performing RBAC login by location")
            loginBuilder.loginPolicy(cern.rbac.common.authentication.LoginPolicy.LOCATION)
        else:
            self.log.info("Performing explicit RBAC login as {0}".format(username))
            loginBuilder.loginPolicy(cern.rbac.common.authentication.LoginPolicy.EXPLICIT)
            loginBuilder.userName(username)
            loginBuilder.userPassword(password)
        self._rbaLoginService = loginBuilder.build()
        self._rbaLoginService.loginNewUser()
        self.log.info("RBAC login successful")

    def rbacLogout(self):
        """Ends your RBAC session (if one is open) and returns your token."""
        cern = jp.JPackage("cern")
        if self._rbaLoginService is not None:
            if self.rbacGetToken() is not None:
                self._rbaLoginService.logout()
                self.log.info("RBAC logout done")
            self._rbaLoginService.close()
            self._rbaLoginService = None
        cern.rbac.util.holder.ClientTierTokenHolder.clear()

    def rbacGetToken(self):
        """Returns the RBAC token as a Java object"""
        cern = jp.JPackage("cern")
        return cern.rbac.util.lookup.RbaTokenLookup.findRbaToken()

    def rbacGetSerializedToken(self):
        """Returns a Base64 encoded serialization of the RBAC token"""
        return base64.b64encode(np.array(self.rbacGetToken().getEncoded(), dtype=np.uint8)).decode()

    def _getDictKeyFromParameterName(self, parameterName):
        """parameterName can be a string or a list of strings
        returns a unique identifier, which can be used as dict key
        """
        if isinstance(parameterName, list) or isinstance(parameterName, tuple):
            # Create a unique, hashable key
            parameterKey = "[PG]" + "".join(sorted(parameterName))
        elif isinstance(parameterName, six.string_types):
            # The key is the parameter name
            parameterKey = parameterName
        else:
            raise Exception("unsupported parameter type {0}. A parameterName should be `str` or `list`".format(
                type(parameterName)
            ))
        return parameterKey

    def _getJapcPar(self, parameterName):
        """Create the JAPC parameter object and return it.

        If parameterName is a String, a Parameter Object is returned

        If parameterName is a list of Strings, a ParameterGroup Object is returned

        Each JAPC parameter object ever requested is cached in a Python
        dictionary.
        """
        parameterKey = self._getDictKeyFromParameterName(parameterName)

        if parameterKey in self._paramDict:
            # Parameter object exists already in dict
            p = self._paramDict[parameterKey]
        else:
            if isinstance(parameterName, six.string_types):
                # Create a new Parameter object and store it in the dict
                p = self._parameterFactory.newParameter(parameterKey)
            else:
                # Create a new ParameterGroup object, populate it
                p = jp.JPackage("cern").japc.core.spi.group.ParameterGroupImpl()
                for parName in parameterName:
                    p.add(self._getJapcPar(parName))
            # Store the newly created object in the dict
            self._paramDict[parameterKey] = p
        return p

    def getParam(self, parameterName, getHeader=False, noPyConversion=False, unixtime=False, onValueReceived=None, onException=None, **kwargs):
        """Fetch the value of a single FESA parameter or of a FESA ParameterGroup

        Args:
            parameterName (str, list[str]): The path + identifier of the
                FESA parameter(s) to fetch. How to assemble a parameterName is
                explained `here <https://wikis.cern.ch/display/JAPC/Parameter+Names>`__.
                If a `list` of `str` is given, a ParameterGroup is created.
                Then the result lists will be in the same order as the
                parameterName list.

            noPyConversion (bool): Set to True if you want to get the raw JAPC
                ParameterValue object instead of a Python native type. You will
                have to extract the values yourself.

            unixtime (bool): If True and noPyConversion is False, the header will be
                converted but the acqStamp and cycleStamp will be returned as seconds
                since epoch.

            onValueReceived (function):
                If you get an asynchronous simple parameter value, the
                callback function should be like:

                    onValueReceived(value).

            onException (function):
                If you get an asynchronous simple parameter value, the
                optional exception callback function should be like:

                    onException(parameterName, description, exception).
                    parameterName and description are strings and exception is a
                    Java Object

            getHeader (bool): Set to True if you want to get a list of
                FESA header-information. This includes the `acqStamp`,
                `cycleStamp`, `selector` and `acqFlags` parameters.

            timingSelectorOverride (str): Override of value set with
                setSelector() for a particular GET.

            dataFilterOverride (dict): Override of value set with
                setSelector() for a particular GET.

        Returns:
            The value of the FESA parameter, converted to a Python native type.

            The type can be one of the following:

             * A simple value like int, float, str, bool
             * A 1D or 2D array of simple values, which is returned as a
               numpy.array
             * A DiscreteFunction is returned as 2D array with the indices
               [x/y, valueIndex]
             * A DiscreteFunctionList is returned as a list of 2D arrays
             * A `Enum` is returned as (enumCode, enumString)
             * A Python dict containing any of the above (only if the
               parameterName does not specify a field with the #-tag)

            If `parameterName` is a `list`, a ParameterGroup is created internally
            and JAPC tries to get all values at the same instance in time.
            A list of return-values is returned, which are in the same order as requested.

            If `getHeader` is `True`, the return-value is always a tuple.
            The first element contains the parameter value. The second element contains a
            dictionary of header information.

            If the automatic type conversion does not work, or if
            noPyConversion is set to True, the JAPC ParameterValue object is
            returned and has to be converted manually to a Python type.

        An example for getting a Parameter with header informations::

            value, header = japc.getParam("LHC.BQS.SCTL/BunchSelector#BunchSelControl", getHeader=True)
            print(value)
                4
            print(header)
                {'acqStamp': datetime.datetime(2016, 3, 11, 13, 10, 25, 515000, tzinfo=<UTC>),
                 'cycleStamp': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=<UTC>),
                 'isFirstUpdate': 0,
                 'isImmediateUpdate': 0}

        An example for getting a ParameterGroup::

            parameters = ["LHC.BQS.SCTL/BunchSelector#BunchSelControl",
                           "LHC.BQS.SCTL/GetElectronics#B1_VER_15DB_PREAMP"]
            values, headers = japc.getParam(parameters, getHeader=True)

        """
        s = self._giveMeSelector(**kwargs)

        # Get the (cached) JAPC Parameter or ParameterGroup object
        p = self._getJapcPar(parameterName)

        # Carry out the Get operation. tempParValue will be of type:
        #  jpype._jclass.cern.japc.value.spi.AcquiredParameterValueImpl
        # or if a GET on a ParameterGroup was done:
        #  jpype._jarray.cern.japc.value.FailSafeParameterValue[]
        if onValueReceived is None:
            temp_val = p.getValue(s)
            return self._processTempValue(temp_value=temp_val, getHeader=getHeader, noPyConversion=noPyConversion, unixtime=unixtime)
        else:
            def callback(parameterName, value, headerInfo=None):
                val = self._processTempValue(temp_value=value,
                                            getHeader=getHeader,
                                            noPyConversion=True, # TODO: JAPC always seems to return scalar value here, thus we force to True
                                            unixtime=unixtime)
                onValueReceived(val)

            listener = self._createValueListener(par=p,
                                                 getHeader=getHeader,
                                                 noPyConversion=noPyConversion,
                                                 unixtime=unixtime,
                                                 onValueReceived=callback,
                                                 onException=onException)
            p.getValue(s, listener)

    def setParam(self, parameterName, parameterValue, checkDims=True, dtype=None, **kwargs):
        """Set the value of a FESA parameter.

        Args:
            parameterName (str): A string specifying the path + identifier of
                the FESA parameter to set. Details on how to assemble a
                parameterName are given `here <https://wikis.cern.ch/display/JAPC/Parameter+Names>`__.
                If you specify the full parameterName (with #-tag) a PARTIAL
                SET of a single parameter is carried out.

            parameterValue: Specifies the new value of the FESA parameter.

                For a single Parameter this can be a primitive Python type or
                a 1D / 2D numpy array.

                If you want to SET several FESA fields in one operation,
                parameterValue must be a Python dict. The keys should
                correspond to the FESA field-names and the values should be of
                identical type and dimension to what you would get from
                getParam(). Examples::

                    # Initialize PyJapc in safe-mode (don't actually SET anything)
                    japc = PyJapc(noSet=True)
                    # Primitive value
                    japc.setParam("CB.BHB1100/Acquisition#currentAverage", 4.211)
                    # Array
                    japc.setParam("LHC.BQS.SCTL/BunchSelector#BunchSel1Slots", ones(3564))
                    # Multiple parameters (MAP)
                    japc.setParam("CB.BHB1100/Acquisition", {'currentAverage':4.2, 'current_status':42})

                A DiscreteFunction is SET with an 2D array, of shape
                [2, nValues]. The first row contain the x-values, the second
                the y-values.

                A DiscreteFunctionList is SET with a list of 2D arrays as
                described above::

                    xValues = [0, 4, 8, 12]
                    yValues = [-1, 0, 2, 4.4]
                    # a:   0 -> -1,   4 -> 0,   8 -> 2,   12 -> 4.4
                    a = numpy.array([xValues, yValues])
                    # b:   0 ->  4,   6 -> 9,   7 -> 0
                    b = numpy.array([[0,6,7],[4,9,0]])
                    # Setting a DiscreteFunction
                    japc.setParam("MyDevice/MyParameter#amplitudes", a)
                    # Setting a DiscreteFunctionList
                    japc.setParam("INCA.TESTDEV-01-001-F3/FunctionControl#amplitudes", [a,b])

                A `Enum` type is either set with an `int` (the enum-code) or a `str`

                Furthermore, parameterValue can be a JAPC ParameterValue
                object. This might be helpful if the automatic type conversion
                from Python to JAPC does not work. Refer to the
                `JAPC docs <https://wikis.cern.ch/display/JAPC/Basic+Actions#BasicActions-AsynchronousSet>`__
                on how to create a ParameterValue.

            timingSelectorOverride (str): Override of value set with
                setSelector() for a particular GET.

            dataFilterOverride (dict): Override of value set with
                setSelector() for a particular GET.

        **About the Python to Java type conversion**

        PyJapc chooses the Java variable type according to the Python type of
        parameterValue.

        Use the numpy types int8, int16, int32, int64, float32, and float64 to
        get a specific Java datatype with an equivalent number of bits.

        `Details about Java data types <https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html>`__.

        parameterName can also be a
        `JPype wrapper class <http://jpype.readthedocs.org/en/latest/userguide.html#conversion-from-python-to-java>`__
        like jpype.JShort(42), which is another way to force a particular data
        type. Examples::

            # Set as Java 64 bit long value
            japc.setParam(parameterName, numpy.int64(42))
            # Set as Java 16 bit short value
            japc.setParam(parameterName, jpype.JShort(42))
            # Set as Java array of  8 bit byte values
            japc.setParam(parameterName, ones(42, dtype=numpy.int8))
            # Set as Java array of 32 bit float values
            japc.setParam(parameterName, ones(42, dtype=numpy.float32))


        General Notes:

        * You might need to call rbacLogin() at least once before doing a SET.
        * If parameterValue is a Python type, array dimensions are checked in
          Python and an exception is thrown if they don't agree with FESA.
        * If parameterValue is a JAPC ParameterValue Object, array dimensions
          and type checks are not explicitly done in Python relying on JAPC
          for that functionality.
        """
        # --------------------------------------------------------------------
        # Check if we want to SET a SimpleValue or a MAP
        # --------------------------------------------------------------------
        p = self._getJapcPar(parameterName)
        if isinstance(parameterValue, jp.JClass("cern.japc.value.ParameterValue")):
            # User provided a Java ParameterValueObject which can be handed to JAPC for SETTING right away
            parValNew = parameterValue

        else:
            # ----------------------------------------------------------------
            # Get parameter value descriptor for dim. checks
            # ----------------------------------------------------------------
            vdesc = p.valueDescriptor
            if (vdesc is None) and (parameterName[0:6] != 'rmi://') and checkDims:
                raise ValueError("Could not get a valueDescriptor. Can not do array dimension checks. "
                                 "Please initialize INCA in the PyJapc() constructor.")

            # Convert Python type to JAPC type
            parValNew = self._convertPyToVal(parameterValue, vdesc=vdesc, checkDims=checkDims, dtype=dtype)
        # --------------------------------------------------------------------
        # Carry out the actual set (if not in safemode)
        # --------------------------------------------------------------------
        if self._noSet:
            self.log.warning("{0} would be set to:\n{1}".format(parameterName, parValNew.toString()))
        else:
            s = self._giveMeSelector(**kwargs)

            # Do the set
            p.setValue(s, parValNew)

    def _processTempValue(self, temp_value, noPyConversion=False, getHeader=False, unixtime=False):
        try:
            if noPyConversion:
                return temp_value
            else:
                # Convert a Group of Parameter Values to Python
                vals, heads = self._convertParGroupToPy(temp_value, unixtime)
                if getHeader:
                    return (vals, heads)
                return vals
        except TypeError:
            # Gets raised when value is not Iterable
            # Convert a single Parameter Value to Python
            # parValue is jpype._jclass.cern.japc.value.spi.AcquiredParameterValueImpl
            parValue = temp_value.getValue()
            if noPyConversion:
                return parValue
            else:
                # Convert it to a Python type
                val = self._convertValToPy(parValue)
                if getHeader:
                    head = self._convertHeaderToPy(temp_value.getHeader(), unixtime)
                    return (val, head)
                return val

    def _convertPyToVal(self, pyVal, vdesc=None, checkDims=True, dtype=None):
        """Converts anything Python (also dict()) to anything JAPC.

        It tries to do an array dimension check if vdesc is provided
        [JAPC ParameterValueDescriptor]
        """

        if isinstance(pyVal, jp.JClass("cern.japc.value.ParameterValue")):
            # It's already a JAPC value - nothing to do here
            return pyVal

        if vdesc is None:
            # Fallback on Python type to decide what kind of Japc value to create (dict --> MAP or array --> SIMPLE)
            # Will not do any array dimension checks as we do not have info aboutr the correct dimensions
            if isinstance(pyVal, dict):
                parValNew = self._mapParameterValueFactory.newValue()

                # Iterate over user provided dict()
                for userKey, userValue in pyVal.items():
                    # Convert user input to SimpleParameterValue
                    simpleParVal = self._convertPyToSimpleVal(userValue, dtype=dtype)

                    # And inject them in the parValNew MAP
                    parValNew.put(userKey, simpleParVal)
            else:
                return self._convertPyToSimpleVal(pyVal, dtype=dtype)
        else:
            # Use the JAPC value descriptor to decide what kind of JAPC value to create
            # Also check array dimensions in Python
            # Can be MAP or SIMPLE
            if vdesc.type.typeString == "Simple":
                # Check input array shape against FESA
                if checkDims:
                    self._checkDimVsJAPC(pyVal, vdesc)
                parValNew = self._convertPyToSimpleVal(pyVal, vdesc, dtype=dtype)
            elif vdesc.type.typeString == "Map":
                # Create a new MAP
                parValNew = self._mapParameterValueFactory.newValue()

                # Iterate over user provided dict()
                for userKey, userValue in pyVal.items():
                    # Get the SimpleValueDescriptor
                    svdesc = vdesc.get(userKey)

                    if svdesc is None:
                        raise NameError("Field {0} does not exist in Parameter {1}".format(userKey, vdesc.getName()))

                    # Check input shape against FESA
                    if checkDims:
                        self._checkDimVsJAPC(userValue, svdesc)

                    # Convert user input to SimpleParameterValue
                    simpleParVal = self._convertPyToSimpleVal(userValue, svdesc, dtype=dtype)

                    # And inject them in the parValNew MAP
                    parValNew.put(userKey, simpleParVal)
            else:
                raise TypeError("Unknown Parameter type: {0}. No idea how to set that.".format(vdesc.type.typeString))

        return parValNew

    def getParamInfo(self, parameterName, noPyConversion=False):
        """Return a string description of the parameter.

        Args:
            parameterName (str): The path + identifier of the FESA parameter
                to set. How to assemble a parameterName is
                explained `here <https://wikis.cern.ch/display/JAPC/Parameter+Names>`__.

            noPyConversion (bool): If True, don't return a String but the
                corresponding Java ParameterDescriptor Object.
        """
        # Get the (cached) JAPC parameter object
        p = self._getJapcPar(parameterName)

        if noPyConversion:
            return p.getParameterDescriptor()
        else:
            return p.getParameterDescriptor().toString()

    def subscribeParam(self, parameterName, onValueReceived=None, onException=None, getHeader=False,
                       noPyConversion=False, unixtime=False, **kwargs):
        """Subscribe to a Parameter with a Python callback function.

        Args:
            parameterName (str): The path + identifier of the FESA parameter
                to subscribe to.

            onValueReceived (function):
                If you subscribe to a simple parameter value, the
                callback function should be like:

                    onValueReceived(parameterName, value, headerInfo).

                `parameterName` is a string and `value` is the same as what you
                would get from .getParam(). `headerInfo` is a dict of header
                information and should only be there when `getHeader` is True

                If you subscribe to a parameter-group, the
                callback function should be like:

                    onValueReceived(values, headerInfos).

                Where `values` is a list of python values and `headerInfos` is
                a list of dicts with header information and should only be there
                when `getHeader` is True

            onException (function): A callback function like
                onException(parameterName, description, exception).
                parameterName and description are strings and exception is a
                Java Object

            getHeader (bool): Set to True if you want to get FESA header-information.
                This includes the `acqStamp`, `cycleStamp`, `selector` and
                `acqFlags` parameters.

            noPyConversion (bool): If True, a `RAW` Java ParameterValue Object will be
                handed over to the callback function. This provides minimum data-
                processing overhead.

            unixtime (bool): If True and noPyConversion is False, the header will be
                converted but the acqStamp and cycleStamp will be returned as seconds
                since epoch.

            timingSelectorOverride (str): Override of value set with
                setSelector() for a particular subscription.

            dataFilterOverride (dict): Override of value set with
                setSelector() for a particular subscription.

        Returns:
            Java SubscriptionHandle object, which can be used to start and stop
            this particular subscription.

        If the callback functions are set to None, a default callback function
        will be registered which prints to the console.

        Don't forget to start your subscriptions with startSubscriptions().

        An example::

            japc = PyJapc()
            def newValueCallback(parameterName, newValue, headerInfo):
                print("New Value received:", newValue, " Cycle Stamp:", headerInfo["cycleStamp"])
            japc.subscribeParam("CB.BHB1100/Acquisition#currentAverage", newValueCallback, getHeader=True)
            japc.startSubscriptions()
        """
        # --------------------------------------------------------------------
        # Create a unique string key for this subscription
        # --------------------------------------------------------------------
        parameterKey = self._getDictKeyFromParameterName(parameterName)
        try:
            sel = kwargs['timingSelectorOverride']
        except KeyError:
            sel = None
        parameterKey = self._transformSubscribeCacheKey(parameterKey=parameterKey,
                                                        selector=sel)

        # Get the (cached) JAPC parameter object
        par = self._getJapcPar(parameterName)
        lisJ = self._createValueListener(par=par,
                                         getHeader=getHeader,
                                         noPyConversion=noPyConversion,
                                         unixtime=unixtime,
                                         onValueReceived=onValueReceived,
                                         onException=onException)

        # --------------------------------------------------------------------
        # !!! Subscribe !!!
        # --------------------------------------------------------------------
        s = self._giveMeSelector(**kwargs)
        sh = par.createSubscription(s, lisJ)

        # --------------------------------------------------------------------
        # Add SubscriptionHandle to cache for later access
        # --------------------------------------------------------------------
        self._subscriptionHandleDict.setdefault(parameterKey, []).append(sh)

        return sh

    def stopSubscriptions(self, parameterName=None, selector=None):
        """Stop Monitoring on all previously subscribed parameters.

        Args:
            parameterName (Optional[str]): If not None, only the subscription
                of this particular parameter will be stopped.
            selector (Optional[str]): If not None, it augments the parameterName to stop
                subscription for the particular selector only.
        """
        for handler in self._filterSubscriptions(parameterName, selector):
            handler.stopMonitoring()

    def clearSubscriptions(self):
        """Clear the internal list of subscription handles.

        Call this to avoid that startSubscriptions() starts old and unwanted
        subscriptions.
        """
        self.stopSubscriptions()
        self._subscriptionHandleDict.clear()

    def startSubscriptions(self, parameterName=None, selector=None):
        """Start Monitoring on all previously Subscribed Parameters.

        Args:
            parameterName (Optional[str]): If not None, only the subscription
                of this particular parameter will restarted.
            selector (Optional[str]): If not None, it augments the parameterName to stop
                subscription for the particular selector only.
        """
        for handler in self._filterSubscriptions(parameterName, selector):
            handler.startMonitoring()

    def _filterSubscriptions(self, parameterName, selector):
        if parameterName is not None:
            if selector is not None:
                key = self._transformSubscribeCacheKey(
                    parameterKey=parameterName, selector=selector)
                if key in self._subscriptionHandleDict:
                    for sh in self._subscriptionHandleDict[key]:
                        yield sh
            else:
                for name, handles in self._subscriptionHandleDict.items():
                    # undefined selector will yield subscriptions to all
                    # selectors of this parameter
                    if (name == parameterName
                            or name.startswith(parameterName + '@')):
                        for sh in handles:
                            yield sh
        else:
            for pN, handles in self._subscriptionHandleDict.items():
                for sh in handles:
                    yield sh

    def _createValueListener(self, par, getHeader, noPyConversion, onValueReceived, onException, unixtime):

        if isinstance(par, jp.JClass("cern.japc.core.spi.group.ParameterGroupImpl")):
            # ----------------------------------------------------------------
            # We are dealing with a subscription to a Parameter Group
            # http://abwww.cern.ch/~pcrops/releaseinfo/pcropsdist/japc/japc/PRO/build/docs/api/
            # ----------------------------------------------------------------

            # Assign default callback functions
            def _defaultOnGrpValueReceived(vals, *args):
                print("ParameterGroup received:\n{0}".format(pprint.pformat(vals)))
                sys.stdout.flush()

            if onValueReceived is None:
                onValueReceived = _defaultOnGrpValueReceived

            # Wrap user callback function for value conversion
            def onGrpValueReceivedWrapper(vals):
                # The lock makes sure only one callback runs at one time
                with self._subscriptionCallbackLock:
                    try:
                        # Get a list of parameter names
                        parameternames = [v.getParameterName() for v in vals]
                        values, headers = self._convertParGroupToPy(vals)

                        # For compatibility, only return the header on request
                        if getHeader:
                            onValueReceived(parameternames, values, headers)
                        else:
                            onValueReceived(parameternames, values)
                    except Exception as e:
                        self.log.error("Exception in Subscription callback [{0}]\n{1}".format(
                            vals, traceback.format_exc()))
                        sys.stdout.flush()

            # Implement and register JAPC callback interface
            d = {'valueReceived': onValueReceived if noPyConversion else onGrpValueReceivedWrapper}
            return jp.JProxy("cern.japc.core.group.FailSafeParameterValueListener", d)
        else:
            # ----------------------------------------------------------------
            # We are dealing with a subscription to a
            # Simple Parameter Value (not a group)
            # ----------------------------------------------------------------

            # Assign default callback functions
            def _defaultOnException(parameterName, description, exception):
                self.log.error("Parameter {1} received exception:\n{0}".format(description, parameterName))
                sys.stdout.flush()

            def _defaultOnValueReceived(parameterName, val, *args):
                print("Parameter {1} received value:\n{0}".format(pprint.pformat(val), parameterName))
                sys.stdout.flush()

            onValueReceived = onValueReceived or _defaultOnValueReceived
            onException = onException or _defaultOnException

            # Wrap user callback function for value conversion
            def onValueReceivedWrapper(parameterName, value):
                # The lock makes sure only one callback runs at one time
                with self._subscriptionCallbackLock:
                    try:
                        val = self._convertValToPy(value.getValue())
                        # For compatibility, only return the header on request
                        if getHeader:
                            header = self._convertHeaderToPy(value.getHeader(), unixtime)
                            onValueReceived(parameterName, val, header)
                        else:
                            onValueReceived(parameterName, val)
                    except Exception as e:
                        self.log.error("Exception in Subscription callback [{0}]\n{1}".format(
                            parameterName, traceback.format_exc()))
                        sys.stdout.flush()

            # Implement and register JAPC callback interface
            d = {
                'exceptionOccured': onException,
                'valueReceived': onValueReceived if noPyConversion else onValueReceivedWrapper
            }
            return jp.JProxy("cern.japc.core.ParameterValueListener", d)

    def _checkDimVsJAPC(self, npArray, simpleValueDesc):
        """Check input array shape of a simple value against FESA"""
        tStr = simpleValueDesc.valueType.typeString

        npArray = np.array(npArray)

        if tStr == "DiscreteFunction":
            # Can there be more than 2 columns (x,y,...) ???
            if npArray.ndim != 2 or npArray.shape[0] != 2:
                raise TypeError("The parameter {0} is of type {1}. Please provide a 2D array of shape "
                                "[2, nValues]".format(simpleValueDesc.name, tStr))
            return

        if tStr == "DiscreteFunctionList":
            for temp in npArray:
                # Can there be more than 2 columns (x,y,...) ???
                if temp.ndim != 2 or temp.shape[0] != 2:
                    raise TypeError("The parameter {0} is of type {1}. Please provide a list of 2D arrays of shape "
                                    "[2, nValues]".format(simpleValueDesc.name, tStr))
            return

        npArray = np.atleast_2d(npArray)
        rc = simpleValueDesc.rowCount
        cc = simpleValueDesc.columnCount
        l = simpleValueDesc.length

        # We set a 1D array
        if cc == l or rc == l:
            if npArray.size == l:
                return
            else:
                raise TypeError("Array dimensions do not agree for {0}. Please provide a 1D array of "
                                "length {1}.".format(simpleValueDesc.name, l))

        if rc == 0:
            rc = 1
        if cc == 0:
            cc = 1

        # Get JAPC 2D array dimensions (can be [1,1] for primitive types)
        japc2Dshape = (rc, cc)
        input2Dshape = npArray.shape

        if japc2Dshape != input2Dshape:
            raise TypeError("Array dimensions do not agree for {0}. Please provide a 2D array of shape "
                            "[{1}, {2}]".format(simpleValueDesc.name, *japc2Dshape))

    def _getJavaValue(self, numpyType, pyValue=None):
        """Converts Numpy to basic Python first and then to JPype type.

        Workaround for this: x = numpy.int64(1), y = jpype.JLong(x)
        Do this:             y = getJavaValue(type(x), x)

        If pyValue==None: Returns the equivalent JPype type.
        """
        # Lookup table. Input = Python type, output = [Python scalar type, JPype Java Type]
        typeLookup = {
            int: [jp.JInt],
            float: [jp.JDouble],
            bool: [jp.JBoolean],
            str: [jp.JString],

            np.int_: [jp.JInt],
            np.float_: [jp.JDouble],
            np.bool_: [jp.JBoolean],
            np.str_: [jp.JString],

            np.int8: [int, jp.JByte],
            np.int16: [int, jp.JShort],
            np.int32: [int, jp.JInt],
            np.int64: [int, jp.JLong],

            # Java does not have unsigned types, take the next bigger ones instead.
            np.uint8: [int, jp.JShort],
            np.uint16: [int, jp.JInt],
            np.uint32: [int, jp.JLong],
            np.uint64: [int, jp.JLong],

            np.float32: [float, jp.JFloat],
            np.float64: [float, jp.JDouble]
        }

        if numpyType not in typeLookup:
            raise TypeError("Python type {0} can not be converted to a JAPC type".format(numpyType))
        if pyValue is None:
            return typeLookup[numpyType][-1]
        jValue = pyValue

        for cast in typeLookup[numpyType]:
            jValue = cast(jValue)

        return jValue

    def _getSimpleValFromDesc(self, valueDescriptor):
        """Return an empty `SimpleParameterValue` of the same type as `valueDescriptor`
        This can be filled with a value and then handed to a `ParameterValue`
        to do a `SET` with .setValue()
        """
        vdWrapper = jp.JObject(valueDescriptor, "cern.japc.value.SimpleDescriptor")
        parValNew = self._simpleParameterValueFactory.newValue(vdWrapper)
        return parValNew

    def _convertPyToSimpleVal(self, pyVal, valueDescriptor=None, dtype=None):
        """Convert a numpy array/primitive to a JAPC SimpleParameterValue
        of different types.

        How do we know what kind of SimpleParameterValue JAPC Object to produce?
        * if valueDescriptor is not provided, fall-back on looking at the Python
          type provided by the user
        * otherwise inspect the valueDescriptor and create a similar
          empty `SimpleParameterValue`
        * For now, this is only done for
          `DiscreteFunction`, `DiscreteFunctionList` and `EnumItem`
          but long-term I want to do this for all SimpleParameterValues
        """
        if dtype is None:
            if valueDescriptor is None:
                return self._convertPyToSimpleValFallback(pyVal)

            ts = valueDescriptor.valueType.typeString
        else:
            ts = dtype

        # --------------------------------------------------------------------
        # Special case: Numpy array to JAPC DiscreteFunction(List)
        # --------------------------------------------------------------------
        if ts == "DiscreteFunction":
            # DiscreteFunction is always double (I hope :p)
            pyVal = np.array(pyVal, dtype="double")
            df = self._functionFactory.newDiscreteFunction(pyVal[0, :], pyVal[1, :])
            parValNew = jp.JPackage("cern").japc.value.spi.value.simple.DiscreteFunctionValue(df)

        elif ts == "DiscreteFunctionList":
            # Allcoate JArray for DFs
            dfa = jp.JArray(jp.JPackage("cern").japc.value.spi.value.DiscreteFunctionImpl)(len(pyVal))
            # Iterate over first dimension of user data
            for i, funcDat in enumerate(pyVal):
                funcDat2 = np.array(funcDat, dtype="double")
                dfa[i] = self._functionFactory.newDiscreteFunction(funcDat2[0, :], funcDat2[1, :])
            dfl = self._functionFactory.newDiscreteFunctionList(dfa)
            parValNew = jp.JPackage("cern").japc.value.spi.value.simple.DiscreteFunctionListValue(dfl)

        elif ts == "Enum":
            parValNew = self._getSimpleValFromDesc(valueDescriptor)
            # For now, enums can only be SET with an INT or STR
            if isinstance(pyVal, six.string_types):
                parValNew.setString(pyVal)
            else:
                parValNew.setInt(pyVal)

        else:
            # This is a bit lame. For all primitives and arrays, the value descriptor is
            # completely ignored and we rely on the python type completely.
            # ToDo: evaluate the valuedescriptor for simpleValues
            parValNew = self._convertPyToSimpleValFallback(pyVal)

        return parValNew

    def _convertPyToSimpleValFallback(self, pyVal):
        """Conv. numpy array/primitive to a JAPC SimpleParameterValue
        We will guess what kind of `SimpleParameterValue` object to produce
        by looking at the Python type the user has provided

        We need this fallback as without INCA there are no value-descriptors
        """
        # --------------------------------------------------------------------
        # Preprocessing: convert lists to numpy arrays
        # --------------------------------------------------------------------
        # Python type of input variable
        pValT = type(pyVal)

        # Convert input list / tuple to a numpy array
        if pValT in (list, tuple):
            pyVal = np.array(pyVal)
            pValT = type(pyVal)

        # --------------------------------------------------------------------
        # User entered a numpy array.
        # E.g., japc.setParam("blaParam", arange(3, dtype=double))
        # --------------------------------------------------------------------
        if isinstance(pyVal, np.ndarray):
            # Use lookup table to get Java type
            # Use complex numpy type as input e.g. float32
            javaVarType = self._getJavaValue(pyVal.dtype.type, None)

            # Convert the numpy array to a list and then to a 1D JArray (flattened)
            # Note that at some point JPype will be able to digest
            # numpy arrays directly and .tolist() will not be needed any more (faster)
            # 11.1.16: Checked and array conversion still does not work with JPype 0.6.1
            jArrayValues = jp.JArray(javaVarType, 1)(pyVal.flatten().tolist())

            if pyVal.ndim == 1:
                # Create the shiny new 1D JAPC ParameterValue object
                parValNew = self._simpleParameterValueFactory.newValue(jArrayValues)
            elif pyVal.ndim == 2:
                # Store array shape in JAPC friendly format
                jArrayShape = jp.JArray(jp.JInt)(pyVal.shape)
                # Create the shiny new 2D JAPC ParameterValue object
                parValNew = self._simpleParameterValueFactory.newValue(jArrayValues, jArrayShape)
            elif pyVal.ndim == 0:
                # This is a single number from a numpy array arange(3)[0] for example
                parValNew = self._simpleParameterValueFactory.newValue(pyVal)
            else:
                raise TypeError("JAPC does only support arrays with <= 2 dimensions, {0} were given.".format(
                    pyVal.ndim)
                )

        # --------------------------------------------------------------------
        # User entered a Java type explicitly.
        # E.g., japc.setParam("blaParam", jp.JLong(123456))
        # --------------------------------------------------------------------
        elif isinstance(pyVal, jp._jwrapper._JWrapper):
            parValNew = self._simpleParameterValueFactory.newValue(pyVal)

        # --------------------------------------------------------------------
        # User entered a common Python type,
        # E.g., japc.setParam("blaParam", 1.2)
        # We will use the lookup table to cast it to a Java type
        # --------------------------------------------------------------------
        else:
            # Explicitly cast Python type to Java type with the Lookup table
            jVal = self._getJavaValue(pValT, pyValue=pyVal)
            parValNew = self._simpleParameterValueFactory.newValue(jVal)
        return parValNew

    def _convert2DJarrayToNumpy(self, jArr):
        """Faster conversion of 2D JArrays to numpy arrays.

        If jArr is 2D then jArr[:] will be a list of 1D JArrays. 1D JArrays can
        be converted fast to numpy with 1djArr[:].

        Due to a `bug <https://github.com/originell/jpype/issues/133>`_ this
        will return a list on Windows and a numpy array on Linux.
        """
        try:
            arrType = type(jArr[0][0])
        except:
            # Workaround for empty arrays
            return np.array(jArr)

        if arrType == str:
            # Workaround for str arrays
            return np.array(jArr)

        arrShape = (len(jArr), len(jArr[0]))
        resultArray = np.empty(arrShape, dtype=arrType)

        for i, cols in enumerate(jArr[:]):
            # This should work on Win (list) and Linux (numpy array)
            resultArray[i, :] = cols[:]
        return resultArray

    def _convertSimpleValToPy(self, val):
        """Convert the Java JAPC SimpleParameterValue object to a Python type
        or numpy array we do getXXX() for primitives and array2D.getXXXArray2D()
        for arrays.
        """
        knownTypes = ["boolean", "byte", "double", "float", "int", "long", "short", "string"]
        tStr = val.getValueType().typeString.lower()

        # -------------------------------------------------------
        # Handle the DiscreteFunction(List)
        # -------------------------------------------------------
        if tStr == "discretefunction":
            df = val.getDiscreteFunction()

            # Safe but very slow
            # xVal = np.array(df.getXArray())
            # yVal = np.array(df.getYArray())

            # Fast! works for 1D arrays only but OK here.
            # https://github.com/originell/jpype/issues/133
            xVal = df.getXArray()[:]
            yVal = df.getYArray()[:]

            return np.array((xVal, yVal))

        if tStr == "discretefunctionlist":
            dfl = val.getDiscreteFunctionList()
            dfValues = []

            for df in dfl.iterator():
                xVal = df.getXArray()[:]
                yVal = df.getYArray()[:]
                dfValues.append(np.array((xVal, yVal)))

            return dfValues

        # -------------------------------------------------------
        # Handle the cern.japc.value.spi.value.simple.EnumValue
        # Note that some `enum` parameters are returned as
        # `int` straight away. Probaply an internal conversion
        # done by INCA on a lower layer
        # -------------------------------------------------------
        if tStr == "enum":
            return (val.getInt(), val.getString())

        # -------------------------------------------------------
        # Handle enumsets
        # -------------------------------------------------------
        if tStr == "enumset":
            return [(v.code, v.string) for v in val.value]

        # -------------------------------------------------------
        # Handle the Primitives / arrays
        # -------------------------------------------------------
        for knownType in knownTypes:
            if tStr.startswith(knownType):
                # We found a type match!

                # Check if it is not an array (tStr does not contain any [])
                # Then we can use the simple .getInt() function
                if tStr.find("[]") == -1:
                    getFunctionName = 'get{0}'.format(knownType.title())
                    return getattr(val, getFunctionName)()
                else:
                    # We are dealing with an array (1D or 2D) and have to use the .array2D.getIntArray2D() function
                    getFunctionName = 'get{0}Array2D'.format(knownType.title())
                    jArr = getattr(val.array2D, getFunctionName)()

                    # Safest but _EEXTREMELY_ slow
                    # npArr = np.atleast_1d(np.array(jArr).squeeze())

                    # Fastest but n-D array not supported by JPype yet
                    # npArr = np.atleast_1d(jArr[:].squeeze())

                    npArr = np.atleast_1d(self._convert2DJarrayToNumpy(jArr).squeeze())

                    # If the array only contains one value, return the naked value
                    if npArr.size == 1:
                        return npArr.item()

                    return npArr

        self.log.warning("No Python match found for JAPC - Simple type {0}. Please convert it yourself.".format(tStr))

        return val

    def _convertValToPy(self, val):
        """Convert the Java JAPC ParameterValue Map or SimpleParameter object
        to a Python equivalent.
        """
        if val is None:
            return None

        t = val.type.typeString

        # Can be "Map" or "Simple"
        if t == "Simple":
            return self._convertSimpleValToPy(val)
        elif t == "Map":
            # Do a quick and dirty conversion to Python dict()
            d = dict()
            for n in val.getNames():
                d[n] = self._convertSimpleValToPy(val.get(n))
            return d
        else:
            self.log.warning("No Python match found for JAPC type {0}. Please convert it yourself.".format(t))
            return val

    def _convertParGroupToPy(self, failSafeParValues, unixtime=False):
        """Convert the Java JAPC FailSafeParameterValue[] object
        to a Python equivalent (list of values, list of headers).
        Will raise an TypeError, if called with a simple (non-iterable) Parameter object
        """
        values = []
        headers = []

        for fspv in failSafeParValues:
            # fspv is of type jpype._jclass.cern.japc.value.spi.FailSafeParameterValueImpl
            values.append(self._convertValToPy(fspv.getValue()))
            headers.append(self._convertHeaderToPy(fspv.getHeader(), unixtime))

        return values, headers

    def _convertHeaderToPy(self, valueHeader, unixtime=False):
        """ Convert a `ValueHeader` object to a python dictionary """
        headerDict = dict()
        if unixtime:
            headerDict["acqStamp"] = valueHeader.getAcqStamp() / 1e9
            headerDict["cycleStamp"] = valueHeader.getCycleStamp() / 1e9
        else:
            headerDict["acqStamp"] = datetime.datetime.fromtimestamp(valueHeader.getAcqStamp() / 1e9,
                                                                     tz=self._selectedTimezone)
            # headerDict["acqStampMillis"] = valueHeader.getAcqStampMillis()
            headerDict["cycleStamp"] = datetime.datetime.fromtimestamp(valueHeader.getCycleStamp() / 1e9,
                                                                       tz=self._selectedTimezone)
            # headerDict["cycleStampMillis"] = valueHeader.getCycleStampMillis()

        headerDict["isFirstUpdate"] = bool(valueHeader.isFirstUpdate())
        headerDict["isImmediateUpdate"] = bool(valueHeader.isImmediateUpdate())
        if valueHeader.getSelector() is not None:
            headerDict["selector"] = valueHeader.getSelector().toString()
        else:
            headerDict["selector"] = None
        return headerDict

    def _transformSubscribeCacheKey(self, parameterKey, selector):
        return parameterKey + '@' + selector if selector is not None else parameterKey
