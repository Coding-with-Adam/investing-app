import dash_ag_grid as dag
from dash import Dash, html, dcc, callback, Input, Output, State, no_update, ctx, register_page
import dash_bootstrap_components as dbc  # version 1.4.0
import pandas as pd  # version 1.5.3
import plotly.express as px
from numerize import numerize

register_page(__name__, path="/")

df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/my-portfolio.csv")

input_style = {
    "backgroundColor": "black",
    "color": "white",
    "width": 150,
}


# list of options for the pie chart dropdown
dropdown_col_names = df.columns.tolist()
dropdown_col_names.remove("balance_dollar")
dropdown_col_names.remove("balance_prct")


columnDefs = [
    {
        "headerName": "Region",  # Name of table displayed in app
        "field": "region",  # ID of table
        "checkboxSelection": True,
        "minWidth":200,
    },
    {
        "headerName": "Market",
        "field": "market",
    },
    {
        "headerName": "Balance $",
        "field": "balance_dollar",
        "type": "numberColumn",
        "filter": "agNumberColumnFilter",
        "editable": False,
        "valueFormatter": {
            "function": "d3.format('$,.0f')(params.value)"  # add a dollar sign
        },
    },
    {
        "headerName": "Balance %",
        "field": "balance_prct",
        "type": "numberColumn",
        "filter": "agNumberColumnFilter",
    },
    {
        "headerName": "Investment",
        "field": "investment",
    },
    {
        "headerName": "Account",
        "field": "account",
    },
    {
        "headerName": "Platform",
        "field": "platform",
    },
    {
        "headerName": "Owner",
        "field": "owner",
        "cellEditor": "agSelectCellEditor",
        "cellEditorParams": {
            "values": ["Cricket", "Ladybug", "Joint"],  # add dropdown to the column
        },
    },
]

# color the `Balance %` column gray
cellStyle = {
    "styleConditions": [
        {
            "condition": "params.colDef.headerName == 'Balance %'",
            "style": {"backgroundColor": "#444"},
        },
    ]
}

defaultColDef = {
    "filter": True,
    "floatingFilter": True,
    "resizable": True,
    "sortable": True,
    "editable": True,
    "minWidth": 125,
    "cellStyle": cellStyle
}


table = dag.AgGrid(
    id="portfolio-table",
    className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection": "multiple"},
)


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [
                                        dbc.Row([
                                            dbc.Col([
                                                html.Label(
                                                    children="Total Balance (USD): ",
                                                    className="me-2",
                                                ),
                                                dcc.Input(
                                                    id="money-to-invest",
                                                    value=df.balance_dollar.sum(),
                                                    type="number",
                                                    step=1000,
                                                    style=input_style,
                                                ),
                                            ], width=12, xl=4),
                                            dbc.Col([
                                                html.Label(
                                                    children="Total Percentage: ",
                                                    className="me-2",
                                                ),
                                                dcc.Input(
                                                    id="total-percentage",
                                                    value=df.balance_prct.astype(float).sum(),
                                                    type="number",
                                                    step=1000,
                                                    disabled=True,
                                                    style=input_style,
                                                ),
                                            ], width=12, xl=4),
                                            dbc.Col([
                                                html.Label(
                                                    children="Outstanding: ",
                                                    className="me-2",
                                                ),
                                                dcc.Input(
                                                    id="changed_percent",
                                                    value=df.balance_prct.astype(float).sum()-100,
                                                    type="number",
                                                    disabled=True,
                                                    style=input_style
                                                ),
                                            ], width=12, xl=4),
                                        ])
                                    ]
                                ),
                                dbc.CardBody(
                                    [
                                        table,
                                        # Span ensures that both buttons display on the same row
                                        html.Span(
                                            [
                                                dbc.Button(
                                                    id="delete-row-btn",
                                                    children="Delete row",
                                                    color="secondary",
                                                    size="md",
                                                    className="mt-3 me-1",
                                                ),
                                                dbc.Button(
                                                    id="add-row-btn",
                                                    children="Add row",
                                                    color="primary",
                                                    size="md",
                                                    className="mt-3",
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=7,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    dcc.Dropdown(
                                        options=dropdown_col_names,
                                        id="col-name",
                                        value="owner",
                                        clearable=False,
                                        style={"color": "black"},
                                    )
                                ),
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            id="pie-breakdown", className="card-text"
                                        )
                                    ]
                                ),
                            ],
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=5,
                ),
            ],
            className="py-4",
        ),
    ], fluid=True
)


# add or delete rows of table
@callback(
    Output("portfolio-table", "deleteSelectedRows"),
    Output("portfolio-table", "rowData"),
    Input("delete-row-btn", "n_clicks"),
    Input("add-row-btn", "n_clicks"),
    State("portfolio-table", "rowData"),
    prevent_initial_call=True,
)
def update_dash_table(n_dlt, n_add, data):
    if ctx.triggered_id == "add-row-btn":
        new_row = {
            "region": [""],
            "market": [""],
            "balance_dollar": None,
            "balance_prct": [0],
            "investment": [""],
            "account": [""],
            "platform": [""],
            "owner": ["Ladybug"],
        }
        df_new_row = pd.DataFrame(new_row)
        updated_table = pd.concat(
            [pd.DataFrame(data), df_new_row]
        )  # add new row to orginal dataframe
        return False, updated_table.to_dict("records")

    elif ctx.triggered_id == "delete-row-btn":
        return True, no_update

# calculate "Balance $" column, update Total Percentage and Outstanding fields
@callback(
    Output("portfolio-table", "rowData", allow_duplicate=True),
    Output("total-percentage", "value"),
    Output("changed_percent", "value"),
    Input("portfolio-table", "cellValueChanged"),
    Input("money-to-invest", "value"),
    State("portfolio-table", "rowData"),
    prevent_initial_call=True,
)
def update_balance(cell_change, total_investment, data):
    # Ensure cell_change is a dictionary
    if isinstance(cell_change, dict) and "colId" in cell_change:
        if cell_change["colId"] == "balance_prct":
            # Your existing logic when the balance percentage column is changed
            dff = pd.DataFrame(data)
            dff["balance_prct"] = pd.to_numeric(dff["balance_prct"], errors="coerce")
            dff["balance_dollar"] = (dff["balance_prct"] * total_investment / 100)
            outstanding = numerize.numerize(100 - dff["balance_prct"].sum(), 2)
            return dff.to_dict("records"), dff["balance_prct"].sum(), outstanding

    if ctx.triggered_id == "money-to-invest":
        # Your existing logic for updating based on total investment
        if total_investment is None:
            return no_update, no_update, no_update
        else:
            dff = pd.DataFrame(data)
            dff["balance_prct"] = pd.to_numeric(dff["balance_prct"], errors="coerce")
            dff["balance_dollar"] = (dff["balance_prct"] * total_investment / 100)
            return dff.to_dict("records"), no_update, no_update

    return no_update, no_update, no_update


# build the Pie Chart
@callback(
    Output("pie-breakdown", "children"),
    Input("col-name", "value"),
    Input("portfolio-table", "cellValueChanged"),
    State("money-to-invest", "value"),
    State("portfolio-table", "rowData"),
)
def update_portfolio_stats(col_selected, cell_change, total_investment, data):
    dff = pd.DataFrame(data)
    dff["balance_prct"] = pd.to_numeric(dff["balance_prct"], errors="coerce")

    if dff["balance_prct"].sum() == 100:
        return [
            html.Div(
                f"Portfolio Total: ${total_investment:,.0f}",
                style={"textAlign": "center"},
            ),
            dcc.Graph(
                figure=px.pie(
                    dff,
                    values="balance_prct",
                    names=col_selected,
                    hole=0.3,
                    height=400,
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.Jet,
                ).update_layout(margin=dict(l=20, r=20, t=20, b=20))
            ),
        ]
    else:
        return dbc.Alert(
            "Balance total does not equal 100%. Please update Balance %", color="danger"
        )