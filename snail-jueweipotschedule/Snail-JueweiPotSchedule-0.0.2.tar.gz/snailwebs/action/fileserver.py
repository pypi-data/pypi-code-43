import os
import re
import time
from flask import Blueprint, request

fileserver = Blueprint('fileserver', __name__)


@fileserver.route('/upload', methods=['POST'])
def upload():
    tempfile = request.files.get('file')  # 获取上传的文件

    date = None

    if tempfile:
        root = os.path.dirname(__file__) + '/../../data/schedule'

        if not os.path.exists(root):
            os.makedirs(root)

        old_fname = tempfile.filename

        m = re.search(r'\d{8}', old_fname)

        if m:
            date = m.group()
        else:
            m = re.search(r'\d{4}\-\d{1,2}\-\d{1,2}', old_fname)

            if m:
                date = m.group()
                date = time.strftime('%Y%m%d', time.strptime(date, '%Y-%m-%d'))

        if not date:
            date = time.strftime('%Y%m%d')

        new_fname = root + '/DATA_' + date + '.' + old_fname.rsplit('.', 1)[-1]

        if os.path.exists(new_fname):
            os.remove(new_fname)

        tempfile.save(new_fname)  # 保存文件到指定路径

        return '{"code": "200", "data": "' + date + '", "message":"上传成功"}'
    else:
        return '{"code": "403", "data": null, "message":"无效"}'
