from __future__ import (absolute_import, division, print_function, unicode_literals)

import csv
import logging
import pprint

from .klass_path import Path
from .klass_slice import Slice

_logger = logging.getLogger('dyools dataframe')


class DataFrame(object):

    def __init__(self, df, env=False, logger=False):
        self.__df = df
        self.__env = env
        self.__logger = logger or _logger

    def enumerate_by(self, column, new_column='enum', concat_column=False):
        df = self.__df

        class Obj(object):
            def __init__(self, i=0, last_value=False):
                self.i = i
                self.last_value = last_value

        obj = Obj()

        def enum_df(row, obj):
            if row[column] != obj.last_value:
                obj.i = 0
                obj.last_value = row[column]
            obj.i += 1
            return obj.i

        df.sort_values(by=column, ascending=True, inplace=True)
        df[new_column] = df.apply(lambda row: enum_df(row, obj), axis=1)
        if concat_column:
            df[concat_column] = df.apply(lambda row: '{}_{}'.format(row[column], row[new_column]), axis=1)
        return self

    def to_odoo(self, model, by=100, csv_path=False, ctx={'tracking_disable': True}):
        df = self.__df
        logger = self.__logger
        env = self.__env
        logger.info('size = {}'.format(df.count()))
        header = df.columns.to_list()
        all_data = []
        ids = []
        for item, percent in Slice(df, by, with_percent=True):
            data = []
            logger.info('Load {} {:.2f} %'.format(model, percent * 100))
            for i, row in item.iterrows():
                data.append(row.to_list())
            all_data.extend(data)
            res = env[model].with_context(**ctx).load(header, data)
            if not res.get('ids'):
                logger.error(pprint.pformat(res))
                raise ImportError(res)
            else:
                ids.extend(res['ids'])
            env.cr.commit()
        if csv_path:
            Path.remove('res_partner.csv')
            with open('res_partner.csv', 'w+') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerow(header)
                writer.writerows(all_data)
        return ids

    def get_dataframe(self):
        return self.__df
