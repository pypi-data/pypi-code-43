from cicada.analysis.cicada_analysis import CicadaAnalysis
from time import sleep, time
import numpy as np


class CicadaDeepCinacPredictionAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        """
        CicadaAnalysis.__init__(self, name="DeepCINAC prediction", family_id="Infering neural activity",
                                short_description="Predict neural activity using DeepCINAC")

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        super().check_data()

        if self._data_format != "nwb":
            self.invalid_data_help = "Non NWB format compatibility not yet implemented"
            return False

        try:
            from deepcinac.cinac_predictor import CinacPredictor, CinacRecording, CinacDataMovie, CinacTiffMovie
        except ImportError:
            self.invalid_data_help = "deepcinac package not installed"
            return False

        for data in self._data_to_analyse:
            segmentations = data.get_segmentations()

            # we need at least one segmentation by session
            if segmentations is None or len(segmentations) == 0:
                self.invalid_data_help = "No segmentation data available"
                return False

        for data in self._data_to_analyse:
            ci_movies_dict = data.get_ci_movies(only_2_photons=False)
            # we need a movie, and it should be a tiff if external
            if len(ci_movies_dict) == 0:
                self.invalid_data_help = "No calcium imaging movie available"
                return False

            for movie_data in ci_movies_dict.values():
                if isinstance(movie_data, str):
                    # means an external file
                    if (not movie_data.endswith("tif")) and (not movie_data.endswith("tiff")):
                        self.invalid_data_help = "Calcium imaging movie in a format other than tiff not supported yet"
                        return False

        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        # range_arg = {"arg_name": "psth_range", "value_type": "int", "min_value": 50, "max_value": 2000,
        #              "default_value": 500, "description": "Range of the PSTH (ms)"}
        # self.add_argument_for_gui(**range_arg)
        #
        network_name_arg = {"arg_name": "network_name", "value_type": "str",
                            "default_value": "default", "short_description": "Name of network used for prediction",
                            "family_widget": "network data"}
        self.add_argument_for_gui(**network_name_arg)

        key_names = [data.identifier for data in self._data_to_analyse]

        json_file_arg = {"arg_name": "json_file", "value_type": "file",
                         "extensions": "json",
                         "short_description": "Json file containing the model", "mandatory": True,
                         "family_widget": "network data"}

        if len(key_names) > 1:
            json_file_arg.update({"key_names": key_names})

        self.add_argument_for_gui(**json_file_arg)

        weights_file_arg = {"arg_name": "weights_file", "value_type": "file",
                            "extensions": "h5",
                            "short_description": "h5 file containing the weights", "mandatory": True,
                            "family_widget": "network data"}

        if len(key_names) > 1:
            weights_file_arg.update({"key_names": key_names})

        self.add_argument_for_gui(**weights_file_arg)

        # results_path_arg = {"arg_name": "results_path", "value_type": "dir",
        #                     "default_value": default_results_path, "short_description": "Directory to save the results",
        #                     "with_incremental_order": False, "order_index": 1000, "mandatory": mandatory}
        # self.add_argument_for_gui(**results_path_arg)

        #
        # plot_arg = {"arg_name": "plot_options", "choices": ["lines", "bars"],
        #             "default_value": "bars", "short_description": "Options to display the PSTH"}
        # self.add_argument_for_gui(**plot_arg)
        #
        # avg_arg = {"arg_name": "average_fig", "value_type": "bool",
        #            "default_value": True, "short_description": "Add a figure that average all sessions"}
        #
        # self.add_argument_for_gui(**avg_arg)
        #
        # format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
        #             "default_value": "pdf", "short_description": "Formats in which to save the figures",
        #             "multiple_choices": True}
        #
        # self.add_argument_for_gui(**format_arg)

        self.add_ci_movie_arg_for_gui()

        self.add_segmentation_arg_for_gui()

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        test
        :param kwargs:
        :return:
        """
        CicadaAnalysis.run_analysis(self, **kwargs)

        if self._data_format != "nwb":
            print(f"Format others than nwb not supported yet")
            return

        self.run_nwb_format_analysis(**kwargs)

    def run_nwb_format_analysis(self, **kwargs):
        from deepcinac.cinac_predictor import CinacPredictor, CinacRecording, CinacDataMovie, CinacTiffMovie
        start_time = time()
        n_sessions = len(self._data_to_analyse)

        segmentation_dict = kwargs['segmentation']

        arg_ci_movies_dict = kwargs["ci_movie"]

        # TODO: be able to choose different network and weights for each session and cells
        # changing them as dict if the value is a string
        json_file_name = kwargs['json_file']
        if isinstance(json_file_name, str):
            json_file_name_dict = {}
            for session_data in self._data_to_analyse:
                json_file_name_dict[session_data.identifier] = json_file_name
            json_file_name = json_file_name_dict

        weights_file_name = kwargs['weights_file']
        if isinstance(json_file_name, str):
            weights_file_name_dict = {}
            for session_data in self._data_to_analyse:
                json_file_name_dict[session_data.identifier] = weights_file_name
            weights_file_name = weights_file_name_dict
        network_name = kwargs['network_name']

        for session_index, session_data in enumerate(self._data_to_analyse):
            session_identifier = self.session_data.identifier
            # TODO: load 'ophys' module and plane_segmentation based on data selected in arguments gui.
            mod = session_data.modules['ophys']
            if isinstance(segmentation_dict, str):
                name_mode = segmentation_dict
            else:
                name_mode = segmentation_dict[session_identifier]
            plane_seg = mod[name_mode].get_plane_segmentation('my_plane_seg')

            if 'pixel_mask' not in plane_seg:
                print(f"pixel_mask not available in for {session_data.identifier} "
                      f"in {name_mode}")
                self.update_progressbar(start_time, 100 / n_sessions)
                continue

            cinac_predictor = CinacPredictor()

            cinac_recording = CinacRecording(identifier=session_identifier)

            # setting the movie
            session_ci_movie_dict = session_data.get_ci_movies(only_2_photons=False)
            if isinstance(arg_ci_movies_dict, str):
                arg_movie_name = arg_ci_movies_dict
            else:
                arg_movie_name = arg_ci_movies_dict[session_identifier]
            session_ci_movie_data = session_ci_movie_dict[arg_movie_name]
            if isinstance(session_ci_movie_data, str):
                cinac_movie = CinacTiffMovie(tiff_file_name=session_ci_movie_data)
            else:
                cinac_movie = CinacDataMovie(movie=session_ci_movie_data)

            cinac_recording.set_movie(cinac_movie)

            # adding the ROIs
            cinac_recording.set_rois_from_nwb(nwb_data=session_data, name_module="ophys",
                                              name_segmentation=name_mode, name_seg_plane="my_plane_seg")
            model_files_dict = dict()
            # predicting 2 first cells with this model,  weights and string identifying the network
            model_files_dict[(json_file_name[session_identifier], weights_file_name[session_identifier],
                              network_name)] = np.arange(2)
            cinac_predictor.add_recording(cinac_recording=cinac_recording,
                                          removed_cells_mapping=None,
                                          model_files_dict=model_files_dict)

            cinac_predictor.predict(results_path=self.get_results_path())

            self.update_progressbar(start_time, 100 / n_sessions)
