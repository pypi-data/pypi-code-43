import logging

log = logging.getLogger("django")

from django.contrib.auth.backends import ModelBackend
from . import helper

class WeiXinBackend(ModelBackend):
    """
    Custom auth backend that uses an email address and password

    For this to work, the User model must have an 'email' field
    """

    def authenticate(self, code):
        md = helper.api.login(code)
        if 'errcode' in md:
            if not md['errcode'] in [40029, 40163]:  # errmsg: invalid code , code been used
                log.error("WeiXinBackend.authenticate error, data: %s" % md)
            return
        try:
            user = helper.api.get_or_create_user(md).user
            setattr(user, 'login_type', 'wechat.mp')
            return user
        except Exception, e:
            import traceback
            log.error("WeiXinBackend.authenticate error, data: %s; traceback: %s", md, traceback.format_exc())
