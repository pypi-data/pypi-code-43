import numpy as np
import os
from .observatory import ObservatoryGroup

GO_VERSION = '.V29'
VO_VERSION = '.0112'


class ObsData:
    """
    Class handling the list of ObservatoryGroups and interfaces it with the webpage.
    """
    def __init__(self):
        """
        Creates the obsGroups dict and loads the data from the current directory.
        """
        self.obsGroups = {}
        self.loadFromDirectory(os.path.dirname(__file__))

    def getDataInfo(self):
        """
        Returns a JSON with group names as keys.

        The Values of the JSON are also dictionaries with the following keys,values :

         - 'coordinates': coordinates of the observatories of the group
         - 'search_radius': search radius of the group
         - 'display_r': display radius of the group

        """
        jsondata = {}
        for obsGroupName in self.obsGroups:
            jsondata[obsGroupName] = {
                "coordinates": self.obsGroups[obsGroupName].coordinates,
                "search_radius": self.obsGroups[obsGroupName].search_radius,
                "display_r": self.obsGroups[obsGroupName].display_r
            }
        return jsondata

    def addObsGroup(self, groupName, display_r, search_radius=None):
        """
        Creates a new ObservatoryGroup.

        :param groupName: name of the group to create. Raises an Error if it already exists.
        :type groupName: str
        :param display_r: radius where the group data should be displayed
        :type display_r: float or None
        :param search_radius: ?
        :type search_radius:
        """
        if groupName in self.obsGroups:
            raise ValueError("An observatories group named %s already exists." % groupName)
        self.obsGroups[groupName] = ObservatoryGroup(groupName, display_r, search_radius)

    def getObsR(self, th, ph, groupName):
        """
        :param th: colatitude at which the r should be fetched.
        :type th: float
        :param ph: azimuth at which the r should be fetched.
        :type ph: float
        :param groupName: name of the group in which the data should be fetched.
        :type groupName:
        :return: radius of the group
        :rtype: float
        """
        return self.obsGroups[groupName].getObsR(th, ph)

    def getData(self, measureName, th, ph, groupName):
        """
        Gets the observed data for the given parameters.

        :param measureName: name of the measure to fetch
        :type measureName: str
        :param th: colatitude at which the data should be fetched.
        :type th: float
        :param ph: azimuth at which the data should be fetched.
        :type ph: float
        :param groupName: name of the group for which the data should be fetched
        :type groupName: str
        :return: Temporal array of the observed data at th,ph.
        :rtype: np.array
        """
        return self.obsGroups[groupName].getObservatoryData(th, ph, measureName)

    def loadFromDirectory(self, dataDirectory):
        """
        Reads VO files into CHAMP, SWARM and GO files in Magnetic ObservatoryGroups.

        :param dataDirectory: directory where the files are located
        :type dataDirectory: str
        """
        # Read CHAMP & SWARM
        for obsGroupName in ["CHAMP", "SWARM"]:
            self.addObsGroup(obsGroupName, display_r=None, search_radius=850)
            for measureName in ["MF", "SV"]:
                print("Reading %s %s data" % (obsGroupName, measureName))
                cols_to_read = range(9) if measureName == 'MF' else range(7)
                # Read data
                data = np.loadtxt(os.path.join(dataDirectory, "VO_" + obsGroupName + "_" + measureName + VO_VERSION),
                                  comments="%", usecols=cols_to_read)
                # remove nan
                data[np.where(data == 99999.)] = np.nan
                nObs = data.shape[0]

                for iObs in range(nObs):
                    if measureName == "MF":
                        theta, phi, year, month, time_, r, data_r, data_th, data_ph = data[iObs]
                        time = year + month / 12
                    else:
                        theta, phi, time, r, data_r, data_th, data_ph = data[iObs]

                    if np.isnan(data_r) or np.isnan(data_th) or np.isnan(data_ph) or np.isnan(time):
                        continue
                    phi = (phi + 360) % 360

                    if self.obsGroups[obsGroupName].display_r is None:
                        self.obsGroups[obsGroupName].display_r = r

                    self.obsGroups[obsGroupName].addObservatory(obsGroupName, r, theta, phi)  # Add if not exists
                    self.obsGroups[obsGroupName].addObservatoryData(theta, phi, measureName, time, data_r, data_th,
                                                                    data_ph)

        # Read magnetic observatories
        obsGroupName = "Magnetic observatories"
        self.addObsGroup(obsGroupName, display_r=6371.2, search_radius=None)
        for measureName in ["MF", "SV"]:
            print("Reading %s %s data" % (obsGroupName, measureName))
            # Read data
            if measureName == "MF":
                data = np.loadtxt(os.path.join(dataDirectory, "GR_OBS_RMM_" + measureName + "_less_bias" + GO_VERSION),
                                  comments="%", usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8))
                obsnames = np.loadtxt(os.path.join(dataDirectory, "GR_OBS_RMM_" + measureName + "_less_bias" + GO_VERSION),
                                      dtype='str', comments="%", usecols=(9))
            else:
                data = np.loadtxt(os.path.join(dataDirectory, "GR_OBS_RMM_" + measureName + GO_VERSION), comments="%",
                                  usecols=(0, 1, 2, 3, 4, 5, 6))
                obsnames = np.loadtxt(os.path.join(dataDirectory, "GR_OBS_RMM_" + measureName + GO_VERSION), dtype='str',
                                      comments="%", usecols=(7))
            # remove nan
            data[np.where(data == 99999.)] = np.nan
            nObs = data.shape[0]

            for iObs in range(nObs):
                if measureName == "MF":
                    theta, phi, year, month, time_, r, data_r, data_th, data_ph = data[iObs]
                    time = year + month / 12
                else:
                    theta, phi, time, r, data_r, data_th, data_ph, = data[iObs]

                obsname = obsnames[iObs]

                if np.isnan(data_r) or np.isnan(data_th) or np.isnan(data_ph) or np.isnan(time):
                    continue

                phi = (phi + 360) % 360

                self.obsGroups[obsGroupName].addObservatory(obsname, r, theta, phi)  # Add if not exists
                self.obsGroups[obsGroupName].addObservatoryData(theta, phi, measureName, time, data_r, data_th, data_ph)
