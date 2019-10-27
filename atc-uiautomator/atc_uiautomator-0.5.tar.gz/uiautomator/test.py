#coding=utf-8
from uiautomator import device as d
import time


# d.watcher("auto_yunxu").when(packageName='com.android.systemui').when(text="允许").click(text="允许")
# # d.watcher("auto_yunxu").when(packageName='com.android.systemui').when(text="允许").click(text="允许")
# # print "ffff"
# print d.watchers
# # d.watchers.remove()
# print d.watchers
print d.getPhoneInfo(1)
print d.checkPermission('android.permission.READ_SMS')
print d.getSmsInfo(1)

# print d.jumpAppDetail("com.github.uiautomator")



