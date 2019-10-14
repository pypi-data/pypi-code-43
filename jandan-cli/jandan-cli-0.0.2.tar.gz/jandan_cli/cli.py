# -*- coding: utf-8 -*-
from __future__ import absolute_import

import click
import sys
import os
import json
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from bs4 import BeautifulSoup as bsoup
from base64 import b64encode
from datetime import datetime

from jandan_cli import __version__
from jandan_cli.crawler import (
  start_request,
  render_article_list,
  render_article_detail,
  render_comment_list,
  render_comment_detail,
  render_tucao_list,
  parse_post_id
)

from jandan_cli.utils import (
  make_dict,
  save_log,
  get_userinfo,
  set_userinfo,
  set_json,
  get_json,
  del_json,
  output
)

from jandan_cli.const import (
  HEADERS,
  CATEGORY_LIST,
  TUCAO_LIST,
  ARTICLE_LIST,
  ARTICLE_DETAIL,
  COMMENT_LIST,
  COMMENT_DETAIL,
  COMMENT_CATEGORIES,
  JD_VOTE,
  JD_REPORT,
  JD_TUCAO,
  JD_COMMENT,
  IMAGE_PATH,
  USER_CONFIG,
  USER_FAVOUR
)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command()
@click.option('-c', '--category', default='pic', help='qa/treehole/zoo/pic/ooxx/faq/zhoubian/app/pond/top', type=click.Choice(COMMENT_CATEGORIES))
@click.option('-d', '--download', is_flag=True, help='download all pics in the list?')
@click.argument('page', required=False, type=int)
def comment_list(category, page, download):
  url = COMMENT_LIST.format(category)
  if page:
    today = datetime.now().strftime('%Y%m%d')
    page_encode = b64encode(f'{today}-{page}'.encode('utf-8')).decode('utf-8')
    url = f'{url}/{page_encode}#comments'
  r = start_request(url)
  render_comment_list(r, download)


@click.command()
@click.argument('comment_id', required=True, type=int)
@click.option('-o', '--oo', is_flag=True, help='oo it')
@click.option('-x', '--xx', is_flag=True, help='xx it')
@click.option('-f', '--favour', is_flag=True, help='favour it')
@click.pass_context
def comment_detail(ctx, comment_id, oo, xx, favour):
  r = start_request(COMMENT_DETAIL.format(comment_id))
  render_comment_detail(r)
  r = start_request(TUCAO_LIST.format(comment_id))
  render_tucao_list(r)
  if oo:
    #ctx.forward(post_vote, comment_id=comment_id)
    ctx.invoke(post_vote, comment_id=comment_id, vote_type='pos', data_type='comment')
    xx = False
  if xx:
    ctx.invoke(post_vote, comment_id=comment_id, vote_type='neg')
  if favour:
    _add_favour(comment_id, category='comment')



@click.command()
@click.argument('page', required=False, default=1, type=int)
def article_list(page):
  r = start_request(ARTICLE_LIST.format(page))
  render_article_list(r)


@click.command()
@click.option('-s', '--silence', is_flag=True, help='hidden the comment list?')
@click.option('-f', '--favour', is_flag=True, help='favour it')
@click.argument('article_id', required=True, type=int)
def article_detail(article_id, silence, favour):
  r = start_request(ARTICLE_DETAIL.format(article_id))
  render_article_detail(r, silence)
  if favour:
    _add_favour(article_id, category='article')


@click.command()
@click.option('-e', '--email', required=False, type=str, help='your email, this usually need to be set at first post, then it will be store in the cache, only when you try to change it, you set it')
@click.option('-a', '--author', required=False, type=str, help='your nickname, this usually need to be set at first post, then it will be store in the cache, only when you try to change it, you set it')
@click.option('-c', '--content', required=True, help='the tucao content, you should quote it with \' or "')
@click.argument('comment_id', required=True, type=int, nargs=1)
def post_tucao(author, email, content, comment_id):
  last_user = get_userinfo(USER_CONFIG)
  data = {
    'content': content,
    'comment_id': comment_id
  }
  data = _make_user_info(author, email, data, last_user)
  if 'author' not in data or 'email' not in data:
    output.error(f'author and email must set')
    sys.exit(0)

  r = start_request(JD_TUCAO, headers=make_dict(HEADERS, 'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'), method='post', data=data)
  if 'code' in r and r['code'] == 0:
    output.succeed(f'tucao {r["msg"]}, [tucao_id] {r["data"]["comment_ID"]}, [author] {r["data"]["comment_author"]}')
  else:
    print(r)


@click.command()
@click.option('-e', '--email', required=False, type=str, help='your email, this usually need to be set at first post, then it will be store in the cache, only when you try to change it, you set it')
@click.option('-a', '--author', required=False, type=str, help='your nickname, this usually need to be set at first post, then it will be store in the cache, only when you try to change it, you set it')
@click.option('-c', '--comment', required=True, help='the comment content, you should quote it with \' or "')
@click.option('-t', '--category', required=False, type=click.Choice(COMMENT_CATEGORIES[0:9]), help='if your ignore it, post_id must be set')
@click.argument('post_id', required=False, default=0, type=int, nargs=1)
def post_comment(author, email, comment, category, post_id):
  data = {'comment': comment}
  last_user = get_userinfo(USER_CONFIG)
  data = _make_user_info(author, email, data, last_user)
  if 'author' not in data or 'email' not in data:
    output.error(f'author and email must set')
    sys.exit(0)

  if category:
    r = start_request(COMMENT_LIST.format(category))
    comment_post_ID = parse_post_id(r['text'])
  else:
    if post_id == 0:
      output.error('post_id must be an integer not equal 0', bold=True)
      sys.exit(0)
    comment_post_ID = post_id

  data['comment_post_ID'] = comment_post_ID

  r = start_request(JD_COMMENT, headers=make_dict(HEADERS, 'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'), method='post', data=data)
  if isinstance(r, int):
    output.succeed(f'post comment succeed, [comment_id] {r}')
  else:
    print(r)


@click.command()
@click.option('-v', '--vote_type', required=False, default='pos', type=click.Choice(['pos', 'neg']), help='choose vote type')
@click.option('-d', '--data_type', required=False, default='comment', type=click.Choice(['comment', 'tucao']), help='choose data type')
@click.argument('comment_id', required=True, type=int)
def post_vote(comment_id, vote_type, data_type):
  data = {
    'comment_id': comment_id,
    'vote_type': vote_type,
    'data_type': data_type
  }
  r = start_request(JD_VOTE, headers=make_dict(HEADERS, 'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'), method='post', data=data)
  print(r)


@click.command()
@click.option('-r', '--reason', required=True, default='test report', help='why report the comment?, you should quote it with \' or "')
@click.option('-a', '--action', required=False, default='report', help='the action, only support report now')
@click.option('-t', '--typo', required=False, default=1, help='when report comment, ignore it; when report tucao, pass it with any value not equal 1')
@click.argument('comment_id', required=True, type=int, nargs=1)
def post_report(comment_id, action, typo, reason):
  data = {
    'comment_id': comment_id,
    'action': action,
    'reason': reason
  }
  if typo == 1:
    data['type'] = 1
  r = start_request(JD_REPORT, headers=make_dict(HEADERS, 'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8'), method='post', data=data)
  print(r)


@click.command()
@click.option('-a', '--author', required=True, type=str, help='your nickname')
@click.option('-e', '--email', required=True, type=str, help='your email')
def set_user(author, email):
  user = {'author': author, 'email': email}
  set_userinfo(USER_CONFIG, user)
  output.info(f'user info setted, check {USER_CONFIG}')
  output.info(f'now while running command jandan-py post-tucao/post-comment, you may ignore option email/author')
  output.color_print(json.dumps(user), fg='green', bold=True)


@click.command()
@click.option('-r', '--remove', required=False, type=int, help='the id will be removed')
@click.option('-t', '--truncate', is_flag=True, help='truncate your favour list')
def my_favour(remove, truncate):
  if truncate:
    set_userinfo(USER_FAVOUR, {})
    output.warn('your favour list truncated!')
    sys.exit(0)

  data = get_json(USER_FAVOUR)
  if remove:
    k1 = f'article_{remove}'
    if k1 in data:
      del_json(USER_FAVOUR, k1)
      output.warn('{} {} removed'.format(k1.split('_')[0], remove))
      sys.exit(0)
    k2 = f'comment_{remove}'
    if k2 in data:
      del_json(USER_FAVOUR, k2)
      output.warn('{} {} removed'.format(k2.split('_')[0], remove))
      sys.exit(0)
  summary = {'comment': [], 'article': []}
  for key in data.keys():
    if key.startswith('comment'):
      summary['comment'].append(key[8:])
    elif key.startswith('article'):
      summary['article'].append(key[8:])
  output.info(f'your favour list summary below: \n')
  output.warn('[comment] total {}, [article] total {}'.format(len(summary['comment']), len(summary['article'])))
  output.succeed('comment list: {}'.format(', '.join(summary['comment'])))
  output.succeed('article list: {}'.format(', '.join(summary['article'])))
  output.color_print('\n you can view article via: jandan-py article-detail [article_id]\n view comment via: jandan-py comment-detail [comment_id]', fg='blue', bold=True)


def _init():
  if not os.path.isdir(IMAGE_PATH):
    os.makedirs(IMAGE_PATH)


def _add_favour(id, category='comment'):
  key = f'{category}_{id}'
  set_json(USER_FAVOUR, {key: 1})
  output.succeed(f'{category} {id} favoured')


def _make_user_info(author, email, data={}, user={}):
  if email:
    data['email'] = email
    user['email'] = email
  else:
    if 'email' in user:
      data['email'] = user['email']

  if author:
    data['author'] = author
    user['author'] = author
  else:
    if 'author' in user:
      data['author'] = user['author']

  set_userinfo(USER_CONFIG, user)
  return data


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def run():
  _init()


run.add_command(article_list)
run.add_command(article_detail)
run.add_command(comment_list)
run.add_command(comment_detail)
run.add_command(post_report)
run.add_command(post_vote)
run.add_command(post_comment)
run.add_command(post_tucao)
run.add_command(set_user)
run.add_command(my_favour)


if __name__ == '__main__':
    run()
