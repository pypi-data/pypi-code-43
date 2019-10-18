from cicada.analysis.cicada_analysis import CicadaAnalysis
from time import time


class CicadaAssembliesPromaxCsAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        """
        CicadaAnalysis.__init__(self, name="Promax Circular Shift", family_id="Assemblies detection",
                                short_description="Romano et al. 2015 Neuron")

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        super().check_data()

        self.invalid_data_help = "Not implemented yet"
        return False

        if self._data_format != "nwb":
            self.invalid_data_help = "Non NWB format compatibility not yet implemented"
            return False

        # check is raw traces available

        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

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

        start_time = time()
        print("Promax CS assemblies detection: coming soon...")
        n_sessions = len(self._data_to_analyse)
        self.update_progressbar(start_time, 100 / n_sessions)
