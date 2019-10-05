# -*- coding: UTF-8 –*-

import os
import time

from lofter_utils.TagDownloader import downloadTag


def download_line(line, add_file_timestamp=False, output_dir='.'):
    line = line.replace('\r', '')
    line = line.replace('\n', '')
    allTypes = ['new', 'total', 'mouth', 'week', 'date']
    print('开始下载line: "%s".' % line)
    params = line.split('\t')
    for i in range(4 - len(params)):
        params.append(None)
    tag, types, limit, offset = params
    if tag == None:
        print('跳过空行')
        return
    if types == None:
        types = allTypes
    else:
        types = types.split(',')
    if limit == None:
        limit = 500
    else:
        limit = int(limit)
    if offset == None:
        offset = 0
    else:
        offset = int(offset)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for type in types:
        try:
            pages = downloadTag(tag, type, limit, offset)
        except Exception as e:
            print('下载pages出错: tag = %s, type = %d, limit = %d, offset = %d' % (tag, type, limit, offset))
            print(e)
            continue
        for page in pages:
            filename = 'tag_%s_type_%s_limit_%s_offset_%s.tag' % (
                page['tag'], page['type'], page['limit'], page['offset'])
            if add_file_timestamp:
                tmp_1 = os.path.splitext(filename)
                timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
                filename = tmp_1[0] + '_' + timestamp + tmp_1[1]
            filename = os.path.join(output_dir, filename)
            with open(filename, 'wb') as f:
                f.write(page['body'])


def download_file(filename, add_dir_timestamp=False, add_file_timestamp=False, output_dir=None):
    print('开始下载taglist文件: "%s".' % filename)
    tmp_1 = os.path.splitext(filename)
    if tmp_1[1] == '.' + 'taglist':
        out_dir = tmp_1[0]
    else:
        out_dir = filename
    if output_dir != None:
        out_dir = output_dir
    if add_dir_timestamp:
        timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        out_dir = out_dir + '_' + timestamp
    with open(filename, encoding='utf8') as f:
        for line in f:
            try:
                download_line(line, add_file_timestamp=add_file_timestamp, output_dir=out_dir)
            except Exception as e:
                print('下载line时出错')
                print(e)
                continue
    print('taglist文件中tag已下载至: "%s"' % out_dir)


def download_dir(dirname, tool, add_dir_timestamp=False, add_file_timestamp=False, output_dir=None):
    print('开始下载taglist目录: "%s".' % dirname)
    for filename in os.listdir(dirname):
        filename = os.path.join(dirname, filename)
        if not os.path.isfile(filename):
            continue
        if os.path.splitext(filename)[1] != '.' + 'taglist':
            continue
        download_file(filename, add_dir_timestamp=add_dir_timestamp, add_file_timestamp=add_file_timestamp,
                      output_dir=output_dir)
    print('taglist目录中taglist文件已下载至: "%s"' % dirname)
