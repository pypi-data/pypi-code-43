from datetime import datetime
from os import makedirs
from os.path import exists, join
from time import sleep

from bs4 import BeautifulSoup as bs
import numpy as np
import requests
import pandas as pd


# A public league for current week and player IDs
LG = 39345


def scrape(lg):
    '''Scrape data

    :param lg: league ID
    '''

    # Start timer
    startTime = datetime.now()

    # Create data folder
    folder = 'data'
    if not exists(folder):
        makedirs(folder)

    # Requests headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    }

    # Parse current week from a public league
    r = requests.get(
        'https://football.fantasysports.yahoo.com/f1/{}'.format(LG),
        headers=headers,
    )
    soup = bs(r.text, 'lxml')
    span = soup.select_one('a.flyout_trigger span.flyout-title')
    week = span.text.split()[1]
    filename = join(folder, '{:%Y-%m-%d %H%M} week {}.csv'.format(startTime, week))

    # Scrape player IDs from a public league
    IDs = []
    groups = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']
    for group in groups:
        for i in range(10):
            # Request next 25 best players
            r = requests.get(
                'https://football.fantasysports.yahoo.com/f1/{}/players'.format(LG),
                headers=headers,
                params=dict(
                    status='ALL',
                    pos=group,
                    stat1='S_PN4W',
                    count=i * 25,
                ),
            )
            soup = bs(r.text, 'lxml')
            table = soup.select_one('#players-table table')
            rows = table.select('tbody tr')
            if not rows: break
            IDs.extend([
                row.select('td')[1].select_one('span.player-status a')['data-ys-playerid']
                for row in rows
            ])
    df = pd.DataFrame(IDs, columns=['ID'])

    # Scrape projections
    def get_projections(row):
        pid = row['ID']
        url = 'https://football.fantasysports.yahoo.com/f1/{}/playernote?pid={}'.format(lg, pid)
        r = requests.get(url)
        for _ in range(10):
            if r: break
            # Retry query
            print('Retrying projections for pid {}'.format(pid))
            sleep(60)
            r = requests.get(url, headers=headers)
        html = r.json()['content']
        soup = bs(html, 'lxml')
        playerinfo = soup.select_one('.playerinfo')
        row['Name'] = playerinfo.select_one('.name').text
        #row['Team'] = playerinfo.select_one('.player-team-name').text
        row['Position'] = playerinfo.select_one('dd.pos').text[:-1]
        row['Owner'] = playerinfo.select_one('dd.owner').text[:-1]

        # Owner ID
        a = playerinfo.select_one('dd.owner a')
        if a:
            row['Owner ID'] = a['href'].split('/')[-1]
        else:
            row['Owner ID'] = np.nan

        row['% Owned'] = playerinfo.select_one('dd.owned').text.split()[0]

        # Weekly projections
        df2 = pd.read_html(html)[0]
        for _, row2 in df2.iterrows():
            week = 'Week {}'.format(row2['Week'])
            points = row2['Fan Pts']
            if points[0] == '*':
                # Game hasn't occured yet
                row[week] = float(points[1:])
                #row[week + ' projection'] = float(points[1:])
                #row[week + ' actual'] = np.nan
            elif points == '-':
                # Bye week
                row[week] = 0
                #row[week + ' projection'] = 0
                #row[week + ' actual'] = 0
            else:
                # Game completed
                row[week] = float(points)
                #row[week + ' projection'] = np.nan
                #row[week + ' actual'] = float(points)

        return row
    df = df.apply(get_projections, axis=1)
    print(df)

    # Print runtime
    print('Total runtime: {}'.format(datetime.now() - startTime))

    # Save data
    df.to_csv(filename, index=False)
