import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html, dcc, Input, Output, State, callback
import dash_ag_grid as dag
from dash_iconify import DashIconify
from utils import tratamento
from utils import enviar_mail
import plotly.graph_objects as go
_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

app = Dash(external_stylesheets=dmc.styles.ALL)
server = app.server

#### IMPORTAR DADOS E CRIAR DATAFRAME GRAFICO ####
df = tratamento.merged()
df_max = df.groupby("timestamp")['UNIDADE'].min().reset_index()

lowest_price_all = df_max.sort_values('timestamp').iloc[-1]['UNIDADE']


df_produtos = df.groupby(['QUALIDADE',"timestamp"])['UNIDADE'].min().reset_index()
grouped = df.groupby('MARCA')['QUALIDADE'].agg(lambda x: list(set(x))).reset_index()



def headers():

    nome = dmc.TextInput(label="Nome", placeholder="nome", id='nome')
    email = dmc.TextInput(label="Email", placeholder="email", id='email')
    seletor_produto = dmc.Select(
                label="Escolha um produto",
                placeholder="Selecione uma opção",
                id="alerta-produto",
                value="",
                data= ["Todos"] + [q.capitalize() for q in df['QUALIDADE'].unique()],
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

def price_history():

    multiselect_products = grouped.rename(columns={'MARCA': 'group', 'QUALIDADE': 'items'}).to_dict(orient='records')
    product_selector = dmc.Select(
                                    id='product_selector',
                                    label="",
                                    placeholder="PRODUTO",
                                    data=multiselect_products,
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
                                dcc.Graph(id='chart', figure=tratamento.line_chart(df_max), style={'height': '100%','padding': '10px'}, config={"displayModeBar": False, 'responsive': True}),
                            ],style={'border': f"1px solid lightgray", 'height': 400},
                        )


    return html.Div([
            historico_texto,
            dmc.Space(h=10),
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.TabsTab("XG", value="XG", pb='xs', size='xs'),
                            dmc.TabsTab("XXG", value="XXG", pb='xs', size='xs'),
                        ]
                    ),
                    dmc.Space(h=10),
                    dmc.TabsPanel(
                        painel,
                        value="XG",
                    ),
                    dmc.TabsPanel(
                        dmc.Text("List View Placeholder"),
                        value="XXG",
                    ),
                ],
                orientation='vertical',
                placement='left',
                # variant='pills',
                value="XG",
            )
        ])

def best_deal():

    last_day = (df
        [df['timestamp'] == df['timestamp'].max()]
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
    # Define AG Grid Columns
    columns = [
        {"headerName": "MARCA", "field": "MARCA"},
        {"headerName": "QUALIDADE", "field": "GRID_LINK", "linkTarget": "_blank"},
        {"headerName": "UNIDADE", "field": "UNIDADE", "type": "numericColumn"},
    ]

    grid = dag.AgGrid(
            id="product-grid",
            rowData=df_grid.to_dict("records"),
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
                                dmc.Anchor(href=url, target='_blank', children=f"{store}", size="xl", fw=500),
                            ],
                            gap="xs",
                        ),
                    ],
                    span=6,
                    ),
                    dmc.GridCol(
                        dmc.Text(f"R$ {price:.2f}", size="lg", fw=700, c="black"),
                        span=6,
                        style={"textAlign": "right"}
                    ),
                ],
                gutter=0,
                mt=6,
            ),
            dmc.Text(product, size="md", c="gray"),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        p="sm",
    )

    return html.Div(
                children=[
                    dmc.Text("Melhor Preço", fw=600, size="xl"),
                    dmc.Text(f"Última atualização | {df['timestamp'].max():%d/%m/%Y - %H:%M}", size="md", c="gray"),
                    dmc.Space(h=10),
                    lowest_price,
                    dmc.Space(h=5),
                    grid
                ]
            )


layout = dmc.Container(
    [
        headers(),
        dmc.Text("VERSÃO EXCLUSIVA PARA FRALDAS", size="sm", c="gray"),
        dmc.Divider(mb=10),
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
)


@callback(
    Output("chart", "figure"),
    Input("product_selector", "value"),
    # prevent_initial_call=True,
)
def update_charts(product):
    if not product:
        df_max = df.groupby("timestamp")['UNIDADE'].min().reset_index()
    else:
        df_max = df[df['QUALIDADE'] == product].groupby("timestamp")['UNIDADE'].min().reset_index()

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

app.layout = dmc.MantineProvider(layout)

if __name__ == "__main__":
    app.run(debug=True)