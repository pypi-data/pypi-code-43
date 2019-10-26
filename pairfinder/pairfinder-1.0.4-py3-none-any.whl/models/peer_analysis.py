import os, sys
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0,project_dir)

from pathlib import Path
from builds.asset import asset_factory, Pair
from data.source import data, NaverEvents
from builds.xlsx_manager import XlsxMgr
from utils import get_project_dir, bloomberg2asset
from builds.pairplotlib import PairPlotLib
from models.spread_builder import SpreadBuilder
from builds.statistics import ADF, Half_Life, Hurst
import itertools

import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from tqdm import tqdm
from datetime import datetime, timedelta
from SETTINGS import METHODS, FROM_, PLOT_FROM_, ROLLING, WINDOW, ADDITIONAL_FEATURES, SHEET_COLUMNS, SHEET_HEIGHT

IN_DIR = os.path.join(get_project_dir(), 'data', 'peer_groups')

class PeerGroup:
    settings = {
        'window': 365,
        'analysis': ("2015-01-01", datetime.now().strftime("%Y-%m-%d")),
        'plot': ('2015-01-01', datetime.now().strftime("%Y-%m-%d")),
    }

    def __init__(self, params={}):
        self.settings.update(params)
        self._analysis = self._summary = []

    def set_peer_group(self, peer_group, **kwargs):
        lst = peer_group[['LONG ASSET SYMBOL', 'LONG ASSET NAME', 'SHORT ASSET SYMBOL', 'SHORT ASSET NAME']].values.tolist()
        lst = [[[x[0], x[1]], [x[2], x[3]]] for x in lst]

        self._group = lst

    def analyze(self, filter_ks=True):
        for pair in tqdm(self._group, total=len(self._group), desc=" [*] Analyzing Pairs..."):
            y_asset = bloomberg2asset(bloomberg_symbol=pair[0][0], name=pair[0][1], filter_ks=filter_ks)
            x_asset = bloomberg2asset(bloomberg_symbol=pair[1][0], name=pair[1][1], filter_ks=filter_ks)

            pair = Pair(y_asset=y_asset, x_asset=x_asset)

            try:
                spread_builder = SpreadBuilder(window=self.settings['window'], from_=self.settings['analysis'][0])
                if 'TLS' not in METHODS:  # TLS Scatter PLOT
                    spread_builder.calculate(pair, methods=['TLS'] + METHODS)
                else:
                    spread_builder.calculate(pair, methods=METHODS)
            except Exception as e:
                print(e)
                continue

            self._add_features(pair, ADDITIONAL_FEATURES)
            self._add_p_statistics(pair, METHODS)
            self._analysis.append(pair)

    def __len__(self):
        return len(self._group)

    def __getitem__(self, position):
        return self._group[position]

    def _add_p_statistics(self, pair, methods):
        for method in methods:
            adf = ADF()
            half_life = Half_Life()
            hurst = Hurst()
            spread = pair.spread[method].dropna()
            try:
                adf.apply_adf(spread)
            except:
                adf.p_value = 999
            try:
                half_life.apply_half_life(spread)
            except:
                half_life.half_life = 999
            try:
                hurst.apply_hurst(spread)
            except:
                hurst.h_value = 999

            pair.data[method + '_p_value'] = adf.p_value
            pair.data[method + '_half_life'] = half_life.half_life
            pair.data[method + '_hurst'] = hurst.h_value

    def _add_features(self, pair, features):
        for feature in features:
            if feature == 'AVG_TRADING_VALUE':
                close_volume_dic = data.history([pair.x_asset, pair.y_asset],
                                                field_arr=["CLOSE", "VOLUME"], from_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
                for asset in [pair.x_asset, pair.y_asset]:
                    close_volume = close_volume_dic[asset.use()]
                    asset.data[feature] = np.mean(close_volume.iloc[:, 0] * close_volume.iloc[:, 1])

            elif feature == 'DIVIDEND_YIELD':
                # 배당 데이터 받기
                start_date = datetime.now() - pd.DateOffset(days=365)

                for i, asset in enumerate([pair.y_asset, pair.x_asset]):
                    try:
                        if asset.exchange == 'KS':
                            dy = NaverEvents().request(symbol=asset.symbol, fields=[feature])[feature] / 100
                        else:

                            div = data.events(
                                [asset],
                                field_arr=["DIVIDENDS"],
                                start_date=self.settings['analysis'][0])

                            dvd = div[asset.use()]['DIVIDENDS']
                            dvd.sort_index(ascending=False)
                            price = pair.data['y'][-1] if i == 0 else pair.data['x'][-1]
                            dy = dvd.loc[start_date:].values.sum() / price
                        asset.data[feature] = dy
                    except:
                        asset.data[feature] = -999

    def summarize(self, outpath=os.path.join(get_project_dir(), 'output', 'peer_analysis',
                                             '{}'.format(datetime.now().strftime('%Y%m%d%H%M%S')))):

        Path(outpath).mkdir(exist_ok=True)
        xlsx_manager = XlsxMgr(path=outpath, fname='summary.xlsx')

        for i, method in enumerate(METHODS):

            xlsx_manager.add_sheet(method)
            xlsx_manager.set_sheet(method)

            # Initialize Sheet
            for col, items in enumerate(SHEET_COLUMNS.items()):
                key, value = items[0], items[1]
                xlsx_manager.sheet.set_column(col, col, float(value[1]), xlsx_manager.format_dic[value[2]])
                xlsx_manager.write(0, col, value[0], cell_format=xlsx_manager.format_dic['header'])
                xlsx_manager.sheet.write_comment(row=0, col=col, comment=value[3])

            matrix = np.empty(shape=(len(self._analysis), len(SHEET_COLUMNS)), dtype=object)
            for row, pair in tqdm(enumerate(self._analysis), total=len(self._analysis),
                                    desc=" {} Method ... ({}/{})".format(method, i+1, len(METHODS))):

                ppl = PairPlotLib(pair, from_=self.settings['plot'][0])
                xlsx_manager.sheet.set_row(row + 1, SHEET_HEIGHT)

                for col, items in enumerate(SHEET_COLUMNS.items()):
                    key, format_ = items[0], xlsx_manager.format_dic[items[1][2]]
                    if key == 0: # 순서
                        value = row + 1
                    elif key == 1:
                        value = '{} {} Equity'.format(pair.y_asset.symbol, pair.y_asset.exchange)
                    elif key == 2:
                        value = '{} {} Equity'.format(pair.x_asset.symbol, pair.x_asset.exchange)
                    elif key == 3:
                        value = pair.y_asset.name
                    elif key == 4:
                        value = pair.x_asset.name
                    elif key == 5:
                        value = pair.spread[method][-1] if len(pair.spread[method]) > 0 else None
                    elif 6 <= key <= 10:
                        value = ' '

                        if key == 6:
                            y = pair.data['y']
                            x = pair.data['x']
                            fig, _ = ppl.price(x=x, y=y, title='Abs Price')
                        elif key == 7:
                            fig, _ = ppl.spread(method=method)

                        elif key == 8:
                            fig, _ = ppl.spread_box(method=method)

                        elif key == 9:
                            fig, _ = ppl.spread_dist(method=method)

                        elif key == 10:
                            fig, _ = ppl.linear_regression(method='TLS')
                        fig.savefig(xlsx_manager.get_path(path=outpath,
                                                          file_name='{}_{}_{}_{}.png'.format(
                                                              pair.x_asset.symbol,
                                                              pair.y_asset.symbol,
                                                              method, key),
                                                          is_img=True), bbox_inches="tight")
                        xlsx_manager.insert_img(row + 1, col,
                                                file_name='{}_{}_{}_{}.png'.format(pair.x_asset.symbol,
                                                                                   pair.y_asset.symbol,
                                                                                   method, key),
                                                scale={'y_offset': 15, 'x_offset': 15})
                    elif key == 11:
                        value = pair.data['y'][-1]
                    elif key == 12:
                        value = pair.data['x'][-1]
                    elif key == 13:
                        value = pair.data['rolling_corr'][-1] if len( pair.data['rolling_corr']) > 0 else None
                    elif key == 14:
                        value = pair.data[method + '_p_value']
                    elif key == 15:
                        value = pair.data[method + '_hurst']
                    elif key == 16:
                        value = pair.data[method + '_half_life']
                    elif key == 17:
                        value = pair.y_asset.data['AVG_TRADING_VALUE']
                    elif key == 18:
                        value = pair.x_asset.data['AVG_TRADING_VALUE']
                    elif key == 19:
                        value = pair.y_asset.data["DIVIDEND_YIELD"]
                    elif key == 20:
                        value = pair.x_asset.data["DIVIDEND_YIELD"]
                    else:
                        raise Exception

                    xlsx_manager.write(row+1, col, value, cell_format=format_)
                    matrix[row, col] = value

            xlsx_manager.sheet.autofilter(0, 0, 0, len(SHEET_COLUMNS) - 1)

        writer = xlsx_manager.writer
        xlsx_manager.close()

        return

def main():
    cred_path = r'C:\Users\Administrator\OneDrive\Code Archieves\pairs-framework\data\_cridentials\spreadsheet-245601-24ecd3f4c25f.json'
    peer_group = PeerGroup(cred_path=cred_path)
    peer_group.set_peer_group(sheet_name='pairs', **{'LONG ASSET SYMBOL': '000075 KS Equity'})
    peer_group.analyze(filter_ks=True)
    peer_group.summarize(out_dirname='pfd_pfd_ks_')

if __name__ == '__main__':
    main()
