# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

K_SYSTEM = 'unique_letter'
K_PLC = 'plc'
K_DEVICE_TYPE = 'device_type'
K_ID = 'id'
K_NAME = "device_name"
K_QUANTITY = "quantity"
K_LEVEL2 = "level2"
K_LEVEL3 = "level3"
K_WP = 'wp_responsible'
K_SW_DEVICE = 'sw_device'


# table columns must be field name of devices 
TBL_COLUMNS  = [K_ID, K_NAME, K_QUANTITY]

# field for dropdown selection menu in form
DROPDOWN_FIELDS = [K_SYSTEM, K_PLC, K_DEVICE_TYPE, K_LEVEL2, K_LEVEL3, K_WP, K_SW_DEVICE]
RANGE_FIELD = [K_QUANTITY]

def list_str(s):
    """ [s] if s is str else s """
    return [s] if isinstance(s, str) else s
    
def filter_device(devices, search , *args):
    """ Apply form """
    if search:
        devices = devices.filter_device('*', ("%", search))
          
    for flt, key in zip(args, DROPDOWN_FIELDS):
        if flt:
            dts = sum(([key, ("==", dt)] for dt in list_str(flt)) , [] )
            devices = devices.filter_device_or(*dts)                    
    return devices

def choices(devices, field_name):     
    return sorted( [{'label':"%s"%v, 'value':v} for v in (devices.get_field(field_name).choices or set())], key=lambda r: r['value'])
    
def form(devices):                
    wdg = []
    for field in DROPDOWN_FIELDS:
        wdg.append((field , dcc.Dropdown(
                options=choices(devices, field), 
                id=field, value='',  multi=True)))
    
    
    for field_name in []:#RANGE_FIELD:
        field = devices.get_field(field_name)
                
        wdg.append((field, dcc.RangeSlider(
        count=1,
        min=field['min'],
        max=field['max'],
        step=1,
        value=[field['min'], field['max']],
        id=field_name, 
        )))
        
    wdg += [('',dcc.Input(placeholder='Search any fields (reg. exp.)...',type='text',
                       value='', id='search-field', style={'width':'400px'}))]
    
    if len(wdg)%2: wdg = wdg+[('','')]
    
    tbl_childs = []
    sfs = {'width':'400px', 'border':'0px'}
    sns = {'width':'50px', 'border':'0px'}
    
    for (a_name, a),(b_name,b) in zip(wdg[::2], wdg[1::2]):
        tbl_childs.append(html.Tr([html.Td(a_name,style=sns), html.Td(a, style=sfs),
                 html.Td(b_name,style=sns), html.Td(b,style=sfs)]))
                 
    return html.Table(tbl_childs)

def device_info(device):
    head = [html.H2(device[K_ID]+" : "+device[K_NAME]), html.H4(device[K_DEVICE_TYPE])]
    
    children = []
    for field_name, field in device.field_items():
        children.append(device_property(device, field_name))    
    return html.Div([html.Div(head),html.Div(children,id='device-%s'%device.id)])

def device_property(device, field_name):
    return html.Div( [html.Span(field_name, style={'font-weight': 'bold'}), ': ', html.Span(device[field_name]) ],  style={'width': '100%'}) 

def device_info_2(device):
    head = [html.H2(device[K_ID]+" : "+device[K_NAME]), html.H4(device[K_DEVICE_TYPE])]
    
    children = []
    for field_name, field in device.field_items():
        children.extend(device_property_2(device, field_name))    
    return html.Div([html.Div(head),html.Dl(children,id='device-%s'%device.id)])

def device_property_2(device, field_name):
    return [html.Dt(field_name, style={'font-weight': 'bold'}),   html.Dd(device[field_name] , style={'width': '100%'})]



def device_table(devices): 
    tbl = dash_table.DataTable(
    id='table',
    columns=[{"name":k, "id":k} for k in TBL_COLUMNS],
    data=device_table_data(devices),     
    style_table={
        'maxHeight': '1200px',
        'overflowY': 'scroll', 
        'width':'400px'
    },
    style_cell={
        'height': 'auto',
        #'width': '20px', 'maxWidth': '80px',
        'whiteSpace': 'normal'
    },
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left', 
            'maxWidth': '200px',
            'height': 'auto',
        } for c in [K_NAME]
    ]+[    
    {
        'if': {'column_id': c},
        'width': '10px',
    } for c in [K_QUANTITY]
    ]+[    
    {
        'if': {'column_id': c},
        'textAlign': 'left', 
        'width': '20px',
    } for c in [K_ID]
    ],
    #fixed_rows={ 'headers': True, 'data': 0 },
    #row_selectable='multi',
    #style_cell={'width': '150px'}
    )
    return tbl
    #return html.Div(tbl, style={'width':'600px'})
    
       

def device_table_data(devices):
    return [dict(device) for device in devices]

def device_output(devices):
    childs = device_output_children(devices)
    return html.Div(childs, id='device_output', style={'column-count':2, 'maxHeight':'400px'})

def device_output_children(devices):
    #return str(list(devices.device_keys()))    
    if not devices or not len(devices):
        return "Click on table row for device informations"
    return [device_info(device) for device in devices]

def result_summary(devices):
    return html.Div(result_summary_children(devices),id="result-summary")    

def result_summary_children(devices):
    return "Found %d device type leading to a quantity of %d devices"%(len(devices), sum((d[K_QUANTITY] or 0 for d in devices)) )

def layout(devices):
    global app_data
    app_data = {'all_devices':devices, 'filtered_devices':devices, 'selected_devices':None}
    return html.Div([
        html.Div( form(devices) ),
        html.Hr(style={'border': '5px solid #888888', 
                       'border-radius': '5px'}), 
        html.Div( result_summary(devices)), 
        html.Div(html.Table(html.Tr([
                html.Td(html.Div( device_table(devices)), style={'vertical-align':'top'}), 
                html.Td(html.Div( device_output(app_data['selected_devices']) , style={'display':'inline', 'height':'400px', 'overflowY':'scroll', }), style={'vertical-align':'top'})            
            ]), 
            ), style={'margin-left':'10px'}),                
        ], style={'margin-left':'50px', 'margin-right':'50px'}) 
    

def make_callbacks(app, devices):
        
    inputs = [Input(component_id='search-field', component_property='value')]+\
             [Input(component_id=k, component_property='value') for k in DROPDOWN_FIELDS]
            
    @app.callback(
    [Output(component_id='table', component_property='data'), 
    Output(component_id='result-summary', component_property='children')
    ],
    inputs
    )
    def tbl_callback(*args):
        app_data['filtered_devices'] = filter_device(app_data['all_devices'],*args)
        return device_table_data(app_data['filtered_devices']), result_summary_children(app_data['filtered_devices']) 
        
    @app.callback(
    Output('device_output','children'),
    [
     Input('table', 'active_cell')
    ])
    def tbl_callback(active_cell):
        #either:
        #selected_rows=[rows[i] for i in selected_row_ids]
                
        if not active_cell:
            app_data['selected_devices'] = None
        else:
            app_data['selected_devices'] = app_data['all_devices'].filter_device( K_ID, ('==',active_cell['row_id']))                      
        return device_output_children(app_data['selected_devices'])
    
    
    # @app.callback(
    # Output('table','style_data_conditional'),
    # [
    #  Input('table', 'active_cell')
    # ])
    # def tbl_styling_callback(active_cell):
    #     if active_cell:
    #         return [{
    #         "if": {"row_index": active_cell['row']},
    #         "backgroundColor": "#3D9970",
    #         'color': 'white'
    #         }]
    #     else: 
    #         return []
    
    
    def reset_device_type(*args):
        return ''
        



