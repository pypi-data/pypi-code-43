#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########
##  Springheel - Comic Navigation Block Generation
########
##  Copyright 2017 garrick. Some rights reserved.
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.

##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU Lesser General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.

import springheel.parseconf, springheel.parsemeta
from springheel.__init__ import logMsg

class Arrow:
    def __init__(self, relation, page):
        self.relation = relation
        self.page = page

## Generate navigation boxes and link rel navigation.
def navGen(navdirection,zero_padding,scrollto,page_int,first_page,last_page,first,final,series_slug,site_style,translated_strings):

    strips = range(1,(last_page+1))
    if page_int not in strips:
        logmesg = """Building failed! Navigation could not be built because {page_int} is an invalid page number. The .meta value "page" may have been set to something incorrect, or the scan may have failed to detect a comic. Please double-check.""".format(page_int=page_int)
        print(logmesg)
        logMsg(logmesg,".")

    if page_int == last_page:
        final = True
    elif page_int == 1:
        first = True
    if zero_padding == False:
        first_page = str(first_page)
        last_page = str(last_page)
    else:
        first_page = "{page:0{zero_padding}}".format(page=first_page,zero_padding=zero_padding)
        last_page = "{page:0{zero_padding}}".format(page=last_page,zero_padding=zero_padding)

    first_s = translated_strings["first_s"]
    prev_s = translated_strings["prev_s"]
    next_s = translated_strings["next_s"]
    last_s = translated_strings["last_s"]
    home_s = translated_strings["home_s"]

    firsts_s = translated_strings["firsts_s"]
    prevs_s = translated_strings["prevs_s"]
    nexts_s = translated_strings["nexts_s"]
    lasts_s = translated_strings["lasts_s"]

    navl = [' <ul class="cominavbox">']
    linkl = ['<link rel="alternate" type="application/rss+xml" title="RSS" href="feed.xml">']

    image_template = """<li><a href="{series_slug}_{page}.html#{scrollto}"><img src="arrows/{site_style}_{relation}.png" alt="{image_long_string}" /><br/>{image_short_string}</a></li>"""
    linkrel_template = """<link rel="{relation}" href="{series_slug}_{page}.html" title="{page_string}">"""
        
    navl = [' <ul class="cominavbox">']
    linkl = ['<link rel="alternate" type="application/rss+xml" title="RSS" href="feed.xml">']
    relations = []
    if not first:
        fd = {"rel":"first","page":first_page}
        relations.append(fd)
        if zero_padding == False:
            prev_page = str(page_int-1)
        else:
            prev_page = "{page:0{zero_padding}}".format(page=(page_int-1),zero_padding=zero_padding)
        pd = {"rel":"prev","page":prev_page}
        relations.append(pd)
    if not final:
        if zero_padding == False:
            next_page = str(page_int+1)
        else:
            next_page = "{page:0{zero_padding}}".format(page=(page_int+1),zero_padding=zero_padding)
        nd = {"rel":"next","page":next_page}
        relations.append(nd)
        ld = {"rel":"last","page":last_page}
        relations.append(ld)
    if navdirection == "rtl":
        image_strings = [{"rel":"first","long":last_s,"short":lasts_s}, {"rel":"prev","long":next_s,"short":nexts_s}, {"rel":"next","long":prev_s,"short":prevs_s},
        {"rel":"last","long":first_s,"short":firsts_s},]
    else:
        image_strings = [{"rel":"first","long":first_s,"short":firsts_s}, {"rel":"prev","long":prev_s,"short":prevs_s}, {"rel":"next","long":next_s,"short":nexts_s},
        {"rel":"last","long":last_s,"short":lasts_s},]
    for rel in relations:
        arr = Arrow(relation=rel["rel"], page=rel["page"])
        arr.strings = [item for item in image_strings if item["rel"] == arr.relation][0]
        arr.long = arr.strings["long"]
        arr.short = arr.strings["short"]
        img = image_template.format(series_slug=series_slug,
                                   page=arr.page,
                                   scrollto=scrollto,
                                   site_style=site_style,
                                   relation=arr.relation,
                                   image_long_string=arr.long,
                                   image_short_string=arr.short)
        navl.append(img)
        linkrel = linkrel_template.format(relation=arr.relation,
                                     series_slug=series_slug,
                                     page=arr.page,
                                     page_string=arr.long)
        linkl.append(linkrel)

    navl.append(" </ul>")
    nav = """\n""".join(navl)

    linkrels = """\n""".join(linkl)

    return(nav,linkrels)
