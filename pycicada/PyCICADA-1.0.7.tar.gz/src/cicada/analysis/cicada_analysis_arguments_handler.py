from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
# to import the Widgets for the GUI
from cicada.gui.cicada_analysis_parameters_gui import *
from cicada.utils.constants import CICADA_VERSION
import yaml


class AnalysisArgument:

    def __init__(self, **kwargs):
        """
        Arguments passed to the function can't be named '_widget' or '_final_value'
        Args:
            **kwargs:
                - arg_name
                - order_index
                - default_value
                - range_values
                - max_value
                - min_value
                - value_type
                - mandatory
                - description
                - ...
        """
        for attribute_name, value in kwargs.items():
            setattr(self, attribute_name, value)

        self._widget = None

        self._final_value = None

    def get_gui_widget(self):
        """

        Returns:

        """

        # make it crash
        # if self.widget:
        #     return self.widget
        """
                create_widgets
                self.layout.addWidget(gui_widget)
                RuntimeError: wrapped C/C++ object of type SliderWidget has been deleted

        """

        if getattr(self, "value_type", None) == "int":
            if hasattr(self, "min_value") and hasattr(self, "max_value"):
                self._widget = SliderWidget(analysis_arg=self)
                return self._widget
        elif getattr(self, "value_type", None) == "bool":
            self._widget = CheckBoxWidget(analysis_arg=self)
            return self._widget
        elif getattr(self, "value_type", None) == "dir":
            self._widget = FileDialogWidget(analysis_arg=self, directory_only=True)
            return self._widget
        elif getattr(self, "value_type", None) == "file":
            extensions = getattr(self, "extensions", None)
            self._widget = FileDialogWidget(analysis_arg=self, directory_only=False, extensions=extensions)
            return self._widget
        elif getattr(self, "value_type", None) == "color":
            self._widget = ColorDialogWidget(analysis_arg=self, show_alpha_channel=False)
            return self._widget
        elif getattr(self, "value_type", None) == "color_with_alpha":
            self._widget = ColorDialogWidget(analysis_arg=self, show_alpha_channel=True)
            return self._widget
        elif hasattr(self, "choices"):
            if getattr(self, "multiple_choices", False):
                self._widget = ListCheckboxWidget(analysis_arg=self, choices_attr_name="choices")
            else:
                self._widget = ComboBoxWidget(analysis_arg=self)
            return self._widget
        else:
            self._widget = LineEditWidget(analysis_arg=self)
            return self._widget

    def set_argument_value(self, value):
        self._final_value = value

    def set_argument_value_from_widget(self):
        """
        Look in the widget to get the final_value of this argument
        Returns:

        """
        self._final_value = self.get_argument_value()

    def get_family_widget(self):
        """
        Return a string reprenting the family widget to which this argument belongs, or None if it doesn't belong to any
        :return:
        """

        return getattr(self, "family_widget", None)

    def get_all_attributes(self):
        """
        Return a dict containing all attributes of this argument except for the widget one
        Returns:

        """
        # first we upddate _final_value
        self.set_argument_value_from_widget()
        attr_dict = dict()
        for attr_name in self.__dict__.keys():
            if attr_name.startswith("_") and attr_name != "_final_value":
                continue
            attr_dict[attr_name] = getattr(self, attr_name, None)

        return attr_dict

    def set_widget_to_default_value(self):
        """
        Set the widget to the default value of this analysis argument
        Returns:

        """
        self._widget.set_value(value=self.get_default_value())

    def set_widget_value_from_saved_data(self, args_content):
        """

        Args:
            args_content: dict with key the attribute name and value the content

        Returns:

        """
        # if there is no "final_value", then something wrong
        if "_final_value" not in args_content:
            print(f"No final_value found while using set_widget_value_from_saved_data for analysis_argument "
                  f"{self.arg_name}")
            return

        # first we check if each attribute corresponds the actual one in terms of value
        # for attr_name, attr_value in args_content.items():
        #     if attr_name == "_final_value":
        #         continue

        # _final_value will be set later when the analysis is launched
        # not need to checked if the value is correct, like if the value from a list should be selected
        # and this value doesn't exist, then the widget should handle it by its own
        self._widget.set_value(args_content["_final_value"])

    def is_mandatory(self):
        """

        Returns: boolean, True means the argument is mandatory, so need to have a value

        """
        if hasattr(self, "mandatory"):
            return getattr(self, "mandatory")

        # else if there is a default_value, it means it's not mandatory
        return not hasattr(self, "default_value")

    def __eq__(self, other):
        """
        self == other
        Args:
            other:

        Returns:

        """
        return ((self.is_mandatory(), getattr(self, "order_index", None)) ==
                (other.is_mandatory(), getattr(other, "order_index", None)))

    def __ne__(self, other):
        """
        self != other
        Args:
            other:

        Returns:

        """
        return ((self.is_mandatory(), getattr(self, "order_index", None)) !=
                (other.is_mandatory(), getattr(other, "order_index", None)))

    def __lt__(self, other):
        """
        self < other
        Args:
            other:

        Returns:

        """
        if self.is_mandatory() and (not other.is_mandatory()):
            return True
        if (not self.is_mandatory()) and other.is_mandatory():
            return False

        self_order_index = getattr(self, "order_index", None)
        other_order_index = getattr(other, "order_index", None)
        if (other_order_index is not None) and (self_order_index is None):
            return False
        if (other_order_index is None) and (self_order_index is not None):
            return True
        if (other_order_index is None) and (self_order_index is None):
            # then there equals
            return False

        return self_order_index < other_order_index

    def __le__(self, other):
        """
        self <= other
        Args:
            other:

        Returns:

        """
        if self.is_mandatory() and (not other.is_mandatory()):
            return True
        if (not self.is_mandatory()) and other.is_mandatory():
            return False

        self_order_index = getattr(self, "order_index", None)
        other_order_index = getattr(other, "order_index", None)

        if (other_order_index is not None) and (self_order_index is None):
            return False
        if (other_order_index is None) and (self_order_index is not None):
            return True
        if (other_order_index is None) and (self_order_index is None):
            # then there equals
            return True

        return self_order_index <= other_order_index

    def __gt__(self, other):
        """
        self > other
        Args:
            other:

        Returns:

        """
        if self.is_mandatory() and (not other.is_mandatory()):
            return False
        if (not self.is_mandatory()) and other.is_mandatory():
            return True

        self_order_index = getattr(self, "order_index", None)
        other_order_index = getattr(other, "order_index", None)
        if (other_order_index is not None) and (self_order_index is None):
            return True
        if (other_order_index is None) and (self_order_index is not None):
            return False
        if (other_order_index is None) and (self_order_index is None):
            # then there equals
            return False

        return self_order_index > other_order_index

    def __ge__(self, other):
        """
        self >= other
        Args:
            other:

        Returns:

        """
        if self.is_mandatory() and (not other.is_mandatory()):
            return False
        if (not self.is_mandatory()) and other.is_mandatory():
            return True

        self_order_index = getattr(self, "order_index", None)
        other_order_index = getattr(other, "order_index", None)
        if (other_order_index is not None) and (self_order_index is None):
            return True
        if (other_order_index is None) and (self_order_index is not None):
            return False
        if (other_order_index is None) and (self_order_index is None):
            # then there equals
            return True

        return self_order_index >= other_order_index

    def get_default_value(self):
        return getattr(self, "default_value", None)

    def get_short_description(self):
        return getattr(self, "short_description", None)

    def get_long_description(self):
        return getattr(self, "long_description", None)

    def get_argument_value(self):
        if self._widget is None:
            return None
        return self._widget.get_value()


class AnalysisArgumentsHandler:
    """
    Handle the AnalysisArgument instances for a given CicadaAnalysis instance.
    Allows to create the widgets and get the values to pass to run_analysis() of the CicadaAnalysis instance.
    """

    def __init__(self, cicada_analysis):
        self.args_dict = dict()
        self.cicada_analysis = cicada_analysis

    def add_argument(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        arg_analysis = AnalysisArgument(**kwargs)
        self.args_dict[arg_analysis.arg_name] = arg_analysis

    def save_analysis_arguments_to_yaml_file(self, path_dir, yaml_file_name):
        """
        Save the arguments value to a yaml file.
        The first key will represent the argument name
        then the value will be a dict with the argument details such as the type etc...
        Args:
            path_dir: directory in which save the yaml file
            yaml_file_name: yaml file name, with the extension or without (will be added in that case)

        Returns:

        """
        analysis_args_for_yaml = dict()

        # first we add the subjects id
        session_identifiers = [session.identifier for session in self.cicada_analysis.get_data_to_analyse()]
        analysis_args_for_yaml["session_identifiers"] = session_identifiers

        # then we add the version of CICADA used
        analysis_args_for_yaml["CICADA_VERSION"] = CICADA_VERSION

        for arg_name, analysis_arg in self.args_dict.items():
            analysis_args_for_yaml[arg_name] = analysis_arg.get_all_attributes()

        if (not yaml_file_name.endswith(".yaml")) and (not yaml_file_name.endswith(".yml")):
            yaml_file_name = yaml_file_name + ".yaml"

        if not os.path.isdir(path_dir):
            os.mkdir(path_dir)

        with open(os.path.join(path_dir, yaml_file_name), 'w') as outfile:
            yaml.dump(analysis_args_for_yaml, outfile, default_flow_style=False)

    def load_analysis_argument_from_yaml_file(self, file_name):
        """
        Set the analysis argument value based on the value in the yaml file.
        The
        Args:
            file_name:

        Returns:

        """

        with open(file_name, 'r') as stream:
            analysis_args_from_yaml = yaml.load(stream, Loader=yaml.FullLoader)

        # sys.stderr.write(f"{analysis_args_from_yaml}")
        for arg_name, args_content in analysis_args_from_yaml.items():
            # now we check if an arg with this name exists
            # we also check that the attributes other than final_value match the one we want to load
            # otherwise it means the analysis function change since the time the file was saved and it's not safe
            # to us this value.
            # if everything is good, then we change the value in the widget accordingly
            if arg_name in self.args_dict:
                self.args_dict[arg_name].set_widget_value_from_saved_data(args_content)

    def get_analysis_argument(self, arg_name):
        """

        Args:
            arg_name:

        Returns:

        """
        self.args_dict.get(arg_name)

    def get_analysis_arguments(self, sorted=False):
        """

        Args:
            sorted:

        Returns:

        """
        analysis_arguments = list(self.args_dict.values())
        if sorted:
            analysis_arguments.sort()
        return analysis_arguments

    def set_widgets_to_default_value(self):
        """
        Set the widgets to the default value of their AnalysisArgument
        Returns:

        """
        for analysis_argument in self.args_dict.values():
            analysis_argument.set_widget_to_default_value()

    def set_argument_value(self, arg_name, **kwargs):
        """
        Set an argument values, will be use to run analysis
        Args:
            arg_name:
            **kwargs:

        Returns:

        """
        pass

    def get_gui_widgets(self, group_by_family=False):
        """
        Get the list of widgets necessary to fill the arguments for the cicada analysis associated
        Args:
            group_by_family: if True, group the widgets in one widget to be grouped together if they belong to the same
            family. AnalysisArgument will have an attribute named family_widget whose value is a string.
        Returns:

        """
        gui_widgets = []
        analysis_arguments = self.get_analysis_arguments(sorted=True)
        if not group_by_family:
            for analysis_argument in analysis_arguments:
                widget = analysis_argument.get_gui_widget()
                if widget:
                    gui_widgets.append(widget)
            return gui_widgets

        # first we get all the families present
        family_widgets_dict = dict()
        # we're keeping just the first arg of each family and other args not in family, just to keep the order of the
        # args
        analysis_arguments_filtered = []
        for analysis_argument in analysis_arguments:
            family_widget = analysis_argument.get_family_widget()
            if family_widget is not None:
                if family_widget in family_widgets_dict:
                    family_widgets_dict[family_widget].append(analysis_argument)
                else:
                    family_widgets_dict[family_widget] = [analysis_argument]
                    analysis_arguments_filtered.append(analysis_argument)
            else:
                analysis_arguments_filtered.append(analysis_argument)

        for analysis_argument in analysis_arguments_filtered:
            family_widget = analysis_argument.get_family_widget()
            if family_widget is not None:
                family_gui_widgets = []
                for a_a_in_family in family_widgets_dict[family_widget]:
                    widget = a_a_in_family.get_gui_widget()
                    if widget:
                        family_gui_widgets.append(widget)
                # building the widget that will contain those of the same family
                gui_widgets.append(SameFamilyWidgetsContainer(widgets=family_gui_widgets))
            else:
                widget = analysis_argument.get_gui_widget()
                if widget:
                    gui_widgets.append(widget)
        return gui_widgets

    def check_arguments_validity(self):
        """
        Check if all mandatory arguments have been filled
        Returns: True if we can run the analysis
        """
        for arg_name, analysis_argument in self.args_dict.items():
            value = analysis_argument.get_argument_value()
            if analysis_argument.is_mandatory() and (value is None):
                return False
        return True

    def run_analysis(self):
        kwargs = {}
        for arg_name, analysis_argument in self.args_dict.items():
            kwargs[arg_name] = analysis_argument.get_argument_value()
        self.cicada_analysis.run_analysis(**kwargs)