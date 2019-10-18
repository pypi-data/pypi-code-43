import yaml
import os
from random import randint


class ConfigHandler:
    """
    Class used for handling the configuration for the GUI.
    At term, it should also open a config GUI to set the parameters.
    All GUI parameters should be available there.
    """

    def __init__(self, path_to_config_file="../config/config.yaml"):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path_to_config_file = os.path.join(my_path, path_to_config_file)
        self._path_to_config_file = path_to_config_file

        with open(path_to_config_file, 'r') as stream:
            config_dict = yaml.load(stream, Loader=yaml.FullLoader)

        if config_dict is None:
            config_dict = dict()

        self._yaml_analysis_args_dir_name = config_dict.get('yaml_analysis_args_dir_name', None)

        # TODO: change dir_name by a more meaningful name
        self._files_to_analyse_dir_name = config_dict.get('dir_name', None)

        # Path of the directory where to save new results
        # usually a new directory specific to the analysis done will be created in this directory
        self._default_results_path = config_dict.get('default_results_path', None)

        self.main_window_bg_pictures_displayed_by_default = True

        self._widget_bg_pictures_folder = dict()
        self._widget_bg_pictures_folder["sessions"] = config_dict.get('sessions_widget_bg_pictures_folder', None)
        self._widget_bg_pictures_folder["tree"] = config_dict.get('tree_widget_bg_pictures_folder', None)
        self._widget_bg_pictures_folder["overview"] = config_dict.get('overview_widget_bg_pictures_folder', None)
        self._widget_bg_pictures_folder["analysis_data"] = config_dict.get('analysis_data_widget_bg_pictures_folder', None)
        self._widget_bg_pictures_folder["analysis_params"] = config_dict.get('analysis_params_widget_bg_pictures_folder', None)
        self._widget_bg_pictures_file_names = dict()
        for widget_id, folder_path in self._widget_bg_pictures_folder.items():
            if folder_path is None:
                continue
            # we list the pictures
            if os.path.isdir(folder_path):
                file_names = []
                for (dirpath, dirnames, local_filenames) in os.walk(folder_path):
                    file_names = local_filenames
                    break
                for file_name in file_names:
                    if (file_name.lower().endswith(".png") or file_name.lower().endswith(".jpg") or
                        file_name.lower().endswith(".jpeg")) and (not file_name.startswith(".")):
                        if widget_id not in self._widget_bg_pictures_file_names:
                            self._widget_bg_pictures_file_names[widget_id] = []
                        self._widget_bg_pictures_file_names[widget_id].append(os.path.join(
                            folder_path, file_name))

    def get_random_main_window_bg_picture(self, widget_id=None):
        """

        Args:
            widget_id: string identifying the widget for which the picture is meant
            could be: "sessions", "tree", "overview"

        Returns:

        """
        # not default background
        if widget_id is None:
            return None

        if widget_id not in self._widget_bg_pictures_file_names:
            return None
        file_names = self._widget_bg_pictures_file_names[widget_id]
        if len(file_names) == 0:
            return None
        pic_index = randint(0, len(file_names) - 1)
        return file_names[pic_index]

    @property
    def main_window_bg_pictures_folder(self):
        return self._main_window_bg_pictures_folder

    @main_window_bg_pictures_folder.setter
    def main_window_bg_pictures_folder(self, value):
        # TODO: update the pictures choice
        self._main_window_bg_pictures_folder = value

    @property
    def yaml_analysis_args_dir_name(self):
        return self._yaml_analysis_args_dir_name

    @property
    def files_to_analyse_dir_name(self):
        return self._files_to_analyse_dir_name

    @property
    def default_results_path(self):
        return self._default_results_path

    @default_results_path.setter
    def default_results_path(self, value):
        self._default_results_path = value
