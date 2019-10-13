import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from weather_api.WeatherAPI import WeatherAPI


def main():

    print('Please provide following inputs to know the weather forecast/ current temperature of your city.')
    print('\nPlease enter the name of your town :')
    place = input().strip()
    print('\nEnter the date on which you want to know the forecast')
    print('We can forecast for five upcoming days.')
    print('Date format should be  YYYY-MM-DD')
    date = input().strip() or 'current_time'  # default.
    print('\nEnter the forecast type i.e. Daily/ Hourly')
    print('We can provide forecast for next 5 days/ next 3 hours')
    print('For Daily forecast -> please input Daily')
    print('For hourly forecast -> please input Hourly')
    forecast_type = input().strip() or 'daily'  # default.
    #print(place, forecast_type, date)

    sanitize_and_process_data(place, forecast_type, date)


def sanitize_and_process_data(place, forecast_type, date):

    try:
        weather_obj = WeatherAPI(place, date, forecast_type)
        result = weather_obj.fetch_required_data()
        #print('res', result)
        if type(result) == str:
            print(result)
        else:
            for key, value in result.items():
                if key == 'Weather Forecast':
                    print('Weather Forecast: ')
                    for time_instance, temperature in result[key].items():
                        if temperature:
                            print('On {} -> The temperature [Celsius] forecast is {} '
                                  .format(time_instance, str(temperature)))
                else:
                    print('{}: {}'.format(key, str(value)))
    except Exception:
        print('Some error cccured while fetching the temperature data for the city.')
