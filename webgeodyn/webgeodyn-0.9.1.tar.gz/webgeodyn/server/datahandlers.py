from tornado.web import *
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from tornado.web import HTTPError

import re
import json

globalExecutor = ThreadPoolExecutor(max_workers=10)


class ServerError(HTTPError):
    def __init__(self, reason, **kwargs):
        super().__init__(reason=reason,  **kwargs)


class GenericDataHandler(RequestHandler):
    def initialize(self, models, obsdata):
        self.models = models
        print("{0} initialisation...".format(type(self).__name__))
        self.obsdata = obsdata

    def getModel(self, dataName):
        if self.models.isCached(dataName):
            return self.models[dataName]
        else:
            raise ValueError("No model named " + dataName)

    @run_on_executor
    def async_getModel(self, dataName):
        # Loads model from data directory, async = ask to load and return nothing
        if not self.models.isCached(dataName) and not self.models.isModelLoading(dataName):
            self.getModel(dataName)
        return True

    def write_error(self, status_code, **kwargs):
        print("Raised error '{}' (status code {}) in {}".format(self._reason, status_code, type(self).__name__))
        self.finish(json.dumps({
                'SUCCESS': False,
                'ERROR': self._reason,
                'error_code': status_code
            }))


class DataListHandler(GenericDataHandler):
    def get(self):
        json_output_data = {"datalist": {}}
        for dataName in self.models.getModelList():
            model = self.getModel(dataName)
            if not model:
                continue
            json_output_data["datalist"][dataName] = model.getDataInfo()
        self.write(json.dumps(json_output_data))


class ExportFileInfoHandler(GenericDataHandler):
    """ Handler that gets the info of files to export for all the models BUT COV-OBS and CHAOS. """
    def get(self):
        json_output_data = {"exportfileinfo": {}}
        for dataName in self.models.getModelList():
            model = self.getModel(dataName)
            if not model:
                continue
            # Skip CHAOS and COV-OBS model that will not be available for export
            if re.match("(cov.?obs|chaos)", model.dataFormat, re.IGNORECASE) is not None:
                continue
            json_output_data["exportfileinfo"][dataName] = model.getFileInfo()
        self.write(json.dumps(json_output_data))


class ObservatoryDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {}
        json_output_data["SUCCESS"] = False
        print("ObservatoryDataHandler post", json_request)

        if "theta" not in json_request:
            json_output_data["obsdata"] = self.obsdata.getDataInfo()
            json_output_data["SUCCESS"] = True
        elif "phi" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify theta and phi"
        elif "selecteddata" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify selecteddata"
        elif "obstypes" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify obstypes"
        else:
            theta = json_request.get("theta")
            phi = json_request.get("phi")
            obstypes = json_request.get("obstypes")
            selecteddata = json_request.get("selecteddata")
            measuretype = json_request.get("measuretype")

            r = self.obsdata.getObsR(theta,phi,obstypes)

            json_output_data["modeldata"] = {}
            for data in selecteddata:
                dataName = data.get("dataname")
                measureName = data.get("measurename")
                if dataName not in json_output_data["modeldata"]:
                    json_output_data["modeldata"][dataName] = {}
                json_output_data["modeldata"][dataName][measureName] = \
                    self.getModel(dataName).getObservatoryData(measureName, r, theta, phi)

            json_output_data["obsdata"] = self.obsdata.getData(measuretype, theta, phi, obstypes)
            json_output_data["SUCCESS"] = True

        self.write(json.dumps(json_output_data))


class GlobeDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        async_compute = False
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {}
        json_output_data["SUCCESS"] = False

        if "dataname" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify dataname"
        elif "measure" not in json_request:
            if self.models.isCached(json_request["dataname"]):
                json_output_data = self.getModel(json_request["dataname"]).getDataInfo()
            else:
                json_output_data["computing"] = "loading " + json_request["dataname"] + " data files"
                self.async_getModel(json_request["dataname"])  # Get model data for further
            json_output_data["SUCCESS"] = True
        elif "time" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify time"
        else:
            datatime = json_request.get("time")
            measureName = json_request.get("measure")
            vectorComponent = json_request.get("vectorcomponent")
            removemean = json_request.get("removemean")
            dataName = json_request.get("dataname")
            toCompute, isComputing = \
                self.getModel(dataName).canGetGlobeData(measureName, vectorComponent)
            if (not toCompute) and (not isComputing):
                # Return cached value
                json_output_data["computing"] = False
                json_output_data["data"] = \
                    yield self.async_getData(dataName, measureName, vectorComponent, datatime, removemean)
            else:
                # Return computing in progress
                json_output_data["computing"] = "computing real space grid"
                json_output_data["computingState"] = self.getModel(dataName).getGlobeDataComputingState(measureName)
                if not isComputing:
                    # Tell to compute
                    async_compute = True

            json_output_data["SUCCESS"] = True

        self.write(json.dumps(json_output_data))
        self.finish()

        if async_compute:
            #self.executor.submit(self.getModel(dataName).getGlobeData,*(measureName,vectorComponent,datatime,removemean))
            #Compute after anwser
            #self.async_getData(dataName, measureName, vectorComponent, datatime, removemean)
            self.async_getData(dataName, measureName, vectorComponent, datatime, removemean)

    @run_on_executor
    def async_getData(self, dataName, measureName, vectorComponent, datatime, removemean):
        return self.getModel(dataName).getGlobeData(measureName, vectorComponent, datatime, removemean)


class LodDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {"SUCCESS": False}

        print("LodDataHandler post", json_request)

        if "selecteddata" not in json_request:
            raise ServerError("Invalid data request, please select some data")

        if "removemean" not in json_request:
            raise ServerError("Invalid data request, please specify removemean")

        selected_data = json_request.get("selecteddata")
        removemean = json_request.get("removemean")

        for data in selected_data:
            data_name = data.get("dataname")
            if data_name not in json_output_data:
                json_output_data[data_name] = {}
            try:
                json_output_data[data_name] = self.getModel(data_name).getLodData(removemean)
            except ValueError as e:
                # Transform the ValueError in HTTPError that will be caught by tornado write_error
                raise ServerError("Error while getting LOD data of {}: {}".format(data_name, e))

        json_output_data["SUCCESS"] = True
        self.write(json.dumps(json_output_data))


class SpectraDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {"SUCCESS": False}

        print("SpectraDataHandler post", json_request)

        if "selecteddata" not in json_request:
            raise ServerError("Invalid data request, please select some data")

        if "type" not in json_request:
            raise ServerError("Invalid data request, please specify a spectra type")

        if "date" not in json_request:
            raise ServerError("Invalid data request, please specify a date")

        selected_data = json_request.get("selecteddata")
        spectra_type = json_request.get("type")
        spectra_date = json_request.get("date")

        if type(spectra_date) is not float:
            spectra_date = float(spectra_date)

        for data in selected_data:
            data_name = data.get("dataname")
            measure_name = data.get("measurename")
            if data_name not in json_output_data:
                json_output_data[data_name] = {}
            try:
                json_output_data[data_name][measure_name] = self.getModel(data_name).getSpectraData(measure_name, spectra_type, spectra_date)
            except ValueError as e:
                # Transform the ValueError in HTTPError that will be catched by tornado write_error
                raise ServerError("Error while computing spectra of {}: {}".format(data_name, e))

        json_output_data["SUCCESS"] = True
        self.write(json.dumps(json_output_data))


class SpherHarmDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {}
        json_output_data["SUCCESS"] = False
        print("SpherHarmDataHandler post", json_request)

        if "selecteddata" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify selecteddata"
        elif "m" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify l"
        elif "l" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify l"
        else:
            l = json_request.get("l")
            m = json_request.get("m")
            removemean = json_request.get("removemean")
            selecteddata = json_request.get("selecteddata")

            for data in selecteddata:
                dataName = data.get("dataname")
                measureName = data.get("measurename")
                if dataName not in json_output_data:
                    json_output_data[dataName] = {}
                json_output_data[dataName][measureName] = \
                    self.getModel(dataName).getSpherHarmData(measureName, l, m, removemean)

            json_output_data["SUCCESS"] = True

        self.write(json.dumps(json_output_data))


class TimeSerieDataHandler(GenericDataHandler):
    executor = globalExecutor

    @tornado.gen.coroutine
    def post(self):
        str_data = tornado.escape.url_unescape(self.request.body)
        json_request = json.loads(str_data)
        json_output_data = {}
        json_output_data["SUCCESS"] = False
        print("TimeSerieDataHandler post", json_request)

        if "dataname" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify dataname"
        elif "measure" not in json_request:
            if self.models.isCached(json_request["dataname"]):
                json_output_data = self.getModel(json_request["dataname"]).getDataInfo()  # True is for analysis times only
            else:
                json_output_data["computing"] = "loading " + json_request["dataname"] + " data files"
                self.async_getModel(json_request["dataname"])  # Get model data for further
            json_output_data["SUCCESS"] = True
        elif "cutvalue" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify cutvalue"
        elif "cutvariable" not in json_request:
            json_output_data["ERROR"] = "Invalid data request, please specify cutvariable"
        else:
            measureName = json_request.get("measure")
            vectorComponent = json_request.get("vectorcomponent")
            removemean = json_request.get("removemean")
            cutvalue = json_request.get("cutvalue")
            cutvariable = json_request.get("cutvariable")
            dataName = json_request.get("dataname")
            coordtype = json_request.get("coordtype")
            print("getting timeSerieData", measureName, vectorComponent, cutvariable, cutvalue, coordtype)
            json_output_data = \
                self.getModel(dataName).getTimeSerieData(measureName, vectorComponent, cutvariable, cutvalue, removemean, coordtype)
            json_output_data["SUCCESS"] = True

        self.write(json.dumps(json_output_data))
