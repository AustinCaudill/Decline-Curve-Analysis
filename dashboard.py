""" 
Austin Caudill
11/17/2021
V2
 """
import time
from inspect import EndOfBlock
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
                dbc.DropdownMenuItem("GitHub Repo", href="https://github.com/AustinCaudill/Petroleum-Engineering-Basics"),
                dbc.DropdownMenuItem("Donate", href="https://www.paypal.com/donate/?business=FL4XB8U8KC4UU&no_recurring=0&item_name=Thank+you+for+supporting+my+work.&currency_code=USD"),
            ],
            nav=True,
            in_navbar=True,
            label="Explore",
        )],
    brand="Decline Curve Generator V2.0",
    brand_href="#",
    color="primary",
    dark=True,
    class_name="mb-4",
)

body_md = dcc.Markdown('''

Exponential: b = 0

Hyperbolic:  0< b <1

Harmonic:  b = 1


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
                value='1',
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
    [
        dbc.Button(
            "Found this app useful - Donate!", href="https://www.paypal.com/donate/?business=FL4XB8U8KC4UU&no_recurring=0&item_name=Thank+you+for+supporting+my+work.&currency_code=USD", target='_blank', id="example-button", outline=True, color="success", className="me-1"
        ),
        html.Span(id="example-output", style={"verticalAlign": "middle"}),
        dbc.Row(dbc.Card(("© 2021 Austin Caudill"), className="text-center p-2")),
    ],
    className="d-grid",
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
                    value='1065',
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
                    value='5',
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
                    value='26',
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
                    value='50',
                    min='1',
                    className="me-auto"
                    )
                ]
            )
        ),
        ]
)

sample_data = html.Div(
    [
        dcc.Dropdown(
            id="radios",
            className="mb-4",
            options=[
                {"label": "Clear Sample Data", "value": 1},
                {"label": "BOZEMAN UNIT 802WA", "value": 2},
                {"label": "LYNN UNIT 2H", "value": 3},
                {"label": "GOLDSMITH-LANDRETH/SAN ANDRES/UT 211R", "value": 4},
            ],
            value=2,
        ),
        html.Div(id="output"),
    ],
    className="radio-group",
)

sidebar = dbc.Card([dbc.CardHeader("Choose b-value"), dbc.CardBody(Body, style={})], className="")

samples = dbc.Card([dbc.CardHeader("Sample Data"), dbc.CardBody(sample_data, style={})])

notes = dbc.Card(
    [
        dbc.CardHeader("Notes"), 
        dbc.Badge("Warning", color="warning", className="me-1"),
        dbc.CardBody(notes_md, style={})
    ], 
    class_name="mb-4"
)

graph_card = dbc.Card(
    dbc.CardBody(
        [
            dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        ),
            dcc.Graph(id="fig", style={"height": 400})
        ]
        ), 
        className="my-4"
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
            for i in range(1, 1)
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
                dbc.Col(
                    [
                        dbc.Col([sidebar]),
                        dbc.Col([samples])
                    ],
                    width=3,
                ),
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

@app.callback(Output("loading-output-1", "children"), Input("radios", "value"))
def input_triggers_spinner(value):
    time.sleep(2)
    return

@app.callback(
    Output("output", "children"), 
    Input("radios", "value"))
def well_information(value):
    if value == 2:
        # table_header = [html.Thead(html.Tr([html.Th("Property"), html.Th("Value")]))]
        row1 = html.Tr([html.Td("Well Name:"), html.Td("BOZEMAN UNIT 802WA")])
        row2 = html.Tr([html.Td("API:"), html.Td("42-329-41603-0000")])
        row3 = html.Tr([html.Td("Basin:"), html.Td("Permian")])
        row4 = html.Tr([html.Td("Operator:"), html.Td("Diamondback E&P LLC")])
        table_body = [html.Tbody([row1, row2, row3, row4])]
        info_card = dbc.Table(table_body, bordered=True)
    elif value == 3:
        # table_header = [html.Thead(html.Tr([html.Th("Property"), html.Th("Value")]))]
        row1 = html.Tr([html.Td("Well Name:"), html.Td("LYNN UNIT 2H")])
        row2 = html.Tr([html.Td("API:"), html.Td("42-337-34517-0000")])
        row3 = html.Tr([html.Td("Basin:"), html.Td("Fort Worth Syncline")])
        row4 = html.Tr([html.Td("Operator:"), html.Td("EOG Resources, Inc")])
        table_body = [html.Tbody([row1, row2, row3, row4])]
        info_card = dbc.Table(table_body, bordered=True)
    elif value == 4:
        # table_header = [html.Thead(html.Tr([html.Th("Property"), html.Th("Value")]))]
        row1 = html.Tr([html.Td("Well Name:"), html.Td("GOLDSMITH-LANDRETH/SAN ANDRES/UT 211R")])
        row2 = html.Tr([html.Td("API:"), html.Td("42-135-41592-0000")])
        row3 = html.Tr([html.Td("Basin:"), html.Td("Permian")])
        row4 = html.Tr([html.Td("Operator:"), html.Td("KINDER MORGAN PRODUCTION CO LLC")])
        table_body = [html.Tbody([row1, row2, row3, row4])]
        info_card = dbc.Table(table_body, bordered=True)
    else:
        info_card = "No sample data selected."
    return info_card

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
    Input('prod_table', 'columns'),
    Input("radios", "value"))
def update_fig(q_init,q_next,t_months, t_tot, b_value, rows, columns, radios):
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
        elif 0< value < 1:
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

    # Plot user-selected sample data
    if radios == 2:
        sd2 = pd.read_csv("42-329-41603-0000.csv")
        sd2['Oil'] = sd2['Oil'].astype(float)
        sd2['Oil'] = sd2['Oil'].div(30.437)
        # sd2['Water'] = sd2['Water'].astype(float)
        # sd2['Water'] = sd2['Water'].div(30.437)
        sd2['Gas'] = sd2['Gas'].astype(float)
        sd2['Gas'] = sd2['Gas'].div(30.437)
        fig.add_trace(go.Scatter(x=sd2.index, y=sd2['Oil'], name='Oil Production', line=dict(color='green', width=1)))
        # fig.add_trace(go.Scatter(x=sd2.index, y=sd2['Water'], name='Water Production', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=sd2.index, y=sd2['Gas'], name='Gas Production', line=dict(color='red', width=1)))
    elif radios == 3:
        sd3 = pd.read_csv("42-337-34517-0000.csv")
        sd3.replace('-', '0', inplace=True)
        sd3['Oil'] = sd3['Oil'].astype(float)
        sd3['Oil'] = sd3['Oil'].div(30.437)
        sd3['Water'] = sd3['Water'].astype(float)
        sd3['Water'] = sd3['Water'].div(30.437)
        sd3['Gas'] = sd3['Gas'].astype(float)
        sd3['Gas'] = sd3['Gas'].div(30.437)
        fig.add_trace(go.Scatter(x=sd3.index, y=sd3['Oil'], name='Oil Production', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=sd3.index, y=sd3['Water'], name='Water Production', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=sd3.index, y=sd3['Gas'], name='Gas Production', line=dict(color='red', width=1)))
    elif radios == 4:
        sd4 = pd.read_csv("42-135-41592-0000.csv")
        sd4.replace('-', '0', inplace=True)
        sd4['Oil'] = sd4['Oil'].astype(float)
        sd4['Oil'] = sd4['Oil'].div(30.437)
        sd4['Water'] = sd4['Water'].astype(float)
        sd4['Water'] = sd4['Water'].div(30.437)
        sd4['Gas'] = sd4['Gas'].astype(float)
        sd4['Gas'] = sd4['Gas'].div(30.437)
        fig.add_trace(go.Scatter(x=sd4.index, y=sd4['Oil'], name='Oil Production', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=sd4.index, y=sd4['Water'], name='Water Production', line=dict(color='blue', width=1)))
        fig.add_trace(go.Scatter(x=sd4.index, y=sd4['Gas'], name='Gas Production', line=dict(color='red', width=1)))
    else:
        pass
    


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
    fig.update_yaxes(title_text="Rate (STB/Day or MCF/Day)", secondary_y=False)
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