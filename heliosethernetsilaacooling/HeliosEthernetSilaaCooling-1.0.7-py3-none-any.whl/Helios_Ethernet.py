"""
@ Stefanie Fiedler 2019
@ Alexander Teubert 2019
Version vom 13.10.2019

for Hochschule Anhalt, University of Applied Sciences
in coorperation with axxeo GmbH
"""

from EasyModbusSilaaCooling.modbusClient import ModbusClient as MBC
from HeliosEthernetSilaaCooling.Helios_HexConverter import str2duohex, duohex2str
from HeliosEthernetSilaaCooling.Helios_Errors import errortable, warningtable, infotable

class COM():
    """
    Implementation of a Modbus TCP/IP-Client to access read and writeable attributes of a Helios KWL Device
    """

    def __init__(self, ip = "192.168.1.199", port = 502):
        if isinstance(ip, str): self.__ip = ip
        if isinstance(port, int): self.__port = port

        self.__timeout = 2
        self.__device_id = 180

        """
        setup for the Modbus-Connection
        """

        self.modbusclient = MBC(self.__ip, self.__port)
        self.modbusclient.unitidentifier = self.__device_id
        self.modbusclient.timeout = self.__timeout
        self.modbusclient.connect()

        """
        set date-format to dd.mm.yyyy
        """

        self.modbusclient.write_multiple_registers(0, str2duohex("v00052=mm.dd.yyyy"))

        """
        set mode to automatic
        """

        self.modbusclient.write_multiple_registers(0, str2duohex("v00101=0"))

        #self.modbusclient.close()

    def __del__(self):
        self.modbusclient.close()

    def read_temp(self):
        """
        reads several temperature values from slave and returns them as a list of float-values
        """

        """
        read outdoor-air-temperature (variable v00104) / Aussenluft
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00104"))
        outTemp = duohex2str(self.modbusclient.read_holdingregisters(0,8))[7:-3]

        """
        read supplied-air-temperature (variable v00105) / Zuluft
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00105"))
        suppTemp = duohex2str(self.modbusclient.read_holdingregisters(0,8))[7:-3]

        """
        read exhaust-air-temperature (variable v00106) / Fortluft
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00106"))
        exhaustTemp = duohex2str(self.modbusclient.read_holdingregisters(0,8))[7:-3]

        """
        read extract-air-temperature (variable v00107) / Abluft
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00107"))
        extractTemp = duohex2str(self.modbusclient.read_holdingregisters(0,8))[7:-3]

        return float(outTemp), float(suppTemp), float(exhaustTemp), float(extractTemp)

    def get_date(self):
        """
        outputs the slaves time and date
        """

        """
        read system-clock (variable v00005)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00005"))
        time = duohex2str(self.modbusclient.read_holdingregisters(0,9))[7:]

        """
        read system-date (variable v00004)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00004"))
        date = duohex2str(self.modbusclient.read_holdingregisters(0,9))[7:]

        return time, date

    def set_date(self, time, date):
        """
        sets the slave time and date
        """

        """
        sets the slave date / v00004
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00004="+date) )

        """
        sets the slave time / v00005
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00005="+time) )

    def read_management_state(self):
        """
        outputs the state of the humidity, carbon-dioxide and voc-management
        """

        """
        read humidity management-state (variable v00033)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00033") )
        humidity_state = duohex2str(self.modbusclient.read_holdingregisters(0,5))[7:]

        """
        read carbon-dioxide management-state (variable v00037)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00037") )
        carbon_state = duohex2str(self.modbusclient.read_holdingregisters(0,5))[7:]

        """
        read voc management-state (variable v00040)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00040") )
        voc_state = duohex2str(self.modbusclient.read_holdingregisters(0,5))[7:]

        return int(humidity_state), int(carbon_state), int(voc_state)

    def read_management_opt(self):
        """
        outputs the defined optimum value for the humidity, carbon-dioxide and voc-management
        """

        """
        read optimum humidity value in percent (variable v00034)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00034"))
        humidity_val = duohex2str(self.modbusclient.read_holdingregisters(0,5))[7:]

        """
        read optimum carbon-dioxide concentration in ppm (variable v00038)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00038") )
        carbon_val = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]

        """
        read optimum voc concentration in ppm (variable v00041)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00041") )
        voc_val = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]

        return int(humidity_val), int(carbon_val), int(voc_val)

    def write_management_state(self, state_humidity, state_carbon, state_voc):
        """
        writes the state of the humidity, carbon-dioxide and voc-management
        """

        """
        write humidity management-state (variable v00033)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00033="+ str(state_humidity)) )

        """
        write carbon-dioxide management-state (variable v00037)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00037="+ str(state_carbon)) )

        """
        write voc management-state (variable v00040)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00040="+ str(state_voc)) )

    def write_management_opt(self, opt_humidity, opt_carbon, opt_voc):
        """
        sets the optimum value for the humidity, carbon-dioxide and voc-management
        """

        """
        set the optimum percentage of air-humidity /  between 20% and 80% (variable v00034)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00034="+ str(opt_humidity)) )

        """
        set the optimum concentration of carbon-dioxide / between 300 and 2000 ppm (variable v00038)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00038="+ str(opt_carbon)) )

        """
        set the optimum concentration of voc / between 300 and 2000 ppm (variable v00041)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00041="+ str(opt_voc)) )

    def state_preheater(self, *preheater):
        """
        sets/ reads the state of the preheater / 0 = off, 1 = on (variable v00024)
        """
        try:
            if isinstance(preheater[0], int): self.modbusclient.write_multiple_registers(0, str2duohex("v00024="+ str(preheater[0])) )

        except IndexError:
            self.modbusclient.write_multiple_registers(0, str2duohex("v00024"))
            state = duohex2str(self.modbusclient.read_holdingregisters(0,5))[7:]
            return state

    def read_fan_level(self):
        """
        read fan level in percents (variable v00103)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00103") )
        level = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]
        return int(level)

    def read_fan_rpm(self):
        """
        read the revolutions per minute for the supply fan (variable v00348)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00348") )
        supply = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]

        """
        read the revolutions per minute for the extraction fan (variable v00349)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v00349") )
        extraction = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]
        return int(supply), int(extraction)

    def write_fan_stage(self, supply, extraction):
        """
        sets the state for the supply and  extraction fans / stages 1-4
        """

        """
        sets the stage for the supply fan (variable v01050)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v01050="+ str(supply)) )

        """
        sets the stage for the extraction fan (variable v01051)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v01051="+ str(extraction)) )

    def read_fan_stage(self):
        """
        read supply fan stage / 1-4 (variable v01050)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v01050") )
        supply = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]

        """
        read extraction fan stage / 1-4 (variable v01051)
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v01051") )
        extraction = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]
        return int(supply), int(extraction)

    def get_state(self):
        """
        receive error messages from the Helios Slave
        """

        string = ""

        """
        read errors as integer values / v01123
        """
        try:
            self.modbusclient.write_multiple_registers(0, str2duohex("v01123") )
            string = duohex2str(self.modbusclient.read_holdingregisters(0,8))[7:]
            return errortable(int(string)), "error"

        except KeyError:
            """
            read warnings as integer values / v01124
            """
            try:
                self.modbusclient.write_multiple_registers(0, str2duohex("v01124") )
                string = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]
                return warningtable(int(string)), "warning"

            except KeyError:
                """
                read informations on the state of the KWL EC 170 W / v01125
                """
                try:
                    self.modbusclient.write_multiple_registers(0, str2duohex("v01125") )
                    string = duohex2str(self.modbusclient.read_holdingregisters(0,6))[7:]
                    return infotable(int(string)), "state"

                except KeyError:
                    return "Keine Fehler, Warnungen oder Infos vorhanden!"

    def clear_state(self):
        """
        clears the memory of the error register
        """
        self.modbusclient.write_multiple_registers(0, str2duohex("v02015=1") )
