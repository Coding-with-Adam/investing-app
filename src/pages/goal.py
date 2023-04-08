from dash import Dash, html, dcc, callback, Input, Output, no_update, register_page
import dash_bootstrap_components as dbc  #  version 1.4.0
import pandas as pd  # version 1.5.3
import plotly.express as px
from numerize import numerize

register_page(__name__)

input_style = {
    "backgroundColor": "black",
    "color": "white",
    "width": 150,
}


def comound_interest(t, initial, annual, interest_rate):
    return (
        initial * (1 + interest_rate) ** t
        + annual * (1 + interest_rate) * ((1 + interest_rate) ** t - 1) / interest_rate
    )


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Label(
                                            "Years to Retire",
                                            size="sm",
                                            class_name="mb-1",  # margin bottom
                                        ),
                                        dbc.Input(
                                            id="years-to-retire",
                                            value="25",
                                            type="text",
                                            persistence=True,
                                            class_name="mb-3",
                                            style=input_style,
                                        ),
                                        dbc.Label(
                                            "Initial Investment",
                                            size="sm",
                                            class_name="mb-1",
                                        ),
                                        dbc.Input(
                                            id="initial-invest",
                                            value="100000",
                                            type="text",
                                            persistence=True,
                                            class_name="mb-3",
                                            style=input_style,
                                        ),
                                        dbc.Label(
                                            "Annual Contribution",
                                            class_name="mb-1",
                                            size="sm",
                                            width="auto",
                                        ),
                                        dbc.Input(
                                            id="annual-contribute",
                                            value="5000",
                                            persistence=True,
                                            type="text",
                                            class_name="mb-3",
                                            style=input_style,
                                        ),
                                        dbc.Label(
                                            "Annual Interest Rates",
                                            className="mb-1",
                                            size="sm",
                                        ),
                                        dbc.Input(
                                            id="annual-interest",
                                            value="9",
                                            type="text",
                                            persistence=True,
                                            style=input_style,
                                        ),
                                    ],
                                    style={"padding": 45},
                                ),
                            ],
                            style={"margin-top": 25},
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=3,  # if screen is large or X-large, use only 3 columns to display control panel
                ),
                dbc.Col(
                    [dbc.Card([dbc.CardBody([html.Div(id="goal-chart")])])],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=9,
                ),
            ], className="py-4",
        ),
    ], fluid=True
)

@callback(
    Output("goal-chart", "children"),
    Input("years-to-retire", "value"),
    Input("initial-invest", "value"),
    Input("annual-contribute", "value"),
    Input("annual-interest", "value"),
)
def update_goal(years, invest, contribute, interest):
    if interest == "0" or years == "0":
        return no_update
    for x in [years, invest, contribute, interest]:
        if not str(x).isdigit():  # if the text values do not represent digits
            return no_update

    # convert text to float
    years, invest, contribute, interest = (
        float(years),
        float(invest),
        float(contribute),
        float(interest),
    )

    result = []
    for y in range(0, int(years) + 1):
        ci = comound_interest(y, invest, contribute, interest / 100)
        result.append(ci)
    end_result = numerize.numerize(result[-1], 2)
    fig_title = f"${end_result} after {int(years)} years"
    fig = px.line(
        x=range(0, int(years) + 1),
        y=result,
        template="plotly_dark",
        markers=True,
        title=fig_title,
    )
    fig.update_layout(xaxis_title="Years", yaxis_title="USD")
    return dcc.Graph(figure=fig)
