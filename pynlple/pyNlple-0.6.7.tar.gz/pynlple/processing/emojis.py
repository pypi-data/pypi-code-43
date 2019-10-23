# -*- coding: utf-8 -*-
import emoji.unicode_codes as codes
import re
from itertools import repeat
from pynlple.data.datasource import TsvDataframeSource
from pynlple.module import abs_path, append_paths

DEFAULT_EMOJI_CLASS_NAME = 'emoji'
DEFAULT_COMPONENT_CLASS_NAME = 'emoji-component'
CLASS_NAME_DELIMITER = '_'


class UnicodeEmojiProvider(object):

    def __iter__(self):
        ws_patt = re.compile(r'\s+')
        source = codes.EMOJI_UNICODE.items()
        emojis = sorted(source, key=len, reverse=True)
        for name, emoji_ in emojis:
            yield (ws_patt.sub('', emoji_), 'emoji:' + name)


class UnicodeEmojiProviderV11(object):


    def __init__(self, full_names=True, class_name=DEFAULT_EMOJI_CLASS_NAME):
        self.full_names = full_names
        self.class_name = class_name

        path = append_paths(abs_path(__file__, 'data'), 'emoji', 'emojis.txt')
        emoji_df = TsvDataframeSource(path, encoding='utf-8').get_dataframe()
        emoji_df.loc[:,'len'] = emoji_df.loc[:,'char'].apply(len)
        emoji_df.sort_values(by=['len', 'char'], ascending=False, inplace=True)

        self.emojis = list(emoji_df.loc[:,'char'].tolist())
        if self.full_names and self.class_name:
            self.names = list(map(lambda e: self.class_name + CLASS_NAME_DELIMITER + e, emoji_df.loc[:,'cldr_alias']))
        elif self.full_names and not self.class_name:
            self.names = list(emoji_df.loc[:,'cldr_alias'].tolist())
        else:
            self.names = repeat(self.class_name if self.class_name else DEFAULT_EMOJI_CLASS_NAME)

    def __iter__(self):
        return iter(zip(self.emojis, self.names))


class UnicodeClusteredEmojiProviderV11(object):

    def __init__(self, class_name=DEFAULT_EMOJI_CLASS_NAME):
        self.class_name = class_name

        path = append_paths(abs_path(__file__, 'data'), 'emoji', 'emojis_clustered.txt')
        emoji_df = TsvDataframeSource(path, encoding='utf-8').get_dataframe()
        emoji_df.loc[:,'len'] = emoji_df.loc[:,'char'].apply(len)
        emoji_df.sort_values(by=['len', 'char'], ascending=False, inplace=True)

        self.emojis = list(emoji_df.loc[:,'char'].tolist())
        if self.class_name:
            prefix = self.class_name
        else:
            prefix = DEFAULT_EMOJI_CLASS_NAME
        self.cluster_names = list(map(lambda c: prefix + CLASS_NAME_DELIMITER + str(c), emoji_df.loc[:,'cluster']))

    def __iter__(self):
        return iter(zip(self.emojis, self.cluster_names))


class UnicodeEmojiComponentProviderV11(object):

    def __init__(self):
        path = append_paths(abs_path(__file__, 'data'), 'emoji', 'emoji_components.txt')
        emoji_df = TsvDataframeSource(path, encoding='utf-8').get_dataframe()
        emoji_df.loc[:,'len'] = emoji_df.loc[:,'char'].apply(len)
        emoji_df.sort_values(by=['len', 'char'], ascending=False, inplace=True)
        self.emojis = list(emoji_df.loc[:,'char'].tolist())
        self.names = list(emoji_df.loc[:,'class'].tolist())

    def __iter__(self):
        return iter(zip(self.emojis, self.names))
