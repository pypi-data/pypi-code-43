#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import requests

from .util import safe_urlencode, force_unicode


class SolrCoreAdmin(object):
    """
    Handles core admin operations: see http://wiki.apache.org/solr/CoreAdmin

    This must be initialized with the full admin cores URL::

        solr_admin = SolrCoreAdmin('http://localhost:8983/solr/admin/cores')
        status = solr_admin.status()

    Operations offered by Solr are:
       1. STATUS
       2. CREATE
       3. RELOAD
       4. RENAME
       5. ALIAS
       6. SWAP
       7. UNLOAD
       8. LOAD (not currently implemented)
    """

    def __init__(self, url, *args, **kwargs):
        super(SolrCoreAdmin, self).__init__(*args, **kwargs)
        self.url = url

    def _get_url(self, url, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}

        resp = requests.get(url, data=safe_urlencode(params), headers=headers)
        return force_unicode(resp.content)

    def status(self, core=None):
        """
        Get core status information

        See https://wiki.apache.org/solr/CoreAdmin#STATUS
        """
        params = {"action": "STATUS"}

        if core is not None:
            params.update(core=core)

        return self._get_url(self.url, params=params)

    def create(
            self, name, instance_dir=None, config="solrconfig.xml", schema="schema.xml"
    ):
        """
        Create a new core

        See https://wiki.apache.org/solr/CoreAdmin#CREATE
        """
        params = {"action": "CREATE", "name": name, "config": config, "schema": schema}

        if instance_dir is None:
            params.update(instanceDir=name)
        else:
            params.update(instanceDir=instance_dir)

        return self._get_url(self.url, params=params)

    def reload(self, core):  # NOQA: A003
        """
        Reload a core

        See https://wiki.apache.org/solr/CoreAdmin#RELOAD
        """
        params = {"action": "RELOAD", "core": core}
        return self._get_url(self.url, params=params)

    def rename(self, core, other):
        """
        Rename a core

        See http://wiki.apache.org/solr/CoreAdmin#RENAME
        """
        params = {"action": "RENAME", "core": core, "other": other}
        return self._get_url(self.url, params=params)

    def swap(self, core, other):
        """
        Swap a core

        See http://wiki.apache.org/solr/CoreAdmin#SWAP
        """
        params = {"action": "SWAP", "core": core, "other": other}
        return self._get_url(self.url, params=params)

    def unload(self, core):
        """
        Unload a core

        See http://wiki.apache.org/solr/CoreAdmin#UNLOAD
        """
        params = {"action": "UNLOAD", "core": core}
        return self._get_url(self.url, params=params)

    def load(self, core):
        raise NotImplementedError("Solr 1.4 and below do not support this operation.")