# -*- coding: UTF-8 –*-
import os
import re
from bs4 import BeautifulSoup

from lofter_utils.TagConverter import processPage


def processTagFileList(filenames):
    res = {}
    for filename in filenames:
        filename = os.path.split(filename)[1]
        subFilename = re.match(r"^tag_(.+)_type_(.+)_limit_(\d+)_offset_(\d+)(_.*)?\.tag", filename)
        tag = subFilename.group(1)
        type = subFilename.group(2)
        limit = int(subFilename.group(3))
        offset = int(subFilename.group(4))
        suffix = subFilename.group(5)
        key = (tag, type, limit, suffix)
        if not key in res:
            value = []
            res[key] = value
        else:
            value = res[key]
        value.append(offset)
        res[key] = value
    for key in res:
        res[key].sort()
    return res


def isTagFile(filename):
    if not os.path.isfile(filename):
        return False
    if os.path.splitext(filename)[1] != '.tag':
        return False
    return True


def writeArticlesToFile(articles, f):
    for article in articles:
        blogPageUrl = article['blogPageUrl']
        blogPageUrl = '# ' + blogPageUrl + '\r\n'
        f.write(blogPageUrl.encode('utf-8'))
        title = article['title']
        try:
            title += '\r\n'
            title = title.encode('utf-8').decode("raw_unicode_escape").encode('utf-16', 'surrogatepass').decode('utf-16')
            f.write(title.encode('utf-8'))
        except Exception as e:
            print('title转码出现问题')
            print(e)
            f.write('title转码出现问题\r\n'.encode('utf-8'))
            continue
        content = article['content']
        try:
            content += '\r\n'
            content = content.encode('utf-8').decode("raw_unicode_escape").encode('utf-16', 'surrogatepass').decode('utf-16')
            content = BeautifulSoup(content, 'html.parser').prettify()
            f.write(content.encode('utf-8'))
        except Exception as e:
            print('content转码出现问题')
            print(e)
            f.write('content转码出现问题\r\n'.encode('utf-8'))
            continue


def convert_file(filename, output_dir=None):
    print('开始转换文件: "%s".' % filename)
    # Determine output file name
    tmp_1 = os.path.splitext(filename)
    if tmp_1[1] == '.' + 'taglist':
        out_filename = tmp_1[0] + '.' + 'txt'
    else:
        out_filename = filename + '.' + 'txt'
    if output_dir != None:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        out_filename = os.path.join(output_dir, os.path.split(out_filename)[1])
    with open(out_filename, 'w', encoding='utf-8', errors='surrogatepass') as out_f:
        with open(filename, 'r', encoding='utf-8') as f:
            str = f.read()
            articles = processPage(str)
            writeArticlesToFile(articles, out_f)


def convert_dir(dir, output_dir=None):
    filenames = os.listdir(dir)
    filenames = map(lambda x: os.path.join(dir, x), filenames)
    filenames = filter(isTagFile, filenames)
    fileTypeList = processTagFileList(filenames)
    for key in fileTypeList:
        print(key)
        tag, type, limit, suffix = key
        if suffix == None:
            suffix = ''
        out_filename = 'tag_%s_type_%s_limit_%d%s.txt' % (tag, type, limit, suffix)
        out_filename = os.path.join(dir, out_filename)
        print('outFilename = %s' % out_filename)
        with open(out_filename, 'wb') as out_f:
            for offset in fileTypeList[key]:
                in_filename = 'tag_%s_type_%s_limit_%d_offset_%d%s.tag' % (tag, type, limit, offset, suffix)
                in_filename = os.path.join(dir, in_filename)
                print('in_filename = %s' % in_filename)
                with open(in_filename, 'r', encoding='utf-8') as in_f:
                    str = in_f.read()
                    articles = processPage(str)
                    writeArticlesToFile(articles, out_f)
