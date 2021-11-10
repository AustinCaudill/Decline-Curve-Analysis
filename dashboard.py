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



navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("Decline Curve Generator", class_name="navbar-brand")),
                    ],
                    align="center",
                ),
                href="",
                style={"textDecoration": "none"},
            ),
        ],
        class_name="navbar navbar-expand-lg navbar-dark bg-primary",
    ),
)

inputs = dbc.Card(
    [
        dcc.Input(
        id="q_init",
        placeholder='Initial Rate (STB/day)',
        type='number',
        value='1000',
        className="my-4 p-4"
        ),
        dcc.Input(
        id="q_next",
        placeholder='Next Rate (STB/day)',
        type='number',
        value='900',
        className="my-4 p-4"
        ),
        dcc.Input(
        id="t_months",
        placeholder='Time (Months)',
        type='number',
        value='1',
        className="my-4 p-4"
        ),
        dcc.Input(
        id="t_tot",
        placeholder='Project Life',
        type='number',
        value='120',
        className="my-4 p-4"
        ),
    ]
)

card = dbc.Card([dbc.CardHeader("Header"), dbc.CardBody("Body", style={"height": 250})])

graph_card = dbc.Card(
    dbc.CardBody([dcc.Graph(id="fig", style={"height": 400})]), className="my-4"
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col([card, inputs], width=3),
                dbc.Col(
                    [
                        graph_card,
                    ],
                    width=8,
                ),
            ]
        ),
    ],
    fluid=True,
    class_name="dbc_dark",
)

@app.callback(
    Output('fig', 'figure'),
    Input('q_init', 'value'),
    Input('q_next', 'value'),
    Input('t_months', 'value'),
    Input('t_tot', 'value'))

def update_fig(q_init,q_next,t_months, t_tot):
    # Input Data
    t = np.arange(0.1,int(t_tot),0.5) # 120 months by 1/2 month
    t_0m = 0 # month
    q_init = int(q_init)
    q_next = int(q_next)
    t_months = int(t_months)

    # Exponential Decline

    b = np.log(q_init/q_next)/(t_months - t_0m)
    q = q_init * np.exp(-b * t) # Forecast
    Np = (q_init - q) * 365/(b * 12)

    # Plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=t, y=q, name='Rate (q)', line=dict(color='green', width=4)))
    fig.add_trace(go.Scatter(x=t, y=(Np/1000000), name='Cum Production (Np)', line=dict(color='green', width=4, dash='dash')), secondary_y=True)

    # Set x-axis title
    fig.update_xaxes(title_text="Time in Months")

    # Set y-axes titles
    fig.update_yaxes(title_text="Rate (STB/Day)", secondary_y=False)
    fig.update_yaxes(title_text="Cum Production (MMSTB)", secondary_y=True)

    fig.update_layout(
        title={'text': "Exponential", 'xanchor': "center"},
        legend={
        'yanchor': "top",
        'xanchor': "right",
        }
        )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)