#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import requests

import py3Solr


class Demo:
    def __init__(self, cloud_model: bool = True,
                 solr_url: str = "localhost:8983",
                 collection: str = "/demo",
                 zk_host: str = ""):
        if cloud_model and zk_host and len(zk_host) > 1:
            zookeeper = py3Solr.ZooKeeper(zk_host)
            self._solr = py3Solr.SolrCloud(zookeeper, collection)
        else:
            url = solr_url + "/" + collection
            self._solr = py3Solr.Solr(url, always_commit=True)

    def search(self, query, and_or="and", start=0, handler: str = "select", rows: int = 10):
        params = {"start": str(start), 'rows': str(rows), 'q.op': and_or}

        rep = self._solr.search(q=query, search_handler=handler, **params)
        if not rep:
            return None
        return rep.raw_response["response"]

    def spell_check(self, str_in, handler: str = "spell"):
        rep = self._solr.search(q=str_in, search_handler=handler)

        res = None
        if rep is not None and hasattr(rep, "spellcheck"):
            if "suggestions" in rep.spellcheck:
                res = rep.spellcheck["suggestions"]
        # return first suggestion word.
        if res and len(res) >= 2 and "suggestion" in res[1] and len(
                res[1]["suggestion"]) >= 1 and "word" in res[1]["suggestion"][0]:
            res = res[1]["suggestion"][0]["word"]
        return res


def spellcheck(query):
    params = [('q', query)]
    _url = "http://110.64.66.207:8983/solr"
    url_search_music = _url + '/search_music/spell?wt=json'
    s = requests.session()
    s.keep_alive = False
    #  headers={"Connection": "close"} # close solr connection
    res = s.get(url=url_search_music, params=params, headers={"Connection": "close"})

    res = None if not res else res.json()["spellcheck"]["suggestions"]
    if res and len(res) >= 2 and "suggestion" in res[1] and len(
            res[1]["suggestion"]) >= 1 and "word" in res[1]["suggestion"][0]:
        res = res[1]["suggestion"][0]["word"]
    else:
        res = None
    return res


if __name__ == '__main__':
    print(spellcheck("周杰轮"))

    demo = Demo(cloud_model=False,
                solr_url="http://110.64.66.208:8983/solr",
                collection="msds_music",
                zk_host="")
    print(demo.search(query="title:周杰伦"))
    print(demo.spell_check("周杰轮"))
