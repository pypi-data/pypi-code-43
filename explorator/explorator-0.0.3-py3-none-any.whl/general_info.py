import pandas as pd
import numpy as np

pd.options.display.max_columns = 999


def get_df_general_info(dfc):
    df_info = pd.DataFrame()

    # total_rows
    dfc_count = dfc.reset_index().count()['index']

    # general info
    df_info['type'] = dfc.dtypes
    df_info['count'] = dfc.count()
    df_info['null_count'] = dfc_count - df_info['count']
    df_info['pc_count'] = df_info['count'] / dfc_count
    df_info['uniq'] = dfc.nunique()
    df_info['pc_uniq'] = df_info['uniq'] / dfc_count
    df_info = pd.concat([df_info], axis=1, keys=['general info'])
    return df_info


def get_df_examples(dfc):
    # examples
    df_examples = dfc.head(5).transpose()
    if df_examples.shape[1] < 5:
        for i in range(5 - df_examples.shape[1] - 1, 5):
            df_examples[i] = np.NaN

    df_examples = pd.concat([df_examples], axis=1, keys=['examples'])
    return df_examples


def get_df_top_column_values(dfc):
    outside = 5 * ['value'] + 5 * ['count']
    inside = list(range(5)) + list(range(5))
    hier_index = list(zip(outside, inside))
    hier_index = pd.MultiIndex.from_tuples(hier_index)

    top_values = pd.DataFrame(index=hier_index).transpose()

    for col in dfc.columns:
        dfc_top = dfc[col].value_counts().head(5).reset_index()
        dfc_top.columns = ['value', 'count']
        if dfc_top.shape[0] == 0:
            dfc_top = dfc_top.append([np.nan, np.nan])
        top_values = pd.concat([top_values, dfc_top[['value', 'count']].unstack(1).to_frame().transpose()])
    top_values.set_index(dfc.columns, inplace=True)
    return top_values[['value', 'count']]


def get_get_description(dfc):

    digit_types = [np.dtype('byte'), np.dtype('short'), np.dtype('intc'), np.dtype('int_'), np.dtype('longlong'),
                   np.dtype('intp'), np.dtype('int8'), np.dtype('int16'), np.dtype('int32'), np.dtype('int64'),
                   np.dtype('ubyte'), np.dtype('ushort'), np.dtype('uintc'), np.dtype('uint'), np.dtype('ulonglong'),
                   np.dtype('uintp'), np.dtype('uint8'), np.dtype('uint16'), np.dtype('uint32'), np.dtype('uint64'),
                   np.dtype('half'), np.dtype('single'), np.dtype('double'), np.dtype('float_'), np.dtype('longfloat'),
                   np.dtype('float16'), np.dtype('float32'), np.dtype('float64'), np.dtype('float96'),
                   np.dtype('float128'), np.dtype('csingle'), np.dtype('complex_'), np.dtype('clongfloat'),
                   np.dtype('complex64'), np.dtype('complex128'), np.dtype('complex192'), np.dtype('complex256')
                   ]

    arr = []
    for col in dfc.columns:
        series = pd.Series(name=col)
        if dfc[col].dtype in digit_types:
            series['avg'] = dfc[col].mean()
            series['std'] = dfc[col].std()
            series['25%'] = dfc[col].quantile(.25)
            series['50%'] = dfc[col].quantile(.50)
            series['75%'] = dfc[col].quantile(.75)
            series['min'] = dfc[col].dropna().min()
            series['max'] = dfc[col].dropna().max()
        else:
            series['avg'] = np.nan
            series['std'] = np.nan
            series['25%'] = np.nan
            series['50%'] = np.nan
            series['75%'] = np.nan

            if dfc[col].dtype == np.dtype('<M8[ns]'):
                series['min'] = dfc[col].dropna().min().strftime('%Y-%m-%d')
                series['max'] = dfc[col].dropna().max().strftime('%Y-%m-%d')
            else:
                str_dfc_col = dfc[col].dropna().apply(lambda x: str(x))
                series['min'] = str_dfc_col.min()
                series['max'] = str_dfc_col.max()

        arr.append(series)

    descr = pd.concat(arr, axis=1, sort=False).T
    descr = descr[['min', 'max', 'avg', 'std', '25%', '50%', '75%']]
    descr = pd.concat([descr], axis=1, keys=['describe'])
    return descr


def write_reports_view_to_one_excel(reports, report_name,
                                    info=['general', 'value', 'counts', 'examples', 'description']):
    '''
    DOESNT WORK
    '''
    # report_name='! rr.xlsx'
    writer = pd.ExcelWriter(r'./' + report_name, engine='xlsxwriter')
    workbook = writer.book
    int_format = workbook.add_format({'num_format': '# ### ### ##0'})
    float_format = workbook.add_format({'num_format': '# ### ### ##0.00'})
    percent_format = workbook.add_format({'num_format': '0%'})

    g_sheetname = 'general'
    rep_to_xl = pd.DataFrame()

    for rep in reports.keys():  # files_ok:
        rep_i = reports[rep]
        rep_i['file'] = rep
        rep_to_xl = rep_to_xl.append(rep_i)

    rep_to_xl[info].to_excel(writer, g_sheetname, startcol=0)
    worksheet = writer.sheets[g_sheetname]

    for letter in ['D', 'E', 'G', 'N', 'O', 'P', 'Q', 'R', 'W', 'X', 'Y']:
        worksheet.set_column('{0}:{0}'.format(letter), None, int_format)

    for letter in ['S', 'T', 'U', 'V']:
        worksheet.set_column('{0}:{0}'.format(letter), None, float_format)

    for letter in ['F', 'H']:
        worksheet.set_column('{0}:{0}'.format(letter), None, percent_format)

    # df_gen.to_excel(writer, g_sheetname)
    # worksheet = writer.sheets[g_sheetname]

    writer.save()


def get_total(dfc, info=['general', 'values', 'examples', 'description']):
    '''
    params:
        - dfc (pd.DataFrame) : DataFrame to analyze
        - info (list) : paragrahps of analysis report
    returns:
        - df_total_info (pd.DataFrame) : DataFrame with analysis
    '''
    tools = {'general': get_df_general_info,
             'values': get_df_top_column_values,
             'examples': get_df_examples,
             'description': get_get_description}
    df_total_info = tools[info[0]](dfc)
    for page in info[1:]:
        df_total_info = df_total_info.join(tools[page](dfc))

    return df_total_info
