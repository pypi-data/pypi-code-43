# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.objects import Context
from suanpan.utils import env

g = Context(
    # App
    appType=env.get("SP_APP_TYPE", required=True),
    appParams=env.get("SP_PARAM", default=""),
    nodeInfo=env.get("SP_NODE_INFO", default=""),
    userId=env.get("SP_USER_ID", required=True),
    appId=env.get("SP_APP_ID", required=True),
    nodeId=env.get("SP_NODE_ID", required=True),
    nodeGroup=env.get("SP_NODE_GROUP", default="default"),
    # Api
    host=env.get("SP_HOST", required=True),
    hostTls=env.get("SP_HOST_TLS", type=env.bool, default=False),
    apiHost=env.get("SP_API_HOST", required=True),
    apiHostTls=env.get("SP_API_HOST_TLS", type=env.bool, default=False),
    affinity=env.get("SP_AFFINITY"),
    accessKey=env.get("SP_ACCESS_KEY", required=True),
    accessSecret=env.get("SP_ACCESS_SECRET", required=True),
    userIdHeaderField=env.get("SP_USER_ID_HEADER_FIELD", default="x-sp-user-id"),
    userSignatureHeaderField=env.get(
        "SP_USER_SIGNATURE_HEADER_FIELD", default="x-sp-signature"
    ),
    userSignVersionHeaderField=env.get(
        "SP_USER_SIGN_VERSION_HEADER_FIELD", default="x-sp-sign-version"
    ),
    # Screenshots
    screenshotsType=env.get("SP_SCREENSHOTS_TYPE", default="index"),
    screenshotsPattern=env.get("SP_SCREENSHOTS_PATTERN"),
    screenshotsStorageKey=env.get("SP_SCREENSHOTS_STORAGE_KEY"),
    screenshotsThumbnailStorageKey=env.get("SP_SCREENSHOTS_THUMBNAIL_STORAGE_KEY"),
)
