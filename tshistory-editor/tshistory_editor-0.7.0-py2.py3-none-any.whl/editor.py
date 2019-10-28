import json
from urllib.parse import urlparse, parse_qs

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np

from tshistory.util import tojson, fromjson


def unpack_dates(graphdata):
    fromdate = None
    todate = None
    if graphdata and 'xaxis.range[0]' in graphdata:
        fromdate = pd.to_datetime(graphdata['xaxis.range[0]'])
    if graphdata and 'xaxis.range[1]' in graphdata:
        todate = pd.to_datetime(graphdata['xaxis.range[1]'])
    return fromdate, todate


def editor(app, engine, tshclass,
           routes_pathname_prefix='/tseditor/',
           request_pathname_prefix='/',
           additionnal_info=None,
           alternative_table=None):

    tsh = tshclass()

    external_stylesheets = [
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'
    ]

    if request_pathname_prefix != '/':
        request_pathname_prefix_adv = request_pathname_prefix + routes_pathname_prefix
        dashboard = dash.Dash(
            'tsview',
            server=app,
            routes_pathname_prefix=routes_pathname_prefix,
            requests_pathname_prefix=request_pathname_prefix_adv,
            external_stylesheets=external_stylesheets
        )
        prefix_link = request_pathname_prefix_adv
    else:
        dashboard = dash.Dash(
            'tsview',
            server=app,
            url_base_pathname=routes_pathname_prefix,
            external_stylesheets=external_stylesheets
        )
        prefix_link = routes_pathname_prefix


    dashboard.config['suppress_callback_exceptions'] = True
    if request_pathname_prefix != '/':
        dashboard.config.requests_pathname_prefix = request_pathname_prefix_adv

    dashboard.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(
            html.Button(id='tse_refresh_snapshot',
                        n_clicks=0,
                        children='refresh graph',
                        style={"width": "100%",
                               'background-color': '#F7F7F7'}
                        )
        ),

        html.P('Zoom to select the date interval:',
               style={'text-align': 'center'}
        ),

        dcc.Graph(id='ts_snapshot'),

        # a bunch of placeholders
        html.Div(html.Button(id='refresh_data', n_clicks=0,
                             children='Refresh data in Table'),
                 style={'display': 'none'}),
        html.Div(id='rev_id', style={'display': 'none'}),
        html.Div(id='diff', style={'display': 'none'}),
        html.Div(id='tse_var_id_serie', style={'display': 'none'}),

        html.Div(id='button-container',
        ),

        html.Div(id='table_container',
                 style={'float': 'left',
                        'min-width': '49%',
                        'padding-top' : '2em'}),

        html.Div([
            html.Table([
                html.Tr([
                    html.Td([
                        html.P(
                            'Metadata:',
                            style={
                                'font-family': 'Helvetica',
                                "font-size": "130%",
                            }
                        ),
                        html.Div(
                            id='info',
                            style={'text-align': 'center'})
                    ],
                            style={'border-width': '0'}
                    )
                ]),
                html.Tr([
                    html.Td([
                        html.P('Manual differences:',
                               style={'font-family': 'Helvetica',
                                      "font-size": "130%"}
                        ),
                        html.Div(
                            id='display_diff',
                            style={'text-align': 'center'}
                        )],
                            style={'border-width': '0'}),
                ]),
                html.Tr([
                    html.Td([
                        html.Button(
                            id='send_diff',
                            n_clicks=0,
                            children='Save diff',
                            style={'width': '100%',
                                   'background-color': '#F7F7F7',
                            }),
                    ],
                            style={'border-width': '0'})
                ],
                        style={
                            'float': 'center',
                            'border': '0'
                        }
                ),
                html.Tr([
                    html.Td([
                        html.P(
                            'Log:',
                            style={
                                'font-family': 'Helvetica',
                                "font-size": "130%"
                            }
                        ),
                        html.Div(
                            id='log_result',
                            style={'text-align': 'center'}
                        )],
                            style={'border-width': '0'})]
                )],
                       style={'width': '100%',
                              'align': 'center',
                       })],
                 id='column_info',
                 style={'float': 'right'},
                 className='six columns'
        ),
    ])

    @dashboard.callback(dash.dependencies.Output('tse_var_id_serie', 'children'),
                        [dash.dependencies.Input('url', 'href')])
    def ts_div_id_serie(href):
        if href is None:
            return {
                'name': '', #formated_names[0]['value'],
                'startdate': None,
                'enddate': None,
                'author': None
            }

        startdate = None
        enddate = None
        author = None
        query = parse_qs(urlparse(href).query)

        if not len(query):
            id_serie = ''
        else:
            id_serie = query['name'][0] if 'name' in query else None
            startdate = query['startdate'][0] if 'startdate' in query else None
            enddate = query['enddate'][0]  if 'enddate' in query else None
            author = query['author'][0] if 'author' in query else None

        return json.dumps({
            'name': id_serie,
            'startdate': startdate,
            'enddate': enddate,
            'author': author
        })

    @dashboard.callback(dash.dependencies.Output('info', 'children'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children')])
    def display_info(info_serie):
        if info_serie is None:
            return 'None'
        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']
        if additionnal_info is not None:
            info_metadata = additionnal_info(engine, id_serie)
            if not info_metadata:
                return 'None'
            data = list(info_metadata.items())
            inside_table = [
                html.Tr([
                    html.Td(elt)
                    for elt in things
                ])
                for things in data
            ]
            table = html.Table(inside_table, style={'margin': '0 auto'})
            return table

    @dashboard.callback(dash.dependencies.Output('button-container', 'children'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children')])
    def dynamic_button(_):
        return html.Button(
            id='refresh_data',
            n_clicks=0,
            children='Refresh data in Table',
            style={"width": "100%",
                   'background-color': '#F7F7F7'}
        )

    @dashboard.callback(dash.dependencies.Output('ts_snapshot', 'figure'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children'),
                         dash.dependencies.Input('tse_refresh_snapshot', 'n_clicks')])
    def snapshot_display(info_serie, n_clicks):
        if info_serie is None:
            return {'data': [], 'layout': {}}

        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']
        startdate = info_serie['startdate']
        enddate = info_serie['enddate']
        if startdate and enddate:
            xaxisrange = {'range': [
                pd.to_datetime(startdate),
                pd.to_datetime(enddate)
            ]}
        else:
            xaxisrange = {}

        tsh = tshclass()

        ts = tsh.get(engine, id_serie)
        if ts is None:
            return {'data': [], 'layout': {}}
        trace = [
            go.Scatter(
                x=ts.index,
                y=ts.values,
                name= id_serie,
                mode='lines',
                line={'color': ('rgb(255, 127, 80)')
                }
            )
        ]
        layout = go.Layout({
            'yaxis': {'fixedrange' : True},
            'xaxis': xaxisrange,
            'showlegend': False,
            'height': 300,
            'margin': go.layout.Margin(b=30, t=0),
        })
        return {
            'data': trace,
            'layout': layout
        }

    def editable_table(engine, tsh, id_serie, fromdate=None, todate=None):
        with engine.begin() as cn:
            ts, marker = tsh.get_ts_marker(cn, id_serie)

        if len(ts) != len(marker): # Some na have been inserted
            new_ts = pd.Series(index=marker.index)
            new_ts[ts.index] = ts
            ts = new_ts

        if fromdate and todate:
            mask = (ts.index >= fromdate) & (ts.index <= todate)
            ts = ts[mask]
            marker = marker[mask]

        idx_marker = np.arange(len(marker))[marker.values]
        htmldiv = dt.DataTable(
            data=[{'Index':elt[0], 'Value': elt[1]}
                  for elt in ts.to_frame().itertuples()],
            id='table',
            columns=[{'id': 'Index', 'name': 'Index'},
                     {'id': 'Value', 'name': 'Value'}],
            editable=True,
            row_selectable=True,
            selected_rows=idx_marker.tolist(),
        )
        return htmldiv


    @dashboard.callback(dash.dependencies.Output('table_container', 'children'),
                        [dash.dependencies.Input('refresh_data', 'n_clicks')],
                        [dash.dependencies.State('tse_var_id_serie', 'children'),
                         dash.dependencies.State('ts_snapshot', 'relayoutData')])
    def dynamic_table(n_clicks, info_serie, graphdata):
        if not info_serie:
            return ''

        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']
        author = info_serie['author']
        if graphdata and 'autosize' not in graphdata:
            fromdate, todate = unpack_dates(graphdata)
        else:
            fromdate = pd.to_datetime(info_serie['startdate'])
            todate = pd.to_datetime(info_serie['enddate'])

        if (info_serie['startdate'] is None and
            info_serie['enddate'] is None and
            n_clicks == 0):
            # i.e. the serie is not bounded by the url parameters
            # we want that the user bound it before showing the data
            return  ''

        tsh = tshclass()
        if alternative_table is not None:
            return alternative_table(
                engine, tsh, id_serie, fromdate, todate, author, additionnal_info,
                prefix_link
            ) or editable_table(engine, tsh, id_serie, fromdate, todate)

        return editable_table(engine, tsh, id_serie, fromdate, todate)


    @dashboard.callback(dash.dependencies.Output('rev_id', 'children'),
                        [dash.dependencies.Input('refresh_data', 'n_clicks')],
                        [dash.dependencies.State('tse_var_id_serie', 'children')])
    def store_id_rev(n_clicks, info_serie):
        if not info_serie:
            return ''

        id_serie = json.loads(info_serie)['name']
        tsh = tshclass()
        kind = tsh.type(engine, id_serie)
        if kind != 'primary' or not id_serie:
            return ''
        rev_id = tsh.last_id(engine, id_serie)
        return rev_id

    @dashboard.callback(dash.dependencies.Output('diff', 'children'),
                        [dash.dependencies.Input('table', 'data')],
                        [dash.dependencies.State('tse_var_id_serie', 'children')])
    def calculate_diff(rows, info_serie):
        df_modif = pd.DataFrame(rows)
        info_diff = {'msg': None, 'diff': None}
        if not info_serie or rows == [{}]:
            return json.dumps(info_diff)

        id_serie = json.loads(info_serie)['name']
        try:
            ts_modif = df_modif.set_index('Index')['Value']
            ts_modif.index = pd.to_datetime(ts_modif.index)
        except Exception as error:
            return json.dumps({'msg':'Error :' + str(error), 'diff': None})
        try:
            ts_modif = pd.to_numeric(ts_modif)
        except:
            pass

        ts_base = tsh.get(engine, id_serie)
        try:
            diff = tsh.diff(ts_base, ts_modif)
            info_diff['diff'] = diff
        except Exception as error:
            return json.dumps({'msg':'Error :' + str(error), 'diff': None})

        if not len(diff):
            return json.dumps({'msg': 'None', 'diff': None})
        return json.dumps({'msg': None, 'diff': tojson(diff)})

    @dashboard.callback(dash.dependencies.Output('display_diff', 'children'),
                        [dash.dependencies.Input('diff', 'children')])
    def display_diff(info_diff):
        if not info_diff:
            return 'None'

        info_diff = json.loads(info_diff)
        if info_diff['msg']:
            return info_diff['msg']

        if info_diff['diff']:
            tudiff = fromjson(info_diff['diff'], 'name').to_frame().itertuples()
            inside_table = [
                html.Tr(
                    f'{elt1} : {elt2}'
                )
                for elt1, elt2 in tudiff
            ]
            return html.Table(inside_table, style={'margin': '0 auto'})

        # might be redundant with 1 branch
        return 'None'

    @dashboard.callback(dash.dependencies.Output('log_result', 'children'),
                        [
                            dash.dependencies.Input('send_diff', 'n_clicks')
                        ],
                        [
                            dash.dependencies.State('tse_var_id_serie', 'children'),
                            dash.dependencies.State('diff', 'children'),
                            dash.dependencies.State('rev_id', 'children')
                        ])
    def insert_diff(n_clicks, info_serie, info_diff, rev_id_stored):
        if not info_serie:
            return ''

        id_serie = json.loads(info_serie)['name']
        author = json.loads(info_serie)['author']
        author = 'webui' if author is None else author
        if info_diff:
            info_diff = json.loads(info_diff)
        if info_diff['diff'] is None:
            return ''

        ts = fromjson(info_diff['diff'], tsname=id_serie)
        rev_id = tsh.last_id(engine, id_serie)

        if str(rev_id) != str(rev_id_stored):
            return ('Updating aborted: version conflict! '
                    'Please reload the data and redo the manual edition')

        try:
            with engine.begin() as cn:
                diff = tsh.update(
                    cn, ts, id_serie, author, manual=True
                )
        except Exception as error:
            return str(error)

        if len(diff):
            msg = (f'Series {id_serie} has been succefuly updated by {author} '
                   f'with {len(diff)} new values')
        else:
            msg = 'No changes'
        return msg
