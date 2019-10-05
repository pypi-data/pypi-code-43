# -*- coding: UTF-8 –*-

import re
import os


def processPage(page):
    print('processPage()')
    blocks = page.split('\n\n')
    print('len(blocks) = %d' % len(blocks))
    articles = []
    i = 0
    for block in blocks:
        article = {}
        blogPageUrls = re.findall(r'\.blogPageUrl="(.+?)(?<!\\)"', block)
        if len(blogPageUrls) == 0:
            hasBlogPageUrls = False
            print('block[i], i = %d' % i)
            blogPageUrl = 'blogPageUrl未找到'
            print(blogPageUrl)
            print(block)
        else:
            hasBlogPageUrls = True
            blogPageUrl = blogPageUrls[0]
        contents = re.findall(r'\.content="(?:(.+?)(?<!\\))?"', block)
        if len(contents) == 0:
            hasContents = False
            print('block[i], i = %d' % i)
            content = 'content未找到'
            print(content)
            print(block)
        else:
            hasContents = True
            content = contents[0]
        if (not hasBlogPageUrls) and (not hasContents):
            continue
        title = re.findall(r'\.title="(?:(.+?)(?<!\\))?"', block)
        if len(title) == 0:
            hasTitle = False
            print('block[i], i = %d' % i)
            title = 'title未找到'
            print(title)
            print(block)
        else:
            hasTitle = True
            title = title[0]
        article['blogPageUrl'] = blogPageUrl
        article['content'] = content
        article['title'] = title
        articles.append(article)
        i += 1
    return articles


def processTagFileList(filenames):
    res = {}
    for filename in filenames:
        subFilename = re.match(r"^tag_(.+)_type_(.+)_limit_(\d+)_offset_(\d+)\.tag", filename)
        tag = subFilename.group(1)
        type = subFilename.group(2)
        limit = int(subFilename.group(3))
        offset = int(subFilename.group(4))
        key = (tag, type, limit)
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
