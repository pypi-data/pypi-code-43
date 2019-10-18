from abc import ABC, abstractmethod, abstractproperty


class CicadaAnalysisFormatWrapper(ABC):
    """
    An abstract class that should be inherit in order to create a specific format wrapper

    """

    def __init__(self, data_ref, data_format, load_data=True):
        """

        Args:
            data_ref: A reference to the data to analyse. It could be the data directly instanciate.
            But more commonly, it would a file_name or a directory. Will be used by load_data method to load the data.
            load_data: load the data in the __init__ methods, otherwise the user will have to call load_data()
        """
        super().__init__()
        self._data_ref = data_ref
        self.load_data_at_init = load_data
        self._data_format = data_format

    @property
    def data_format(self):
        return self._data_format

    @abstractmethod
    def load_data(self):
        """
        Load data in memory
        Returns:

        """
        pass

    # it's only needed to provide an implementation only for the getter in the class works and allows for instantiation
    @property
    @abstractmethod
    def identifier(self):
        """
        Identifier of the session
        :return:
        """
        pass

    # it's only needed to provide an implementation only for the getter in the class works and allows for instantiation
    @property
    @abstractmethod
    def age(self):
        """
         Age of the subject
         :return: None if age unknown
            """
        pass

    @property
    @abstractmethod
    def genotype(self):
        """
         Genotype of the subject
         :return: None if age unknown
        """
        pass

    @property
    @abstractmethod
    def species(self):
        """
         Species of the subject
         :return: None if age unknown
        """
        pass

    @property
    @abstractmethod
    def subject_id(self):
        """
         Id of the subject
         :return: None if age unknown
        """
        pass

    @property
    @abstractmethod
    def weight(self):
        """
         Id of the subject
         :return: None if age unknown
        """
        pass

    @property
    @abstractmethod
    def sex(self):
        """
         Sex (gender) of the subject
         :return: None if sex unknown
        """
        pass

    # @identifier.setter
    # @abstractmethod
    # def identifier(self):
    #     pass



    @abstractmethod
    def get_segmentations(self):
        """

        Returns: a list or dict of objects representing all segmentation names up the segmentation planes (like in nwb)
        Object could be strings, or a list of strings, that identify a segmentation and give information
        how to get there.

        """
        pass

    @abstractmethod
    def get_roi_response_series(self):
        """

        Returns: a list or dict of objects representing all roi response series (rrs) names
        rrs could represents raw traces, or binary raster, and its link to a given segmentation.
        The results returned should allow to identify the segmentation associated.
        Object could be strings, or a list of strings, that identify a rrs and give information
        how to get there.

        """
        pass

    @abstractmethod
    def get_pixel_mask(self, segmentation_info):
        """
        Return pixel_mask which is a list of list of pair of integers representing the pixels coordinate (x, y) for each
        cell. the list length is the same as the number of cells.
        Args:
            segmentation_info: object (could be list, dict etc...) given information about how to reach the pixel_mask
            data

        Returns:

        """
        pass

    @abstractmethod
    def contains_ci_movie(self, consider_only_2_photons):
        """
        Indicate if the data object contains at least one calcium imaging movie
        Args:
            consider_only_2_photons: boolean, it True means we consider only 2 photons calcium imaging movies,
            if other exists but not 2 photons, then False will be return
        Returns: True if it's the case, False otherwise

        """
        pass

    @abstractmethod
    def get_ci_movies(self, only_2_photons):
        """
        Return a dict with as key a string identifying the movie, and as value a dict of CI movies
        a string as file_name if external, or a 3d array
        Args:
            only_2_photons: return only the 2 photon movies

        Returns:

        """
        pass

    @abstractmethod
    def get_identifier(self, session_data):
        """
        Get the identifier of one of the data to analyse
        Args:
            session_data: Data we want to know the identifier

        Returns: A hashable object identfying the data

        """
        pass

    @abstractmethod
    def get_intervals_names(self):
        """
        Return a list representing the intervals contains in this data
        Returns:

        """
        pass
