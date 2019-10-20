import os
class ExperimentFiles():
    def __init__(self, foldername):
        self.main_folder = foldername
        if not os.path.isdir(self.main_folder):
            os.makedirs(self.main_folder)
        self.raw_signal = os.path.join(foldername, "raw_signal.csv")
        self.pump_data = os.path.join(foldername, "pump_data.csv")
        self.laser_calibration = os.path.join(foldername, "laser_calibration.csv")
        self.logfile = os.path.join(foldername, "log.csv")
        self.pump_calibration = os.path.join(foldername, "pump_calibration.csv")
        self.volumes = os.path.join(foldername, "volumes.csv")

        if not os.path.isfile(self.volumes):
            with open(self.volumes, "w+") as f:
                f.write("time,vacuum,peace,death\n")

        if not os.path.isfile(self.pump_calibration):
            with open(self.pump_calibration, "w+") as f:
                f.write("time,death_units_to_ml_p1,peace_units_to_ml_p2,vacuum_units_to_ml_p1\n")

        if not os.path.isfile(self.logfile):
            with open(self.logfile, "w+") as f:
                f.write("time\tcomment\n")

        if not os.path.isfile(self.pump_data):
            with open(self.pump_data, "w+") as f:
                f.write("time,tube,pump,vol\n")
        self.pump_calibration = os.path.join(foldername, "pump_calibration.csv")
        if not os.path.isfile(self.raw_signal):
            header = "time"
            for i in range(7):
                for signalname in ["onFS", "onSS", "offFS", "offSS"]:
                    header += "," + signalname + str(i)
            header += "\n"
            with open(self.raw_signal, "a") as f:
                f.write(header)

    def __repr__(self):
        return self.main_folder