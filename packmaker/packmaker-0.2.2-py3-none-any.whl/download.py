# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import requests
import urllib.parse

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .framew.log import getlog

log = getlog()

##############################################################################


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

##############################################################################


class HttpDownloader (object):

    def __init__(self, download_dir):
        super(HttpDownloader, self).__init__()
        self.download_dir = download_dir

    ##########################################################################

    def subdownloader(self, download_dir):
        return HttpDownloader(os.path.join(self.download_dir, download_dir))

    ##########################################################################

    def download(self, url, filename=None):
        if filename is None:
            filename = os.path.basename(urllib.parse.urlparse(url).path)
        localfile = os.path.join(self.download_dir, filename)
        if not os.path.exists(localfile):
            log.info('  downloading : {}'.format(url))
            self.do_file_download(url, localfile)
        else:
            log.info('  [cached]    : {}'.format(url))
        return localfile

    ##########################################################################

    def do_file_download(self, url, dest):
        destdir = os.path.dirname(dest)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        tempfile = os.path.join(destdir, '.downloading_{}'.format(os.path.basename(dest)))
        if os.path.exists(tempfile):
            os.remove(tempfile)
        try:
            with requests_retry_session().get(url, stream=True, timeout=(5, 15)) as r:
                r.raise_for_status()
                with open(tempfile, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
            os.rename(tempfile, dest)
        finally:
            try:
                os.remove(tempfile)
            except FileNotFoundError:
                pass

##############################################################################


class MavenDownloader (HttpDownloader):

    def __init__(self, download_dir, maven_repos):
        super(MavenDownloader, self).__init__(download_dir)
        self.maven_repos = maven_repos

    ##########################################################################

    def find_maven_repo(self, library):
        group, artifact, version = library.split(':')
        library_filename = '{}-{}.jar'.format(artifact, version)

        cached_library = os.path.join(self.download_dir, library_filename)
        cached_library_meta = '{}.meta'.format(cached_library)

        if os.path.exists(cached_library_meta):
            with open(cached_library_meta, 'r') as lmf:
                meta = json.load(lmf)
            mavenrepo = meta.get('mavenRepo', None)
            if mavenrepo is not None:
                log.info('  [cached]    : {} - {}'.format(library, mavenrepo))
                return mavenrepo

        localfile, mavenrepo = self.download_library_from_repo(group, artifact, version, library_filename)
        if mavenrepo is None:
            raise Exception('Cannot find a maven repository for  {}'.format(library))

        meta = {'mavenRepo': mavenrepo}
        with open(cached_library_meta, 'w') as mf:
            mf.write(json.dumps(meta))

        return mavenrepo

    ##########################################################################

    def download_library_from_repo(self, group, artifact, version, filename):
        urlpath = '{}/{}/{}/{}'.format(group.replace('.', '/'), artifact, version, filename)
        localfile = os.path.join(self.download_dir, filename)

        for mavenrepo in self.maven_repos:
            url = '{}{}'.format(mavenrepo, urlpath)
            log.info('  downloading : {}'.format(url))
            try:
                self.do_file_download(url, localfile)
            except requests.exceptions.HTTPError:
                continue
            return localfile, mavenrepo

        return None, None

##############################################################################
# THE END
