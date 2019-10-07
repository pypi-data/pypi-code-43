"""Froglabs API clients."""

import contextlib
import tempfile
import os

import pandas as pd
import requests
import six
import xarray as xr

from tqdm.auto import tqdm

from froglabs import exceptions


__copyright__ = 'Copyright 2019 Froglabs, Inc.'
__all__ = ['Client', 'WeatherClient']


if six.PY2:
    FileNotFoundError = IOError


@contextlib.contextmanager
def safe_open(path_or_obj, mode):
    if isinstance(path_or_obj, six.string_types):
        with open(path_or_obj, mode) as fh:
            yield fh
    else:
        yield path_or_obj


class Client(object):
    """Froglabs client.

    :param host: Hostname for the froglabs backend. Keep default for the
                 production version.
    :type host: string
    :param scheme: The url scheme to use. Defaults to http. Https will be
                   supported soon.
    :type scheme: string
    :param token: Authentication token - not needed for now.
    :type token: string
    """

    def __init__(self, host=None, scheme='http', token=None):
        if scheme not in ('http',):
            raise ValueError('scheme %r is not supported' % scheme)
        self._host = host or 'api.froglabs.ai'
        self._token = token
        self._api_url = '{}://{}'.format(scheme, self._host)
        self._session = requests.session()
        # We only want JSON back.
        self._session.headers.update({
            'Accept': 'application/json'
        })
        if token is not None:
            self._session.headers.update({
                'Authorization': 'Token {}'.format(token)
            })

    def _build_url(self, *path):
        return '/'.join([self._api_url] + list(map(str, path))) + '/'

    def request(self, method, path, params=None, data=None, json=None,
                files=None):
        """
        Makes an API request.

        Argument:
            method: str
                The HTTP method name (e.g. 'GET', 'POST', etc.)
            path: str, tuple
                A tuple of path tokens or full URL string. A tuple will be
                translated to a URL as follows: path[0]/path[1]/...
        """
        url = (self._build_url(*path)
               if not isinstance(path, six.string_types) else
               self._build_url(path))
        response = self._session.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            files=files
        )
        self.validate_response(response)
        return response

    @classmethod
    def validate_response(cls, response):
        if response.status_code >= 400:
            raise exceptions.HttpError(response)
        else:
            response.raise_for_status()

    def query(self,
              location,
              variables=None,
              start_time=None,
              end_time=None,
              spatial_resolution=None,
              space_aggregation_method=None,
              time_aggregation_step=None,
              time_aggregation_method=None,
              output=None,
              progress_bar=False):
        """Get and write weather to the output file.


        :param location: Geographical location to query. This can be:
             An address, e.g. "Atlantic Ocean", "Pacific Ocean", "Black Sea".
             Or A geographical point in latitude and longitude coordinate,
             measured in degrees. Or A geographical bounding box, defined by
             its southwest and northeast points in latitude and longitude, e.g.
             "40.90888,27.4426426,46.627499,41.7775873" (Black Sea).
        :param variables: Variables to query. See the get_variables method to
                          get an up-to-date list. Some Variables are only
                          available for forecast, others only for analysis.
                          see http://api.froglabs.ai/sanity_preserver for
                          details.
        :type variables: list of strings
        :param start_time: Start time (optional - defaults to now)
        :type start_time: datetime object, timezone aware
        :param end_time: End time (optional - defaults to now + 1 day)
        :type end_time: datetime object, timezone aware
        :param spatial_resolution: Optional spatial resolution, e.g. 0.5, 1.0
        :type spatial_resolution: float
        :param space_aggregation_method: Optional space aggregation method,
            e.g. 'sum', 'mean', if spatial resolution was provided
        :type space_aggregation_method: str
        :param time_aggregation_step: Optional time aggregation step, e.g. '3H'
        :type time_aggregation_step: str
        :param time_aggregation_method: Optional time aggregation method,
            e.g. 'sum', 'mean', if time aggregation step was provided
        :type time_aggregation_method: str
        :param output: The output file, either a filename or a file object.
        :type output: str, object
        :param progress_bar: Whether or not to enable progress bar.
        :type progress_bar: bool

        """
        if variables is None:
            variables = [
                'air_surface_temperature',
                '10m_u_component_of_wind',
                '10m_v_component_of_wind'
            ]
        # Set default time range if not provided.
        if start_time is None:
            start_time = pd.Timestamp.now('UTC')
        if end_time is None:
            end_time = start_time + pd.to_timedelta('1D')

        start_time = pd.to_datetime(start_time, utc=True)
        end_time = pd.to_datetime(end_time, utc=True)

        if start_time.tzinfo is None or end_time.tzinfo is None:
            raise ValueError('start_time and end_time should be '
                             'timezone-aware')
        if start_time >= end_time:
            raise ValueError('start_time >= end_time: %r >= %r' %
                             (start_time, end_time))
        url = self._build_url('weather')
        if not isinstance(location, six.string_types):
            if len(location) not in (2, 4):
                raise ValueError('Invalid location shape: %d' % len(location))
            location = ','.join(map(str, location))
        query = {
            'location': location,
            'variables': ','.join(variables),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
        }

        # Add space aggregation if provided.
        if (spatial_resolution is not None and
                space_aggregation_method is not None):
            query.update({
                'spatial_resolution': spatial_resolution,
                'space_aggregation_method': space_aggregation_method
            })

        # Add time aggregation if provided.
        if (time_aggregation_step is not None and
                time_aggregation_method is not None):
            query.update({
                'time_aggregation_step': time_aggregation_step,
                'time_aggregation_method': time_aggregation_method
            })

        chunk_size = 8 * 1024
        if progress_bar:
            def progress(response):
                desc = output if isinstance(output, six.string_types) else None
                size = int(response.headers['content-length'])
                return tqdm(
                    response.iter_content(chunk_size=chunk_size),
                    total=(size / chunk_size),
                    desc=desc,
                    unit='KB'
                )
        else:
            def progress(response):
                return response.iter_content(chunk_size=chunk_size)

        def stream(path_or_obj):
            with self._session.post(url, json=query, stream=True) as response:
                self.validate_response(response)
                with safe_open(path_or_obj, 'wb') as fh:
                    for chunk in progress(response):
                        if chunk:
                            fh.write(chunk)
            if not isinstance(path_or_obj, six.string_types):
                path_or_obj.seek(0)

        if output is None:
            with tempfile.NamedTemporaryFile(suffix='.nc') as fp:
                stream(fp)
                return xr.load_dataset(fp.name)
        else:
            stream(output)

    def get_variables(self):
        """Get supported weather variables.

        :returns: A table with all the available variables.
        :return type: Pandas dataframe.
        """
        response = self.request('GET', 'variables')
        return pd.read_json(response.text)

    def create_dataset(self, location, variables, path_or_obj):
        """Create training dataset.

        Arguments:
            location str, list
                Location name or coordinates.
            variables: list
                List of variable names
            path_or_obj: str, obj
                Path to time series data file
        """
        if isinstance(path_or_obj, six.string_types):
            if not os.path.exists(path_or_obj):
                raise FileNotFoundError(path_or_obj)
        if not isinstance(location, six.string_types):
            location = ','.join(map(str, location))

        with safe_open(path_or_obj, 'rb') as fh:
            response = self.request(
                'POST',
                'datasets',
                data={
                    'variables': ','.join(variables),
                    'location': location
                },
                files={'file': fh}
            )
        return response.json()

    def create_training_task(self, model, dataset, num_epochs=128,
                             batch_size=16,
                             window_size=None, seed=None, num_workers=0):
        """Creates training task for the given model and dataset.

        Arguments:
            model: str
                A model name (e.g. pvnet).
            dataset: int
                A dataset identifier.
        """
        response = self.request(
            'POST',
            'training_tasks',
            json={
                'model': model,
                'dataset': dataset,
                'num_epochs': num_epochs,
                'batch_size': batch_size,
                'window_size': window_size,
                'seed': seed,
                'num_workers': num_workers,
            }
        )
        return response.json()

    def get_training_task(self, task_id):
        response = self.request('GET', ('training_tasks', task_id))
        return response.json()


# XXX: add WeatherClient for backward compatibility.
WeatherClient = Client
