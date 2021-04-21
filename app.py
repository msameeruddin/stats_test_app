import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff

from dash.dependencies import Input, Output, State
from scipy.stats import (chi2_contingency, chi2, ttest_ind, t)

###################
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'Hypothesis Testing'

server = app.server
###################

def compute_chi2_test(dtable, alpha):
    prob = 1 - alpha
    stat, pval, dof, expected = chi2_contingency(dtable)
    critical = chi2.ppf(prob, dof)
    return prob, round(stat, 3), round(critical, 3), round(pval, 3)

def compute_ttest_ind(dtable, alpha):
    prob = 1 - alpha
    dof = len(dtable[0]) * len(dtable) - len(dtable)
    samp1_vals = dtable[0]
    samp2_vals = dtable[1]
    stat, pval = ttest_ind(samp1_vals, samp2_vals)
    critical = t.ppf(prob, dof)
    return prob, round(stat, 3), round(critical, 3), round(pval, 3)

###################
max_col = 5

app.layout = html.Div([
    html.Meta(charSet='UTF-8'),
    html.Meta(name='viewport', content='width=device-width, initial-scale=1.0'),

    html.Div([
        html.Div([
            html.H3('Statistical Hypothesis Testing', style={'textAlign' : 'center'})
        ], className='header-part'),

        html.Div([
            html.Div([
                dcc.Input(
                    id='adding-rows-name',
                    placeholder='New column name',
                    value='',
                    style={'padding': 10}
                ),
            ], className='three columns'),
            html.Div([
                html.Button('Add Column', id='adding-rows-button', n_clicks=0)
            ], className='three columns')
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

        html.Div([
            html.Div([
                html.Div([
                    html.Div(
                        id='stat-type-test',
                        children=[
                            html.P('Test Type'),
                        ], className='three columns'
                    ),
                    
                    html.Div([
                        dcc.Dropdown(
                            id='test-type',
                            options=[
                                {'label' : 'Chi2-test', 'value' : 'chi2test'}, 
                                {'label' : 'T-test', 'value' : 'ttest'}
                            ],
                            value='chi2test',
                            clearable=False,
                            searchable=False,
                        )
                    ], className='three columns'),
                    
                    html.Div(
                        id='alpha-level-val',
                        children=[
                            html.P('Select Alpha'),
                        ], className='three columns'
                    ),

                    html.Div([
                        dcc.Dropdown(
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
                    ], className='three columns')
                ], className='row')
            ], className='six columns'),

            html.Div([
                html.Button('Compute Test', id='compute-test', n_clicks=0)
            ], className='six columns', style={'textAlign' : 'center'})

        ], className='input-part row'),

        html.Div([
            html.Div(id='output-conclusion')
        ])

    ], className='container')
])

@app.callback(
    Output('adding-rows-table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns')
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('adding-rows-table', 'columns'),
    Input('adding-rows-button', 'n_clicks'),
    State('adding-rows-name', 'value'),
    State('adding-rows-table', 'columns')
)
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns

@app.callback(
    Output('output-conclusion', 'children'),
    Input('alpha-level', 'value'),
    Input('test-type', 'value'),
    Input('compute-test', 'n_clicks'),
    Input('adding-rows-table', 'data'),
    Input('adding-rows-table', 'columns')
)
def display_output(alpha, test_type, n_clicks, rows, columns):
    data_response = []
    res = html.P("No Data Found", style={'paddingTop' : 20})
    
    if n_clicks > 0:
        try:
            data_matrix = [[row.get(c['id'], 0) for c in columns] for row in rows]
            if data_matrix:
                data_matrix = [[float(j) for j in i] for i in data_matrix]
                data_response.append([' ', 'Summary'])

                if (test_type == 'chi2test'):
                    #### chi2 test ####
                    prob, stat, critical, pval = compute_chi2_test(dtable=data_matrix, alpha=alpha)
                    data_response.append(['Type Test', 'Chi2 Test'])
                elif (test_type == 'ttest'):
                    #### chi2 test ####
                    prob, stat, critical, pval = compute_ttest_ind(dtable=data_matrix, alpha=alpha)
                    data_response.append(['Type Test', 'T Test (independant)'])

                data_response.append(['Level of Significance', alpha])
                data_response.append(['Probability', prob])
                data_response.append(['Calculated Value', stat])
                data_response.append(['Critical Value', critical])
                data_response.append(['p Value', pval])
                
                ### decision ###
                if pval <= alpha:
                    data_response.append(['Decision', 'Reject H0'])
                else:
                    data_response.append(['Decision', 'Accept H0'])
            else:
                res = res
        except Exception as e:
            res = res
    
    if data_response:
        fig_table = ff.create_table(data_response)
        return html.Div([
            dcc.Graph(
                id='summary-table',
                figure=fig_table
            )
        ], style={'paddingTop' : 20})
    return res








if __name__ == '__main__':
    app.run_server(debug=True)