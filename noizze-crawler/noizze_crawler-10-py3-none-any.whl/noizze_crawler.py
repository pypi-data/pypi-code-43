from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse
import json

version = 'v10'

google_api_key = ''


class HostNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HTTPError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def video_id(value):
    query = urllib.parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def is_youtube_url(url):
    for ykwd in ['youtu.be', 'www.youtube.com', 'youtube.com', 'm.youtube.com']:
        if ykwd in url:
            return True
    else:
        return False

def youtube_crawler(url, with_tags=False):
    yid = video_id(url)
    url = 'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&part=snippet,statistics'.format(yid, google_api_key)
    response = urllib.request.urlopen(url)
    data = response.read()
    j = json.loads(data.decode())
    if j and with_tags:
        return {
            'title': j['items'][0]['snippet']['title'],
            'desc': j['items'][0]['snippet']['description'],
            'img': 'https://i.ytimg.com/vi/{}/0.jpg'.format(yid),
            'tags': j['items'][0]['snippet']['tags'],
            }
    else:
        return {
            'title': j['items'][0]['snippet']['title'],
            'desc': j['items'][0]['snippet']['description'],
            'img': 'https://i.ytimg.com/vi/{}/0.jpg'.format(yid),
            }


def fetch_url(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
        'AppleWebKit/537.36 (KHTML, like Gecko) ' + \
        'Chrome/77.0.3865.90 Safari/537.36'

    headers_v4 = {'User-Agent': user_agent}
    url_req = urllib.request.Request(url, headers=headers_v4)

    try:
        urlobj = urllib.request.urlopen(url_req)
    except Exception as e:
        if type(e) == urllib.error.HTTPError:
            raise HTTPError(e.code) from None  # 404 500 etc as int
        elif type(e) == urllib.error.URLError:
            raise HostNotFound(e.reason) from None

    htmlbinary = urlobj.read()
    html = htmlbinary.decode('utf-8', errors="ignore")
    if ' charset=euc-kr"' in html:
        html = htmlbinary.decode('euc-kr', errors="ignore")
    return html


def crawler(url):
    html = fetch_url(url)
    (title, desc, image_url, html) = parser(url, html)
    return title, desc, image_url, html


def parser(url, html):
    if html:
        soup = BeautifulSoup(html, 'html.parser')

        title_soup = soup.find('meta', property='og:title')
        if title_soup and title_soup.get('content', None).strip():
            title = title_soup.get('content', None)
        else:
            if soup.title.string:
                title = soup.title.string
                # title_match = re.search('<title.*>(.*?)</title>', soup.title)
                # title = title_match.group(1)
            else:
                title = ''

        desc_soup = soup.find('meta', attrs={'name': 'og:description'}) or \
            soup.find('meta', attrs={'property': 'description'}) or \
            soup.find('meta', attrs={'name': 'description'})

        if desc_soup:
            desc = desc_soup.get('content', None)
        else:
            desc = ''

        image_soup = soup.find('meta', attrs={'property': 'og:image'}) or \
            soup.find('meta', attrs={'name': 'twitter:image'}) or \
            soup.find('link', attrs={'rel': 'image_src'})

        if image_soup:
            image_url = image_soup.get('content', None)
            image_url = urllib.parse.urljoin(url, image_url)
        else:
            image_url = ''
    else:
        title = ''
        desc = ''
        image_url = ''

    return title, desc, image_url, html


if __name__ == '__main__':
    pass
