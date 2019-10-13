import os
import sys
import requests
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configurations import config


class WeatherAPI:
    """
            This class queries the OpenWeather API with the user inputs.
            And returns the weather forecast of the city mentioned by the user.

            :Parameters:
                # place - The place/ city for which the temperature is to be found.
                # date - The date for which the temperature forecast is to be found. Default (already set)
                        is current_date.
                # forecast_type - Defines the type of forecast needed - hourly/daily.

            :Returns:
                String/ Dictionary -
                        String in case the city itself is not found in the API call.
                        else:
                        dictionary with the weather data.

            :Raises:
                Exception Message : Error while getting the weather data.


            :Sample Code Block:
            .. code-block:: python
                   :emphasize-lines: 1

                related_assets = server.query('{}/related_asset'.format(project), filters=[(input_key, search_key)])


            :Sample executions/results:
            >>>  response = requests.get('http://api.openweathermap.org/data/2.5/forecast{}/{}')

                if response.status_code != 200:
                    raise Exception
                response_data = response.json()

            :Logic:
                Call the API endpoint to get the city results.
                Insert them into dictionary & return back to the caller function.
        """

    def __init__(self, place, input_date, forecast_type):

        self.place = place.lower()
        self.input_date = input_date.lower()
        self.forecast_type = forecast_type.lower()

        self.api_key = config.API_KEY
        self.api_base_adr = config.API_BASE_ADDRESS
        self.api_daily_forecast_base_adr = config.API_DAILY_BASE_ADDRESS

    def fetch_required_data(self):

        result = dict()
        try:
            response_data = self.find_city_weather_forecast()
            weather_forecast = self.find_weather_forecast(response_data)
            #print('lets process', weather_forecast)

            if not weather_forecast.get('success_code'):
                result = 'We are not able to find the details of the city. Sorry for the in-convenience'
                return

            if self.input_date == 'current_time':
                result['Current Temperature [Celsius]'] = self.find_city_current_temp()
            else:
                result['Temperature On Given Date [Celsius}'] = weather_forecast.get('daily')\
                                                      .get('{} {}'.format(self.input_date, '00:00:00')) \
                                                      or 'Data can not be found for this date.'

            if self.forecast_type == 'hourly':
                result['Weather Forecast'] = weather_forecast.get('hourly')
            else:
                result['Weather Forecast'] = weather_forecast.get('daily')
        except Exception:
            result = 'Some Error occurred while fetching the data for the city.'
        finally:
            return result

    def find_city_current_temp(self):

        kelvin_to_celsius = 273.15
        current_temperature = None
        city_binder, api_binder = '?q=', '&appid='
        url_for_fetching_data_from_city_name = '{}{}{}{}{}'.format(self.api_base_adr, city_binder, self.place,
                                                                   api_binder, self.api_key)

        try:
            response = requests.get(url=url_for_fetching_data_from_city_name)

            if response.status_code != 200 or 'message' in response.json():
                raise Exception

            current_temperature = round((response.json().get('main').get('temp') - kelvin_to_celsius), 2)
        except Exception:
            raise
        finally:
            return current_temperature

    def find_city_weather_forecast(self):

        response_data = dict()
        city_binder, api_binder = '?q=', '&appid='
        url_for_fetching_data_from_city_name = '{}{}{}{}{}'.format(self.api_daily_forecast_base_adr, city_binder,
                                                                   self.place, api_binder, self.api_key)

        try:
            response = requests.get(url=url_for_fetching_data_from_city_name)

            if response.status_code != 200:
                raise Exception
            response_data = response.json()
        except Exception:
            pass
        finally:
            return response_data

    def find_weather_forecast(self, weather_data):

        kelvin_to_celsius = 273.15
        weather_forecasts = {'daily': dict(), 'hourly': dict(), 'success_code': 1}
        today = date.today()

        try:
            for i in range(1, 6):
                weather_forecasts['daily']['{} {}'.format((today + timedelta(days=i)), '00:00:00')] = ''

            for data in weather_data.get('list')[1:]:
                if data.get('dt_txt') in weather_forecasts.get('daily'):
                    weather_forecasts['daily'][data.get('dt_txt')] = round((data.get('main').get('temp') -
                                                                            kelvin_to_celsius), 2)

            count = 0

            for data in weather_data.get('list')[1:]:
                if data.get('main').get('temp'):
                    weather_forecasts['hourly'][data.get('dt_txt')] = round((data.get('main').get('temp') -
                                                                             kelvin_to_celsius), 2)
                count += 1
                if count == 5:
                    break
        except IndexError:
            pass
        except Exception:
            pass
        finally:
            if not weather_forecasts.get('hourly'):
                weather_forecasts['success_code'] = 0
            return weather_forecasts
