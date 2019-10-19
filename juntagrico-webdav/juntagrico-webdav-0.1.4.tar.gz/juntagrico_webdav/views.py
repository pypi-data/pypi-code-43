import requests
from xml.etree import ElementTree as ET
from re import sub
from urllib.parse import unquote, urlsplit

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from juntagrico.views import get_menu_dict
from juntagrico_webdav.entity.servers import WebdavServer


@login_required
def list(request, id):
    server = get_object_or_404(WebdavServer, pk=id)
    url = server.url + '/' + server.path
    username = server.username
    password = server.password
    session = requests.Session()
    session.auth = (username, password)
    session.get(url)
    headers = {'Accept': '*/*', 'Depth': '1'}
    response = session.request('PROPFIND', url, headers=headers)
    files = []
    tree = ET.fromstring(response.content)
    for prop in tree.findall('./{DAV:}response'):
        href = prop.find('./{DAV:}href').text
        href = sub("/.+/", '/', href)[1:]
        name = unquote(urlsplit(href).path)
        last_mod_date = prop.find('.//{DAV:}getlastmodified').text
        if name != '':
            element = {'url': href,
                       'name': name,
                       'date': last_mod_date}
            files.append(element)
    renderdict = get_menu_dict(request)
    renderdict .update({
        'webdav_server': server,
        'files': files,
        'menu': {'wd': 'active'},
    })
    return render(request, "wd/list.html", renderdict)

@login_required
def get_item(request, id):
    path = request.GET.get('path')
    server = get_object_or_404(WebdavServer, pk=id)
    url = server.url + '/' + server.path + '/' + path
    username = server.username
    password = server.password
    session = requests.Session()
    session.auth = (username, password)
    session.get(url)
    file_response = session.request('GET', url)
    response = HttpResponse(file_response.content,content_type=file_response.headers['Content-Type'])
    return response
