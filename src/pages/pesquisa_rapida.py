import dash_mantine_components as dmc
import dash
from dash import Dash, _dash_renderer, html, dcc, Input, Output, State, callback, ctx
from dash_iconify import DashIconify
from utils.tratamento import latest_records, listagem_inicial, lista_menores_valores_dia, lowest_per_timestamp
from utils.charts import trend_chart, recomendation_chart
from utils.filter_usage import log_filter_usage
from utils.comprar_click import log_comprar_click
from utils.subscription import add_subscription
import pandas as pd
import uuid

import warnings
warnings.filterwarnings("ignore")

_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

dash.register_page(__name__, path="/", name="Pesquisa Rápida")

listagem_inicial, ultima_atualizacao = listagem_inicial()

unique_categorias = sorted({el["CATEGORIA"] for el in listagem_inicial})

selectors = dmc.Grid(
    gutter="md",
    children=[
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id='selector_categoria',
                    label='Categoria',
                    data=unique_categorias,
                    placeholder="Selecione a categoria",
                    leftSection=DashIconify(icon="mdi:tag", width=18),
                    required=True,
                ),
                dmc.Text("Ex: Fraldas, Lenços, etc.", size="xs", c="gray.6"),
            ], gap=2),
            span=3
        ),
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id='selector_marca',
                    label='Marca',
                    placeholder="Selecione a marca",
                    leftSection=DashIconify(icon="mdi:factory", width=18),
                    required=True,
                ),
                dmc.Text("Ex: Pampers, Huggies...", size="xs", c="gray.6"),
            ], gap=2),
            span=3
        ),
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id='selector_submarca',
                    label='Submarca',
                    placeholder="Selecione a submarca",
                    leftSection=DashIconify(icon="mdi:label-outline", width=18),
                    required=True,
                ),
                dmc.Text("Ex: Ajuste Total, Supreme Care...", size="xs", c="gray.6"),
            ], gap=2),
            span=3
        ),
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id='selector_tamanho',
                    label='Tamanho',
                    placeholder="Selecione o tamanho",
                    leftSection=DashIconify(icon="mdi:ruler", width=18),
                    required=True,
                ),
                dmc.Text("Ex: P, M, G, XG...", size="xs", c="gray.6"),
            ], gap=2),
            span=3
        ),
    ]
)

def generate_card(row_data, is_best=False, search_id=None):
    props = dict(
        p='md',
        radius='lg',
        shadow='xl',
        withBorder=True,
        style={
            "transition": "box-shadow 0.2s, transform 0.2s",
            "boxShadow": "0 4px 16px rgba(0,0,0,0.08)" if is_best else "0 2px 8px rgba(0,0,0,0.04)",
            "border": "2px solid #20c997" if is_best else "2px solid #e9ecef",
            # "background": "#e6fcf5" if is_best else "#f8fafc",
            "position": "relative",
            "transform": "scale(1)" if is_best else "scale(1)",
            # "marginBottom": 16
        }
    )

    store_img_map =  {
        'DPSP': 'assets/dpsp.png',
        'PAGUE MENOS': 'assets/paguemenos.svg',
        'DROGARAIA': 'assets/drogaraia.svg',
        'PANVEL': 'assets/panvel.png',
        'MAGALU': 'assets/magalu.png',
        'PAO DE ACUCAR': 'assets/paodeacucar.png',
        'SHOPPER PROGRAMADA': 'assets/shopper.png',
        'INTER SHOP': 'assets/intershop.jpg'
    }

    img_path = store_img_map.get(row_data['LOJA'], "assets/default.png")

    badge = None
    if is_best:
        badge = dmc.Badge(
            [DashIconify(icon="mdi:star", width=16, color="white"), " Melhor Oferta"],
            color="teal",
            variant="gradient",
            size="lg",
            radius="sm",
            style={"position": "absolute", "top": 12, "right": 12, "zIndex": 2, "paddingLeft": 8, "paddingRight": 8}
        )

    # Create a unique id for the Comprar button using product info
    # Use MongoDB ObjectId for later reference
    comprar_btn_id = {
        'type': 'comprar-btn',
        'index': str(row_data.get('_id', '')),
        'search_id': search_id
    }

    card = dmc.Paper(
        [
            # badge if is_best else None,
            dmc.Group(
                [
                    dmc.Box(
                        [
                            dmc.Group(
                                [
                                    dmc.Box(
                                        [
                                            dmc.Text(
                                                row_data['QUALIDADE'],
                                                fw=700,
                                                size="xl",
                                                c="blue.7",
                                                # mt=8
                                            ),
                                            dmc.Text(
                                                row_data['MARCA'],
                                                size="md",
                                                c="gray.6",
                                            )
                                        ]
                                    ),                                    
                                    dmc.Group(
                                        [
                                            dmc.Badge(row_data['TAMANHO'], variant="outline", size='xl', radius="md", color="gray"),
                                            dmc.Badge(row_data['QTD'], variant="outline", size='xl', radius="md", color="gray"),
                                        ],
                                        justify='flex-end'
                                    )
                                ],
                                justify='flex-start',
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                }

                            ),
                            dmc.Group([
                                dmc.Text(
                                    f'R$ {row_data["UNIDADE"]:.2f}',
                                    fw=700,
                                    c="gray.6",
                                    style={"letterSpacing": 1, "fontSize": 24}
                                ),
                                dmc.Text(' /un', size="sm", c="gray.7"),
                                dmc.Text(
                                    f' • R$ {row_data["PRECO"]:.2f} total',
                                    size="sm",
                                    c="gray.7",
                                ),
                            ], gap=4, style={'alignItems': 'baseline'}, mt=8,)    
                        ], ta='left', style={"flex": 1}
                    ),
                    dmc.Box(
                        dmc.Image(
                            src=img_path,
                            w=96,
                            h=96,
                            radius="md",
                            style={"border": "1px solid #e9ecef", "background": "#fff", "objectFit": "contain"}
                        ),
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "right",
                            "width": 64,
                            "border": "1px solid #e9ecef",
                        }
                    ),
                ],
                align="center",
                justify="space-between",
                style={"marginBottom": 12}
            ),
            dmc.Anchor(
                dmc.Button(
                    "Comprar",
                    id=comprar_btn_id,
                    fullWidth=True,
                    radius='xl',
                    rightSection=DashIconify(icon="mdi:open-in-new", width=20),
                    color="teal.6" if is_best else "blue.6",
                    variant="filled",
                    size="md",
                    mt=8
                ),
                href=row_data['URL'],
                target="_blank",
                style={"width": "100%", "display": "block"}
            ),
        ],
        **props
    )

    return card

def lista_cards(data, search_id=None):
    if not data:
        return dmc.Alert("Nenhuma oferta encontrada para os filtros selecionados.", color="yellow", variant="light", mt="md")

    cards = []
    for idx, row_data in enumerate(data):
        is_best = idx == 0
        cards.append(generate_card(row_data, is_best=is_best, search_id=search_id))

    lista = dmc.Paper(
        [
            dmc.Group(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                'MELHORES PREÇOS POR PRODUTO',
                                fw=700,
                                size="md",
                                c="blue.7",
                                mb=4,
                            ),
                        ],
                        gap=8,
                        align="center"
                    ),
                    dmc.Group(
                        [
                            dmc.Text(
                                f"ATUALIZAÇÃO {ultima_atualizacao.strftime('%d-%m-%Y')}",
                                size="sm",
                                c="gray.6"
                            ),
                        ],
                        gap=4,
                        align="center"
                    )
                ],
                justify='space-between',
                mb=8,
                style={"background": "#f8fafc", "borderRadius": 8,}
            ),
            dmc.Divider(mb=12),
            dmc.Grid(
                [
                    dmc.GridCol(card, span=4)
                    for card in cards
                ],
                gutter="md"
            )
        ],
        p='md',
        shadow="sm",
        withBorder=True,
        style={"marginTop": 8, "marginBottom": 8}
    )
    return lista

def historical(df):
    return dmc.Paper(
        [
            dmc.Text("HISTÓRICO DE PREÇOS", fw=700, size="md", c="blue.7", mb=4),
            dcc.Graph(
                figure=trend_chart(df),
            ),
        ],
        p="md",
        shadow="md",
        withBorder=True,
        style={"height": "100%", "display": "flex", "flexDirection": "column"}
    )

def recommendation(df):

    p10 = df['min_value'].quantile(0.1)
    p25 = df['min_value'].quantile(0.25)
    p75 = df['min_value'].quantile(0.75)
    p90 = df['min_value'].quantile(0.9)

    current_value = df['min_value'].iloc[-1]

    rec_text = dmc.Text(
            [
                dmc.Text("Neutro", size="xl", fw=900, c="gray.7", style={"letterSpacing": 1}),
                dmc.Text("Sem recomendação", size="sm", c="gray.5"),
            ],
            ta="left"
        )

    if current_value <= p25:
        rec_text = dmc.Text(
            [
                dmc.Text("Oportunidade", size="xl", fw=900, c="green.7", style={"letterSpacing": 1}),
                dmc.Text("Preços ainda atrativos", size="sm", c="green.6"),
            ],
            ta="left"
        )
    
    if current_value <= p10:
        rec_text = dmc.Text(
            [
                dmc.Text("Excelente", size="xl", fw=900, c="green.9", style={"letterSpacing": 1}),
                dmc.Text("Bom momento para se abastecer", size="sm", c="green.7"),
            ],
            ta="left"
        )

    if current_value >= p75:
        rec_text = dmc.Text(
            [
                dmc.Text("Aguardar", size="xl", fw=900, c="red.6", style={"letterSpacing": 1}),
                dmc.Text("Preços podem melhorar", size="sm", c="red.5"),
            ],
            ta="left"
        )

    if current_value >= p90:
        rec_text = dmc.Text(
            [
                dmc.Text("Evitar", size="xl", fw=900, c="red.9", style={"letterSpacing": 1}),
                dmc.Text("Preços altos no momento", size="sm", c="red.7"),
            ],
            ta="left"
        )


    return dmc.Paper(
        [
            dmc.Group(
                [
                    dmc.Text("RECOMENDAÇÃO", fw=700, size="md", c="blue.7", mb=4),
                    dmc.Tooltip(
                        label="Receber recomendações por e-mail",
                        position="left",
                        withArrow=True,
                        children=dmc.ActionIcon(
                            DashIconify(icon="fluent:mail-unread-48-regular", width=32),
                            id="subscribe-action",
                            color="blue",
                            variant="light",
                            size="lg",
                            n_clicks=0,
                            style={"cursor": "pointer"}
                        )
                    ),
                ],
                justify='space-between',
                align="center",
                gap=8
            ),
            dmc.Stack(
                [
                    rec_text,
                    dmc.Divider(mb=4, mt=4),
                    dmc.Box(
                        dcc.Graph(
                            figure=recomendation_chart(df),
                            config={"displayModeBar": False},
                            style={"width": "100%", "height": 60, "maxWidth": "100%", "overflow": "hidden"},
                        ),
                        style={"width": "100%", "maxWidth": "100%", "overflow": "hidden", "display": "flex", "justifyContent": "center"},
                    ),

                ],
                gap="xs",
                p=0,
                style={"width": "100%"}
            ),
        ],
        p="md",
        shadow="md",
        withBorder=True,
        style={"height": "100%", "display": "flex", "flexDirection": "column"}
    )

def trend_analysis(df):

    df["MA_7"] = df["min_value"].rolling(window=7).mean()
    df["MA_30"] = df["min_value"].rolling(window=30).mean()

    # Trend flag logic
    def trend_flag(row):
        if row["MA_7"] > row["MA_30"]:
            return "Alta"
        elif row["MA_7"] < row["MA_30"]:
            return "Baixa"
        else:
            return "Neutro"

    df["TREND_FLAG"] = df.apply(trend_flag, axis=1)

    trend = df["TREND_FLAG"].iloc[-1]

    if trend == "Alta":
        rec_text = dmc.Text(
            [
                dmc.Text("Alta", size="xl", fw=900, c="red.8", style={"letterSpacing": 1}),
                dmc.Text("Preços estão subindo", size="sm", c="red.6"),
            ],
            ta="left"
        )
    elif trend == "Baixa":
        rec_text = dmc.Text(
            [
                dmc.Text("Baixa", size="xl", fw=900, c="green.8", style={"letterSpacing": 1}),
                dmc.Text("Preços estão caindo", size="sm", c="green.6"),
            ],
            ta="left"
        )
    elif trend == "Neutro":
        rec_text = dmc.Text(
            [
                dmc.Text("Neutro", size="xl", fw=900, c="gray.7", style={"letterSpacing": 1}),
                dmc.Text("Informação insuficiente", size="sm", c="gray.5"),
            ],
            ta="left"
        )

    return dmc.Paper(
        [
            dmc.Text("TENDÊNCIA", fw=700, size="md", c="blue.7", mb=4),
            dmc.Stack(
                [
                    rec_text
                ],
                gap="xs",
                p=0,
                style={"width": "100%"}
            )
        ],
        p="md",
        shadow="md",
        withBorder=True,
        style={"height": "100%", "display": "flex", "flexDirection": "column"}
    )


layout = dmc.Paper(
    children = [
        dcc.Store(id='search-id-store'),
        dmc.Paper(
            [
                dmc.Text(
                    'ESCOLHA UM PRODUTO PARA PESQUISA',
                    size='md',
                    fw=700,
                    c='blue.7',
                    mb=4,
                ),
                dmc.Text(
                    'Preencha os campos abaixo para encontrar os melhores preços.',
                    size='sm',
                    c='gray.7',
                    mb=10,
                ),
                selectors,
                dmc.Space(h=10),
                dmc.Box(
                    dmc.Button('Pesquisar', id='pesquisar', leftSection=DashIconify(icon="mdi:magnify", width=20)),
                    ta="right"
                ),
            ],
            p='md',
            shadow='md',
            withBorder=True
        ),
        dmc.Space(h=10),
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Box(id='historical_charts', style={"height": "100%"}),
                    span=9,
                    style={"height": "400px"}
                ),
                dmc.GridCol(
                    dmc.Stack(
                        [
                            dmc.Box(id='recommendation_charts', style={"height": "100%"}),
                            dmc.Box(id='trend_analysis', style={"height": "100%"}),
                        ],
                        gap="md",
                        style={"height": "100%"}
                    ),
                    span=3,
                    style={"height": "400px"}
                )
            ],
            align='stretch',
            style={"height": "400px"}
        ),
        dmc.Box(id='cards'),
        # --- Subscription Modal ---
        dmc.Modal(
            id="subscribe-modal",
            title="Receber recomendações por e-mail",
            centered=True,
            zIndex=1000,
            size="md",
            children=[
                dmc.Text(
                    "Informe seu e-mail para receber recomendações deste produto.",
                    size="sm",
                    c="gray.7",
                    mb=12
                ),
                dmc.TextInput(
                    id="subscribe-email",
                    label="E-mail",
                    placeholder="seu@email.com",
                    required=True,
                    leftSection=DashIconify(icon="mdi:email-outline", width=20),
                    style={"marginBottom": 16}
                ),
                dmc.Group(
                    [
                        dmc.Button("Cancelar", id="subscribe-cancel", color="gray", variant="outline"),
                        dmc.Button("Inscrever-se", id="subscribe-confirm", color="blue"),
                    ],
                    mt=8,
                    gap=8,
                    style={"justifyContent": "flex-end"}
                ),
                dmc.Text(id="subscribe-feedback", size="sm", c="red", mt=8)
            ],
            opened=False,
            overlayProps={
                "opacity": 0.55,
                "blur": 2,
            },
        ),
    ],
    # fluid=True,
    px=40,
    style={"width": '100%'}
)



# Flexible filter callbacks: each selector updates based on all others
@callback(
    Output('selector_categoria','data'),
    [
        Input('selector_marca','value'),
        Input('selector_submarca','value'),
        Input('selector_tamanho','value'),
    ]
)
def update_categorias(marca, submarca, tamanho):
    filtered = listagem_inicial
    if marca:
        if isinstance(marca, list):
            filtered = [el for el in filtered if el['MARCA'] in marca]
        else:
            filtered = [el for el in filtered if el['MARCA'] == marca]
    if submarca:
        if isinstance(submarca, list):
            filtered = [el for el in filtered if el['QUALIDADE'] in submarca]
        else:
            filtered = [el for el in filtered if el['QUALIDADE'] == submarca]
    if tamanho:
        if isinstance(tamanho, list):
            filtered = [el for el in filtered if el['TAMANHO'] in tamanho]
        else:
            filtered = [el for el in filtered if el['TAMANHO'] == tamanho]
    unique_categorias = sorted({el["CATEGORIA"] for el in filtered})
    return unique_categorias

@callback(
    Output('selector_marca','data'),
    [
        Input('selector_categoria','value'),
        Input('selector_submarca','value'),
        Input('selector_tamanho','value'),
    ]
)
def update_marcas(categoria, submarca, tamanho):
    filtered = listagem_inicial
    if categoria:
        if isinstance(categoria, list):
            filtered = [el for el in filtered if el['CATEGORIA'] in categoria]
        else:
            filtered = [el for el in filtered if el['CATEGORIA'] == categoria]
    if submarca:
        if isinstance(submarca, list):
            filtered = [el for el in filtered if el['QUALIDADE'] in submarca]
        else:
            filtered = [el for el in filtered if el['QUALIDADE'] == submarca]
    if tamanho:
        if isinstance(tamanho, list):
            filtered = [el for el in filtered if el['TAMANHO'] in tamanho]
        else:
            filtered = [el for el in filtered if el['TAMANHO'] == tamanho]
    unique_marcas = sorted({el["MARCA"] for el in filtered})
    return unique_marcas

@callback(
    Output('selector_submarca','data'),
    [
        Input('selector_categoria','value'),
        Input('selector_marca','value'),
        Input('selector_tamanho','value'),
    ]
)
def update_submarcas(categoria, marca, tamanho):
    filtered = listagem_inicial
    if categoria:
        if isinstance(categoria, list):
            filtered = [el for el in filtered if el['CATEGORIA'] in categoria]
        else:
            filtered = [el for el in filtered if el['CATEGORIA'] == categoria]
    if marca:
        if isinstance(marca, list):
            filtered = [el for el in filtered if el['MARCA'] in marca]
        else:
            filtered = [el for el in filtered if el['MARCA'] == marca]
    if tamanho:
        if isinstance(tamanho, list):
            filtered = [el for el in filtered if el['TAMANHO'] in tamanho]
        else:
            filtered = [el for el in filtered if el['TAMANHO'] == tamanho]
    unique_submarcas = sorted({el["QUALIDADE"] for el in filtered})
    return unique_submarcas

@callback(
    Output('selector_tamanho','data'),
    [
        Input('selector_categoria','value'),
        Input('selector_marca','value'),
        Input('selector_submarca','value'),
    ]
)
def update_tamanhos(categoria, marca, submarca):
    filtered = listagem_inicial
    if categoria:
        if isinstance(categoria, list):
            filtered = [el for el in filtered if el['CATEGORIA'] in categoria]
        else:
            filtered = [el for el in filtered if el['CATEGORIA'] == categoria]
    if marca:
        if isinstance(marca, list):
            filtered = [el for el in filtered if el['MARCA'] in marca]
        else:
            filtered = [el for el in filtered if el['MARCA'] == marca]
    if submarca:
        if isinstance(submarca, list):
            filtered = [el for el in filtered if el['QUALIDADE'] in submarca]
        else:
            filtered = [el for el in filtered if el['QUALIDADE'] == submarca]
    unique_tamanhos = list({el["TAMANHO"] for el in filtered})
    order = ["RN+", "RN", "P", "M", "G", "XG", "XXG", "XXXG", "P-M", "M-G", "G-XG"]
    unique_tamanhos = sorted(unique_tamanhos, key=lambda x: order.index(x) if x in order else len(order))
    return unique_tamanhos

@callback(
    [
        Output('cards','children'),
        Output('historical_charts','children'),
        Output('recommendation_charts','children'),
        Output('trend_analysis','children'),
        Output('search-id-store', 'data'),
    ],
        Input('selector_categoria','value'),
        Input('selector_marca','value'),
        Input('selector_submarca','value'),
        Input('selector_tamanho','value'),
    )
def listar_cards(categoria, marca, submarca, tamanho):
    # If any filter is empty, treat as None
    categoria = categoria if categoria else None
    marca = marca if marca else None
    submarca = submarca if submarca else None
    tamanho = tamanho if tamanho else None

    search_id = str(uuid.uuid4())
    # try:
    #     log_filter_usage(categoria, marca, submarca, tamanho, page="pesquisa_rapida", search_id=search_id)
    # except Exception as e:
    #     print(f"[Filter Usage Logging Error] {e}")

    menores_dia = lista_menores_valores_dia(categoria,marca,submarca,tamanho)
    listagem = lista_cards(menores_dia, search_id=search_id)

    daily_lowest = lowest_per_timestamp(categoria=categoria,marca=marca,qualidade=submarca,tamanho=tamanho)
    daily_lowest_df = pd.DataFrame(daily_lowest)
    daily_lowest_df = daily_lowest_df.set_index('timestamp').resample('D')['min_value'].min().ffill().reset_index()

    historical_box = historical(daily_lowest_df)
    recommendation_box = recommendation(daily_lowest_df)
    trend_box = trend_analysis(daily_lowest_df)

    return listagem, historical_box, recommendation_box, trend_box, search_id

@callback(
    Output("subscribe-modal", "opened", allow_duplicate=True),
    [
        Input("subscribe-action", "n_clicks"),
    ],
    prevent_initial_call=True
)
def open_subscribe_modal(subscribe_action):
    if subscribe_action:
        return True
    raise dash.exceptions.PreventUpdate

@callback(
    [
        Output("subscribe-modal", "opened", allow_duplicate=True),
        Output("subscribe-feedback", "children"),
        Output("subscribe-email", "value"),
    ],
    [
        Input("subscribe-cancel", "n_clicks"),
        Input("subscribe-confirm", "n_clicks"),
    ],
    [
        State("subscribe-email", "value"),
        State("selector_categoria", "value"),
        State("selector_marca", "value"),
        State("selector_submarca", "value"),
        State("selector_tamanho", "value"),
        State("subscribe-modal", "opened"),
    ],
    prevent_initial_call=True
)
def handle_subscribe_modal(cancel_clicks, confirm_clicks, email, categoria, marca, submarca, tamanho, opened):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "subscribe-cancel":
        return False, "", ""

    if button_id == "subscribe-confirm":
        import re
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True, "Por favor, insira um e-mail válido.", email

        try:
            inserted = add_subscription(email, categoria, marca, submarca, tamanho)
            if inserted:
                # Keep modal open and show success message, clear email
                return True, dmc.Text("Inscrição realizada com sucesso! Você receberá recomendações por e-mail.", c="green"), ""
            else:
                return True, "Você já está inscrito para este produto.", email
        except Exception as e:
            return True, f"Erro ao salvar inscrição: {str(e)}", email

    return opened, "", email

# --- Pattern-Matching Callback for Comprar Buttons ---
from dash.dependencies import ALL

@callback(
    Output('cards', 'children', allow_duplicate=True),
    [Input({'type': 'comprar-btn', 'index': ALL, 'search_id': ALL}, 'n_clicks')],
    State('search-id-store', 'data'),
    prevent_initial_call=True
)
def track_comprar_click(n_clicks_list, search_id):
    if not ctx.triggered_id:
        raise dash.exceptions.PreventUpdate

    # Make sure the triggering button has n_clicks > 0
    if all(nc is None or nc <= 0 for nc in n_clicks_list):
        raise dash.exceptions.PreventUpdate

    btn_id = ctx.triggered_id
    object_id = btn_id.get('index')
    search_id_btn = btn_id.get('search_id')

    try:
        log_comprar_click(object_id, search_id_btn, page="pesquisa_rapida")
    except Exception as e:
        print(f"[Comprar Click Logging Error] {e}")

    raise dash.exceptions.PreventUpdate

# --- Pagination Callbacks ---
from dash.exceptions import PreventUpdate

@callback(
    Output('page-store', 'data'),
    [
        Input('page-prev', 'n_clicks'), 
        Input('page-next', 'n_clicks')
    ],
    State('page-store', 'data'),
    prevent_initial_call=True
)
def update_page(prev_clicks, next_clicks, current_page):
    print(current_page)
    ctx = dash.callback_context
    print(ctx)
    if not ctx.triggered:
        raise PreventUpdate
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(button_id)
    if button_id == 'page-prev' and current_page > 1:
        return current_page - 1
    elif button_id == 'page-next':
        print(current_page)
        return current_page + 1
    return current_page
