# -*- coding: utf-8 -*-
import datetime
import os.path as op
import plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event
import pandas as pd
import pyodbc
import numpy as np

UPDATE_TIME = 60  # seconds

app = dash.Dash()

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

df = pd.DataFrame(columns=['VgTrd', 'ThTrd'])

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(children=[html.H4(children=["Vega, Theta Traded"], style={'text-align': 'right'})],
                 style={'width': '150px', 'font-family': 'sans-serif', 'color': '#5282b2', 'justify-content': 'right'}),
        html.Div(children=[
            dcc.Graph(id='tv-graph'),
        ], style={'flex-grow': 1})
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(children=[html.H4(children=["Recent Trades"], style={'text-align': 'center'})],
             style={'font-family': 'sans-serif', 'color': '#5282b2', 'justify-content': 'center'}),
    html.Div(children=[dcc.Graph(id='trades-table')],
             style={'align-items': 'center', 'justify-content': 'center'}),
    html.Div(children=[html.H4(children=["Top Trade Names"], style={'text-align': 'center'})],
             style={'font-family': 'sans-serif', 'color': '#5282b2', 'justify-content': 'center'}),
    html.Div(children=[dcc.Graph(id='trades-agg-table')],
             style={'align-items': 'center', 'justify-content': 'center'}),
    html.Div(children=[dcc.Checklist(id='tv-checkboxes',
                                     options=[{'label': 'Vega', 'value': 'VgTrd'},
                                              {'label': 'Theta', 'value': 'ThTrd'}],
                                     values=['VgTrd', 'ThTrd'])], hidden=True),
    dcc.Interval(id='interval-comp',
                 interval=UPDATE_TIME * 1000)
], style={'width': '100%'})


@app.callback(Output('trades-table', 'figure'),
              [Input('tv-checkboxes', 'values')],
              events=[Event('interval-comp', 'interval')])
def update_trades(checks):
    data = new_trades_data()
    table = ff.create_table(data,
                            height_constant=20,
                            colorscale=[[0, '#5f99cb'], [.5, '#ebf3f9'], [1, '#ffffff']],
                            font_colors=['#ffffff', '#5282b2', '#5282b2'])
    return table


@app.callback(Output('trades-agg-table', 'figure'),
              [Input('tv-checkboxes', 'values')],
              events=[Event('interval-comp', 'interval')])
def update_agg(checks):
    data = new_agg_data()
    table = ff.create_table(data,
                            height_constant=20,
                            colorscale=[[0, '#5f99cb'], [.5, '#ebf3f9'], [1, '#ffffff']],
                            font_colors=['#ffffff', '#5282b2', '#5282b2'])
    return table


@app.callback(Output('tv-graph', 'figure'),
              [Input('tv-checkboxes', 'values')],
              events=[Event('interval-comp', 'interval')])
def update_tv(checks):
    checks = ['VgTrd', 'ThTrd']
    global df
    dff = df.copy()
    if dff.empty:
        dff = new_bar_data()
    elif dff.index[-1] + datetime.timedelta(seconds=UPDATE_TIME - 1) <= datetime.datetime.now():
        new_data = new_bar_data()
        if not np.array_equal(dff.tail(1).values, new_data.values):
            dff = dff.append(new_data)
    dff = dff.tail(2)
    df = dff

    plt = plotly.tools.make_subplots(rows=1, cols=len(checks), shared_yaxes=True,
                                     shared_xaxes=True, vertical_spacing=0, horizontal_spacing=0.05)

    col = 1
    for trade_type in checks:
        data = dff[trade_type]
        head = data.head(1)
        if len(data.index) > 1:
            tail = data.tail(1)

            prev_trace = go.Bar(
                x=[trade_type],
                y=head.values,
                text=str(head.values[0]),
                textposition='auto',
                name=head.index[0].strftime("%I:%M:%S"),
                hoverinfo='skip',
                showlegend=(True if col == 1 else False),
                insidetextfont=dict(
                    color='rgba(82, 130, 178, 1)'
                ),
                outsidetextfont=dict(
                    color='rgba(82, 130, 178, 1)'
                ),
                marker=dict(
                    color='rgba(55, 128, 191, 0.1)',
                    line=dict(
                        color='rgba(55, 128, 191, 0.5)',
                        width=2,
                    )
                )
            )
            plt.append_trace(prev_trace, 1, col)

            curr_trace = go.Bar(
                x=[trade_type],
                y=tail.values,
                text=str(tail.values[0]),
                textposition='auto',
                name=tail.index[0].strftime("%I:%M:%S"),
                hoverinfo='skip',
                showlegend=(True if col == 1 else False),
                insidetextfont=dict(
                    color='rgba(255, 255, 255, 1)'
                ),
                outsidetextfont=dict(
                    color='rgba(82, 130, 178, 1)'
                ),
                marker=dict(
                    color='rgba(55, 128, 191, 0.8)',
                    line=dict(
                        color='rgba(55, 128, 191, 1.0)',
                        width=2,
                    )
                )
            )
            plt.append_trace(curr_trace, 1, col)
        else:
            curr_trace = go.Bar(
                x=[trade_type],
                y=head.values,
                text=str(head.values[0]),
                textposition='auto',
                name=head.index[0].strftime("%I:%M:%S"),
                hoverinfo='skip',
                showlegend=(True if col == 1 else False),
                insidetextfont=dict(
                    color='rgba(255, 255, 255, 1)'
                ),
                outsidetextfont=dict(
                    color='rgba(82, 130, 178, 1)'
                ),
                marker=dict(
                    color='rgba(55, 128, 191, 0.8)',
                    line=dict(
                        color='rgba(55, 128, 191, 1.0)',
                        width=2,
                    )
                )
            )
            plt.append_trace(curr_trace, 1, col)
        col += 1

    plt['layout'].update(font=dict(family='sans-serif', color='#5282b2'), margin=dict(l=50, r=50, t=25, b=25),
                         legend=dict(x=0.01, y=0.02, bordercolor='#5f99cb', bgcolor='#ebf3f9'))
    plt['layout']['xaxis1'].update(gridcolor='rgba(82, 130, 178, 0.1)', zerolinecolor='#5282b2')
    plt['layout']['xaxis2'].update(gridcolor='rgba(82, 130, 178, 0.1)', zerolinecolor='#5282b2')

    return plt


def new_bar_data():
    with open(op.join(op.abspath(op.join(__file__, op.pardir)), 'sql', 'Query-BarChart.sql'), "r") as f:
        sql = f.read()
    cnxn = pyodbc.connect("Driver={SQL Server};Server=[server];UID=[user];PWD=[pw];Database=stocks;")
    data = pd.read_sql_query(sql, cnxn)
    cnxn.close()
    data.index = [datetime.datetime.now()]
    return data


def new_trades_data():
    with open(op.join(op.abspath(op.join(__file__, op.pardir)), 'sql', 'Query-TopPanel.sql'), "r") as f:
        sql = f.read()
    cnxn = pyodbc.connect("Driver={SQL Server};Server=[server];UID=[user];PWD=[pw];Database=stocks;")
    data = pd.read_sql_query(sql, cnxn)
    cnxn.close()
    return data


def new_agg_data():
    with open(op.join(op.abspath(op.join(__file__, op.pardir)), 'sql', 'Query-BottomPanel.sql'), "r") as f:
        sql = f.read()
    cnxn = pyodbc.connect("Driver={SQL Server};Server=[server];UID=[user];PWD=[pw];Database=stocks;")
    data = pd.read_sql_query(sql, cnxn)
    cnxn.close()
    return data


if __name__ == '__main__':
    app.run_server(port=8050, debug=False, host='0.0.0.0')
