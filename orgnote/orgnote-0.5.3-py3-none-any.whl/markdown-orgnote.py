#!/usr/bin/env python
#-*- coding: utf-8 -*-

# markdown-orgnote.py  ---- a implementation of Markdown for OrgNote, convert Hexo markdown into html
#
# Copyright(c) 2019 Leslie Zhu
# <http://www.lesliezhu.com>
#
# Version 1.0.0
# 
# Wed Sep 18 2019

import re

class Markdown(object):
    ''' re-implementation of markdown for OrgNote

    Perl version by John Gruber: 
    - https://raw.githubusercontent.com/mundimark/markdown.pl/master/Markdown.pl
    '''
    def __init__(self,text=""):
        self.empty_element_suffix = " >"
        self.tab_width = 4

        self.text = text # markdown text
        
        self.urls = ()
	self.titles = ()
	self.html_blocks = ()

        
    def mk2html(self):
        # Standardize line endings
        self.text = re.sub(r'\r\n',r'\n',text)  # DOS to Unix
        self.text = re.sub(r'\r',r'\n',text)    # Mac to Unix

        # Make sure text ends with a couple of newlines
        self.text += "\n\n"

        # Convert all tabs to spaces.
	self.text = self._DeTab(self.text)

    def _DeTab(self,text):
        return re.sub(r'\t',' ' * self.tab_width, text)

        


        

        

        

