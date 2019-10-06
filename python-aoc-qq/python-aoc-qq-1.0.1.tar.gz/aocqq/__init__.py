"""API for QQ AoC (aocrec.com)."""
import io
import re
import zipfile
from datetime import datetime

import bs4
import requests

MGZ_EXT = '.mgz'
BASE_URL = 'http://aocrec.com'
MAX_RANK_PAGE_ID = 10
MAX_MATCH_PAGE_ID = 10
LADDER_RANKS_LIMIT = 50
MATCH_LIMIT = 10
COLOR_MAPPING = {
    '#0000ff': 0,
    '#ff0000': 1,
    '#00ff00': 2,
    '#ffff00': 3,
    '#00ffff': 4,
    '#ff00ff': 5,
    '#434343': 6,
    '#ff8201': 7
}


def parse_filename_timestamp(func):
    """Parse timestamp from default rec filename format."""
    if not func.lower().startswith('rec.') or not func.endswith(MGZ_EXT) or len(func) != 23:
        return None
    return datetime(
        year=int(func[4:8]),
        month=int(func[8:10]),
        day=int(func[10:12]),
        hour=int(func[13:15]),
        minute=int(func[15:17]),
        second=int(func[17:19])
    )


def get_ladder(session, ladder, start=0, limit=LADDER_RANKS_LIMIT):
    """Get ladder ranks."""
    ranks = []
    page_id = 1
    done = False
    while not done and page_id < MAX_RANK_PAGE_ID:
        html = session.get('{}/ladder/{}?page={}'.format(BASE_URL, ladder, page_id))
        parsed = bs4.BeautifulSoup(html.text, features='html.parser')
        tbody = parsed.find('table', {
            'class': 'text-center pure-table pure-table-horizontal'
        }).find('tbody')
        for tr_elem in tbody.find_all('tr'):
            cols = tr_elem.find_all('td')
            rank = int(cols[0].text)
            if rank < start:
                continue
            elif rank > start + limit:
                done = True
                break
            ranks.append({
                'rank': rank,
                'uid': cols[1].find('strong').text,
                'display_name': cols[1].find('strong').text,
                'rating': int(cols[2].text),
                'wins': int(cols[3].text),
                'losses': int(cols[4].text),
                'streak': int(cols[5].find('strong').text)
            })
        page_id += 1
    return ranks


def _get_matches(session, params, limit):
    """Get match list via search."""
    page_id = 1
    done = False
    matches = []
    while not done and page_id < MAX_MATCH_PAGE_ID:
        html = session.get('{}/list?is_query=yes&version=UP15&page={}&{}'.format(
            BASE_URL, page_id, params))
        parsed = bs4.BeautifulSoup(html.text, features='html.parser')
        tbody = parsed.find('table', {
            'class': 'text-center pure-table pure-table-horizontal'
        }).find('tbody')
        for tr_elem in tbody.find_all('tr'):
            th_elem = tr_elem.find('th')
            if not th_elem:
                break
            if limit and len(matches) == limit:
                done = True
                break
            matches.append({
                'match_id': int(th_elem.find('a')['href'][1:])
            })
        page_id += 1
        if not matches:
            break
    return matches


def get_user_matches(session, user_id, limit=MATCH_LIMIT):
    """Get matches for specific user."""
    return _get_matches(session, 'rankname={}'.format(user_id), limit)


def get_ladder_matches(session, ladder, limit=MATCH_LIMIT):
    """Get matches for a specific ladder."""
    return _get_matches(session, 'symbol={}'.format(ladder), limit)


def get_match(session, match_id): # pylint: disable=too-many-locals
    """Get match data."""
    html = session.get('{}/{}'.format(BASE_URL, match_id))
    parsed = bs4.BeautifulSoup(html.text, features='html.parser')
    players = []
    ladders = set()
    wrapper = parsed.find('div', {'class': 'player-info-wrapper'})
    url_elem = parsed.find('a', {'class': 'download-link'})
    url = url_elem['href'].strip()
    owner = ''.join(url_elem.find_all(text=True, recursive=False)).strip()
    filename = url_elem.find_next('span', {'class': 'badge-normal badge-aoc'}).text.strip()
    for elem in wrapper.find_all('div', {'class': 'pure-u-17-24 fz-80 text-left'}):
        player = elem.find('span', {'class': 'winning-ratio-name'}).text
        match = re.match(r'(.*?)([0-9]\.?[0-9]*)[\-_]?(.*)', player, re.UNICODE)
        if not match:
            ladder, rating, username = (None, None, player)
        else:
            ladder, rating, username = match.group(1, 2, 3)
            ladder = ladder.upper()
        ladders.add(ladder)
        username = username.strip()
        color = elem.find('i')['style'].split(' ')[1][:-1]
        players.append({
            'url': 'http:{}'.format(url) if player == owner else None,
            'id': username.upper(),
            'username': username,
            'color_id': COLOR_MAPPING.get(color),
            'rate_snapshot': float(rating) if rating else None
        })
    return {
        'timestamp': parse_filename_timestamp(filename),
        'players': players,
        'ladder': ladders.pop() if len(ladders) == 1 else None
    }


def download_rec(session, rec_url, target_path):
    """Download and extract a recorded game."""
    resp = session.get(rec_url)
    downloaded = zipfile.ZipFile(io.BytesIO(resp.content))
    downloaded.extractall(target_path)
    return downloaded.namelist()[0] # never more than one rec
