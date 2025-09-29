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

categoria = 'fraldas'

dash.register_page(__name__, path=f"/{categoria}", name=f"{categoria.capitalize()}")

def get_latest_data(categoria):
    data, timestamp = listagem_inicial(categoria=categoria)
    return data, timestamp

selectors = dmc.Grid(
    gutter="md",
    children=[
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id=f'selector_marca_{categoria}',
                    label='Marca',
                    placeholder="Selecione a marca",
                    leftSection=DashIconify(icon="mdi:factory", width=18),
                    required=True,
                ),
                dmc.Text("Ex: Pampers, Huggies...", size="xs", c="gray.6"),
            ], gap=2),
            span={"base": 12, "sm": 6, "lg": 4},
        ),
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id=f'selector_submarca_{categoria}',
                    label='Submarca',
                    placeholder="Selecione a submarca",
                    leftSection=DashIconify(icon="mdi:label-outline", width=18),
                    required=True,
                ),
                dmc.Text("Ex: Ajuste Total, Supreme Care...", size="xs", c="gray.6"),
            ], gap=2),
            span={"base": 12, "sm": 6, "lg": 4},
        ),
        dmc.GridCol(
            dmc.Stack([
                dmc.MultiSelect(
                    id=f'selector_tamanho_{categoria}',
                    label='Tamanho',
                    placeholder="Selecione o tamanho",
                    leftSection=DashIconify(icon="mdi:ruler", width=18),
                    required=True,
                ),
                dmc.Text("Ex: P, M, G, XG...", size="xs", c="gray.6"),
            ], gap=2),
            span={"base": 12, "sm": 6, "lg": 4},
        ),
    ]
)


def generate_card2(row_data):

    return dmc.Card(
        withBorder=True,
        shadow="sm",
        radius="lg",
        style={"width": "100%", "position": "relative"},
        className="card-hover", 
        children=[
            dmc.Box(
                pos="relative",
                children=[
                    dmc.AspectRatio(
                        ratio=4/3,
                        children=[
                            dmc.Image(
                                src=row_data.get('IMAGEM', 'https://via.placeholder.com/150'),
                                style={
                                    "width": "100%",
                                    "maxHeight": "200px",
                                    "objectFit": "contain" # keeps proportions
                                },
                            ),
                        ]
                    ),
                    dmc.Flex(
                        justify="space-between",
                        align="center",
                        style={
                            "position": "absolute",
                            "top": 0,
                            "left": 0,
                            "right": 0,
                            "padding": "0px"
                        },
                        children=[
                            dmc.Badge("Oportunidade", color="violet", variant="filled", radius="sm") if row_data.get('IS_OPPORTUNITY') else dmc.Box(),
                            dmc.ActionIcon(
                                DashIconify(icon="mdi:heart-outline", width=20),
                                variant="light",
                                color="gray",
                            ),
                        ],
                    ),
                ],
            ),
            dmc.Stack(
                gap="xs",
                mt=8,
                children=[
                    dmc.Text(row_data.get('MARCA') + " " + row_data.get('QUALIDADE'), fw=600, size="sm"),
                    dmc.Group(
                        [
                            dmc.Badge(row_data.get('TAMANHO'), color="violet", variant="filled", radius="md"),
                            dmc.Badge(str(row_data.get('QTD')), color="violet", variant="filled", radius="md"),
                        ]
                    ),
                ],
            ),
            dmc.Stack(
                gap=0,
                mt=10,
                children=[
                    dmc.Box(
                        [
                            dmc.Text(f"R$ {row_data.get('UNIDADE'):.2f}".replace('.', ','), fw=700, size="lg", span=True),
                            dmc.Text(" /un", span=True),
                        ]
                    ),
                    dmc.Text(f"R$ {row_data.get('PRECO'):.2f} total".replace('.', ','), size="md", c="dimmed"),
                ],
            ),

            # Footer: Stores
            dmc.Stack(
                mt=12,
                children=[
                    dmc.Anchor(
                        "Veja histórico de preços e todas ofertas",
                        href=f"/product?categoria={row_data.get('CATEGORIA')}&marca={row_data.get('MARCA')}&submarca={row_data.get('QUALIDADE')}&tamanho={row_data.get('TAMANHO')}",
                        size="sm",
                        c="blue.6"
                    ),
                    dmc.Anchor(
                        dmc.Button(
                            "COMPRAR",
                            id={'type': 'offer-btn', 'index': str(row_data.get('_id', ''))},
                            variant="filled",
                            color="blue.5",
                            radius="sm",
                            fullWidth=True,
                        ),
                        href=row_data.get('URL', '#'),
                        target="_blank",
                        style={"width": "100%", "display": "block"}
                    )
                ],
            ),
        ],
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

def lista_cards(data, ultima_atualizacao):
    if not data:
        return dmc.Alert("Nenhuma oferta encontrada para os filtros selecionados.", color="yellow", variant="light", mt="md")

    cards = []
    for idx, row_data in enumerate(data):
        is_best = idx == 0
        # cards.append(generate_card(row_data, is_best=is_best, search_id=search_id))
        cards.append(generate_card2(row_data))

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
                    dmc.GridCol(
                        card, 
                        span={
                            "base": 12,  # default span (small screens)
                            "sm": 12,     # small screens: 2 cards per row_data
                            "md": 6,     # medium screens: 3 cards per row_data
                            "lg": 4,     # large screens: 4 cards per row_data
                        },
                        )
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
            ],
            p='md',
            shadow='md',
            withBorder=True
        ),
        dmc.Space(h=10),
        dmc.Box(id=f'cards_{categoria}'),
        # Hidden div for tracking offer clicks
        html.Div(id=f"dummy-output-{categoria}", style={"display": "none"}),
    ],
    # fluid=True,
    # px=40,
    # style={"width": '100%'}
    style={
        "maxWidth": 1200,
        "margin": "0 auto",
        "padding": "20px",
        "background": "white",
        "minHeight": "calc(100vh - 120px)",
    }
)


@callback(
    Output(f'selector_marca_{categoria}','data'),
    [
        Input(f'selector_submarca_{categoria}','value'),
        Input(f'selector_tamanho_{categoria}','value'),
    ]
)
def update_marcas(submarca, tamanho):
    filtered, _ = get_latest_data(categoria)
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
    Output(f'selector_submarca_{categoria}','data'),
    [
        Input(f'selector_marca_{categoria}','value'),
        Input(f'selector_tamanho_{categoria}','value'),
    ]
)
def update_submarcas(marca, tamanho):
    filtered, _ = get_latest_data(categoria)
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
    Output(f'selector_tamanho_{categoria}','data'),
    [
        Input(f'selector_marca_{categoria}','value'),
        Input(f'selector_submarca_{categoria}','value'),
    ]
)
def update_tamanhos(marca, submarca):
    filtered, _ = get_latest_data(categoria)
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
        Output(f'cards_{categoria}','children'),
        Input(f'selector_marca_{categoria}','value'),
        Input(f'selector_submarca_{categoria}','value'),
        Input(f'selector_tamanho_{categoria}','value'),
    )
def listar_cards(marca, submarca, tamanho):
    _, ultima_atualizacao = get_latest_data(categoria)
    # If any filter is empty, treat as None
    marca = marca if marca else None
    submarca = submarca if submarca else None
    tamanho = tamanho if tamanho else None

    search_id = str(uuid.uuid4())

    menores_dia = lista_menores_valores_dia(categoria=categoria,marca=marca,submarca=submarca,tamanho=tamanho)
    listagem = lista_cards(menores_dia, ultima_atualizacao)

    return listagem

# Callback for tracking offer clicks
@callback(
    Output(f"dummy-output-{categoria}", "children"),
    Input({"type": "offer-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def log_offer_click(n_clicks):
    if not any(n for n in n_clicks if n):
        return ""
        
    # Get clicked button index
    triggered = dash.callback_context.triggered_id
    if triggered is None:
        return ""
        
    button_index = triggered.get("index", 0)

    # Log the click event
    log_comprar_click(
        object_id=button_index,
        page='categoria'
    )
    
    return ""