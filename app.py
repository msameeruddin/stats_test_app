import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import pandas as pd

import base64
import datetime
import io

from dash.dependencies import (Input, Output, State)
from scipy.stats import (chi2_contingency, chi2, ttest_ind, t)
from input_options import main_layout

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

def parse_contents(contents, filename, date):
    content_string = contents[0].split(',')[1]
    decoded = base64.b64decode(content_string)
    
    fname, ext = filename[0].split('.')
    df = None

    try:
        if (ext == 'csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif (ext == 'xls'):
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        df = None
    
    return df

def get_test_response(data_matrix, test_type, alpha):
    data_response = []
    data_response.append([' ', 'Summary'])

    if (test_type == 'chi2test'):
        #### chi2 test ####
        prob, stat, critical, pval = compute_chi2_test(dtable=data_matrix, alpha=alpha)
        data_response.append(['Type Test', 'Chi2 Test'])
    elif (test_type == 'ttest'):
        #### t test ####
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

    return data_response
###################

max_col = 5
df = 0

app.layout = main_layout

@app.callback(
    Output('output-conclusion', 'children'),
    Input('table-create-upload-option', 'value')
)
def set_output_layout(which_tab):
    if (which_tab == 'c-table'):
        return html.Div([
            html.Div(id='output-for-create')
        ])
    elif (which_tab == 'u-table'):
        return html.Div([
            html.Div(id='output-for-upload')
        ])


@app.callback(
    Output('upload-option-show', 'children'),
    Input('upload-data-file', 'contents'),
    State('upload-data-file', 'filename'),
    State('upload-data-file', 'last_modified')
)
def parse_table_data(contents, filename, date):
    if contents is not None:
        global df
        df = parse_contents(contents, filename, date)
        return html.Div([
            dash_table.DataTable(
                id='input-table',
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i, 'renamable' : False, 'deletable' : False} for i in df.columns]
            ),
        ], style={'height' : 300, 'overflowY' : 'scroll'})

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

######################

@app.callback(
    Output('output-for-create', 'children'),
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
            data_matrix = [[float(j) for j in i] for i in data_matrix]
            data_response = get_test_response(data_matrix=data_matrix, test_type=test_type, alpha=alpha)
        except Exception as e:
            res = res
    
    if data_response:
        fig_table = ff.create_table(data_response)
        return html.Div([
            dcc.Graph(
                id='summary-ctable',
                figure=fig_table
            )
        ])
    return res


@app.callback(
    Output('output-for-upload', 'children'),
    Input('alpha-level', 'value'),
    Input('test-type', 'value'),
    Input('compute-test', 'n_clicks'),
)
def display_output_upload(alpha, test_type, n_clicks):
    data_response = []
    res = html.P("No Data Found", style={'paddingTop' : 20})
    
    if n_clicks > 0:
        try:
            data = df.to_numpy().T
            data_matrix = [[float(j) for j in i] for i in data]
            data_response = get_test_response(data_matrix=data_matrix, test_type=test_type, alpha=alpha)
        except Exception as e:
            res = res
    
    if data_response:
        fig_table = ff.create_table(data_response)
        return html.Div([
            dcc.Graph(
                id='summary-utable',
                figure=fig_table
            )
        ])
    return res







if __name__ == '__main__':
    app.run_server(debug=True)