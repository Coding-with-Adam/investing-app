from dash import Dash, html, dcc, callback, Input, Output, no_update, ctx, register_page
import dash_bootstrap_components as dbc  #  version 1.4.0
import pandas as pd  # version 1.5.3
import plotly.express as px
import yfinance as yf  # version 0.2.12

register_page(__name__)


df_tickers = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/tickers_yahoo.csv")  # dataset of tickers and their names
options = df_tickers["Ticker"]


# function to get ticker data from yahoo's API
def get_stock_data(v_tickers, v_period, v_interval, v_group_by):
    return yf.download(
        tickers=v_tickers, period=v_period, interval=v_interval, group_by=v_group_by
    )


layout = dbc.Container(
    [
        dbc.Tooltip(
            "No data found, symbol may be delisted.",
            id="alert-auto",
            is_open=False,
            target="ticker-select",
            trigger=None,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=options,
                            value="AAPL",
                            clearable=False,
                            searchable=True,
                            persistence=True,
                            className="mb-2",
                            id="ticker-select",
                        ),
                    ],
                    width=3,
                    lg=2,
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.RadioItems(
                                    id="time-line",
                                    className="w-100 mb-2",
                                    inputClassName="btn-check",
                                    labelClassName="btn btn-outline-primary",
                                    labelCheckedClassName="active",
                                    persistence=True,
                                    options=[
                                        {"label": "5D",
                                         "value": "5d"},
                                        {"label": "1M",
                                         "value": "1mo"},
                                        {"label": "6M",
                                         "value": "6mo"},
                                        {"label": "1Y",
                                         "value": "1y"},
                                        {"label": "2Y",
                                         "value": "2y"},
                                        {"label": "5Y",
                                         "value": "5y"},
                                        {"label": "10Y",
                                         "value": "10y"},
                                    ],
                                    value="5y",
                                    inline=True
                                ),
                            ],
                            className="radio-group",
                        )
                    ],
                    width=12,
                    lg=6,
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=options[options != "AAPL"],
                            placeholder="Compare",
                            searchable=True,
                            persistence=True,
                            id="comparison-input",
                        ),
                    ],
                    width=3,
                    lg=2,
                ),
            ],
            justify="between",
            className="my-4",
        ),
        dbc.Row(dcc.Graph(id="ticker-chart")),
    ], fluid=True
)

# selected value from dropdown x would be removed from dropdown y options' list
@callback(
    Output("comparison-input", "options"),
    Output("ticker-select", "options"),
    Input("ticker-select", "value"),
    Input("comparison-input", "value"),
    prevent_initial_call=True,
)
def remove_options(ticker_value, compare_value):
    if ctx.triggered_id == "ticker-select":
        new_options = options[options != ticker_value]
        return new_options, no_update
    elif ctx.triggered_id == "comparison-input":
        new_options = options[options != compare_value]
        return no_update, new_options


# create the line chart
@callback(
    Output("ticker-chart", "figure"),
    Output("alert-auto", "is_open"),
    Output("alert-auto", "target"),
    Input("ticker-select", "value"),
    Input("comparison-input", "value"),
    Input("time-line", "value"),
)
def create_graph(ticker_value, compare_value, time_value):
    # if only the first dropdown has a value selected
    if compare_value is None or len(compare_value) == 0:
        df1 = get_stock_data(ticker_value, time_value, "1d", "ticker")
        if df1.empty:
            return no_update, True, "ticker-select"
        else:
            # calculate change in value over time
            df1[f"delta_{ticker_value}"] = (df1["Open"] / df1["Open"].iloc[0] - 1) * 100
            fig = px.line(
                df1,
                x=df1.index,
                y=f"delta_{ticker_value}",
                color_discrete_sequence=px.colors.qualitative.Dark24,
                template="plotly_dark",
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                yaxis_title=None,
                yaxis_ticksuffix="%",
            )
    # both dropdowns have values selected
    else:
        data = get_stock_data([ticker_value, compare_value], time_value, "1d", "ticker")
        # convert multilevel dataframe to single level
        single_lvl_data = {
            idx: gp.xs(idx, level=1, axis=1)
            for idx, gp in data.groupby(level=1, axis=1)
        }
        new_df = single_lvl_data["Open"]

        if new_df[compare_value].isna().all():  # if column is empty
            return no_update, True, "comparison-input"

        elif new_df[ticker_value].isna().all():  # if column is empty
            return no_update, True, "ticker-select"

        else:
            # ensure both stock tickers start from the same date in case one is newer than the other
            first_valid_date = new_df.loc[:, new_df.isna().any()].first_valid_index()
            df1 = new_df.loc[first_valid_date:, :].copy()

            # calculate change in value over time
            df1[f"delta_{ticker_value}"] = (
                df1[ticker_value] / df1[ticker_value].iloc[0] - 1
            ) * 100
            df1[f"delta_{compare_value}"] = (
                df1[compare_value] / df1[compare_value].iloc[0] - 1
            ) * 100

            fig = px.line(
                df1,
                x=df1.index,
                y=[f"delta_{ticker_value}", f"delta_{compare_value}"],
                color_discrete_sequence=px.colors.qualitative.Dark24,
                template="plotly_dark",
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                yaxis_title=None,
                yaxis_ticksuffix="%",
            )

    return fig, False, no_update

