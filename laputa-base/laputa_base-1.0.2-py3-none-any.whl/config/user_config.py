import getpass
import os
import platform
import sys

android_url = 'http://10.110.1.169/lifestyle/android/lifestyle_rn_shopping' \
              '/dev/20191012/lifestyle_release_v3.9.9_dev_20191012-173736_ef72ab299_vmp.png'
ios_url = 'http://10.110.1.169/lifestyle/ios/master/20190926/lifestyle_3.9.7_20190926-175106_53c664a-test.ipa'

# module 内容范围：'all','基础功能','车辆控制','购车','车商城附件','充电地图','一键加电','专属桩','SO','Debug','我的订单','惊喜','SCR'
module_select = ['基础功能', '朋友']

# priority 内容范围：'P0', 'P1', 'P2', 'P3'
priority_select = ['P0']

# page 内容范围：'发现', '朋友', '爱车', '惊喜', '我的'
page_select = ['发现', '朋友', '爱车', '惊喜', '我的']

# 执行测试类型：Release:结果上传，Debug:本地调试
build_type = 'Debug'

# 测试环境：STG，TEST
test_env = 'STG'

# 要求标题带有 ios 或 android 字段
result_file_name = 'NIO_APP_%s_Function_Test' % ('Android' if 'android' in os.path.abspath(sys.argv[0]).lower() else 'IOS')


if getpass.getuser() == 'jenkins' and platform.system() == 'Linux':
    # android 测试 linux服务器 jenkins触发执行时，部分环境变量无法在脚本中生效，需要手动指定路径
    adb_path = '/opt/android-sdk-linux/platform-tools/adb'
    allure_path = '/home/jenkins/.nvm/versions/node/v11.6.0/bin/allure'
    appium_path = '/home/jenkins/.nvm/versions/node/v11.6.0/bin/appium'
else:
    adb_path = 'adb'
    allure_path = 'allure'
    appium_path = 'appium'

# 需不断起driver的手机udid
re_udid = [
    '86bcaaf',
    'dc3d5227',
    '1fc020ee',
    'KVBYQ4R4WSUGQORG',
    'SCHUAQDES4OZ457T'
]
