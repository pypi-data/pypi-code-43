from .model import Model
from itertools import cycle


class Models(dict):
    """
    Dictionnary containing the loaded models
    """
    def __init__(self):
        super().__init__()
        # ui_colors are taken so that consecutive colors are visually very different (10-class Paired on http://colorbrewer2.org)
        self.ui_colors = cycle(['#1f78b4', '#33a02c', '#e31a1c', '#ff7f00', '#6a3d9a', '#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f', '#cab2d6'])
        self.model_colors = {"archeomag": "#ffaaaa",
                             "ced": "#ff0000",
                             "chaos": "#4daf4a",
                             "covobs": "#984ea3",
                             "enscore": "#af694a",
                             "pygeodyn_asc": "#ff00ff",
                             "pygeodyn_hdf5": "#ff00ff",
                             "midpath": "#00ff00",
                             "nath": "#0000ff",
                             "s1fs": "#aaaaaa",
                             "s1fs2": "#aaaaaa",
                             "zforecast": "#e41a1c"}

    def addModel(self, modelName, model, color=None):
        """
        Add a model to the list of loaded model.

        :param modelName: name of the model
        :type modelName: str
        :param model: Model to add
        :type model: Model
        :param color: color to use for plots of the model (default: None, in this case, uses a dedicated color for eahc model)
        :type color: str (hexadecimal form)
        """
        if color is None:
            try:
                color = self.model_colors[model.dataFormat]
            except KeyError:
                # Use ui_colors if this fails
                color = 'ui'

        if color == 'ui':
            color = next(self.ui_colors)

        model.color = color
        self[modelName] = model

    def loadModel(self, dataDirectory, modelName, dataFormat='default', color=None, keepRealisations=True):
        """
        Creates a Model by loading the files in dataDirectory using the dataFormat and the calls addModel. Note that it sets first the allocated space in the dict to False in case of asynchronous thread checking the loading state.

        :param dataDirectory: Directory where the model files are located
        :type dataDirectory: str (path)
        :param modelName: name of the model to use
        :type modelName: str
        :param dataFormat: format to use to load the model data
        :type dataFormat: str
        :param color: color of the model to use for plots
        :type color: str
        :param keepRealisations: indicates with realisations should be kept or averaged
        :type keepRealisations: bool
        """
        self[modelName] = False
        self.addModel(modelName, Model(dataDirectory, dataFormat, keepRealisations=keepRealisations), color)

    def isModelLoading(self, modelName):
        """
        Checks if the model is present in Models and if it is being loaded.

        :param modelName: name of the model to check
        :type modelName: str
        :return: the state of loading of the model (True means loading)
        :rtype: bool
        """
        return (modelName in self) and (self[modelName] is False)

    def getModelList(self):
        """
        Gets the list of model names.

        :return: list of model names
        :rtype: list
        """
        return list(self.keys())

    def isCached(self, modelName):
        """
        Checks if a model is present and loaded.

        :param modelName: name of the model to check
        :type modelName: str
        :return: the presence of the model in Models (True means present and loaded)
        :rtype: bool
        """
        if modelName not in self:
            return False
        if self[modelName] is False:
            return False
        return True
