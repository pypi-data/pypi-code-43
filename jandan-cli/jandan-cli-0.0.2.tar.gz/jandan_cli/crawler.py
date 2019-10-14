# -*- coding: utf-8 -*-

from __future__ import absolute_import
import gevent
from gevent import monkey
monkey.patch_all()

import json
import sys
from requests import Session
from tabulate import tabulate
from bs4 import BeautifulSoup as bsoup
import grequests

from jandan_cli.utils import is_json, output
from jandan_cli.const import IMAGE_PATH, TUCAO_LIST, HEADERS

session = Session()

def start_request(url, method='get', data={}, headers=HEADERS, timeout=30):
    try:
        if method == 'get':
            r = session.get(url, timeout=timeout, headers=headers)
        else:
            r = session.post(url, timeout=timeout, headers=headers, data=data)

        if r.status_code != 200:
            return {'errcode': r.status_code, 'msg': 'server error'}
        if is_json(r.text):
            return json.loads(r.text)
        return {'text': r.text}
    except Exception as e:
        return {'errcode': 500, 'msg': str(e)}


def download_pics(urls, path=IMAGE_PATH, headers={}):
    try:
        rs = (grequests.get(url, timeout=30, headers=headers, stream=True) for url in urls.split('\n'))
        for r in grequests.map(rs):
            filename = r.url.split('/')[-1].split('#')[0]
            with open(f'{path}/{filename}', 'wb') as f:
                f.write(r.content)
        return True
    except:
        return False


def render_article_list(obj):
    tabulate.PRESERVE_WHITESPACE = True
    table_header = ['id', 'title', 'comments', 'author']
    if 'status' in obj and obj['status'] == 'ok':
        table_data = []
        for post in obj['posts']:
            table_data.append( (post['id'], post['title'], post['comment_count'], post['author']['name'] + ' . ' + post['tags'][0]['title']) )
        output.color_print(tabulate(table_data, headers=table_header, tablefmt='grid'), fg='green', bold=True)
    elif 'errcode' in obj:
        output.color_print(obj['msg'], fg='red')
    else:
        output.color_print('error unknow', fg='red')


def render_article_detail(obj, silence=False):
    if 'status' in obj and obj['status'] == 'ok':
        output.info('id: {}, author: {}, date: {}, category: {}'.format(obj['post']['id'], obj['post']['author']['name'], obj['post']['date'], obj['post']['categories'][0]['description']))
        output.warn('title: {}'.format(obj['post']['title']))
        output.prompt('url: {}\n'.format(obj['post']['url']))
        output.succeed('content:\n {}\n\n'.format(obj['post']['content']))
        if silence == False and obj['post']['comments'] and len(obj['post']['comments']) > 0:
            output.echo('comments below: \n')
            for comment in obj['post']['comments']:
                output.echo('------------------------------\n[{index}] {name} {date}:\n {content} \n [comment_id] {id} [oo] {vote_positive} [xx] {vote_negative}\n'.format(**comment))
    elif 'errcode' in obj:
        output.color_print(obj['msg'], fg='red')
    else:
        output.color_print('error unknow', fg='red')


def render_comment_list(obj, download=False):
    if 'text' in obj:
        obj = _parse_comment_list(obj['text'])
        for comment in obj:
            output.echo('------------------------------\n[{index}] {author} {date}:\n {content}\n{pics} \n [comment_id] {id} [oo] {oo} [xx] {xx} {tucao}\n'.format(**comment))
            if comment['pics'] and download:
                download_pics(comment['pics'])
    elif 'errcode' in obj:
        output.error(obj['msg'])
    else:
        output.error('error unknow')


def render_comment_detail(obj):
    if 'text' in obj:
        obj = _parse_comment_detail(obj['text'])
        output.succeed('{author}: {content} \n {pics}'.format(**obj))
    elif 'errcode' in obj:
        output.error(obj['msg'])
    else:
        output.error('error unknow')

def render_tucao_list(obj, hot_display=False, j=1):
    if 'code' in obj and obj['code'] == 0:
        if 'hot_tucao' in obj and hot_display == False:
            output.color_print('\nhot tucao list: \n', fg='red', bold=True)
            i = 1
            for tucao in obj['hot_tucao']:
                output.color_print('{}.---------------\n [tucao_id] {} [comment_id] {} [post_id] {}\n [author] {} [date] {} \n {} \n [oo] {} [xx] {}'.format(i, tucao['comment_ID'], tucao['comment_parent'], tucao['comment_post_ID'], tucao['comment_author'], tucao['comment_date'], tucao['comment_content'], tucao['vote_positive'], tucao['vote_negative']), fg='white', bold=True)
                i += 1
        if 'tucao' in obj:
            if not hot_display:
                output.color_print('\nnormal tucao list: \n', fg='yellow', bold=True)
            for tucao in obj['tucao']:
                output.color_print('{}.---------------\n [tucao_id] {} [comment_id] {} [post_id] {}\n [author] {} [date] {} \n {} \n [oo] {} [xx] {}'.format(j, tucao['comment_ID'], tucao['comment_parent'], tucao['comment_post_ID'], tucao['comment_author'], tucao['comment_date'], tucao['comment_content'], tucao['vote_positive'], tucao['vote_negative']), fg='white', bold=True)
                j += 1

        if obj['has_next_page']:
            url = TUCAO_LIST.format(obj['tucao'][0]['comment_parent']) + '/n/{}'.format(obj['tucao'][-1]['comment_ID'])
            obj = start_request(url)
            render_tucao_list(obj, hot_display=True, j=j)

    elif 'errcode' in obj:
        output.error(obj['msg'])
    else:
        output.error('error unknow')

def _parse_comment_list(html):
    soup = bsoup(html, 'html.parser')
    obj = []
    i = 1
    for li in soup.select_one('ol.commentlist').select('li[id^="comment-"]'):
        id_ele = li.select_one('span.righttext > a')
        id = id_ele.text if id_ele else li.select_one('a[data-type="pos"]').get('data-id')
        pics = '\n'.join('http:' + img.get('href') for img in li.select('a.view_img_link'))
        content = '\n'. join(p.text for p in li.find('div', class_='commenttext').select('p'))
        obj.append({
            'id': id,
            'author': li.select_one('b').text,
            'oo': li.select_one('a[data-type="pos"]').next_sibling.next_sibling.text,
            'xx': li.select_one('a[data-type="neg"]').next_sibling.next_sibling.text,
            'tucao': li.find('a', class_='tucao-btn').text,
            'content': content,
            'date': li.find('span', class_='time').text,
            'index': i,
            'pics': pics
        })
        i += 1
    return obj


def _parse_comment_detail(html):
    soup = bsoup(html, 'html.parser')
    content = soup.select_one('div.entry')
    author = content.find('b').text
    pics = '\n'.join('http:' + img.get('href') for img in content.select('a.view_img_link'))
    content_text = '\n'.join(p.text for p in content.select('p'))
    return {
        'content': content_text,
        'pics': pics,
        'author': author,
    }

def parse_post_id(html):
    soup = bsoup(html, 'html.parser')
    return soup.select_one('input#comment_post_ID').get('value')