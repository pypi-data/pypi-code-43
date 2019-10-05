# -*- coding: UTF-8 –*-

import requests
from urllib.parse import quote
import re


def hasContent(str):
    blogPageUrls = re.findall('\\.blogPageUrl="(.+?)(?<!\\\\)"', str)
    return len(blogPageUrls) > 0


def downloadPage(tag, type, limit, offset):
    print("downloadPage(), tag = %s, type = %s, limit = %d, offset = %d" % (tag, type, limit, offset))
    tag = quote(tag, 'utf-8')
    type = quote(type, 'utf-8')
    url = 'http://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr'
    referer = 'http://www.lofter.com/tag/%s/%s' % (tag, type)
    body = '''callCount=1
scriptSessionId=${scriptSessionId}187
httpSessionId=
c0-scriptName=TagBean
c0-methodName=search
c0-id=0
c0-param0=string:%s
c0-param1=number:0
c0-param2=string:
c0-param3=string:%s
c0-param4=boolean:false
c0-param5=number:0
c0-param6=number:%s
c0-param7=number:%s
c0-param8=number:0
batchId=978839''' % (tag, type, str(limit), str(offset))
    res = requests.post(url, data=body, headers={'Referer': referer})
    return res.content


def downloadTag(tag, type, limit=500, offset=0):
    print("downloadTag(), tag = %s, type = %s" % (tag, type))
    res = []
    while True:
        page = {}
        body = downloadPage(tag, type, limit, offset)
        if not hasContent(body.decode('utf-8')):
            break
        page['tag'] = tag
        page['type'] = type
        page['limit'] = limit
        page['offset'] = offset
        page['body'] = body
        res.append(page)
        offset += limit
    return res


def downloadTagWithTypes(tag, types=None):
    defaultTypes = ['new', 'total', 'mouth', 'week', 'date']
    if types == None:
        types = defaultTypes
    res = []
    for type in types:
        pages = downloadTag(tag, type)
        res.extend(pages)
    return res


if __name__ == '__main__':
    tags = []
    for tag in tags:
        pages = downloadTagWithTypes(tag)
        for page in pages:
            filename = 'tag_%s_type_%s_limit_%s_offset_%s.tag' % (
                page['tag'], page['type'], page['limit'], page['offset'])
            with open(filename, 'wb') as f:
                f.write(page['body'])
