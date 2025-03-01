import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html, dcc, Input, Output, State, callback
import dash_ag_grid as dag
from dash_iconify import DashIconify
from utils import tratamento
from utils import enviar_mail
import plotly.graph_objects as go
import pandas as pd
_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

app = Dash(external_stylesheets=dmc.styles.ALL)
server = app.server


def headers():

    nome = dmc.TextInput(label="Nome", placeholder="nome", id='nome')
    email = dmc.TextInput(label="Email", placeholder="email", id='email')
    seletor_produto = dmc.Select(
                label="Escolha um produto",
                placeholder="Selecione uma opção",
                id="alerta-produto",
                value="",
                # data= 
                w=200,
                mb=10,
            )
    botao_enviar = dmc.Button("Enviar", id='enviar-alerta')
    alertas = dmc.Fieldset(
        [
            nome,
            email,
            seletor_produto,
            dmc.Group(botao_enviar, justify="flex-end"),
        ],
        legend="Registre para receber alertas",
    )

    titulo = dmc.Text("MONITOR DE PREÇOS", fw=700, style={"fontSize": 32})
    botao_alerta =dmc.Button("Receber Alertas", id='alerta',variant='outline')
    drawer = dmc.Drawer(
                            [
                                alertas
                            ],
                            id='drawer',
                            position='right',
                        )

    return dmc.Group(
                [
                    titulo,
                    dmc.Box([
                        botao_alerta,
                        drawer,
                    ],style={'display':'flex','justifyContent': 'right'}),
                ],
                grow=True,
            )

def chips_tamanho():

    return dmc.Stack([
        dmc.Text("Escolha um tamanho", fw=600, size="xl"),
        dmc.Group(
            dmc.ChipGroup(
                [
                    dmc.Chip("P", value="P",radius='md'),
                    dmc.Chip("M", value="M",radius='md'),
                    dmc.Chip("G", value="G",radius='md'),
                    dmc.Chip("XG", value="XG",radius='md'),
                    dmc.Chip("XXG", value="XXG",radius='md'),
                    dmc.Chip("XXXG", value="XXXG",radius='md'),
                ],
                multiple=False,
                value="XG",
                id="chipgs_tamanho",
            ),
            justify="left",
        )])

def price_history():

    product_selector = dmc.Select(
                                    id='product_selector',
                                    label="",
                                    placeholder="PRODUTO",
                                    # data={},
                                    size='xs',
                                    style={"width": 175, 'padding': '10px'},
                                    styles={
                                        "input": {
                                            "border": "2px solid #828282",
                                        },
                                    },
                                    radius=10,
                                )

    historico_texto = dmc.Text("Histórico de Preços", fw=600, size="xl")
    painel = dmc.Stack(
                            [
                                dmc.Group([
                                    product_selector,
                                ]),
                                dcc.Graph(id='chart', style={'height': '100%','padding': '10px'}, config={"displayModeBar": False, 'responsive': True}),
                            ],style={'border': f"1px solid lightgray", 'height': 400},
                        )


    return html.Div([
            historico_texto,
            dmc.Space(h=10),
            painel,
        ])

def best_deal():

    # Define AG Grid Columns
    columns = [
        {"headerName": "MARCA", "field": "MARCA"},
        {"headerName": "QUALIDADE", "field": "GRID_LINK", "linkTarget": "_blank"},
        {"headerName": "UNIDADE", "field": "UNIDADE", "type": "numericColumn"},
    ]

    grid = dag.AgGrid(
            id="product-grid",
            # rowData={},
            columnDefs=columns,
            columnSize='autoSize',
            defaultColDef={"sortable": True, "filter": False, "resizable": False, "cellStyle": {"fontSize": "12px"}, "cellRenderer": "markdown"},
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
                        dmc.Group(
                            [
                                dmc.ThemeIcon(
                                    DashIconify(icon="mdi:store", width=18),
                                    radius="xl",
                                    size="sm",
                                    variant="light",
                                ),
                                dmc.Anchor(id='anchor', href='', target='_blank', size="xl", fw=500),
                            ],
                            gap="xs",
                        ),
                    ],
                    span=6,
                    ),
                    dmc.GridCol(
                        dmc.Text(id='lowest_price', size="lg", fw=700, c="black"),
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

    return html.Div(
                children=[
                    dmc.Text("Melhor Preço", fw=600, size="xl"),
                    dmc.Text(id='ultima_atualizacao', size="md", c="gray"),
                    dmc.Space(h=10),
                    lowest_price,
                    dmc.Space(h=5),
                    grid
                ]
            )


def serve_layout():

    return dmc.MantineProvider(dmc.Container(
        [
            dcc.Store(id='df_store'),
            headers(),
            dmc.Text("VERSÃO EXCLUSIVA PARA FRALDAS", size="sm", c="gray"),
            dmc.Divider(mb=10),
            chips_tamanho(),
            dmc.Space(h=10),
            dmc.Space(h=10),
            dmc.Grid([
                dmc.GridCol(price_history(), span=8),
                dmc.GridCol(best_deal(), span=4),
            ],
            grow=True
            ),
        ],
        fluid=True,
        py=20,
        style={"maxWidth": 1200, "margin": "auto"},
    ))

@callback(
    [Output('df_store', 'data'),
    Output('product-grid', 'rowData'),
    Output('anchor', 'href'),
    Output('anchor', 'children'),
    Output('lowest_price', 'children'),
    Output('lowest_price_name', 'children'),
    Output('ultima_atualizacao', 'children'),
    Output('alerta-produto', 'data'),
    Output('product_selector', 'data')],
    Input('chipgs_tamanho', 'value'),
)
def filter_data(value):
    df = tratamento.merged()
    df_filtered = df[df['TAMANHO'] == value]

    last_day = (df_filtered
        [df_filtered['timestamp'] == df_filtered['timestamp'].max()]
        .sort_values('UNIDADE')
        .reset_index()
    )

    store = last_day.loc[0,]['LOJA']
    price = last_day.loc[0,]['UNIDADE']
    url = last_day.loc[0,]['URL']
    product = f"{last_day.loc[0,]['MARCA'].capitalize()} {last_day.loc[0,]['QUALIDADE'].capitalize()} {last_day.loc[0,]['QTD']} unidades"

    idxmin = (last_day
        .groupby(['MARCA','QUALIDADE'])['UNIDADE']
        .idxmin()
    )

    df_grid = last_day.loc[idxmin]
    df_grid['GRID_LINK'] = '['+df_grid['QUALIDADE']+']('+df_grid['URL']+')'
    df_grid.sort_values('UNIDADE', inplace=True)

    atualizacao = f"Última atualização | {df['timestamp'].max():%d/%m/%Y - %H:%M}"
    multiselector = df_filtered.groupby('MARCA')['QUALIDADE'].agg(lambda x: list(set(x))).reset_index().rename(columns={'MARCA': 'group', 'QUALIDADE': 'items'}).to_dict(orient='records')
    alerta_produto = ["Todos"] + [q.capitalize() for q in df['QUALIDADE'].unique()],
    return df_filtered.to_dict('records'), df_grid.to_dict('records'), url, store, f"R$ {price:.2f}", product, atualizacao, alerta_produto, multiselector


@callback(
    Output("chart", "figure"),
    Input("product_selector", "value"),
    Input("df_store", "data"),
    prevent_initial_call=True,
)
def update_charts(product, data):
    df_tamanho = pd.DataFrame(data)
    df_tamanho['timestamp'] = pd.to_datetime(df_tamanho['timestamp'])

    lowest_price_all = (df_tamanho
        [df_tamanho['timestamp'] == df_tamanho['timestamp'].max()]
        .sort_values('UNIDADE')
        .reset_index()
        .iloc[0]['UNIDADE']
    )

    if not product:
        df_max = df_tamanho.groupby("timestamp")['UNIDADE'].min().reset_index()
    else:
        df_max = df_tamanho[df_tamanho['QUALIDADE'] == product].groupby("timestamp")['UNIDADE'].min().reset_index()

    fig = tratamento.line_chart(df_max)
    fig.add_hline(y=lowest_price_all, line_dash="dot", line_color="red", annotation_text=f"Melhor Preço: R${lowest_price_all:.2f}", annotation_position="bottom right")
    return fig

@callback(
    Output("drawer", "opened"),
    Input("alerta", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True

@callback(
    [
        Output('nome','value'),
        Output('email','value'),
        Output('alerta-produto','value'),
    ],
    State('nome', 'value'),
    State('email', 'value'),
    State('alerta-produto', 'value'),
    Input('enviar-alerta', 'n_clicks'),
    prevent_initial_call=True,
)
def enviar_alerta(nome, email, produto, n_clicks):
    if n_clicks > 0:
        subject = 'Novo Cadastro Solicitado'
        body = f'Nome: {nome}\nEmail: {email}\nProduto: {produto}'
        
        enviar_mail.send_email(subject, body)

    return [''],[''],['']

app.layout = serve_layout

if __name__ == "__main__":
    app.run(debug=True)