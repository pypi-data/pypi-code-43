# Copyright (C) 2019 Charlie Hoy <charlie.hoy@ligo.org> This program is free
# software; you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os

import numpy as np
from pesummary.core.inputs_new import Input, PostProcessing
from pesummary.gw.file.read import read as GWRead
from pesummary.utils.exceptions import InputError
from pesummary.utils.utils import logger, SamplesDict


class GWInput(Input):
    """Super class to handle gw specific command line inputs
    """
    def __init__(self, opts):
        logger.info("Command line arguments: %s" % (opts))
        self.opts = opts
        self.result_files = self.opts.samples
        self.existing = self.opts.existing
        self.compare_results = self.opts.compare_results
        self.add_to_existing = False
        if self.existing is not None:
            self.add_to_existing = True
            self.existing_data = self.grab_data_from_metafile(
                self.existing, compare=self.compare_results
            )
            self.existing_samples = self.existing_data[0]
            self.existing_injection_data = self.existing_data[1]
            self.existing_file_version = self.existing_data[2]
            self.existing_file_kwargs = self.existing_data[3]
            self.existing_config = self.existing_data[4]
            self.existing_labels = self.existing_data[5]
            self.existing_approximant = self.existing_data[6]
            self.existing_psd = self.existing_data[7]
            self.existing_calibration = self.existing_data[8]
        else:
            self.existing_labels = None
            self.existing_samples = None
            self.existing_file_version = None
            self.existing_file_kwargs = None
            self.existing_config = None
            self.existing_injection_data = None
            self.existing_approximant = None
            self.existing_psd = None
            self.existing_calibration = None
        self.user = self.opts.user
        self.webdir = self.opts.webdir
        self.baseurl = self.opts.baseurl
        self.labels = self.opts.labels
        self.config = self.opts.config
        self.injection_file = self.opts.inj_file
        self.publication = self.opts.publication
        self.kde_plot = self.opts.kde_plot
        self.samples = self.opts.samples
        self.priors = None
        self.custom_plotting = self.opts.custom_plotting
        self.email = self.opts.email
        self.dump = self.opts.dump
        self.hdf5 = self.opts.save_to_hdf5
        self.approximant = self.opts.approximant
        self.gracedb = self.opts.gracedb
        self.detectors = None
        self.calibration = self.opts.calibration
        self.psd = self.opts.psd
        self.nsamples_for_skymap = self.opts.nsamples_for_skymap
        self.sensitivity = self.opts.sensitivity
        self.no_ligo_skymap = self.opts.no_ligo_skymap
        self.multi_threading_for_skymap = self.opts.multi_threading_for_skymap
        self.gwdata = self.opts.gwdata
        self.make_directories()
        self.copy_files()

    @staticmethod
    def grab_data_from_metafile(existing_file, webdir, compare=None):
        """Grab data from an existing PESummary metafile

        Parameters
        ----------
        existing_file: str
            path to the existing metafile
        webdir: str
            the directory to store the existing configuration file
        compare: list, optional
            list of labels for events stored in an existing metafile that you
            wish to compare
        """
        f = GWRead(existing_file)
        labels = f.labels
        indicies = np.arange(len(labels))

        if compare:
            indicies = []
            for i in compare:
                if i not in labels:
                    raise InputError(
                        "Label '%s' does not exist in the metafile. The list "
                        "of available labels are %s" % (i, labels)
                    )
                indicies.append(labels.index(i))
            labels = compare

        DataFrame = f.samples_dict
        if f.injection_parameters != []:
            inj_values = f.injection_dict
        else:
            inj_values = {
                i: [float("nan")] * len(DataFrame[i]) for i in labels
            }
        for i in inj_values.keys():
            for param in inj_values[i].keys():
                if inj_values[i][param] == "nan":
                    inj_values[i][param] = float("nan")

        if f.config is not None:
            config = []
            for i in labels:
                config_dir = os.path.join(webdir, "config")
                f.write_config_to_file(i, outdir=config_dir)
                config_file = os.path.join(
                    config_dir, "{}_config.ini".format(i)
                )
                config.append(config_file)

        psd = {}
        if f.psd is not None and f.psd[labels[0]] != {}:
            for i in labels:
                psd[i] = {
                    ifo: f.psd[i][ifo] for ifo in f.psd[i].keys()
                }
        calibration = {}
        if f.calibration is not None and f.calibration[labels[0]] != {}:
            for i in labels:
                calibration[i] = {
                    ifo: f.calibration[i][ifo] for ifo in f.calibration[i].keys()
                }

        return [
            DataFrame, inj_values,
            {
                i: j for i, j in zip(
                    labels, [f.input_version[ind] for ind in indicies]
                )
            },
            {
                i: j for i, j in zip(
                    labels, [f.extra_kwargs[ind] for ind in indicies]
                )
            }, config, labels,
            {
                i: j for i, j in zip(
                    labels, [f.approximant[ind] for ind in indicies]
                )
            }, psd, calibration
        ]

    @staticmethod
    def grab_data_from_file(file, label, config=None, injection=None):
        """Grab data from a result file containing posterior samples

        Parameters
        ----------
        file: str
            path to the result file
        label: str
            label that you wish to use for the result file
        config: str, optional
            path to a configuration file used in the analysis
        injection: str, optional
            path to an injection file used in the analysis
        """
        f = GWRead(file)
        if config is not None:
            f.add_fixed_parameters_from_config_file(config)
        if injection:
            f.add_injection_parameters_from_file(injection)
        f.generate_all_posterior_samples()
        parameters = f.parameters
        samples = f.samples
        DataFrame = {label: SamplesDict(parameters, samples)}
        kwargs = f.extra_kwargs
        if hasattr(f, "injection_parameters"):
            injection = f.injection_parameters
            if injection is not None:
                for i in parameters:
                    if i not in list(injection.keys()):
                        injection[i] = float("nan")
            else:
                injection = {i: j for i, j in zip(
                    parameters, [float("nan")] * len(parameters))}
        else:
            injection = {i: j for i, j in zip(
                parameters, [float("nan")] * len(parameters))}
        version = f.input_version
        return DataFrame, {label: injection}, {label: version}, {label: kwargs}

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, samples):
        print("gw samples")
        if not samples:
            raise InputError("Please provide a results file")
        samples_dict, injection_data_dict = {}, {}
        file_version_dict, file_kwargs_dict = {}, {}
        approximant_dict, psd_dict, calibration_dict = {}, {}, {}
        config, labels = None, None
        for num, i in enumerate(samples):
            if not os.path.isfile(i):
                raise Exception("File %s does not exist" % (i))
            data = self.grab_data_from_input(
                i, self.labels[num], config=self.config[num],
                injection=self.injection_file[num]
            )
            if len(data) > 4:
                config = data[4]
                labels = data[5]
                for j in labels:
                    samples_dict[j] = data[0][j]
                    injection_data_dict[j] = data[1][j]
                    file_version_dict[j] = data[2][j]
                    file_kwargs_dict[j] = data[3][j]
                    approximant_dict[j] = data[6][j]
                    psd_dict[j] = data[7][j]
                    calibration_dict[j] = data[8][j]
            else:
                samples_dict[self.labels[num]] = data[0][self.labels[num]]
                injection_data_dict[self.labels[num]] = data[1][self.labels[num]]
                file_version_dict[self.labels[num]] = data[2][self.labels[num]]
                file_kwargs_dict[self.labels[num]] = data[3][self.labels[num]]
        self._samples = samples_dict
        self._injection_data = injection_data_dict
        self._file_version = file_version_dict
        self._file_kwargs = file_kwargs_dict
        if config is not None:
            self._config = config
        if labels is not None:
            self.labels = labels
        if approximant_dict != {}:
            self.approximant = approximant_dict
        if psd_dict != {}:
            self.psd = psd_dict
        if calibration_dict != {}:
            self.calibration = calibration_dict

    @property
    def approximant(self):
        return self._approximant

    @approximant.setter
    def approximant(self, approximant):
        approximant_list = {i: None for i in self.labels}
        if approximant is None:
            logger.warn(
                "No approximant passed. Waveform plots will not be generated"
            )
        elif approximant is not None:
            if len(approximant) != len(self.labels):
                raise InputError(
                    "Please pass an approximant for each result file"
                )
            approximant_list = {i: j for i, j in zip(self.labels, approximant)}
        self._approximant = approximant_list

    @property
    def gracedb(self):
        return self._gracedb

    @gracedb.setter
    def gracedb(self, gracedb):
        self._gracedb = gracedb
        if gracedb is not None:
            if gracedb[0] != "G" or gracedb[0] != "g" or gracedb[0] != "S":
                raise InputError(
                    "Invalid GraceDB ID passed. The GraceDB ID must be of the "
                    "form G0000 or S0000"
                )

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, calibration):
        if calibration is not None:
            data = get_psd_or_calibration_data(
                calibration, self.extract_calibration_data_from_file
            )
            self.add_to_prior_dict("calibration", data)
        self._calibration = calibration

    @property
    def detectors(self):
        return self._detectors

    @detectors.setter
    def detectors(self, detectors):
        detector_list = []
        if not detectors:
            for i in self.labels:
                params = list(self.samples[i].keys())
                individual_detectors = []
                for j in params:
                    if "optimal_snr" in j and j != "network_optimal_snr":
                        det = j.split("_optimal_snr")[0]
                        individual_detectors.append(det)
                individual_detectors = sorted(
                    [str(i) for i in individual_detectors])
                if individual_detectors:
                    detector_list.append("_".join(individual_detectors))
                else:
                    detector_list.append(None)
        else:
            detector_list = detectors
        logger.debug("The detector network is %s" % (detector_list))
        self._detectors = detector_list

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, calibration):
        data = {}
        if calibration is not None:
            prior_data = self.get_psd_or_calibration_data(
                calibration, self.extract_calibration_data_from_file
            )
            self.add_to_prior_dict("calibration", prior_data)
        for num, i in enumerate(self.result_files):
            f = GWRead(i)
            calibration_data = f.calibration_data_in_results_file
            if calibration_data is None:
                data[self.labels[num]] = {
                    None: None
                }
            elif isinstance(f, pesummary.gw.file.formats.pesummary.PESummary):
                for num in range(len(calib_data[0])):
                    data[self.labels[num]] = {
                        j: k for j, k in zip(
                            calib_data[1][num], calib_data[0][num]
                        )
                    }
            else:
                data[self.labels[num]] = {
                    j: k for j, k in zip(calib_data[1], calib_data[0])
                }
        self._calibration = data

    @property
    def psd(self):
        return self._psd

    @psd.setter
    def psd(self, psd):
        self._psd = psd
        if psd is not None:
            data = self.get_psd_or_calibration_data(
                psd, self.extract_psd_data_from_file
            )
            self._psd = data

    @property
    def nsamples_for_skymap(self):
        return self._nsamples_for_skymap

    @nsamples_for_skymap.setter
    def nsamples_for_skymap(self, nsamples_for_skymap):
        self._nsamples_for_skymap = nsamples_for_skymap
        if nsamples_for_skymap is not None:
            self._nsamples_for_skymap = int(nsamples_for_skymap)
            number_of_samples = [
                data.number_of_samples for label, data in self.samples.items()
            ]
            if not all(i < self._nsamples_for_skymap for i in number_of_samples):
                min_arg = np.argmin(number_of_samples)
                raise InputError(
                    "You have specified that you would like to use {} "
                    "samples to generate the skymap but the file {} only "
                    "has {} samples. Please reduce the number of samples "
                    "you wish to use for the skymap production".format(
                        self._nsamples_for_skymap, self.result_files[min_arg],
                         number_of_samples[min_arg]
                    )
                )

    @property
    def gwdata(self):
        return self._gwdata

    @gwdata.setter
    def gwdata(self, gwdata):
        from pesummary.gw.file.formats.base_read import GWRead as StrainFile

        self._gwdata = gwdata
        if gwdata is not None:
            for i in gwdata.keys():
                if not os.path.isfile(gwdata[i]):
                    raise InputError(
                        "The file {} does not exist. Please check the path to "
                        "your strain file".format(gwdata[i])
                    )
            timeseries = StrainFile.load_strain_data(gwdata)
            self._gwdata = timeseries

    @staticmethod
    def extract_psd_data_from_file(file):
        """Return the data stored in a psd file

        Parameters
        ----------
        file: path
            path to a file containing the psd data
        """
        if not os.path.isfile(file):
            raise InputError("The file '{}' does not exist".format(file))
        f = np.genfromtxt(file, skip_footer=2)
        return f

    @staticmethod
    def extract_calibration_data_from_file(file):
        """Return the data stored in a calibration file

        Parameters
        ----------
        file: path
            path to a file containing the calibration data
        """
        if not os.path.isfile(file):
            raise InputError("The file '{}' does not exist".format(file))
        f = np.genfromtxt(file)
        return f

    @staticmethod
    def get_ifo_from_file_name(file):
        """Return the IFO from the file name

        Parameters
        ----------
        file: str
            path to the file
        """
        file_name = file.split("/")[-1]
        if any(j in file_name for j in ["H1", "_0", "IFO0"]):
            ifo = "H1"
        elif any(j in file_name for j in ["L1", "_1", "IFO1"]):
            ifo = "L1"
        elif any(j in file_name for j in ["V1", "_2", "IFO2"]):
            ifo = "V1"
        else:
            ifo = file_name
        return ifo

    def get_psd_or_calibration_data(self, input, executable):
        """Return a dictionary containing the psd or calibration data

        Parameters
        ----------
        input: list/dict
            list/dict containing paths to calibration/psd files
        executable: func
            executable that is used to extract the data from the calibration/psd
            files
        """
        data = {}
        if isinstance(input, dict):
            keys = list(input.keys())
        if isinstance(input, dict) and isinstance(input[keys[0]], list):
            if not all(len(input[i]) != len(self.labels) for i in list(keys)):
                raise InputError(
                    "Please ensure the number of calibration/psd files matches "
                    "the number of result files passed"
                )
            for idx in range(len(input[keys[0]])):
                data[self.labels[idx]] = {
                    i: executable(input[i][idx]) for i in list(keys)
                }
        elif isinstance(input, dict):
            for i in self.labels:
                data[i] = {
                    j: executable(input[j]) for j in list(input.keys())
                }
        elif isinstance(input, list):
            for i in self.labels:
                data[i] = {
                    self.get_ifo_from_file_name(j): executable(j) for j in input
                }
        else:
            raise InputError(
                "Did not understand the psd/calibration input. Please use the "
                "following format 'H1:path/to/file'"
            )
        return data

    def default_labels(self):
        """Return a list of default labels.
        """
        label_list = []
        for num, i in enumerate(self.result_files):
            if self.gracedb and self.detectors[num]:
                label_list.append("_".join(
                    [self.gracedb, self.detectors[num]]))
            elif self.gracedb:
                label_list.append(self.gracedb)
            elif self.detectors[num]:
                label_list.append(self.detectors[num])
            else:
                file_name = ".".join(i.split("/")[-1].split(".")[:-1])
                label_list.append("%s_%s" % (round(time()), file_name))

        duplicates = dict(set(
            (x, label_list.count(x)) for x in
            filter(lambda rec: label_list.count(rec) > 1, label_list)))

        for i in duplicates.keys():
            for j in range(duplicates[i]):
                ind = label_list.index(i)
                label_list[ind] += "_%s" % (j)
        if self.add_to_existing:
            for num, i in enumerate(label_list):
                if i in self.existing_labels:
                    ind = label_list.index(i)
                    label_list[ind] += "_%s" % (num)
        return label_list


class GWPostProcessing(PostProcessing):
    """
    """
    def __init__(self, inputs, colors="default"):
        """
        """ 

    @property
    def maxL_samples(self):
        return self._maxL_samples

    @maxL_samples.setter
    def maxL_samples(self):
        key_data = self.grab_key_data_from_result_files()
        maxL_samples = {
            i: {
                j: key_data[i][j]["maxL"] for j in key_data[i].keys()
            } for i in key_data.keys()
        }
        for i in self.labels:
            maxL_samples[i]["approximant"] = self.approximant[i]
        return maxL_samples

    @property
    def pepredicates_probs(self):
        return self._pepredicates_probs

    @pepredicates_probs.setter
    def pepredicates_probs(self, pepredicates_probs):
        classifications = {}
        default_error = (
            "Failed to generate source classification probabilities because {}"
        )
    

        for num, i in enumerate(self.labels):
            try:
                from pesummary.gw.pepredicates import PEPredicates
                from pesummary.utils.utils import RedirectLogger

                with RedirectLogger("PEPredicates", level="DEBUG") as redirector:
                    data = PEPredicates.classifications(
                        self.samples[num], self.parameters[num]
                    )
                classifications[i] = {
                    "default": data[0],
                    "population": data[1]
                }
            except ImportError:
                logger.warn(
                    default_error.format("'PEPredicates' is not installed")
                )
            except Exception as e:
                logger.warn(
                    default_error.format("%s" % (e))
                )

    def grab_key_data_from_result_files(self):
        """Grab the mean, median, maxL and standard deviation for all
        parameters for all each result file
        """
        key_data = {
            i: {
                j: {
                    "mean": self.samples[i][j].mean,
                    "median": self.samples[i][j].median,
                    "std": self.samples[i][j].std,
                    "maxL": self.samples[i][j].maxL
                } for j in self.samples[i].keys()
            } for i in self.labels
        }
        return key_data
