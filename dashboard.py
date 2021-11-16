""" 
Austin Caudill
11/11/2021
 """

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_bootstrap_templates import load_figure_template
load_figure_template("slate")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = 'Decline Curve Generator' 
server = app.server


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("The Petro Guy", href="https://www.thepetroguy.com", target="_new")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("UNAVAILABLE", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Explore",
        )],
    brand="Decline Curve Generator",
    brand_href="#",
    color="primary",
    dark=True,
    class_name="mb-4",
)

body_md = dcc.Markdown('''

Exponential: b = 0

Hyperbolic:  0< b <1

Hyperbolic:  b = 1


[Equations](https://www.researchgate.net/figure/Summary-of-Arps-Equations-Poston-and-Poc-2008_fig1_316103542)
''')

notes_md = dcc.Markdown('''

There are 2 methods of inputting data for plotting:

1. Manually edit the cells to contain your data. Add and remove rows as needed.

2. You may copy and paste your own data into the table. Note that you MUST have the required number of rows in the table BEFORE pasting in your data.

Only NUMBERS and INTEGERS are supported in the databale, i.e. 12345.12 is permissible while 1,2345.12 is not.
''')



Body = html.Div(
    [
        dbc.Card(
            dcc.Input(
                id="b_value",
                placeholder='B-Value',
                type='number',
                value='0',
                min="0",
                max="1",
                step="0.1"
                 ),
            className="mb-3",
        ),
        dbc.Card(body_md, body=True),
    ]
)


footer = html.Div(
        dbc.Row(dbc.Card(("© 2021 Austin Caudill"), className="text-center p-2"))
)

inputs = dbc.CardGroup(
        [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Initial Rate (qi)", className="card-title"),
                    html.P(
                        "Input the initial rate, qi, in STB/day.",
                        className="card-text",
                    ),
                    dcc.Input(
                    id="q_init",
                    placeholder='Initial Rate (STB/day)',
                    type='number',
                    value='1000',
                    min='1',
                    className="me-auto"
                    )
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Production Rate (qt)", className="card-title"),
                    html.P(
                        "Input the production rate, qt, at time (t) in STB/day.",
                        className="card-text",
                    ),
                    dcc.Input(
                    id="q_next",
                    placeholder='Current Rate (STB/day)',
                    type='number',
                    value='900',
                    min='0',
                    className="me-auto"
                    )
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Cum Time (t)", className="card-title"),
                    html.P(
                        "Input the cumulative time, in months, since start of production.",
                        className="card-text",
                    ),
                    dcc.Input(
                    id="t_months",
                    placeholder='Time (Months)',
                    type='number',
                    value='1',
                    min='1',
                    className="me-auto"
                    )
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Time to Generate", className="card-title"),
                    html.P(
                        "Input the total amount of months to plot.",
                        className="card-text",
                    ),
                    dcc.Input(
                    id="t_tot",
                    placeholder='Project Life',
                    type='number',
                    value='120',
                    min='1',
                    className="me-auto"
                    )
                ]
            )
        ),
        ]
)

sidebar = dbc.Card([dbc.CardHeader("Choose b-value"), dbc.CardBody(Body, style={})])

notes = dbc.Card([dbc.CardHeader("Notes"), dbc.CardBody(notes_md, style={})], class_name="mb-4")

graph_card = dbc.Card(
    dbc.CardBody([dcc.Graph(id="fig", style={"height": 400})]), className="my-4"
)

params = [
    'Month', 'Oil', 'Water', 'Gas'
]

prod_table = html.Div([
    dash_table.DataTable(
        id='prod_table',
        columns=(
            [{'id': p, 'name': p} for p in params]
        ),
        data=[
            dict(Model=i, **{param: 0 for param in params})
            for i in range(1, 10)
        ],
        style_header={
        'backgroundColor': '#515960',
        'color': '#aaaaaa',
        'border': '#141619 1px solid'
        },
        style_data={
        'backgroundColor': '#32383e',
        'border': '#141619 1px solid'
        },
        style_cell={'textAlign': 'center'},
        editable=True,
        row_deletable=True,
        # export_format="csv",
    ),
    dbc.Button('Add Row', id='editing-rows-button', n_clicks=0, color="secondary", className="me-1 mb-4"),
],
className="d-grid gap-2",
)


app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col([sidebar], width=3),
                dbc.Col(
                    [
                        dbc.Row(inputs),
                        graph_card,
                    ],
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col([notes], width=3),
                dbc.Col(
                    [
                        prod_table
                    ],
                    width=8,
                ),
            ]
        ),
        footer,
    ],
    fluid=True,
)

@app.callback(
    Output('prod_table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('prod_table', 'data'),
    State('prod_table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '0' for c in columns})
    return rows
   
@app.callback(
    Output('fig', 'figure'),
    Input('q_init', 'value'),
    Input('q_next', 'value'),
    Input('t_months', 'value'),
    Input('t_tot', 'value'),
    Input('b_value', 'value'),
    Input('prod_table', 'data'),
    Input('prod_table', 'columns'))
def update_fig(q_init,q_next,t_months, t_tot, b_value, rows, columns):
    # Input Data
    t_tot = int(t_tot)
    t = np.arange(0.1,t_tot,0.5) # 120 months by 1/2 month
    t_0m = 0 # month
    q_init = int(q_init)
    q_next = int(q_next)
    t_months = int(t_months)
    b_value = float(b_value)

    D = np.log(q_init/q_next)/(t_months - t_0m) # Decline Rate

    def determine_decline(value, q_init, t, D):
        if value == 0:
            decline_choice = "Exponential"
            q = q_init*np.exp(-t*D)
            Np = (((q_init**b_value) / ((1 - b_value) * D)) * ((q_init ** (1 - b_value)) - (q ** (1 - b_value))))
        elif 0< value <1:
            decline_choice = "Hyperbolic"
            q = q_init*np.power((1+b_value*D*t),(-(1/b_value)))
            Np = (((q_init**b_value) / ((1 - b_value) * D)) * ((q_init ** (1 - b_value)) - (q ** (1 - b_value))))
        elif value == 1:
            decline_choice = "Harmonic"
            q = q_init*np.power((1+b_value*D*t),(-1/b_value))
            Np = (q_init/D)*np.log(q_init/q)
        else:
            decline_choice = "Invalid b-value"   
        return decline_choice, q, Np 

    decline_choice, q, Np = determine_decline(b_value, q_init, t, D)
 

    # Plot Calculations
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=t, y=q, name='Rate (q)', line=dict(color='white', width=4)))
    fig.add_trace(go.Scatter(x=t, y=(Np), name='Cum Production (Np)', line=dict(color='white', width=4, dash='dash')), secondary_y=True)

    # Plot User Inputted Production Values
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    df['Oil'] = df['Oil'].astype(float)
    df['Oil'] = df['Oil'].div(30.437)
    df['Water'] = df['Water'].astype(float)
    df['Water'] = df['Water'].div(30.437)
    df['Gas'] = df['Gas'].astype(float)
    df['Gas'] = df['Gas'].div(30.437)
    fig.add_trace(go.Scatter(x=df.index, y=df['Oil'], name='Oil Production', line=dict(color='green', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Water'], name='Water Production', line=dict(color='blue', width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Gas'], name='Gas Production', line=dict(color='red', width=1)))

    # Set x-axis title
    fig.update_xaxes(title_text="Cumulative Time (Months)")

    # Set y-axes titles
    fig.update_yaxes(title_text="Rate (STB/Day)", secondary_y=False)
    fig.update_yaxes(title_text="Cum Production (MMSTB)", secondary_y=True)

    fig.update_layout(
        title={'text': f"{decline_choice} Decline Curve"},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
        )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)