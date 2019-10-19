from django import template

from juntagrico_webdav.dao.webdavserverdao import WebdavServerDao

register = template.Library()


@register.simple_tag
def admin_menu():
    return WebdavServerDao.active_admin_servers()

@register.simple_tag
def user_menu():
    return WebdavServerDao.active_user_servers()