'''
html parser to extract data
'''
import re
from collections import namedtuple
from requests_html import HTML

Tag = namedtuple('Tag', ['type', 'value', 'link'])


def parse_item(text):
    '''
    Args:
        text : str - html text

    Returns:
        tuple: (dict, list)
        dict - meta data for this item
        list - tags for this item
    '''
    html = HTML(html=text)
    title_css = 'body > div.container > h3'
    title = html.find(title_css)[0].text
    cover_img_css = 'body > div.container > div.row.movie > div.col-md-9.screencap > a'
    cover_img_url = html.find(cover_img_css)[0].attrs['href']
    tags_css = 'body > div.container > div.row.movie > div.col-md-3.info'
    tags = html.find(tags_css)[0].find('p')
    add_date = tags[1].text
    length = tags[2].text
    # meta data
    meta = {}
    meta['fanhao'], meta['title'] = title.split(maxsplit=1)
    meta['cover_img_url'] = cover_img_url
    meta['add_date'] = add_date.split()[1]
    meta['length'] = re.search(r'\d+', length).group()

    tag_list = []
    for tag in tags[3:]:
        tag_type = ''
        tag_value = ''
        tag_link = ''
        links = tag.find('a')
        if links and len(links) == 1:
            spans = tag.find('span')
            if spans:
                tag_type = (spans[0].text)
                tag_link = links[0].attrs['href']
                tag_value = links[0].text
        else:
            for link in links:
                tag_link = links[0].attrs['href']
                tag_value = links[0].text
        if 'genre' in tag_link:
            tag_type = 'genre'
        if 'star' in tag_link:
            tag_type = 'star'
        if tag_type != '' and tag_value != '':
            tag_list.append(Tag(tag_type, tag_value, tag_link))
    return meta, tag_list
