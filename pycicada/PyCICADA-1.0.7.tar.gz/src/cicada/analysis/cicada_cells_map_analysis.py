from cicada.analysis.cicada_analysis import CicadaAnalysis
from cicada.utils.display.cells_map_utils import CellsCoord
import sys
from time import sleep, time
import numpy as np
import matplotlib.cm as cm
from cicada.utils.display.colors import BREWER_COLORS
import matplotlib.colors as plt_colors
from cicada.utils.cell_assemblies.malvache.utils import load_cell_assemblies_data
from cicada.utils.display.videos import load_tiff_movie


class CicadaCellsMapAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        """
        CicadaAnalysis.__init__(self, name="Cells map", family_id="Display",
                                short_description="Plot map of the cells")

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

        for data in self._data_to_analyse:

            segmentations = data.get_segmentations()

            # we need at least one segmentation
            if (segmentations is None) or len(segmentations) == 0:
                self.invalid_data_help = "No segmentation data available"
                return False

        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        cell_numbers_arg = {"arg_name": "with_cell_numbers", "value_type": "bool",
                            "default_value": True, "short_description": "Display cell numbers"}

        self.add_argument_for_gui(**cell_numbers_arg)

        format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
                      "default_value": "pdf", "short_description": "Formats in which to save the figures",
                      "multiple_choices": True, "family_widget": "image_format"}

        self.add_argument_for_gui(**format_arg)

        dpi_arg = {"arg_name": "dpi", "value_type": "int", "min_value": 50, "max_value": 800,
                   "long_description": "Dots per inches (dpi) determines how many pixels the figure comprises",
                   "default_value": 200, "short_description": "Dpi (Dots per inches)",
                   "family_widget": "image_format"}

        self.add_argument_for_gui(**dpi_arg)

        pixels_mask_polygon_arg = {"arg_name": "polygon_or_pixel_mask", "choices": ["polygons", "pixel masks"],
                                   "default_value": "polygons", "short_description": "Technique use to draw the cells",
                                   "long_description": "if both are selected, then 2 figures will be produce",
                                   "multiple_choices": True}

        self.add_argument_for_gui(**pixels_mask_polygon_arg)

        cells_color_arg = {"arg_name": "cells_color", "value_type": "color_with_alpha",
                           "default_value": (1, 1, 1, 1.), "short_description": "Cells' color",
                           "family_widget": "colors"}
        self.add_argument_for_gui(**cells_color_arg)

        fill_cells_arg = {"arg_name": "dont_fill_cells_not_in_groups", "value_type": "bool",
                          "default_value": False, "short_description": "Display only edges for cells not in a group",
                          "family_widget": "colors"}

        self.add_argument_for_gui(**fill_cells_arg)

        edge_color_arg = {"arg_name": "edge_color", "value_type": "color_with_alpha",
                          "default_value": (1, 1, 1, 1.), "short_description": "Cells' edge color",
                          "family_widget": "colors"}
        self.add_argument_for_gui(**edge_color_arg)

        # dimgray is the default color
        cell_numbers_color_arg = {"arg_name": "cell_numbers_color", "value_type": "color",
                                  "default_value": (0.412, 0.412, 0.412, 1.),
                                  "short_description": "Cells' number color",
                                  "family_widget": "colors"}
        self.add_argument_for_gui(**cell_numbers_color_arg)

        bg_color_arg = {"arg_name": "background_color", "value_type": "color_with_alpha",
                        "default_value": (0, 0, 0, 1.), "short_description": "Background color",
                        "long_description": "If calcium imaging movie background selected, the background won't matter",
                        "family_widget": "colors"}
        self.add_argument_for_gui(**bg_color_arg)

        img_on_background_arg = {"arg_name": "display_img_on_background", "value_type": "bool",
                                 "default_value": False, "short_description": "Use average movie image as background",
                                 "family_widget": "colors"}

        self.add_argument_for_gui(**img_on_background_arg)

        real_size_image_on_bg_arg = {"arg_name": "real_size_image_on_bg", "value_type": "bool",
                                     "default_value": True, "short_description": "Scale the figure to the background "
                                                                                 "image resolution",
                                     "family_widget": "colors"}

        self.add_argument_for_gui(**real_size_image_on_bg_arg)

        welsh_arg = {"arg_name": "use_welsh_powell_coloring", "value_type": "bool",
                     "default_value": True, "short_description": "Use welsh powell algorithm to color cells",
                     "long_description": "If chosen, then groups of cells will be decide by the algorithm. "
                                         "As well as colors, "
                                         "except for isolated cell, whose color will be the cells' color choosen.",
                     "family_widget": "colors"}

        self.add_argument_for_gui(**welsh_arg)

        key_names = [data.identifier for data in self._data_to_analyse]
        cell_ass_arg = {"arg_name": "cell_assemblies_file", "value_type": "file",
                        "extensions": "txt",
                        "mandatory": False,
                        "short_description": "Txt file with results from kmean cell assemblies analysis",
                        "family_widget": "cell assemblies"}
        if len(key_names) > 1:
            cell_ass_arg.update({"key_names": key_names})
        self.add_argument_for_gui(**cell_ass_arg)

        color_cell_ass_arg = {"arg_name": "color_cell_assemblies", "choices": ["cmap nipy_spectral", "brewer"],
                              "default_value": "pdf", "short_description": "Set of colors for cell assemblies",
                              "multiple_choices": False,
                              "family_widget": "cell assemblies"}

        self.add_argument_for_gui(**color_cell_ass_arg)

        show_polygons_arg = {"arg_name": "show_polygons", "value_type": "bool",
                             "default_value": False, "short_description": "Show a polygon that covers "
                                                                          "the cells of a same cell assembly",
                             "family_widget": "cell assemblies"}

        self.add_argument_for_gui(**show_polygons_arg)

        fill_polygons_arg = {"arg_name": "fill_polygons", "value_type": "bool",
                             "default_value": False, "short_description": "Fill the polygon that covers "
                                                                          "the cells of a same cell assembly",
                             "family_widget": "cell assemblies"}

        self.add_argument_for_gui(**fill_polygons_arg)

        invert_xy_coord_arg = {"arg_name": "invert_xy_coord", "value_type": "bool",
                               "default_value": True, "short_description": "Invert xy coords",
                               "long_description": "Could be useful if the coordinates are inverted"}

        self.add_argument_for_gui(**invert_xy_coord_arg)

        verbose_arg = {"arg_name": "verbose", "value_type": "bool",
                       "default_value": True, "short_description": "Verbose",
                       "long_description": "If selected, some information might be printed during the analysis."}

        self.add_argument_for_gui(**verbose_arg)

        self.add_segmentation_arg_for_gui()

        self.add_ci_movie_arg_for_gui(long_description="Only useful if the average calcium imaging is displayed "
                                                       "on the background")

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
          segmentation

        :return:
        """
        CicadaAnalysis.run_analysis(self, **kwargs)

        n_sessions = len(self._data_to_analyse)

        segmentation_dict = kwargs['segmentation']

        with_cell_numbers = kwargs["with_cell_numbers"]

        save_formats = kwargs["save_formats"]
        if save_formats is None:
            save_formats = "pdf"

        cells_color = kwargs.get("cells_color", None)

        dont_fill_cells_not_in_groups = kwargs.get("dont_fill_cells_not_in_groups", False)

        edge_color = kwargs.get("edge_color", None)

        background_color = kwargs.get("background_color", None)

        display_img_on_background = kwargs.get("display_img_on_background", None)

        real_size_image_on_bg = kwargs.get("real_size_image_on_bg", True)

        cell_numbers_color = kwargs.get("cell_numbers_color", None)

        use_welsh_powell_coloring = kwargs.get("use_welsh_powell_coloring", False)

        invert_xy_coord = kwargs.get("invert_xy_coord", True)

        verbose = kwargs.get("verbose", True)

        dpi = kwargs.get("dpi", 200)

        use_pixel_masks_values = []
        if "polygon_or_pixel_mask" in kwargs:
            option_args = kwargs['polygon_or_pixel_mask']
            if option_args is None:
                use_pixel_masks_values = []
            else:
                if isinstance(option_args, str):
                    option_args = [option_args]
                for option_arg in option_args:
                    if option_arg == "polygons":
                        use_pixel_masks_values.append(False)
                    else:  # "pixel masks"
                        use_pixel_masks_values.append(True)

        cell_assemblies_file = kwargs.get("cell_assemblies_file", None)
        if isinstance(cell_assemblies_file, str):
            if len(self._data_to_analyse) > 1:
                # not matching the len of the data to analyse
                cell_assemblies_file = None
            else:
                cell_assemblies_file = {self._data_to_analyse[0].identifier: cell_assemblies_file}
        # else it should be a dict if not None

        fill_polygons = kwargs.get("fill_polygons", False)

        show_polygons = kwargs.get("show_polygons", False)

        color_cell_assemblies = kwargs.get("color_cell_assemblies", None)
        if color_cell_assemblies is None:
            color_cell_assemblies = "cmap nipy_spectral"

        if display_img_on_background:
            arg_ci_movies_dict = kwargs["ci_movie"]

        for session_index, session_data in enumerate(self._data_to_analyse):
            session_identifier = session_data.identifier
            if verbose:
                print(f"-------------- {session_identifier} -------------- ")
            if isinstance(segmentation_dict, dict):
                segmentation_info = segmentation_dict[session_identifier]
            else:
                segmentation_info = segmentation_dict
            pixel_mask = session_data.get_pixel_mask(segmentation_info=segmentation_info)

            if pixel_mask is None:
                print(f"pixel_mask not available in for {session_data.identifier} "
                      f"in {segmentation_info}")
                self.update_progressbar(self.analysis_start_time, 100 / n_sessions)
                continue

            # pixel_mask of type pynwb.core.VectorIndex
            # each element of the list will be a sequences of tuples of 3 floats representing x, y and a float between
            # 0 and 1 (not used in this case)
            pixel_mask_list = [pixel_mask[cell] for cell in range(len(pixel_mask))]
            # TODO: get the real movie dimensions if available
            cells_coord = CellsCoord(pixel_masks=pixel_mask_list, from_matlab=False, invert_xy_coord=invert_xy_coord)
            if verbose:
                print(f"N cells: {cells_coord.n_cells}")
            args_to_add = dict()
            if cells_color is not None:
                args_to_add["default_cells_color"] = cells_color
            if background_color is not None:
                args_to_add["background_color"] = background_color

            if edge_color is not None:
                args_to_add["default_edge_color"] = edge_color

            if cell_numbers_color is not None:
                args_to_add["cell_numbers_color"] = cell_numbers_color

            cells_groups = None
            cells_groups_colors = None
            cell_assemblies_on = False
            if (cell_assemblies_file is not None) and (session_identifier in cell_assemblies_file) \
                    and (cell_assemblies_file[session_identifier] is not None):
                cell_assemblies_on = True
                assemblies_results = load_cell_assemblies_data(data_file_name=cell_assemblies_file[session_identifier])
                cell_assemblies = assemblies_results[0]
                n_assemblies = len(cell_assemblies)
                cells_groups_colors = []
                cells_groups = cell_assemblies
                for i in np.arange(n_assemblies):
                    if color_cell_assemblies == "cmap nipy_spectral":
                        color = cm.nipy_spectral(float(i + 1) / (n_assemblies + 1))
                    else:
                        # brewer
                        color_hex = BREWER_COLORS[i % len(BREWER_COLORS)]
                        # putting it with value from 0.0 to 1.0
                        color_rgb = plt_colors.hex2color(color_hex)
                        # adding the alpha
                        color_rgba = [c for c in color_rgb]
                        color_rgba.append(0.8)
                        color = color_rgba
                    cells_groups_colors.append(color)

            avg_cell_map_img = None
            if display_img_on_background:
                # setting the movie
                session_ci_movie_dict = session_data.get_ci_movies(only_2_photons=False)
                if isinstance(arg_ci_movies_dict, str):
                    arg_movie_name = arg_ci_movies_dict
                else:
                    arg_movie_name = arg_ci_movies_dict[session_identifier]
                session_ci_movie_data = session_ci_movie_dict[arg_movie_name]
                if isinstance(session_ci_movie_data, str):
                    tiff_movie = load_tiff_movie(tiff_file_name=session_ci_movie_data)
                else:
                    tiff_movie = session_ci_movie_data
                avg_cell_map_img = np.mean(tiff_movie, axis=0)

            for use_pixel_masks in use_pixel_masks_values:
                if use_pixel_masks:
                    title_option = "all_cells_pixel_masks"
                else:
                    title_option = "all_cells_polygons"
                cells_coord.plot_cells_map(path_results=self.get_results_path(),
                                           data_id=session_identifier, show_polygons=show_polygons,
                                           fill_polygons=fill_polygons,
                                           use_pixel_masks=use_pixel_masks,
                                           title_option=title_option, connections_dict=None,
                                           use_welsh_powell_coloring=(not cell_assemblies_on) and
                                                                     use_welsh_powell_coloring,
                                           verbose=verbose,
                                           cells_groups=cells_groups,
                                           cells_groups_colors=cells_groups_colors,
                                           img_on_background=avg_cell_map_img,
                                           real_size_image_on_bg=real_size_image_on_bg,
                                           cells_groups_edge_colors=None,
                                           with_edge=True, cells_groups_alpha=None,
                                           dont_fill_cells_not_in_groups=dont_fill_cells_not_in_groups,
                                           with_cell_numbers=with_cell_numbers, save_formats=save_formats,
                                           dpi=dpi,
                                           save_plot=True, return_fig=False, **args_to_add)

            if verbose:
                print(" ")
            self.update_progressbar(time_started=self.analysis_start_time, increment_value=100 / n_sessions)
        print(f"Cells map analysis run in {time() - self.analysis_start_time} sec")
