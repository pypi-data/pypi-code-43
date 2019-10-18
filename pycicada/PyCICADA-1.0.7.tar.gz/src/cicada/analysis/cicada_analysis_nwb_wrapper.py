from cicada.analysis.cicada_analysis_format_wrapper import CicadaAnalysisFormatWrapper
from pynwb.ophys import ImageSegmentation, TwoPhotonSeries, Fluorescence
from pynwb.image import ImageSeries
import os
from pynwb import NWBHDF5IO


class CicadaAnalysisNwbWrapper(CicadaAnalysisFormatWrapper):
    """
    Allows to communicate with the nwb format
    """

    def __init__(self, data_ref, load_data=True):
        CicadaAnalysisFormatWrapper.__init__(self, data_ref=data_ref, data_format="nwb", load_data=load_data)
        self._nwb_data = None
        if self.load_data_at_init:
            self.load_data()

    def load_data(self):
        io = NWBHDF5IO(self._data_ref, 'r')
        self._nwb_data = io.read()
        # if we close it, then later on we have an exception such as: ValueError: Not a dataset (not a dataset)
        # io.close()

    @property
    def identifier(self):
        return self._nwb_data.identifier

    @property
    def age(self):
        return self._nwb_data.subject.age

    @property
    def genotype(self):
        return self._nwb_data.subject.genotype

    @property
    def species(self):
        return self._nwb_data.subject.species

    @property
    def subject_id(self):
        """
         Id of the subject
         :return: None if subject_id unknown
        """
        return self._nwb_data.subject.subject_id

    @property
    def weight(self):
        """
         Id of the subject
         :return: None if weight unknown
        """
        return self._nwb_data.subject.weight

    @property
    def sex(self):
        """
         Sex (gender) of the subject
         :return: None if sex unknown
        """
        return self._nwb_data.subject.sex

    def get_segmentations(self):
        """

        Returns: a dict that for each step till plane_segmentation represents the different option.
        First dict will have as keys the name of the modules, then for each modules the value will be a new dict
        with keys the ImageSegmentation names and then the value will be a list representing the segmentation plane

        """
        segmentation_dict = dict()
        for name_mod, mod in self._nwb_data.modules.items():
            segmentation_dict[name_mod] = dict()
            for key, value in mod.data_interfaces.items():
                # we want to check that the object in Module is an Instance of ImageSegmentation
                if isinstance(value, ImageSegmentation):
                    image_seg = value
                    # key is the name of segmentation, and value a list of plane_segmentation
                    segmentation_dict[name_mod][key] = []
                    for plane_seg_name in image_seg.plane_segmentations.keys():
                        segmentation_dict[name_mod][key].append(plane_seg_name)

        # it could be empty, but if it would matter, it should have been check by method check_data in CicadaAnalysis
        return segmentation_dict

    def get_roi_response_series(self):
        """

                Returns: a list or dict of objects representing all roi response series (rrs) names
                rrs could represents raw traces, or binary raster, and its link to a given segmentation.
                The results returned should allow to identify the segmentation associated.
                Object could be strings, or a list of strings, that identify a rrs and give information
                how to get there.

        """
        rrs_dict = dict()
        for name_mod, mod in self._nwb_data.modules.items():
            rrs_dict[name_mod] = dict()
            for key, fluorescence in mod.data_interfaces.items():
                # we want to check that the object in Module is an Instance of pynwb.ophys.Fluorescence
                if isinstance(fluorescence, Fluorescence):
                    rrs_dict[name_mod][key] = []
                    for name_rrs, rrs in fluorescence.roi_response_series.items():
                        rrs_dict[name_mod][key].append(name_rrs)
        return rrs_dict

    def get_pixel_mask(self, segmentation_info):
        """
        Return pixel_mask which is a list of list of pair of integers representing the pixels coordinate (x, y) for each
        cell. the list length is the same as the number of cells.
        Args:
            segmentation_info: a list of 3 elements: first one being the name of the module, then the name
            of image_segmentation and then the name of the segmentation plane.

        Returns:

        """
        if len(segmentation_info) < 3:
            return None

        name_module = segmentation_info[0]
        mod = self._nwb_data.modules[name_module]

        name_mode = segmentation_info[1]
        name_plane_seg = segmentation_info[2]
        plane_seg = mod[name_mode].get_plane_segmentation(name_plane_seg)

        if 'pixel_mask' not in plane_seg:
            return None

        return plane_seg['pixel_mask']

    def contains_ci_movie(self, consider_only_2_photons):
        """
        Indicate if the data object contains at least one calcium imaging movie represented by an instance of
        pynwb.image.ImageSeries
        Args:
            consider_only_2_photons: boolean, it True means we consider only 2 photons calcium imaging movies,
            if other exists but not 2 photons, then False will be return
        Returns: True if it's the case, False otherwise

        """
        # a TwoPhotonSeries is an instance of ImageSeries
        has_one = False
        for key, acquisition_data in self._nwb_data.acquisition.items():
            if consider_only_2_photons:
                if isinstance(acquisition_data, TwoPhotonSeries):
                    has_one = True
            else:
                if isinstance(acquisition_data, ImageSeries):
                    has_one = True
        if not has_one:
            return False

        return True

    def get_ci_movies(self, only_2_photons):
        """
        Return a dict with as key a string identifying the movie, and as value a dict of CI movies
        a string as file_name if external, or a 3d array
        Args:
            only_2_photons: return only the 2 photon movies

        Returns:

        """
        ci_movies_dict = dict()

        for key, acquisition_data in self._nwb_data.acquisition.items():
            if only_2_photons:
                if isinstance(acquisition_data, ImageSeries) and \
                        (not isinstance(acquisition_data, TwoPhotonSeries)):
                    continue

            if isinstance(acquisition_data, ImageSeries):
                image_series = acquisition_data
                if image_series.format == "external":
                    movie_file_name = image_series.external_file[0]
                    movie_data = movie_file_name
                else:
                    movie_data = image_series.data
                ci_movies_dict[key] = movie_data

        return ci_movies_dict

    def get_identifier(self, session_data):
        """
        Get the identifier of one of the data to analyse
        Args:
            session_data: Data we want to know the identifier

        Returns: A hashable object identfying the data

        """
        return session_data.identifier

    def get_intervals_names(self):
        """
        Return a list representing the intervals contains in this data
        Returns:

        """
        if self._nwb_data.intervals is None:
            return []

        intervals = []
        for name_interval in self._nwb_data.intervals.keys():
            intervals.append(name_interval)
        return intervals

    def __str__(self):
        """
        Return a string representing the session. Here session.identifier
        :return:
        """
        return self._nwb_data.identifier
