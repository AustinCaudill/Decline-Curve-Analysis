""" 
Austin Caudill
11/11/2021
 """

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_bootstrap_templates import load_figure_template
load_figure_template("slate")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = 'Decline Curve Generator' 


LOGO = ""



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
        dbc.Row(dbc.Card(("© 2021 Austin Caudill"), className="text-center"))
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
                    className="me-auto"
                    )
                ]
            )
        ),
        ]
)

sidebar = dbc.Card([dbc.CardHeader("Choose b-value"), dbc.CardBody(Body, style={"height": 400})])

graph_card = dbc.Card(
    dbc.CardBody([dcc.Graph(id="fig", style={"height": 400})]), className="my-4"
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
        footer,
    ],
    fluid=True,
)



    
@app.callback(
    Output('fig', 'figure'),
    Input('q_init', 'value'),
    Input('q_next', 'value'),
    Input('t_months', 'value'),
    Input('t_tot', 'value'),
    Input('b_value', 'value'))
def update_fig(q_init,q_next,t_months, t_tot, b_value):
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
 

    # Plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=t, y=q, name='Rate (q)', line=dict(color='green', width=4)))
    fig.add_trace(go.Scatter(x=t, y=(Np), name='Cum Production (Np)', line=dict(color='green', width=4, dash='dash')), secondary_y=True)

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
    app.run_server(debug=False)