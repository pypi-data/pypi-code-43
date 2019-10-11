import re


re_show = re.compile( r'https://mangaplus.shueisha.co.jp/titles/\d*' )

re_chapter = re.compile( r'/chapter/([0-9]+)/' )
re_chapter_title = re.compile( r'#[0-9]+"([^*]+)\*' )
re_title = re.compile( r'#MANGA_Plus ([^@]+)@' )
