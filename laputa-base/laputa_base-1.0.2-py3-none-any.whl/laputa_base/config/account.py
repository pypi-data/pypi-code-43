# !/usr/bin/env python3
# coding=utf-8
"""
Copyright (C) 2016-2019 Zhiyang Liu in Software Development of NIO/NEXTEV) All rights reserved.
Author: zhiyang.liu.o@nio.com
Date: 2019-05-20

History:
---------------------------------------------
Modified            Author              Content
"""
import getpass
import os
import platform
import sys

"""
account调用方法（尽量将账号的调用封装到函数中，脚本只传用户身份：owner/share/fans等等）
参考下面范例：
from src.config.account import account
def log_in(self, user='owner'):
    user_info = account[self.i][user]
    user_info['phone']  # 取phone值
    user_info['code']  # 取code值
脚本内使用  #  脚本内account已进行了实例化
    self.account['owner']['name']
"""
if os.getenv('BUILD_URL') is None:
    if getpass.getuser() == 'long.li1.o':  # 邮箱前缀
        account = [  # 个人调试账号
            {  # used by LiLong
                'owner': {
                    'phone': 98762397957,
                    'code': 912463,
                    'name': '98762397957',
                    'idnum': '342221199309026027',
                    'pin': 930902
                },
                'friend': {
                    'phone': 98762397619,
                    'code': 234671,
                    'name': '98762397619'
                },
                'fans': {
                    'phone': 98762397620,
                    'code': 745389,
                    'name': '98762397620'
                },
                'nolight': {
                    'phone': 98762397717,
                    'code': 738495,
                    'name': '98762397717',
                    'idnum': '110101199909092444',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398010,
                    'code': 689271,
                    'name': '98762398010',
                    'idnum': '110101199006106390',
                    'pin': 112233
                },
                'order': {
                    'phone': 98762398009,
                    'code': 371649,
                    'name': '98762398009',
                    'idnum': '110101199006109831',
                    'pin': 112233
                },
                'zero': {
                    'phone': 98762397731,
                    'code': 256417,
                    'name': '98762397731'
                }
            },
            {
                'owner': {
                    'phone': 98762397078,
                    'code': 938512,
                    'name': '97078',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345692,
                    'code': 112233,
                    'name': '98762345692'
                },
                'fans': {
                    'phone': 98762345893,
                    'code': 112233,
                    'name': '893fans'
                },
                'nolight': {
                    'phone': 98762398047,
                    'code': 348756,
                    'name': '8047',
                    'idnum': '110101199010064998',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398036,
                    'code': 748136,
                    'name': '8036',
                    'idnum': '110101198903070450',
                    'pin': 112233,
                    'account_id': '538450670'
                },
                'order': {
                    'phone': 98762398032,
                    'code': 396718,
                    'name': '8032',
                },
                'zero': {
                    'phone': 98762397500,
                    'code': 985612,
                    'name': '蔚来用户'
                }
            }
        ]
    elif getpass.getuser() in ('zhiyang.liu.o', 'jenkins'):
        account = [
            {
                'owner': {
                    'phone': 98762397072,
                    'code': 876532,
                    'name': '97072',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762398654,
                    'code': 176593,
                    'name': '98762398654'
                },
                'fans': {
                    'phone': 98762345890,
                    'code': 112233,
                    'name': '890fans'
                },
                'nolight': {
                    'phone': 98762398045,
                    'code': 267348,
                    'name': '8045',
                    'idnum': '110101199010069633',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398035,
                    'code': 253897,
                    'name': '8035',
                    'idnum': '110101198903078532'
                },
                'order': {
                    'phone': 98762398031,
                    'code': 412986,
                    'name': '8031',
                },
                'zero': {
                    'phone': 98762345890,
                    'code': 112233,
                    'name': '890fans'
                }
            }]
    elif getpass.getuser() == 'jun.yan.o':
        account = [
            {
                'owner': {
                    'phone': 98762397078,
                    'code': 938512,
                    'name': '97078',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345692,
                    'code': 112233,
                    'name': '98762345692'
                },
                'fans': {
                    'phone': 98762345893,
                    'code': 112233,
                    'name': '893fans'
                },
                'nolight': {
                    'phone': 98762398047,
                    'code': 348756,
                    'name': '8047',
                    'idnum': '110101199010064998',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398036,
                    'code': 748136,
                    'name': '8036',
                    'idnum': '110101198903070450',
                    'pin': 112233,
                    'account_id': '538450670'
                },
                'order': {
                    'phone': 98762398032,
                    'code': 396718,
                    'name': '8032',
                },
                'zero': {
                    'phone': 98762397500,
                    'code': 985612,
                    'name': '蔚来用户'
                }
            }
        ]
    else:
        print('需添加个人账号信息')
else:
    # 二次确认，只有在通过test_run.py 启动测试时 且结果需要收录至服务器时才会使用以下账号
    # 如需区分mac和linux测试环境用 platform.system() == 'Darwin' 做为mac分支
    if platform.system() == 'Darwin':
        if getpass.getuser() == 'long.li1.o':  # 邮箱前缀
            account = [  # 个人调试账号
                {  # used by LiLong
                    'owner': {
                        'phone': 98762397957,
                        'code': 912463,
                        'name': '98762397957',
                        'idnum': '342221199309026027',
                        'pin': 930902
                    },
                    'friend': {
                        'phone': 98762397619,
                        'code': 234671,
                        'name': '98762397619'
                    },
                    'fans': {
                        'phone': 98762397620,
                        'code': 745389,
                        'name': '98762397620'
                    },
                    'nolight': {
                        'phone': 98762397717,
                        'code': 738495,
                        'name': '98762397717',
                        'idnum': '110101199909092444',
                        'pin': 112233
                    },
                    'share': {
                        'phone': 98762398010,
                        'code': 689271,
                        'name': '98762398010',
                        'idnum': '110101199006106390',
                        'pin': 112233
                    },
                    'order': {
                        'phone': 98762398009,
                        'code': 371649,
                        'name': '98762398009',
                        'idnum': '110101199006109831',
                        'pin': 112233
                    },
                    'zero': {
                        'phone': 98762397731,
                        'code': 256417,
                        'name': '98762397731'
                    }
                },
                {
                    'owner': {
                        'phone': 98762397078,
                        'code': 938512,
                        'name': '97078',
                        'idnum': '110101199003076851',
                        'pin': 112233
                    },
                    'friend': {
                        'phone': 98762345692,
                        'code': 112233,
                        'name': '98762345692'
                    },
                    'fans': {
                        'phone': 98762345893,
                        'code': 112233,
                        'name': '893fans'
                    },
                    'nolight': {
                        'phone': 98762398047,
                        'code': 348756,
                        'name': '8047',
                        'idnum': '110101199010064998',
                        'pin': 112233
                    },
                    'share': {
                        'phone': 98762398036,
                        'code': 748136,
                        'name': '8036',
                        'idnum': '110101198903070450',
                        'pin': 112233,
                        'account_id': '538450670'
                    },
                    'order': {
                        'phone': 98762398032,
                        'code': 396718,
                        'name': '8032',
                    },
                    'zero': {
                        'phone': 98762397500,
                        'code': 985612,
                        'name': '蔚来用户'
                    }
                }
            ]
    else:
        account = [  # jenkins 测试账号
            {
                'owner': {
                    'phone': 98762397076,
                    'code': 321568,
                    'name': '97076',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762398029,
                    'code': 359681,
                    'name': '98762398029'
                },
                'fans': {
                    'phone': 98762398030,
                    'code': 314672,
                    'name': '98762398030'
                },
                'nolight': {
                    'phone': 98762398050,
                    'code': 539281,
                    'name': '8050',
                    'idnum': '110101199909092444',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398042,
                    'code': 982365,
                    'name': '8042',
                    'idnum': '110101199003080535',
                    'pin': 112233,
                    'account_id': '79973684'
                },
                'order': {
                    'phone': 98762398034,
                    'code': 429857,
                    'name': '8034'
                },
                'zero': {
                    'phone': 98762397504,
                    'code': 569278,
                    'name': '98762397504'
                }
            },
            {
                'owner': {
                    'phone': 98762397468,
                    'code': 495127,
                    'name': '97468',
                    'idnum': '112233',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345706,
                    'code': 112233,
                    'name': '98762345706'
                },
                'fans': {
                    'phone': 98762403308,
                    'code': 236497,
                    'name': '308fans'
                },
                'nolight': {
                    'phone': 98762398058,
                    'code': 649185,
                    'name': '8058',
                    'idnum': '110101199909092444',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398043,
                    'code': 647281,
                    'name': '8043',
                    'idnum': '110101199003081677',
                    'pin': 112233,
                    'account_id': '1259829602'
                },
                'order': {
                    'phone': 98762397735,
                    'code': 721549,
                    'name': '98762397735'
                },
                'zero': {
                    'phone': 98762397505,
                    'code': 614538,
                    'name': '7505'
                }
            },
            {
                'owner': {
                    'phone': 98762397075,
                    'code': 185392,
                    'name': '蔚来用户97075',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345695,
                    'code': 112233,
                    'name': '98762345695'
                },
                'fans': {
                    'phone': 98762345895,
                    'code': 112233,
                    'name': '895fans'
                },
                'nolight': {
                    'phone': 98762398048,
                    'code': 683957,
                    'name': '8048',
                    'idnum': '110101199909092444',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398041,
                    'code': 983452,
                    'name': '8041',
                    'idnum': '110101199003080535',
                    'pin': 112233,
                    'account_id': '1035975493'
                },
                'order': {
                    'phone': 98762397733,
                    'code': 625341,
                    'name': '98762397733'
                },
                'zero': {
                    'phone': 98762397503,
                    'code': 175842,
                    'name': '7503'
                }
            },
            {
                'owner': {
                    'phone': 98762397074,
                    'code': 231479,
                    'name': '97074',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345694,
                    'code': 112233,
                    'name': '98762345694'
                },
                'fans': {
                    'phone': 98762345894,
                    'code': 112233,
                    'name': '894fans'
                },
                'nolight': {
                    'phone': 98762398046,
                    'code': 642158,
                    'name': '8046',
                    'idnum': '110101199909092444',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398040,
                    'code': 619845,
                    'name': '8040',
                    'idnum': '110101199003083357',
                    'pin': 112233,
                    'account_id': '1831010550'
                },
                'order': {
                    'phone': 98762397732,
                    'code': 358649,
                    'name': '98762397732'
                },
                'zero': {
                    'phone': 98762397502,
                    'code': 724593,
                    'name': '7502'
                }
            },
            {
                'owner': {
                    'phone': 98762397073,
                    'code': 926874,
                    'name': '97073',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762345690,
                    'code': 112233,
                    'name': '98762345690'
                },
                'fans': {
                    'phone': 98762345891,
                    'code': 112233,
                    'name': '891fans'
                },
                'nolight': {
                    'phone': 98762398059,
                    'code': 493176,
                    'name': '8059',
                    'idnum': '110101199010060719',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398039,
                    'code': 832574,
                    'name': '8039',
                    'idnum': '110101198903079375',
                    'pin': 112233,
                    'account_id': '549055017'
                },
                'order': {
                    'phone': 98762397730,
                    'code': 816493,
                    'name': '98762397730'
                },
                'zero': {
                    'phone': 98762397501,
                    'code': 869513,
                    'name': '7501'
                }
            },
            {
                'owner': {
                    'phone': 98762397001,
                    'code': 361278,
                    'name': '点亮中国-车主',
                    'idnum': '130102199003077256',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762398656,
                    'code': 531869,
                    'name': '98762398656'
                },
                'fans': {
                    'phone': 98762345896,
                    'code': 112233,
                    'name': '896fans'
                },
                'nolight': {
                    'phone': 98762398051,
                    'code': 162578,
                    'name': '8051',
                    'idnum': '110101199010065755',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398038,
                    'code': 534782,
                    'name': '8038',
                    'idnum': '110101198903070135',
                    'pin': 112233,
                    'account_id': '2088662367'
                },
                'order': {
                    'phone': 98762398033,
                    'code': 692784,
                    'name': '8033'
                },
                'zero': {
                    'phone': 98762397499,
                    'code': 457398,
                    'name': '7499'
                }
            },
            {
                'owner': {
                    'phone': 98762397077,
                    'code': 276493,
                    'name': '97077',
                    'idnum': '110101199003076851',
                    'pin': 112233
                },
                'friend': {
                    'phone': 98762398655,
                    'code': 349861,
                    'name': '998762398655'
                },
                'fans': {
                    'phone': 98762345892,
                    'code': 112233,
                    'name': '892fans'
                },
                'nolight': {
                    'phone': 98762398049,
                    'code': 176349,
                    'name': '8049',
                    'idnum': '110101199010066299',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398037,
                    'code': 468179,
                    'name': '8037',
                    'idnum': '110101198903071613',
                    'pin': 112233,
                    'account_id': '554763828'
                },
                'order': {
                    'phone': 98762397618,
                    'code': 573298,
                    'name': '98762397618',
                },
                'zero': {
                    'phone': 98762397498,
                    'code': 371425,
                    'name': '97498'
                }
            },
            {
                'owner': {
                    'phone': 98762397078,
                    'code': 938512,
                    'name': '97078',
                    'idnum': '110101199003076851',
                    'pin': 332211
                },
                'friend': {
                    'phone': 98762345692,
                    'code': 112233,
                    'name': '98762345692'
                },
                'fans': {
                    'phone': 98762345893,
                    'code': 112233,
                    'name': '893fans'
                },
                'nolight': {
                    'phone': 98762398047,
                    'code': 348756,
                    'name': '8047',
                    'idnum': '110101199010064998',
                    'pin': 112233
                },
                'share': {
                    'phone': 98762398036,
                    'code': 748136,
                    'name': '8036',
                    'idnum': '110101198903070450',
                    'pin': 112233,
                    'account_id': '538450670'
                },
                'order': {
                    'phone': 98762398032,
                    'code': 396718,
                    'name': '8032',
                },
                'zero': {
                    'phone': 98762397500,
                    'code': 985612,
                    'name': '蔚来用户'
                }
            },
        ]
# else:
#     print('个人调试请删除"BUILD_URL"环境变量')
