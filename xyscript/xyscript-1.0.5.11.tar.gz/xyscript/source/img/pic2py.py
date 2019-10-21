#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
 
def pic2py(picture_name):
    """
    将图像文件转换为py文件
    :param picture_name:
    :return:
    """
    open_pic = open("%s" % picture_name, 'rb')
    b64str = base64.b64encode(open_pic.read())
    open_pic.close()
    # 注意这边b64str一定要加上.decode()
    write_data = '%s = "%s"' % ((picture_name.split('.')[0]).split('/')[-1],b64str.decode())
    f = open('/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/img/image.py', 'r+')
    date = f.read()
    f = open('/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/img/image.py', 'w+')
    f.write(date + '\n\r' + write_data)
    f.close()
 
if __name__ == '__main__':
    pics = ["/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/img/jsonfileicon.png"]
    for i in pics:
        pic2py(i)
