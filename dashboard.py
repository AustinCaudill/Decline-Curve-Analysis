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

Body = dcc.RadioItems(
    id="decline_choice",
    options=[
        {'label': 'Exponential', 'value': 'EXP'},
        {'label': 'Hyperbolic', 'value': 'HYP'},
        {'label': 'Harmonic', 'value': 'HAR'}
    ],
    value='EXP',
    labelStyle={'display': 'flex'}
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

sidebar = dbc.Card([dbc.CardHeader("Types of Decline"), dbc.CardBody(Body, style={"height": 250})])

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
    Output('b', 'value'),
    Input('decline_choice', 'value'))
def select_decline(decline_choice):
    if decline_choice == 'EXP':
        b = 0
    elif decline_choice == 'HYP':
        b = 1
    elif decline_choice == 'HAR':
        b = 2    
    else:
        b = 0
    return b

@app.callback(
    Output('fig', 'figure'),
    Input('q_init', 'value'),
    Input('q_next', 'value'),
    Input('t_months', 'value'),
    Input('t_tot', 'value'),
    Input('decline_choice', 'value'))
def update_fig(q_init,q_next,t_months, t_tot, decline_choice):
    # Input Data
    t = np.arange(0.1,int(t_tot),0.5) # 120 months by 1/2 month
    t_0m = 0 # month
    q_init = int(q_init)
    q_next = int(q_next)
    t_months = int(t_months)

    D = np.log(q_init/q_next)/(t_months - t_0m) # Decline Rate
    q = q_init * np.exp(-D * t) # Forecast
    Np = (q_init - q) * 365/(D * 12) # Volume Produced

    # Plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=t, y=q, name='Rate (q)', line=dict(color='green', width=4)))
    fig.add_trace(go.Scatter(x=t, y=(Np/1000000), name='Cum Production (Np)', line=dict(color='green', width=4, dash='dash')), secondary_y=True)

    # Set x-axis title
    fig.update_xaxes(title_text="Cumulative Time (Months)")

    # Set y-axes titles
    fig.update_yaxes(title_text="Rate (STB/Day)", secondary_y=False)
    fig.update_yaxes(title_text="Cum Production (MMSTB)", secondary_y=True)

    fig.update_layout(
        title={'text': "Decline Curves"},
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