# -*- coding: utf-8 -*-
import os

class _GenConst(object):
  def __init__(self, name):
    self._name = name

  def __repr__(self):
    return u'<const: {}>'.format(self._name)

  def __str__(self):
    return self._name


KEY_UP = _GenConst('↑')
KEY_DOWN = _GenConst('↓')

KEY_CTRL_C = _GenConst('Ctrl+C')
KEY_CTRL_N = _GenConst('Ctrl+N')
KEY_CTRL_P = _GenConst('Ctrl+P')

KEY_MAPPING = {
  '\x0e': KEY_CTRL_N,
  '\x03': KEY_CTRL_C,
  '\x10': KEY_CTRL_P
}

IMAGE_PATH = os.getenv('IMAGE_PATH', './jandan_cache')

USER_CONFIG = IMAGE_PATH + '/user.json'

USER_FAVOUR = IMAGE_PATH + '/favour.json'

JD_URL = 'http://i.jandan.net'

JD_API_KEY = 'oxwlxojflwblxbsapi'

MOYU_API = 'http://api.moyu.today/jandan/hot?category={}'

MOYU_CATEGORIES = [
  'recent',
  'week',
  'picture',
  'comment',
  'joke',
  'ooxx'
]

API_CATEGORIES = [
  'ooxx',
  'pic',
  'duan'
]

COMMENT_CATEGORIES = [
  'ooxx',
  'pic',
  'treehole',
  'qa',
  'zoo',
  'zhoubian',
  'pond',
  'faq',
  'app',
  'top',
  'top-4h',
  'top-tucao',
  'top-ooxx',
  'top-zoo',
  'top-comments',
  'top-3days',
  'top-7days'
]


ARTICLE_LIST = JD_URL + '/?' + JD_API_KEY + '=get_recent_posts&page={}'

ARTICLE_DETAIL = JD_URL + '/?' + JD_API_KEY + '=get_post&id={}'

CATEGORY_LIST = JD_URL + '/?' + JD_API_KEY + '=jandan.get_{}_comments&page={}'

TUCAO_LIST = JD_URL + '/tucao/{}'

COMMENT_LIST = JD_URL + '/{}'

COMMENT_DETAIL = JD_URL + '/t/{}'

JD_COMMENT = JD_URL + '/jandan-comment.php'

JD_TUCAO = JD_URL + '/jandan-tucao.php'

JD_VOTE = JD_URL + '/api/comment/vote'

JD_REPORT = JD_URL + '/api/report/comment'

HEADERS = {
  'User-Agent': 'Jandan Android App V5.1.0.2',
  'Host': JD_URL[7:],
  'Referer': JD_URL
}