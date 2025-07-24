import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html, dcc, Input, Output, State, callback
import dash_ag_grid as dag
from dash_iconify import DashIconify
from utils import tratamento
import plotly.graph_objects as go
import pandas as pd

_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

app = Dash(external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)
server = app.server

# ------------------ Layout components ------------------

def headers():
    return dmc.Group([
        dmc.Text("MONITOR DE PREÇOS", fw=700, style={"fontSize": 32})
    ], grow=True)

def chips_categoria():
    return dmc.Stack([
        dmc.Text("CATEGORIAS", fw=600, size="lg"),
        dmc.Group(
            dmc.ChipGroup(
                [
                    dmc.Chip("FRALDAS", value="fraldas", radius='md'),
                    dmc.Chip("APTANUTRI", value="aptanutri", radius='md'),
                ],
                multiple=False,
                value="fraldas",
                id="chips_categoria",
            ),
            justify="left",
        )
    ])

def chips_tamanho_component(category):
    """Return chips group based on selected category"""
    if category == "aptanutri":
        return dmc.Group(
            dmc.ChipGroup(
            [
                dmc.Chip("800g", value="800g", radius='md'),
            ],
            multiple=False,
            value="800g",
            id="chips_tamanho",
        ))
    else:  # default to FRALDAS
        return dmc.Group(
            dmc.ChipGroup(
            [
                dmc.Chip("P", value="P", radius='md'),
                dmc.Chip("M", value="M", radius='md'),
                dmc.Chip("G", value="G", radius='md'),
                dmc.Chip("XG", value="XG", radius='md'),
                dmc.Chip("XXG", value="XXG", radius='md'),
                dmc.Chip("XXXG", value="XXXG", radius='md'),
            ],
            multiple=False,
            value="XG",
            id="chips_tamanho",
        ))

def price_history():
    return html.Div([
        dmc.Text("HISTÓRICO DE PREÇOS", fw=600, size="lg"),
        dmc.Space(h=10),
        dmc.Stack([
            dcc.Graph(
                id='chart',
                style={'height': '100%', 'padding': '10px', 'backgroundColor': 'rgba(0,0,0,0.02)'},
                config={"displayModeBar": False, 'responsive': True}
            ),
        ], style={'border': "1px solid lightgray", 'height': 400})
    ])

def best_deal():
    columns = [
        {"headerName": "MARCA", "field": "MARCA"},
        {"headerName": "QUALIDADE", "field": "GRID_LINK", "linkTarget": "_blank"},
        {"headerName": "UNIDADE", "field": "UNIDADE", "type": "numericColumn"},
    ]

    grid = dag.AgGrid(
        id="product-grid",
        columnDefs=columns,
        columnSize='autoSize',
        defaultColDef={"sortable": True, "filter": False, "resizable": False,
                       "cellStyle": {"fontSize": "12px"}, "cellRenderer": "markdown"},
        dashGridOptions={"domLayout": "autoHeight"},
        className="ag-theme-alpine",
        style={"fontSize": "12px"},
    )

    lowest_price = dmc.Paper(
        children=[
            dmc.Grid(
                [
                    dmc.GridCol(dmc.Text("Vendido Por", size="md", fw=500, c="gray"), span=6),
                    dmc.GridCol(dmc.Text("Preço", size="md", fw=500, c="gray"), span=6, style={"textAlign": "right"}),
                ],
                gutter=0,
                style={"borderBottom": "1px solid #e0e0e0", "paddingBottom": "4px"},
            ),
            dmc.Grid(
                [
                    dmc.GridCol([
                        dmc.Group([
                            dmc.ThemeIcon(
                                DashIconify(icon="mdi:store", width=18),
                                radius="xl",
                                size="sm",
                                variant="light",
                            ),
                            dmc.Anchor(id='anchor', href='', target='_blank', size="xl", fw=500),
                        ], gap="xs"),
                    ], span=6),
                    dmc.GridCol(
                        dmc.Text(id='lowest_price', size="lg", fw=700, c="green"),
                        span=6,
                        style={"textAlign": "right"}
                    ),
                ],
                gutter=0,
                mt=6,
            ),
            dmc.Text(id='lowest_price_name', size="md", c="gray"),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        p="sm",
    )

    return html.Div([
        dmc.Text("MELHOR PREÇO", fw=600, size="lg"),
        dmc.Text(id='ultima_atualizacao', size="md", c="gray"),
        dmc.Space(h=10),
        lowest_price,
        dmc.Space(h=5),
        grid
    ])

def top_products_table():
    columns = [
        {"headerName": "DESCRICAO", "field": "GRID_LINK", "linkTarget": "_blank", "flex": 2},
        {"headerName": "MARCA", "field": "MARCA", "flex": 1},
        {"headerName": "QUALIDADE", "field": "QUALIDADE", "flex": 1},
        {"headerName": "TAMANHO", "field": "TAMANHO", "flex": 1},
        {"headerName": "LOJA", "field": "LOJA", "flex": 1},
        {"headerName": "UNIDADE", "field": "UNIDADE", "flex": 1},
        {"headerName": "QTD", "field": "QTD", "flex": 1},
        {"headerName": "PRECO", "field": "PRECO", "flex": 1},
    ]

    grid = dag.AgGrid(
        id="top-products-grid",
        columnDefs=columns,
        defaultColDef={"sortable": True, "filter": False, "resizable": False,
                       "cellStyle": {"fontSize": "12px"}, "cellRenderer": "markdown"},
        dashGridOptions={"domLayout": "autoHeight", "pagination": True, "paginationPageSize": 10},
        className="ag-theme-alpine",
        style={"fontSize": "12px"},
    )

    return dmc.Paper(
        [
            dmc.Text("TABELA COMPLETA", fw=600, size="lg"),
            dmc.Space(h=10),
            grid
        ],
        withBorder=True,
        shadow="xs",
        radius="md",
        p="sm",
        style={"padding": 16},
        mt=20
    )

# ------------------ Layout assembly ------------------

def serve_layout():
    return dmc.MantineProvider(dmc.Container([
        dcc.Store(id='df_store', data=tratamento.load_data().to_dict('records')),
        dcc.Store(id='df_store_filtered', data={}),

        headers(),
        dmc.Text("VERSÃO FRALDAS / APTANUTRI", size="md", c="gray", style={"fontStyle": "italic"}),
        dmc.Divider(mb=10),

        dmc.Space(h=20),
        dmc.Grid([
            dmc.GridCol(dmc.Paper([
                chips_categoria(),
                dmc.Space(h=20),
                html.Div(id="chips_tamanho_container"),   # dynamic placeholder
                dmc.Space(h=20),
                price_history()
            ],
        withBorder=True,
        shadow="xs",
        radius="md",
        p="sm",
        style={"padding": 16},
        mt=20), span=8),
            dmc.GridCol(dmc.Paper(best_deal(),
        withBorder=True,
        shadow="xs",
        radius="md",
        p="sm",
        style={"padding": 16},
        mt=20), span=4),
        ], grow=True),
        top_products_table(),
    ],
    fluid=True,
    py=20,
    style={"maxWidth": 1200, "margin": "auto"}))

# ------------------ Callbacks ------------------

@callback(
    Output("chips_tamanho_container", "children"),
    Input("chips_categoria", "value"),
)
def update_chips_tamanho(selected_category):
    return dmc.Stack([
        chips_tamanho_component(selected_category)
    ])

@callback(
    [
        Output('df_store_filtered', 'data'),
        Output('product-grid', 'rowData'),
        Output('anchor', 'href'),
        Output('anchor', 'children'),
        Output('lowest_price', 'children'),
        Output('lowest_price_name', 'children'),
        Output('ultima_atualizacao', 'children'),
        Output('top-products-grid', 'rowData'),
        Output("chart", "figure"),
    ],
    Input('chips_tamanho', 'value'),
    State('df_store', 'data'),
)
def filter_data(selected_size, data):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
    df_filtered_by_size = df[df['TAMANHO'] == selected_size]

    latest_day_products = (df_filtered_by_size[df_filtered_by_size['timestamp'] == df_filtered_by_size['timestamp'].max()]
                           .sort_values('UNIDADE')
                           .reset_index(drop=True))

    if latest_day_products.empty:
        return [{}]*8

    store = latest_day_products.loc[0, 'LOJA']
    price = latest_day_products.loc[0, 'UNIDADE']
    url = latest_day_products.loc[0, 'URL']
    product = f"{latest_day_products.loc[0, 'MARCA'].capitalize()} {latest_day_products.loc[0, 'QUALIDADE'].capitalize()} {latest_day_products.loc[0, 'QTD']} unidades"

    idxmin = latest_day_products.groupby(['MARCA', 'QUALIDADE'])['UNIDADE'].idxmin()
    best_deal_grid = latest_day_products.loc[idxmin]
    best_deal_grid['GRID_LINK'] = '[' + best_deal_grid['QUALIDADE'] + '](' + best_deal_grid['URL'] + ')'
    best_deal_grid.sort_values('UNIDADE', inplace=True)

    latest_day_products['GRID_LINK'] = '[' + latest_day_products['DESCRICAO'] + '](' + latest_day_products['URL'] + ')'
    latest_day_products.sort_values('UNIDADE', inplace=True)

    last_update = f"Última atualização | {df['timestamp'].max():%d/%m/%Y - %H:%M}"

    df_chart = (df_filtered_by_size
        .resample('D', on='timestamp')['UNIDADE']
        .aggregate(['min', 'mean', 'max'])
        .ffill())
    
    fig = tratamento.trend_chart(df_chart)

    return (
        df_filtered_by_size.to_dict('records'),
        best_deal_grid.to_dict('records'),
        url,
        store,
        f"R$ {price:.2f}",
        product,
        last_update,
        latest_day_products.to_dict('records'),
        fig
    )

# ------------------ Run app ------------------

app.layout = serve_layout

if __name__ == "__main__":
    app.run(debug=True)
