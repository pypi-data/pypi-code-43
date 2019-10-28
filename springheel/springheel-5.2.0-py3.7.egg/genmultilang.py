#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########
##  Springheel - Multilanguage processing
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

from langcodes import Language

def genMultiLang(multilang):
    other_langs = []
    multilang_kvs = [item.split("=") for item in multilang.split(",")]
    for pair in multilang_kvs:
        d = {"langcode":pair[0], "path":pair[1]}
        other_langs.append(d)
    olang_links = []
    for langsite in other_langs:
        langsite["name"] = Language.get(langsite["langcode"]).autonym()
        langsite["element"] = """<a href="{path}">{name}</a>""".format(path=langsite["path"], name=langsite["name"])
        olang_links.append(langsite["element"])
        olangs = " | ".join(olang_links)
    return(olangs)