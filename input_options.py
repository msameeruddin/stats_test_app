import dash_core_components as dcc
import dash_html_components as html
import dash_table

max_col = 5

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'height' : '44px'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

test_types_stats = dcc.Dropdown(
    id='test-type',
    options=[
        {'label' : 'Chi2-test', 'value' : 'chi2test'}, 
        {'label' : 'T-test', 'value' : 'ttest'}
    ],
    value='chi2test',
    clearable=False,
    searchable=False,
)

alpha_levels = dcc.Dropdown(
    id='alpha-level',
    options=[
        {'label' : '1%', 'value' : 0.01}, 
        {'label' : '2.5%', 'value' : 0.025}, 
        {'label' : '5%', 'value' : 0.05}
    ],
    value=0.05,
    clearable=False,
    searchable=False,
)

essential_inputs = html.Div([
    html.Div([
        html.Div(
            id='stat-type-test',
            children=[html.P('Test Type')], 
            className='three columns'
        ),
        
        html.Div([test_types_stats], className='three columns'),
        
        html.Div(
            id='alpha-level-val',
            children=[html.P('Select Alpha')], 
            className='three columns'
        ),

        html.Div([alpha_levels], className='three columns')
    ], className='row')
], className='six columns')

utable_comp = html.Div([
    html.Div([
        dcc.Upload(
            id='upload-data-file',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            multiple=True
        ),
    ], className='upload-component'),
    html.P('* Please ensure that the data is already processed.', style={'color' : '#A610F1'}),
    html.Div(id='upload-option-show')
], style={'paddingTop' : 30})

ctable_comp = html.Div([
    html.Div([
        html.Div([
            dcc.Input(
                id='adding-rows-name',
                placeholder='New column name',
                value='',
            ),
        ], className='six columns'),
        html.Div([
            html.Button('Add Column', id='adding-rows-button', n_clicks=0)
        ], className='six columns')
    ], className='row', style={'height': 50}),

    html.Div([
        dash_table.DataTable(
            id='adding-rows-table',
            columns=[{
                'name': 'Column {}'.format(i),
                'id': 'column-{}'.format(i),
                'deletable': True,
                'renamable': True
            } for i in range(1, max_col)],
            data=[
                {'column-{}'.format(i): None for i in range(1, max_col)}
            ],
            editable=True,
            row_deletable=True
        ),
        html.Div([
            html.Button('Add Row', id='editing-rows-button', n_clicks=0),
        ], style={'paddingTop' : 10})
    ]),
], style={'paddingTop' : 30})

#############################################

main_layout = html.Div([
    html.Meta(charSet='UTF-8'),
    html.Meta(name='viewport', content='width=device-width, initial-scale=1.0'),

    html.Div([
        html.Div([
            html.H3('Statistical Hypothesis Testing', style={'textAlign' : 'center'})
        ], className='header-part'),

        html.Div([
            essential_inputs,
            html.Div([
                html.Button('Compute Test', id='compute-test', n_clicks=0)
            ], className='six columns', style={'textAlign' : 'center'})
        ], className='input-part row'),

        html.Div([
            dcc.Tabs(
                id='table-create-upload-option',
                value='c-table',
                children=[
                    dcc.Tab(
                        label='Upload Your Data',
                        value='u-table',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[utable_comp]
                    ),
                    dcc.Tab(
                        label='Create Your Data',
                        value='c-table',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[ctable_comp]
                    ),
                ]
            )
        ]),
        html.Div(id='output-conclusion')
    ], className='container')
])