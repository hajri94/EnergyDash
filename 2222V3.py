import base64
import datetime
import io
import plotly.graph_objs as go


import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd

from sqlalchemy import create_engine

# INSERT INTO "data1.db" (data, month, meter) VALUES (6666,'11-UU',844)

colors = {"graphBackground": "#F5F5F5", "background": "#ffffff", "text": "#000000"}



engine = create_engine('sqlite:///data.db', echo=False)



# Dash
def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app = dash.Dash()
app.layout = html.Div([
    dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
    html.P(id='saveSql', style={'display':'none'}),
    dcc.Input(
        id='sql-query',
        value='SELECT * FROM "floor1.db"',
        style={'width': '100%', 'display':'none'},
        type='text'
    ),
    html.Button('Read Data', id='run-query'),

    html.Hr(),

    html.Div([
        html.Div(id='table-container', className="four columns", style={'display': 'none'}),

        html.Div([
            html.Div([
                html.Div([
                    html.Label('Select X'),
                    dcc.Dropdown(
                        id='dropdown-x',
                        clearable=False,
                    )
                ], className="six columns"),
                html.Div([
                    html.Label('Select Y'),
                    dcc.Dropdown(
                        id='dropdown-y',
                        clearable=False,
                    )
                ], className="six columns")
            ], className="row"),
            html.Div(dcc.Graph(id='graph'), className="ten columns")
        ], className="eight columns")
    ], className="row"),

    # hidden store element
    html.Div(id='table-store', style={'display': 'none'}),

    #################################################################

    html.Div([
            dcc.Input(
                id='adding-rows-name',
                placeholder='Enter a column name...',
                value='',
                style={'padding': 10}
            ),
            html.Button('Add Column', id='adding-columns-button', n_clicks=0)
        ], style={'height': 50}),
        dcc.Interval(id='interval_pg', interval=86400000 * 7, n_intervals=0),
        # activated once/week or when page refreshed
        html.Div(id='postgres_datatable'),
        html.Button('Add Row', id='editing-rows-button', n_clicks=0),
        html.Button('Save to PostgreSQL', id='save_to_postgres', n_clicks=0),
        # Create notification when saving to excel
        html.Div(id='placeholder', children=[]),
        dcc.Store(id="store", data=0),
        dcc.Interval(id='interval', interval=1000)

])


@app.callback(Output('saveSql', 'children'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def update_graph(contents, filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        df.to_sql('floor1.db', con=engine, if_exists='replace')


def parse_data(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df

def update_table(contents, filename):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)

        table = html.Div(
            [
                html.H5(filename),
                dash_table.DataTable(
                    data=df.to_dict("rows"),
                    columns=[{"name": i, "id": i} for i in df.columns],
                ),
                html.Hr(),
                html.Div("Raw Content"),
                html.Pre(
                    contents[0:200] + "...",
                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
                ),
            ]
        )

    return table



@app.callback(
    dash.dependencies.Output('table-store', 'children'),
    [dash.dependencies.Input('run-query', 'n_clicks')],
    state=[dash.dependencies.State('sql-query', 'value')])
def sql(number_of_times_button_has_been_clicked, sql_query):
    dff = pd.read_sql_query(
        sql_query,
        engine
    )
    return dff.to_json()


@app.callback(
    dash.dependencies.Output('table-container', 'children'),
    [dash.dependencies.Input('table-store', 'children')])
def dff_to_table(dff_json):
    dff = pd.read_json(dff_json)
    return generate_table(dff)


@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('table-store', 'children'),
     dash.dependencies.Input('dropdown-x', 'value'),
     dash.dependencies.Input('dropdown-y', 'value')])
def dff_to_table(dff_json, dropdown_x, dropdown_y):
    dff = pd.read_json(dff_json)
    return {
        'data': [{
            'x': dff[dropdown_x],
            'y': dff[dropdown_y],
            'type': 'bar'
        }],
        'layout': {
            'margin': {
                'l': 20,
                'r': 10,
                'b': 60,
                't': 10
            }
        }
    }


@app.callback(
    dash.dependencies.Output('dropdown-x', 'options'),
    [dash.dependencies.Input('table-store', 'children')])
def create_options_x(dff_json):
    dff = pd.read_json(dff_json)
    return [{'label': i, 'value': i} for i in dff.columns]


@app.callback(
    dash.dependencies.Output('dropdown-y', 'options'),
    [dash.dependencies.Input('table-store', 'children')])
def create_options_y(dff_json):
    dff = pd.read_json(dff_json)
    return [{'label': i, 'value': i} for i in dff.columns]

############################################################
@app.callback(Output('postgres_datatable', 'children'),
              [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    df = pd.read_sql_table('floor1.db', con=engine)
    return [
        dash_table.DataTable(
            id='our-table',
            columns=[{
                         'name': str(x),
                         'id': str(x),
                         'deletable': False,
                     } if x == 'Month'
                     else {
                'name': str(x),
                'id': str(x),
                'deletable': True,
            }
                     for x in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",  # give user capability to sort columns
            sort_mode="single",  # sort across 'multi' or 'single' columns
            page_action='none',  # render all of the data at once. No paging.
            style_table={'height': '300px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'right'
                } for c in ['Month']
            ]
        ),
    ]

@app.callback(
    Output('our-table', 'columns'),
    [Input('adding-columns-button', 'n_clicks')],
    [State('adding-rows-name', 'value'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def add_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'name': value, 'id': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns

@app.callback(
    Output('our-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('our-table', 'data'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows




@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_postgres', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our-table', 'data'),
     State('store', 'data')],
    prevent_initial_call=True)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("The data has been saved to  database.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})
    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_triggered == "save_to_postgres":
        s = 6
        pg = pd.DataFrame(dataset)
        pg.to_sql('floor1.db', con=engine, if_exists='replace', index=False)
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s



app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True)