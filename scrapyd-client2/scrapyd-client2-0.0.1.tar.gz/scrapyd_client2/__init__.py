from json import JSONDecodeError
from urllib.parse import urljoin

import requests

from .exceptions import ScrapydException

__all__ = ['ScrapydClient']


class ScrapydClient:
    def __init__(self, url, timeout=None):
        self._base_url = url
        self._timeout = timeout

    def daemon_status(self):
        url = urljoin(self._base_url, 'daemonstatus.json')
        d = self._request_return_dict('get', url)
        return d

    def add_version(self, project, version, egg):
        url = urljoin(self._base_url, 'addversion.json')
        data = {
            'project': project,
            'version': version
        }
        files = {'egg': egg}
        d = self._request_return_dict('post', url, data=data, files=files)
        return d['spiders']

    def schedule(self, project, spider, settings=None, job_id=None, version=None, **kwargs):
        url = urljoin(self._base_url, 'schedule.json')
        data = [
            ('project', project),
            ('spider', spider),
            ('jobid', job_id),
            ('_version', version)
        ]
        if settings:
            data.extend([('setting', '%s=%s' % (k, v)) for k, v in settings.items()])
        data.extend(kwargs.items())
        d = self._request_return_dict('post', url, data=data)
        return d['jobid']

    def cancel(self, project, job_id):
        url = urljoin(self._base_url, 'cancel.json')
        data = {'project': project, 'job': job_id}
        d = self._request_return_dict('post', url, data=data)
        return d['prevstate']

    def list_projects(self):
        url = urljoin(self._base_url, 'listprojects.json')
        d = self._request_return_dict('get', url)
        return d['projects']

    def list_versions(self, project):
        url = urljoin(self._base_url, 'listversions.json')
        d = self._request_return_dict('get', url, params={'project': project})
        return d['versions']

    def list_spiders(self, project, version=None):
        url = urljoin(self._base_url, 'listspiders.json')
        d = self._request_return_dict('get', url, params={'project': project, '_version': version})
        return d['spiders']

    def list_jobs(self, project):
        url = urljoin(self._base_url, 'listjobs.json')
        d = self._request_return_dict('get', url, params={'project': project})
        return d

    def del_version(self, project, version):
        url = urljoin(self._base_url, 'delversion.json')
        self._request_return_dict('post', url, data={'project': project, 'version': version})

    def del_project(self, project):
        url = urljoin(self._base_url, 'delproject.json')
        self._request_return_dict('post', url, data={'project': project})

    def get_log(self, project, spider, job_id, encoding='utf-8'):
        url = urljoin(self._base_url, 'logs/%s/%s/%s.log' % (project, spider, job_id))
        response = self._request('get', url)
        response.encoding = encoding
        return response.text

    def _request(self, *args, **kwargs):
        try:
            response = requests.request(*args, **kwargs, timeout=self._timeout)
        except Exception as exc:
            raise ScrapydException(exc) from exc

        if not response.ok:
            raise ScrapydException('Scrapyd response error (status code %d): %s' %
                                   (response.status_code, response.text))

        return response

    def _request_return_dict(self, *args, **kwargs):
        response = self._request(*args, **kwargs)
        try:
            d = response.json()
        except JSONDecodeError as exc:
            raise ScrapydException('Scrapyd responded an invalid JSON: %s' % response.text) from exc

        if d['status'] != 'ok':
            raise ScrapydException('Scrapyd error: %s' % d)

        d.pop('status')
        return d
