from nanpy import SerialManager, DHT
from time import sleep

class DhtSensor(object):
    
    def __init__(self, connection=None, pin: int = 2):
        self.__setup(connection, pin)

    def __setup(self, connection, pin) -> None:
        try:
            self.__connection = connection if connection is not None else \
                SerialManager()
            self.__pin = pin
            self.__dht = DHT(self.__pin, DHT.DHT22,
                             connection=self.__connection)
        except Exception as err:
            raise err

    def set_connection(self, connection):
        self.__connection = connection

    @property
    def read_celcius_temperature(self):
        return self.__dht.readTemperature(False)

    @property
    def read_fahrenheit_temperature(self):
        return self.__dht.readTemperature(True)

    @property
    def read_humidity(self):
        return self.__dht.readHumidity()

    def __loop(self) -> None:
        try:
            while self.__dht is not None:
                print("Celcius: {0} Fahrenheit: {1} Humidity: {2}".format(
                    self.read_celcius_temperature,
                    self.read_fahrenheit_temperature,
                    self.read_humidity))
                sleep(1)
        except KeyboardInterrupt:
            print("Closing Serial Connection to Arduino")
            self.close_connection()
            print("Done...")

    def close_connection(self) -> None:
        self.__dht.connection.close()

    def test_run(self):
        self.__loop()


if __name__ == "__main__":
    conn = SerialManager("COM5")
    dht = DhtSensor(connection=conn)
    dht.test_run()
