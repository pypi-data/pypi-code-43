import requests
owmkey = "fe198ba65970ed3877578f728f33e0f9"

class Weather:

    def find(self):
        finder = requests.post('http://api.openweathermap.org/data/2.5/weather?APPID=' + str(
                    owmkey) + f'&lang=en&units=metric&q={self}')
        if finder.json()['cod'] == "404":
            f = {"error_code": "404", "status": "city not found"}
            return f
        elif finder.json()['cod'] == "400":
            f = {"error_code": "400", "status": "city not found"}
            return f
        else:
            f = {"weather": {"city": finder.json()['name'], "temp": finder.json()['main']['temp'], "pressure": finder.json()['main']['pressure'], "humidity": finder.json()['main']['humidity'], "lon": finder.json()['coord']['lon'], "lat": finder.json()['coord']['lat']}, "main": finder.json()['weather'][0]['main'], "description": finder.json()['weather'][0]['description'], "wind": {"speed": finder.json()['wind']['speed']}, "error_code": "-1"}
            return f
