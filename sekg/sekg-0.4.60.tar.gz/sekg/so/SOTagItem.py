#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SOTagItem:

    def __init__(self, tag_name=None, id=None, count=None, excerpt_post_id=None, wiki_post_id=None,
                 short_description=None, long_description=None, synonyms=None, info_html=None, tag_info_dic={}):
        self.tag_name = tag_name
        self.id = id
        self.count = count
        self.excerpt_post_id = excerpt_post_id
        self.wiki_post_id = wiki_post_id
        self.short_description = short_description
        self.long_description = long_description
        self.synonyms = synonyms
        self.info_html = info_html
        if tag_info_dic:
            self.__init_from_tag_info_dic(tag_info_dic)

    def is_valid(self):
        if self.short_description or self.long_description or self.synonyms:
            # print(self.short_description, self.long_description, self.synonyms)
            return True
        return False

    def __init_from_tag_info_dic(self, tag_info_dic):
        if "TagName" in tag_info_dic.keys():
            self.tag_name = tag_info_dic["TagName"]
        if "Id" in tag_info_dic.keys():
            self.id = tag_info_dic["Id"]
        if "Count" in tag_info_dic.keys():
            self.count = tag_info_dic["Count"]
        if "ExcerptPostId" in tag_info_dic.keys():
            self.excerpt_post_id = tag_info_dic["ExcerptPostId"]
        if "WikiPostId" in tag_info_dic.keys():
            self.wiki_post_id = tag_info_dic["WikiPostId"]
        if "ShortDescription" in tag_info_dic.keys():
            self.short_description = tag_info_dic["ShortDescription"]
        if "LongDescription" in tag_info_dic.keys():
            self.long_description = tag_info_dic["LongDescription"]
        if "InfoHtml" in tag_info_dic:
            self.info_html = tag_info_dic["InfoHtml"]

    def get_tag_name(self):
        return self.tag_name

    def get_short_description(self):
        return self.short_description

    def get_long_description(self):
        return self.long_description

    def get_tag_synonyms(self):
        return self.synonyms

    def get_info_html(self):
        return self.info_html

    def get_tag_id(self):
        return self.id

    def get_tag_count(self):
        return self.count

    def get_excerpt_post_id(self):
        return self.excerpt_post_id

    def get_wiki_post_id(self):
        return self.wiki_post_id

    def update_tag_name(self, tag_name):
        self.tag_name = tag_name

    def update_short_description(self, short_description):
        self.short_description = short_description

    def update_long_description(self, long_description):
        self.long_description = long_description

    def update_tag_synonyms(self, synonyms):
        self.synonyms = synonyms

    def update_info_html(self, info_html):
        self.info_html = info_html

    def update_tag_id(self, id):
        self.id = id

    def update_tag_count(self, count):
        self.count = count

    def update_excerpt_post_id(self, excerpt_post_id):
        self.excerpt_post_id = excerpt_post_id

    def update_wiki_post_id(self, wiki_post_id):
        self.wiki_post_id = wiki_post_id
