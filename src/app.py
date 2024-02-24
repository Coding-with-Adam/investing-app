import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, State, Patch, no_update, ctx
import dash_bootstrap_components as dbc  #  version 1.4.0
import pandas as pd  # version 1.5.3
import plotly.express as px
import yfinance as yf

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"  # styling sheet
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CYBORG, dbc_css])
server = app.server


navbar = dbc.NavbarSimple(
            [
                dbc.Nav(
                    [
                        dbc.NavLink(page["name"], href=page["path"], style={'color':'white'})
                        for page in dash.page_registry.values()
                    ],
                ),
            ],
            brand='My Investments Portfolio',
            dark=True,
            color='primary',
            className="mb-2",
)

app.layout = dbc.Container(
    [

        navbar,
        dash.page_container


    ], fluid=True, className="dbc"  # incorporates the dbc_css from above)
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8055)
