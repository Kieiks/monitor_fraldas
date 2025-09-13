import dash
import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html, dcc, Input, Output, State, callback
import dash_ag_grid as dag
from dash_iconify import DashIconify
from utils import tratamento
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date

_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

dash.register_page(__name__, path="/dashboard", name="Dashboard")

df = pd.DataFrame(tratamento.latest_records())

# Pivot table
pivot_df = (
    df#.query('TAMANHO == "G"')
      .pivot_table(index=['MARCA','TAMANHO','QUALIDADE'],
                   columns='LOJA',
                   values='UNIDADE',
                   aggfunc='min')
      .reset_index()
)

# Convert to Dash AG Grid format
row_data = pivot_df.to_dict('records')

index_cols = ['MARCA', 'TAMANHO', 'QUALIDADE']
store_cols = [c for c in pivot_df.columns if c not in index_cols]

cellClassRules = {
                "min-green": "params.value == MinObject(params.data)"
            }

column_defs = [
    {"field": "MARCA", "pinned": "left", "filter": "agTextColumnFilter", "floatingFilter": True},
    {"field": "TAMANHO", "pinned": "left", "filter": "agTextColumnFilter", "floatingFilter": True},
    {"field": "QUALIDADE", "pinned": "left", "filter": "agTextColumnFilter", "floatingFilter": True},
]

# Attach heatmap-style cellStyle function to each store column
for col in store_cols:
    column_defs.append({
        "field": col,
        "type": "numericColumn",
        "valueSetter": {"function": "MakeFloat(params)"},
        "valueFormatter": {"function": "TwoDecimalFormatter(params)"}
    })

defaultColDef = {
    "resizable": True,
    "sortable": True,
    "editable": True,
    "minWidth": 100,
    "cellClassRules": cellClassRules,
    "cellStyle": {"textAlign": "center"}
}

grid = dag.AgGrid(
    columnDefs=column_defs,
    rowData=row_data,
    columnSize="responsiveSizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={
        "suppressRowHoverHighlight": True,
        "domLayout": "autoHeight"
        },
)

datepicker = dmc.DatePickerInput(
        id="date-picker-input",
        label="DATA DE ANÁLISE",
        # description="You can also provide a description",
        minDate=date(2025, 8, 15),
        maxDate=date(2025,8,21),
        # value=datetime.now().date(),  # or string in the format "YYYY-MM-DD"
        w=250,
    ),

layout = dmc.Paper(
    [
        dmc.Box(datepicker),
        dmc.Space(h=10),
        grid,
    ],
    px=40,
    style={"width": '100%', "margin": "auto"}
)