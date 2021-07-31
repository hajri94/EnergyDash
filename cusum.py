import pandas as pd
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from app import app
from dash.dependencies import Input, Output

df = pd.read_excel('EleConsumption.xlsx', sheet_name='CusumGround')
df2 = pd.read_excel('EleConsumption.xlsx', sheet_name='CusumFirst')
df3 = pd.read_excel('EleConsumption.xlsx', sheet_name='CusumSecond')
df4 = pd.read_excel('EleConsumption.xlsx', sheet_name='CusumThird')

cusum1 = html.Div([dcc.Graph(
    figure=px.line(df, x='Month', y='Cusum(666)', title='central AC, Amphitheatre, '
                                                        'B-003 -> B-006 ')
), dcc.Graph(
    figure=px.line(df, x='Month', y='Cusum(667)', title='student affairs-mezzanine, '
                                                                                       'frontDesk ')
)])

cusum2 = html.Div([dcc.Graph(
    figure=px.line(df2, x='Month', y='Cusum(670)', title='B-105 -> B-108')
), dcc.Graph(
    figure=px.line(df2, x='Month', y='Cusum(669)', title='IT office, server room - '
                                                                                       'student life office, B-100 ')
), dcc.Graph(
    figure=px.line(df2, x='Month', y='Cusum(659)', title='library')
), dcc.Graph(
    figure=px.line(df2, x='Month', y='Cusum(658)', title='Boxes & B-111 -> B-115')
)])

cusum3 = html.Div([dcc.Graph(
    figure=px.line(df3, x='Month', y='Cusum(672)', title='B-204 -> B-210')
), dcc.Graph(
    figure=px.line(df3, x='Month', y='Cusum(671)', title='B-200 -> B-203 & kitchen')
)])

cusum4 = html.Div([dcc.Graph(
    figure=px.line(df4, x='Month', y='Cusum(674)', title='B-300 -> B-303')
)])

cusumGraph = html.Div([
    dcc.Tabs(id="tabs-cusum", value='tab-1', children=[
        dcc.Tab(label='ground', value='Groundfloor'),
        dcc.Tab(label='floor 1', value='floorOne'),
        dcc.Tab(label='floor 2', value='floorTwo'),
        dcc.Tab(label='floor 3', value='floorThree')
    ]),
    html.Div(id='tabs-content-cusum')
]

)


@app.callback(Output('tabs-content-cusum', 'children'),
              Input('tabs-cusum', 'value'))
def render_content(tab):
    if tab == 'Groundfloor':
        return html.Div([
            cusum1
        ])
    elif tab == 'floorOne':
        return html.Div([
            cusum2
        ])
    elif tab == 'floorTwo':
        return html.Div([
            cusum3
        ])
    elif tab == 'floorThree':
        return html.Div([
            cusum4
        ])
