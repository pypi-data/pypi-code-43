#!/usr/bin/env python
#-*- coding: utf-8 -*-

# markdown.py  ---- a implementation of Markdown for OrgNote, convert Hexo markdown into html
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
        self.text = re.sub(r'\r\n',r'\n',self.text)  # DOS to Unix
        self.text = re.sub(r'\r',r'\n',self.text)    # Mac to Unix

        # Make sure text ends with a couple of newlines
        self.text += "\n\n"

        # Convert all tabs to spaces.
	self.text = self._DeTab(self.text)

        
        

        return self.text

    def _DeTab(self,text):
        return re.sub(r'\t',' ' * self.tab_width, text)

    def _HashHTMLBlocks(self,text):
        self.less_than_tab = self.tab_width - 1

        # Hashify HTML blocks:
	# We only want to do this for block-level HTML tags, such as headers,
	# lists, and tables. That's because we still want to wrap <p>s around
	# "paragraphs" that are wrapped in non-block-level tags, such as anchors,
	# phrase emphasis, and spans. The list of tags we're looking for is
	# hard-coded:
        self.block_tags_a = r"p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|script|noscript|form|fieldset|iframe|math|ins|del"
        self.block_tags_b = r"p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|script|noscript|form|fieldset|iframe|math"

        
	# First, look for nested blocks, e.g.:
	# 	<div>
	# 		<div>
	# 		tags for inner block must be indented.
	# 		</div>
	# 	</div>
	#
	# The outermost tags must start at the left margin for this to match, and
	# the inner nested divs must be indented.
	# We need to do this before the next, more liberal match, because the next
	# match will start at the first `<div>` and stop at the first `</div>`.
        

        


        

        

        

