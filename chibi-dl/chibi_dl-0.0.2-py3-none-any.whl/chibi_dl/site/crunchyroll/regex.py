import re


re_lenguage = re.compile( r'.+/([a-z]{2})/.+' )

re_show = re.compile(
    r'https?://(?:(?P<prefix>www|m)\.)?(?P<url>crunchyroll\.com/[a-z]{2}/'
    '(?!(?:news|anime-news|library|forum|launchcalendar|lineup|store|comics'
    '|freetrial|login))(?P<id>[\w\-]+))/?(?:\?|$)' )
re_video = re.compile(
    r'https?:\/\/(?:(?P<prefix>www|m)\.)?(?P<url>crunchyroll\.'
    '(?:com|fr)/[a-z]{2}/(?:media(?:-|/\?id=)|[^/]*/[^/?&]*?)'
    '(?P<video_id>[0-9]+))(?:[/?&]|$)' )

re_csrf_token = re.compile( r'login_form\[\_token\]\"\ value\=\"(.*?)\"' )


re_episodes = re.compile( r'\<a href\=\"\/(.*?)\"\ title\=\"(.*?)' )
