import numpy as np
import os
import json
import importlib

from webgeodyn.data import GHData, TSData
from webgeodyn.data.normPnm import semiNormalisedSchmidt, noNorm
from webgeodyn.constants import rE, rC

ACCELERATION = False


class Model:
    """
    Class handling models that contain measures data
    """

    # CONSTRUCTING METHODS

    def __init__(self, dataDirectory=None, dataFormat='default', nth=90, nph=180, normalisation=semiNormalisedSchmidt,
                 keepRealisations=True):
        """
        :param dataDirectory: directory where the data is located
        :type dataDirectory: str (path)
        :param dataFormat: format to use for loading the data
        :type dataFormat: str
        :param nth: size of the theta grid
        :type nth: int
        :param nph: size of the phi grid
        :type nph: int
        :param normalisation: normalisation to use for Legendre polynomials
        :type normalisation: function
        :param keepRealisations: indicating if realisations should be kept or averaged
        :type keepRealisations: bool
        """
        self.nth = nth
        self.nph = nph
        self.normalisation = normalisation
        self.setGridSize(nth, nph)
        self.times = None

        if normalisation is None:
            self.PnmNorm = noNorm
        else:
            self.PnmNorm = normalisation

        self.dataDirectory = dataDirectory
        # Put the dataFormat to lower for consistency with future checks
        self.dataFormat = dataFormat.lower()
        self.color = "#000000"

        # Measures that are under the form of Gauss coefficients (Spherical Harmonics)
        self.measures = {}
        self.measures_rms = {}
        # Measures NOT under the form of Gauss coefficients
        self.notSH_measures = {}

        if dataDirectory is not None:
            self.loadDataFromFile(keepRealisations)

    def copy(self):
        """
        Returns a copy of current model.

        :return: Copy of the model with same measures, normalisation and grid sizes.
        :rtype: Model
        """
        returnedModel = Model(nth=self.nth, nph=self.nph, normalisation=self.normalisation)
        for measureName in self.measures:
            measure = self.measures[measureName]
            newcoefs = measure.data.copy()
            if self.hasRMSData(measureName):
                newcoefs_rms = self.measures_rms[measureName].data.copy()
            else:
                newcoefs_rms = None

            returnedModel.addMeasure(measureName, measure.measureType, measure.lmax, measure.units, newcoefs,
                                     newcoefs_rms, times=self.times)
        return returnedModel

    def hasRMSData(self, measureName):
        """
        Checks if the measure exists and if RMS data exists for it.

        :param measureName: name of the measure to probe
        :type measureName: str
        :return: a boolean indicating if RMS data exists for the measure
        :rtype: bool
        """
        return (measureName in self.measures_rms) and (self.measures_rms[measureName].data is not None)

    def toMeanRMS(self):
        """
        Converts a Model with realisations to a Model contaning only Mean and RMS.

        :return: Model with the same measures but under the form Mean/RMS
        :rtype: Model
        """
        returnedModel = Model(nth=self.nth, nph=self.nph, normalisation=self.normalisation)
        for measureName in self.measures:
            measure = self.measures[measureName]
            newcoefs = np.mean(measure.data, axis=2)
            newcoefs_rms = np.std(measure.data, axis=2)
            returnedModel.addMeasure(measureName, measure.measureType, measure.lmax, measure.units, newcoefs,
                                     newcoefs_rms, times=self.times)

        return returnedModel

    def clearCache(self):
        """
        Clears the cache of all measures
        """
        for measureName in self.measures:
            self.measures[measureName].clearCache()

    def setGridSize(self, nth, nph):
        """
        Sets the grid theta ]0,pi[ (size: nth+1) and phi grid [0, 2pi] (size: nph). Called in __init__.

        :param nth: size of the theta grid
        :type nth: int
        :param nph: size of the phi grid
        :type nph: int
        """
        self.nth = nth
        self.nph = nph
        self.th_step = np.pi / (nth + 1)
        self.ph_step = 2 * np.pi / nph

        self.th = np.arange(np.pi / (nth + 1), np.pi, self.th_step)
        self.ph = np.arange(0, 2 * np.pi, self.ph_step)

    def addMeasure(self, measureName, measureType, lmax, units=None, data=None, rmsdata=None, times=None):
        """
        Adds a new measure to the model. Also computes secondary measures ('DIVHU' and 'LOD') for 'U'.

        :param measureName: Name of the measure
        :type measureName: str
        :param measureType: Type of the measure
        :type measureType: str
        :param lmax: Maximal degree
        :type lmax: int
        :param units: unit of the measure (default: None)
        :type units: str
        :param data: measure data (default: None, in this case, only creates a times array)
        :type data: np.array
        :param rmsdata: RMS data (optional: default to None)
        :type rmsdata: np.array
        :param times: times corresponding of the measure (default:None, in this case do nothing)
        :type times: np.array
        """
        if times is not None:
            if self.times is not None:
                if not np.allclose(self.times, times):
                    raise ValueError("Time array must be all the same for a given modeldata")
            self.times = times
        if measureType == "U" or (measureType == "DIVHU" or measureType == "dU/dt"):
            if data is not None:
                self.measures[measureName] = TSData(
                    data,
                    int(lmax),
                    units,
                    measureType,
                    self.PnmNorm,
                    self.th,
                    self.ph
                )

                # Compute secondary measures only for U
                if measureType == "U":
                    # Compute the divH if not already done and if DivHU was not added
                    if "DIVHU" not in self.measures:
                        divh_data = self.computeDivH(self.measures[measureName])

                        if divh_data.shape != data.shape:
                            raise RuntimeError("Computation of DivHU went wrong for measure={}".format(measureName))

                        # Once the data is built, add the measure DivHU to the model
                        self.measures["DIVHU"] = TSData(
                            divh_data,
                            int(lmax),
                            "yr-1",
                            "DIVHU",
                            self.PnmNorm,
                            self.th,
                            self.ph
                        )

                        if ACCELERATION:
                            acc_data = self.computeAcceleration()
                            self.measures["dU/dt"] = TSData(
                                acc_data,
                                int(lmax),
                                "km/yr2",
                                "dU/dt",
                                self.PnmNorm,
                                self.th,
                                self.ph
                            )

                    # Compute the LOD if not already done nor added
                    if "LOD" not in self.notSH_measures:
                        lod_data = self.computeLOD()

                        # Once the data is built, add the measure LOD to the model
                        self.notSH_measures["LOD"] = lod_data

                if rmsdata is not None:
                    self.measures_rms[measureName] = TSData(
                        rmsdata,
                        int(lmax),
                        units,
                        measureType,
                        self.PnmNorm,
                        self.th,
                        self.ph,
                    )
        else:
            if data is not None:
                self.measures[measureName] = GHData(
                    data,
                    int(lmax),
                    units,
                    measureType,
                    self.PnmNorm,
                    self.th,
                    self.ph
                )
                if rmsdata is not None:
                    self.measures_rms[measureName] = GHData(
                        rmsdata,
                        int(lmax),
                        units,
                        measureType,
                        self.PnmNorm,
                        self.th,
                        self.ph
                    )
        return

    def loadDataFromFile(self, keepRealisations):
        """
        Loads the data from files according to the dataDirectory and dataFormat of the model. Uses dedicated load functions of the inout module.

        :param keepRealisations: indicating if realisations should be kept or averaged
        :type keepRealisations: bool
        """
        self.measures = {}
        self.measures_rms = {}

        # If no specified format, read "dataFormat" file in data directory
        if self.dataFormat is None:
            if os.path.exists(os.path.join(self.dataDirectory, "dataFormat")):
                with open(os.path.join(self.dataDirectory, "dataFormat"), 'r') as f:
                    self.dataFormat = f.readline().rstrip()

        # If specified data format (or dataFormat file), read via the built-in format from inout.py
        if self.dataFormat is not None:
            print("Reading model using predefined format", self.dataFormat)
            load_fct = importlib.import_module("webgeodyn.inout." + self.dataFormat).load
            load_fct(self.dataDirectory, self, keepRealisations)

        # Else raise an error
        else:
            raise ValueError("dataFormat is not defined.")

    def saveDataToFile(self, dataDirectory, forceOverwrite=False, dataformat="default"):
        """
        Saves the data of the model in a designated format. Uses dedicated save functions of the inout module.

        :param dataDirectory: directory where to save the file
        :type dataDirectory: str (path)
        :param forceOverwrite: indicates if files of the same name should be overwritten
        :type forceOverwrite: bool
        :param dataformat: dataformat under which the data should be saved (default: "default")
        :type dataformat: str
        """
        save_fct = importlib.import_module("webgeodyn.inout." + dataformat).save
        save_fct(dataDirectory, self, forceOverwrite)

    # GETTERS CALLED BY AJAX REQUESTS

    def getSpherHarmData(self, measureName, l, mlist, removemean, computeallrealisation=False, irealisation=-1):
        """
        Extracts the spherical harmonic coefficients of a measure for asked degrees and orders.

        :param measureName: name of the measure
        :type measureName: str
        :param l: degree for which to extract coefficients
        :type l: int
        :param mlist: orders for which to extract coefficients
        :type mlist: int or list of ints
        :param removemean: indicates if the temporal mean should be removed
        :type removemean: bool
        :param computeallrealisation: not used
        :type computeallrealisation:
        :param irealisation: not used
        :type irealisation:
        :return: JSON containing the times ('times') and coefficients of the measure for the asked degrees and orders ('data')
        :rtype: dict
        """
        jsondata = {"times": self.times.tolist(), "data": {}, "unit": self.measures[measureName].units}

        if mlist is None:
            mlist = np.arange(l + 1)  # Returns all m for given l
        if isinstance(mlist, int):
            mlist = [mlist]  # Return a single m

        print("ASKING FOR l=", l, "m=", mlist)

        for m in mlist:
            jsondata["data"][str(m)] = {}
            for coef in self.measures[measureName].coefs_list:
                k = self.measures[measureName].lm2k(int(l), int(m), coef)
                if k is None:
                    continue  # it has no k indice (e.g. h10)
                jsondata["data"][str(m)][coef] = {}

                if self.measures[measureName].has_realisations:
                    if removemean:
                        jsondata["data"][str(m)][coef]["values"] = np.mean(
                            (self.measures[measureName].data[:, k] - self.measures[measureName].coefs_mean[k]),
                            axis=1).tolist()
                    else:
                        jsondata["data"][str(m)][coef]["values"] = np.mean(self.measures[measureName].data[:, k],
                                                                           axis=1).tolist()
                    jsondata["data"][str(m)][coef]["rms"] = np.std(self.measures[measureName].data[:, k],
                                                                   axis=1).tolist()
                else:
                    if removemean:
                        jsondata["data"][str(m)][coef]["values"] = (self.measures[measureName].data[:, k] - self.measures[measureName].coefs_mean[k]).tolist()
                    else:
                        jsondata["data"][str(m)][coef]["values"] = self.measures[measureName].data[:, k].tolist()

                    if self.hasRMSData(measureName):
                        jsondata["data"][str(m)][coef]["rms"] = np.hstack(
                            self.measures_rms[measureName].data[:, k]).tolist()
                        # Comment: hstack on rms is for returning an array containing [left,right,left,right,left,...] if each rms point is [left,right]

        return jsondata

    def getTimeSerieData(self, measureName, vectorComponent, cutvariable, cutvalue, removemean, coordtype,
                         computeallrealisation=False, irealisation=-1):
        """
        Computes the time evolution of a component (radial or angular) of a measure.

        :param measureName: name of the measure
        :type measureName: str
        :param vectorComponent: vector component to compute
        :type vectorComponent: str
        :param cutvariable: variable along which the cut is made
        :type cutvariable: str ('phi' or 'theta')
        :param cutvalue: value of the cut angle
        :type cutvalue: float
        :param removemean: indicates if the temporal mean should be removed
        :type removemean: bool
        :param coordtype: type of the coordinate asked (angle or curvilinear (s_north or s_south))
        :type coordtype: str
        :param computeallrealisation: boolean indicating if the computation should be on all realisations or on the mean (default=False)
        :type computeallrealisation: bool
        :param irealisation: index of the realisation to use (default=-1 and takes the mean instead)
        :type irealisation: int
        :return: JSON containing the times ('times'), the angles used for the computation ('angles') and the time series of the measure ('data')
        :rtype: dict
        """

        jsondata = {"times": self.times.tolist(), "data": {}}

        def get_coords_list(input_th, coord_type):
            """ Get data for computation and display from coord_type (angle or curvilinear) """
            if coord_type == "s_north":
                display_data = np.linspace(0, 1., len(input_th))[1:-1]
                angles_to_compute = np.arcsin(display_data)
            elif coord_type == "s_south":
                # Compute angles for s = ]-1,0[ to have the correct sampling...
                s = np.linspace(-1, 0., len(input_th))[1:-1]
                # ...but add np.pi to have the angle between ]pi/2,pi[ (South)...
                angles_to_compute = np.arcsin(s) + np.pi
                # Recompute y_data in consequence
                display_data = np.sin(angles_to_compute)
                # Flip both to have the same order as s_north
                angles_to_compute = np.flip(angles_to_compute)
                display_data = np.flip(display_data)
            else:
                display_data = (input_th * 180 / np.pi)
                angles_to_compute = input_th
            return angles_to_compute, display_data.tolist()

        # Separate treatment for geostrophic component
        if vectorComponent == 'geos':
            th, jsondata['angles'] = get_coords_list(self.th, coordtype)
            data = self.measures[measureName].computeUGeostrophic(rC, th, computeallrealisation=computeallrealisation, irealisation=irealisation)

        else:
            if cutvalue is None:
                raise TypeError('{} is not a valid number'.format(cutvalue))
            cutvalue = cutvalue / 180 * np.pi
            if cutvariable == "phi":
                ph = [cutvalue]
                th, jsondata['angles'] = get_coords_list(self.th, coordtype)
            elif cutvariable == "theta":
                th = [cutvalue]
                ph = self.ph
                jsondata["angles"] = (ph * 180 / np.pi).tolist()
            else:
                print("ERROR, cutvariable should be theta or phi")
                return jsondata

            data = self.measures[measureName].computeRThetaPhiData(rC, th, ph, [vectorComponent],
                                                               computeallrealisation=computeallrealisation,
                                                               irealisation=irealisation)[vectorComponent]

            data = data.reshape((data.shape[0], data.shape[1] * data.shape[2]))

        # Common operations
        if removemean:
            data = data - np.mean(data, axis=0)

        jsondata["unit"] = self.measures[measureName].units
        jsondata["data"] = data.tolist()

        return jsondata

    def getObservatoryData(self, measureName, r, strth, strph):
        """
        Computes all components of a measure to compare it with observatory data.

        :param measureName: name of the measure
        :type measureName: str
        :param r: radius where to evaluate the measure components
        :type r: float
        :param strth: theta where to evaluate the measure components (under string format, in degrees)
        :type strth: str
        :param strph: phi where to evaluate the measure components (under string format, in degrees)
        :type strph: str
        :return: JSON containing the times ('times'), the parameters used for the computation ('r', 'th', 'ph), the measure parameters ('unit', 'measuretype') and the computed components ('mean' and 'rms' if present)
        :rtype: dict
        """
        jsondata = {}

        # Or compute it from this data
        jsondata["mean"] = {"times": self.times.tolist()}
        if self.measures[measureName].has_realisations:
            jsondata["rms"] = {"times": self.times.tolist()}
            data = self.measures[measureName].computeRThetaPhiData(float(r), [float(strth) / 180 * np.pi],
                                                                   [float(strph) / 180 * np.pi], ["r", "th", "ph"],
                                                                   computeallrealisation=True)
        else:
            data = self.measures[measureName].computeRThetaPhiData(float(r), [float(strth) / 180 * np.pi],
                                                                   [float(strph) / 180 * np.pi], ["r", "th", "ph"])

        for component in data:
            if self.measures[measureName].has_realisations:
                jsondata["mean"][component] = np.mean(data[component], axis=3).flatten().tolist()
                jsondata["rms"][component] = np.std(data[component], axis=3).flatten().tolist()
            else:
                jsondata["mean"][component] = data[component].flatten().tolist()

        jsondata["r"] = float(r)
        jsondata["th"] = float(strth)
        jsondata["ph"] = float(strph)
        jsondata["unit"] = self.measures[measureName].units
        jsondata["measuretype"] = self.measures[measureName].measureType
        return jsondata

    def getDataInfo(self):
        """
        Gets info on the model (measures, times and color).

        :return: JSON containing the measures type and lmax ('measures'), the times ('times') and the color ('color') of the model.
        :rtype: dict
        """
        datainfo = {
            "measures":
                {measureName: {
                    "type": self.measures[measureName].measureType,
                    "lmax": self.measures[measureName].lmax,
                } for measureName in self.measures},
            "notSH_measures":
                {measureName: {
                    "type": measureName
                } for measureName in self.notSH_measures},
            "times": self.times.tolist(),
            "color": self.color,
        }

        return datainfo

    def getFileInfo(self):
        """
        Gets the info on the location and the format of the files used to load the model.

        :return: JSON containing the data directory ('directory'), the format of the files ('format') and if the measures have rms ('rms').
        :rtype: dict
        """
        fileinfo = {
            "directory": self.dataDirectory,
            "format": self.dataFormat,
            "rms": {measureName: self.hasRMSData(measureName) for measureName in self.measures}
        }

        return fileinfo

    def canGetGlobeData(self, measureName, vectorComponent, r=rC):
        """
        Gets the component to compute to compute vectorComponent of a measure.

        :param measureName: name of the measure
        :type measureName: str
        :param vectorComponent: component to compute
        :type vectorComponent: str
        :param r: radius where the component must be computed (default: constants.rC)
        :type r: float
        :return: the components to compute and the state of computation
        :rtype: tuple
        """
        if vectorComponent is None:
            # Test whole vector
            oneComponentToCompute = False
            oneComponentComputing = False
            for component in self.measures[measureName].components:
                isComponentToCompute, isComponentComputing = self.measures[measureName].isAlreadyComputed(r, component)
                # If at least one isComponentToCompute is True, oneComponentToCompute is True
                oneComponentToCompute = isComponentToCompute or oneComponentToCompute
                # Idem for oneComponentComputing
                oneComponentComputing = isComponentComputing or oneComponentComputing
            return oneComponentToCompute, oneComponentComputing
        else:
            isComponentToCompute, isComponentComputing = self.measures[measureName].isAlreadyComputed(r,
                                                                                                      vectorComponent)
            return isComponentToCompute, isComponentComputing

    def getGlobeDataComputingState(self, measureName):
        """
        Gets the computing state of a measure.

        :param measureName: name of the measure to check
        :type measureName: str
        :return: computing state
        :rtype: float
        """
        return self.measures[measureName].computingState

    def getGlobeData(self, measureName, vectorComponent, itime, removemean, r=rC):
        """
        Computes a component of a measure on the whole globe.

        :param measureName: Name of the measure
        :type measureName: str
        :param vectorComponent: component to compute
        :type vectorComponent: str
        :param itime: index of the date at which the computation will be done
        :type itime: int
        :param removemean: indicates if the temporal mean should be removed
        :type removemean: bool
        :param r: radius where the component must be computed (default: constants.rC)
        :type r: float
        :return: JSON containing the parameters of the computation ("theta_step" in degrees, "phi_step" in degrees, "time"), the unit of the measure ("unit") and the data computed on the angular grid ('dataarray').
        :rtype: dict
        """
        jsondata = {"theta_step": self.th_step * 180 / np.pi,
                    "phi_step": self.ph_step * 180 / np.pi,
                    "time": self.times[itime],
                    "unit": self.measures[measureName].units}
        if vectorComponent is None:
            # Return whole vector
            data = []
            for component in self.measures[measureName].components:
                print(component, "in", self.measures[measureName].components)
                componentData = self.measures[measureName].getRThetaPhiGridData(r, itime, removemean, component)
                if componentData is not None:
                    data.append(componentData)
            gridData = np.dstack(tuple(componentData for componentData in data)).tolist()
        else:
            gridData = self.measures[measureName].getRThetaPhiGridData(r, itime, removemean, vectorComponent).tolist()

        jsondata["dataarray"] = gridData
        return jsondata

    def getSpectraData(self, measureName, spectraType, spectraDate):
        """
        Returns a JSON with the Lowes spectra of the asked type and measure.

        :param measureName: name of the measure used of the computation
        :type measureName: str
        :param spectraType: type of spectra ("spectraofmean", "meanofspectra", "dated" or "deviation")
        :type spectraType: str
        :param spectraDate: date at which the timed spectrum should be evaluated
        :type spectraDate: float
        :return: JSON containing the degrees, the Lowes spectrum and the units of the measure
        :rtype: dict
        """
        measure = self.measures[measureName]

        if spectraType == "dated":
            date_index = np.where(self.times == spectraDate)
            # If no index was found, raise an error
            if len(date_index) == 0:
                raise KeyError('{} is not a valid date of model {}'.format(spectraDate, self.dataFormat))
            # Else compute for the first occurrence
            else:
                itime = date_index[0][0]
        else:
            itime = 0

        degrees, lowes_spectrum = measure.computeSpectra(spectraType, spectraDate, itime)

        jsondata = {'degrees': degrees.tolist(), 'data': lowes_spectrum.tolist(),
                    'unit': measure.units, 'has_reals': measure.has_realisations}

        return jsondata

    def getLodData(self, removemean):
        loddata = self.notSH_measures['LOD']

        if removemean:
            loddata = loddata - loddata.mean(axis=0)

        if loddata.ndim > 1:
            mean_lod = loddata.mean(axis=1)
            rms_lod = loddata.std(axis=1)
        else:
            mean_lod = loddata
            rms_lod = np.zeros_like(loddata)

        return {'times': self.times.tolist(), 'data': mean_lod.tolist(), 'rmsdata': rms_lod.tolist()}

    # COMPUTATION OF SECONDARY MEASURES

    def computeAcceleration(self):
        """
        Computes the acceleration dU/dt by finite differences.  The 'U' measure must be loaded.

        :return: NumPy array containing the computed acceleration
        :rtype: np.array (same shape as measure U data)
        """
        if "U" not in self.measures:
            raise ValueError("Cannot compute acceleration: no measure for core flow was found !")
        measure_U = self.measures["U"].data

        # Get unique times
        unique_times, unique_indexes = np.unique(self.times, return_index=True)
        dt = unique_times[1] - unique_times[0]

        acceleration = np.zeros_like(measure_U)

        # Compute acceleration for each unique time...
        for i_unique in unique_indexes:
            if i_unique == 0:
                continue
            # dU/dt(t) = U(t) - U(t-dt) / dt
            acc = (measure_U[i_unique] - measure_U[i_unique-1])/dt
            current_t = self.times[i_unique]
            # ...but set it at every index corresponding to the current time
            current_indexes = np.where(self.times == current_t)[0]
            for i_t in current_indexes:
                acceleration[i_t] = acc

        return acceleration

    def computeDivH(self, measure_U):
        """ Computes the coefficients of DivH from a flow measure.

        :param measure_U: Core flow measure
        :type measure_U: TSData
        :return: NumPy array containing the computed DivHU
        :rtype: np.array (same shape as measure U data)
        """
        if not isinstance(measure_U, TSData):
            raise ValueError("Cannot compute DivH(U): the given core flow measure has not the right type !")

        # DivH is computed only from poloidal coeffs
        # so I build a bool array that is True only for poloidal coeffs
        is_s = np.logical_or(measure_U.is_sc, measure_U.is_ss)
        L = measure_U.l

        # If U has realisations, expand the dims to be able to broadcast
        if measure_U.has_realisations:
            is_s = measure_U.expand_dims(is_s)
            L = measure_U.expand_dims(L)

        Lplus1 = L + 1

        # The coeffs of DivH are the poloidal ones of U multiplied by -l(l+1)/rC
        # DivH has no toroidal coeffs so these are put to 0
        data_divh = np.where(is_s, -L * Lplus1 * measure_U.data / rC, 0)

        return data_divh

    def computeLOD(self):
        """ Computes the length-of-day variation (LOD) from the measure of U. The 'U' measure must be loaded.

        :return: NumPy array containing the computed LOD
        :rtype: np.array (times, 1) or (times, 1, coef)
        """
        if "U" not in self.measures:
            raise ValueError("Cannot compute LOD: no measure for core flow was found !")
        measure_U = self.measures["U"].data

        lmax = self.measures["U"].lmax

        # If there are realisations put the coef axis at the end
        if self.measures["U"].has_realisations:
            measure_U = np.swapaxes(measure_U, 1, 2)

        # Compute LOD with the available data (realisations included if present)
        LOD = measure_U[..., 0]
        if lmax > 1:
            LOD = LOD + 1.776 * measure_U[..., 8]
        if lmax > 2:
            LOD = LOD + 0.080 * measure_U[..., 24]
        if lmax > 3:
            LOD = LOD + 0.002 * measure_U[..., 48]
        LOD = LOD * 1.232

        return LOD

    def computeLowes(self, gauss_coefs, measureName, squared=True):
        """
        Computes the Lowes spectrum for any measure ("U" and "DIVHU" included) of the model.

        :param gauss_coefs: 1D NumPy array containing the (squared or not) gauss coeffs for every degree
        :type gauss_coefs: np.array
        :param measureName: name of the measure used for computation
        :type measureName: str
        :param squared: indicates if the supplied gauss_coefs are already squared or not (default = True)
        :type squared: bool
        :return: 1D NumPy array containing the Lowes spectrum
        :rtype: np.array (dim: lmax)
        """
        degrees = self.measures[measureName].l
        lmax = self.measures[measureName].lmax

        if degrees.shape != gauss_coefs.shape or degrees.ndim != 1:
            raise ValueError(
                'Problem while computing Lowes spectrum. Got {} and {} that are not the same or not unidimensionnal'.format(
                    degrees.shape, gauss_coefs.shape))

        if not squared:
            squared_gauss_coefs = np.square(gauss_coefs)
        else:
            squared_gauss_coefs = gauss_coefs

        lowes_spectrum = np.zeros(lmax, dtype=np.float64)

        if measureName == "U" or measureName == "DIVHU":
            for i_l, l in enumerate(degrees):
                # Indexes of arrays start from 0 so the index is l-1
                lowes_spectrum[l - 1] += l * (l + 1) / (2 * l + 1) * squared_gauss_coefs[i_l]
        else:
            for i_l, l in enumerate(degrees):
                # Indexes of arrays start from 0 so the index is l-1
                lowes_spectrum[l - 1] += (l + 1) * squared_gauss_coefs[i_l]

        return lowes_spectrum
