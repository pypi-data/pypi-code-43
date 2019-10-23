class ObservatoryGroup:
    """ Class handling groups of observatories (Ground magnetic obs, CHAMP or SWARM) """
    def __init__(self, groupName, display_r, search_radius=None):
        """
        Creates the empty dict of Observatories and empty list of coordinates.

        :param groupName: Name of the group
        :type groupName: str
        :param display_r: radius at which the data should be displayed
        :type display_r: float
        :param search_radius: TODO
        :type search_radius:
        """
        self.groupName = groupName
        self.search_radius = search_radius
        self.display_r = display_r
        self.observatories = {}
        self.coordinates = []

    def addObservatory(self, obscode, r, th, ph):
        """
        Add an Observatory to the internal dict with th and ph as keys.

        :param obscode: code of the observatory
        :type obscode: str
        :param r: radius of the observatory
        :type r: float
        :param th: colatitude of the observatory
        :type th: float
        :param ph: azimuth of the observatory
        :type ph: float
        """
        th = str(th)
        ph = str(ph)
        if th not in self.observatories:
            self.observatories[th] = {}
        if ph in self.observatories[th]:
            return
        self.coordinates.append([th, ph])
        self.observatories[th][ph] = Observatory(obscode, r, th, ph)

    def addObservatoryData(self, th, ph, measureName, times, rdata, thdata, phdata):
        """
        Adds the data for th, ph.

        :param th: colatitude at which the data was taken
        :type th: float
        :param ph: azimuth at which the data was taken
        :type ph: float
        :param measureName: name of the measure to add
        :type measureName: str
        :param times: times array
        :type times: np.array
        :param rdata: radial data
        :type rdata: np.array
        :param thdata: colatitudinal data
        :type thdata: np.array
        :param phdata: azimuthal data
        :type phdata: np.array
        :return: 0 if everything went well, -1 otherwise
        :rtype: int
        """
        th = str(th)
        ph = str(ph)
        if th not in self.observatories:
            print("setObservatoryData failed, no observatory with th=%s" % th)
            return -1
        if ph not in self.observatories[th]:
            print("setObservatoryData failed, no observatory with ph=%s" % ph)
            return -1
        self.observatories[th][ph].addData(measureName, times, rdata, thdata, phdata)
        return 0

    def getObservatoryData(self, th, ph, measureName):
        """
        Gets the measure data at a given position.

        :param th: colatitude at which the data should be fetched
        :type th: float
        :param ph: azimuth at which the data should be fetched
        :type ph: float
        :param measureName: name of the measure to fetch
        :type measureName: str
        :return: dict with group name as key and data as value
        :rtype: dict
        """
        th = str(th)
        ph = str(ph)
        if th not in self.observatories:
            print("getObservatoryData failed, no observatory with th=%s" % th)
            return
        if ph not in self.observatories[th]:
            print("getObservatoryData failed, no observatory with ph=%s" % ph)
            return
        return {self.groupName: self.observatories[th][ph].getData(measureName)}

    def getObsR(self, th, ph):
        """
        Get the radius of observatory.

        :param th: colatitude at which the r should be fetched
        :type th: float
        :param ph: azimuth at which the r should be fetched
        :type ph: float
        :return: radius of observatory if th and ph exist as keys. None otherwise.
        :rtype: float or None
        """
        th = str(th)
        ph = str(ph)
        if th not in self.observatories:
            return None
        if ph not in self.observatories[th]:
            return None
        return self.observatories[th][ph].r


class Observatory:
    """ Class representing a single observatory. """
    def __init__(self, obscode, r, th, ph):
        """
        :param obscode: code of the observatory
        :type obscode: str
        :param r: radius of the observatory
        :type r: float
        :param th: colatitude of the observatory
        :type th: float
        :param ph: azimuth of the observatory
        :type ph: float
        """
        self.obscode = obscode
        self.r = r
        self.th = th
        self.ph = ph
        self.times = {}
        self.rdata = {}
        self.thdata = {}
        self.phdata = {}

    def addData(self, measureName, times, rdata, thdata, phdata):
        """
        Adds data to the observatory.

        :param measureName: name of the measure to add
        :type measureName: str
        :param times: times array
        :type times: np.array
        :param rdata: radial data
        :type rdata: np.array
        :param thdata: colatitudinal data
        :type thdata: np.array
        :param phdata: azimuthal data
        :type phdata: np.array
        :return: 0 if everything went well, -1 otherwise
        :rtype: int
        """
        for data in [self.times, self.rdata, self.thdata, self.phdata]:
            if measureName not in data:
                data[measureName] = []
        self.times[measureName].append(times)
        self.rdata[measureName].append(rdata)
        self.thdata[measureName].append(thdata)
        self.phdata[measureName].append(phdata)

    def getData(self, measureName):
        """
        Gets the data of the observatory.

        :param measureName: name of the measure to fetch
        :type measureName: str
        :return: dict with 'obscode', 'times', 'r', 'th' and 'ph' as keys and corresponding data as values
        :rtype: dict
        """
        data = {
            "obscode": self.obscode
        }
        if measureName in self.times:
            data["times"] = self.times[measureName]
            if measureName in self.rdata:
                data["r"] = self.rdata[measureName]
            if measureName in self.thdata:
                data["th"] = self.thdata[measureName]
            if measureName in self.phdata:
                data["ph"] = self.phdata[measureName]

        return data
