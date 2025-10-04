import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
from utils.tratamento import latest_records, lowest_per_timestamp
from utils.charts import trend_chart, recomendation_chart
from utils.comprar_click import log_comprar_click
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

# Register page with URL parameter pattern
dash.register_page(
    __name__,
    path="/product",
    path_template="/product",
    name="Detalhes do Produto"
)

# Layout for product details page with placeholders
def layout(categoria=None, marca=None, submarca=None, tamanho=None, **kwargs):

    tamanho = tamanho.replace(' ', '+')
    # Clean parameters from URL for title display
    product_title = f"{marca or 'Marca'} - {submarca or 'Submarca'} - {tamanho or 'Tamanho'}"
    
    # Fetch data for this product
    if marca and submarca and tamanho:
        # Get historical data for price trend
        historical_data = lowest_per_timestamp(categoria=categoria, 
                                             marca=marca, 
                                             qualidade=submarca, 
                                             tamanho=tamanho)
        historical_df = pd.DataFrame(historical_data)
        historical_df = historical_df.resample('D', on='timestamp').min().ffill().reset_index()

        # Get current offers for this product
        current_offers = latest_records(categoria=categoria, 
                                      marca=marca, 
                                      qualidade=submarca, 
                                      tamanho=tamanho)
        
        # Calculate statistics
        if not historical_df.empty:
            min_price = historical_df['min_value'].min()
            max_price = historical_df['min_value'].max()
            avg_price = historical_df['min_value'].mean()
            
            # Get current lowest price
            current_min = historical_df['min_value'].iloc[-1] if len(historical_df) > 0 else 0
            
            # Calculate percentile of current price
            percentile = int(100 * (1 - (current_min - min_price) / (max_price - min_price if max_price > min_price else 1)))
            
            # Determine recommendation text and color
            if percentile >= 75:
                rec_text = f"{percentile}% dos"
                rec_color = "teal"
                rec_message = "Excelente momento para comprar!"
            elif percentile >= 50:
                rec_text = f"{percentile}% dos"
                rec_color = "blue"
                rec_message = "Bom momento para comprar!"
            elif percentile >= 25:
                rec_text = f"{percentile}% dos"
                rec_color = "yellow"
                rec_message = "Considere esperar por ofertas melhores"
            else:
                rec_text = f"{percentile}% dos"
                rec_color = "red"
                rec_message = "Preço acima da média histórica"
            
            # Count number of stores with offers
            num_offers = len(current_offers) if current_offers else 0
        else:
            # Default values if no data is available
            min_price = max_price = avg_price = current_min = 0
            percentile = 0
            rec_text = "N/A"
            rec_color = "gray"
            rec_message = "Dados insuficientes"
            num_offers = 0
    else:
        # Default values if no parameters provided
        historical_df = pd.DataFrame()
        current_offers = []
        min_price = max_price = avg_price = current_min = 0
        percentile = 0
        rec_text = "N/A"
        rec_color = "gray"
        rec_message = "Selecione um produto"
        num_offers = 0
    
    return dmc.Paper(
        children=[
            # Hidden component to access URL parameters in callbacks
            dcc.Location(id="url", refresh=False),
            # Header section with back button and product title
            dmc.Group(
                [
                    dmc.Anchor(
                        dmc.Button(
                        f"Voltar para {categoria.capitalize()}",
                        leftSection=DashIconify(icon="mdi:arrow-left"),
                        variant="subtle",
                        color="gray",
                        size="sm",
                    ),
                    href=f'/{categoria}'
                    ),
                    dmc.Badge("Detalhes do Produto", color="blue", size="lg", variant="outline"),
                ],
                justify="space-between",
                mb="md",
            ),
            
            # Product title and info
            dmc.Title(product_title, order=2, mb="lg"),
            
            # Price history chart
            dmc.Paper(
                children=[
                    dmc.Group(
                        [
                            dmc.Title("Histórico de Preços", order=4, c="blue.7"),
                            dmc.Badge("Últimos 90 dias", color="blue", variant="light"),
                        ],
                        justify="space-between",
                        mb="md",
                    ),
                    # Price history chart with actual data
                    dcc.Graph(
                        id="price-history-chart",
                        figure=trend_chart(historical_df) if not historical_df.empty else go.Figure(
                            layout=dict(
                                xaxis=dict(visible=False),
                                yaxis=dict(visible=False),
                                annotations=[
                                    dict(
                                        text="Dados insuficientes para exibir gráfico",
                                        xref="paper",
                                        yref="paper",
                                        showarrow=False,
                                        font=dict(size=16)
                                    )
                                ],
                                height=300,
                                margin=dict(l=0, r=0, t=0, b=0),
                            )
                        ),
                        config={"displayModeBar": False},
                    ),
                ],
                p="lg",
                withBorder=True,
                shadow="sm",
                radius="md",
            ),
            
            dmc.Space(h="md"),
            
            # Recommendation chart section showing price percentile
            dmc.Paper(
                children=[
                    dmc.Group(
                        [
                            dmc.Title("Recomendação de Compra", order=4, c="blue.7"),
                            dmc.Badge("Análise de Preço", color="violet", variant="light"),
                        ],
                        justify="space-between",
                        mb="md",
                    ),
                    # Actual recommendation chart
                    dcc.Graph(
                        id="recommendation-chart",
                        figure=recomendation_chart(historical_df) if not historical_df.empty else go.Figure(
                            layout=dict(
                                xaxis=dict(visible=False),
                                yaxis=dict(visible=False),
                                annotations=[
                                    dict(
                                        text="Dados insuficientes para análise",
                                        xref="paper",
                                        yref="paper",
                                        showarrow=False,
                                        font=dict(size=14)
                                    )
                                ],
                                height=40,
                                margin=dict(l=0, r=0, t=0, b=0),
                            )
                        ),
                        config={"displayModeBar": False},
                    ),
                    dmc.Space(h="md"),
                    dmc.Group(
                        [
                            dmc.Group(
                                [
                                    DashIconify(icon="mdi:chart-bell-curve", width=20, color="#228be6"),
                                    dmc.Text("O preço atual é melhor que", fw=500),
                                    dmc.Text(f"{rec_text}", fw=700, c=rec_color),
                                    dmc.Text("preços históricos.", fw=500),
                                ],
                                gap="xs",
                            ),
                            dmc.Badge(
                                rec_message,
                                color=rec_color,
                                variant="filled",
                                size="lg",
                            ),
                        ],
                        justify="space-between",
                    ),
                ],
                p="lg",
                withBorder=True,
                shadow="sm",
                radius="md",
            ),
            
            dmc.Space(h="md"),
            
            # Current offers section
            dmc.Paper(
                children=[
                    dmc.Group(
                        [
                            dmc.Title("Ofertas Disponíveis", order=4, c="blue.7"),
                            dmc.Badge(f"{num_offers} {('oferta' if num_offers == 1 else 'ofertas')}", 
                                    color="teal" if num_offers > 0 else "gray", 
                                    variant="light"),
                        ],
                        justify="space-between",
                        mb="md",
                    ),
                    
                    # Desktop view - Table layout
                    dmc.Box(
                        # Hide on small screens using responsive styles
                        children=[
                            # Table header
                            dmc.Grid(
                                [
                                    dmc.GridCol(dmc.Text("Loja", fw=700, c="gray.7"), span=3),
                                    dmc.GridCol(dmc.Text("Preço Un.", fw=700, c="gray.7"), span=2),
                                    dmc.GridCol(dmc.Text("Preço Total", fw=700, c="gray.7"), span=2),
                                    dmc.GridCol(dmc.Text("Quantidade", fw=700, c="gray.7"), span=2),
                                    dmc.GridCol(dmc.Text("Ações", fw=700, c="gray.7"), span=3),
                                ],
                                mb="md",
                                style={"borderBottom": "2px solid #e9ecef", "paddingBottom": "8px"}
                            ),
                            
                            # Actual offer rows from database
                            *([
                                dmc.Grid(
                                    [
                                        dmc.GridCol(
                                            dmc.Group([
                                                # Store logo can be added here if needed
                                                dmc.Text(offer.get('LOJA', ''), fw=500),
                                            ]),
                                            span=3
                                        ),
                                        dmc.GridCol(
                                            dmc.Text(f"R$ {offer.get('UNIDADE', 0):.2f}".replace('.', ','), fw=600, c="blue.8"),
                                            span=2
                                        ),
                                        dmc.GridCol(
                                            dmc.Text(f"R$ {offer.get('PRECO', 0):.2f}".replace('.', ','), fw=500),
                                            span=2
                                        ),
                                        dmc.GridCol(
                                            dmc.Text(f"{offer.get('QTD', 0)} un", fw=500),
                                            span=2
                                        ),
                                        dmc.GridCol(
                                            dmc.Anchor(
                                                dmc.Button(
                                                    "Ver Oferta",
                                                    id={"type": "offer-button", "index": str(offer.get('_id', ''))},
                                                    rightSection=DashIconify(icon="mdi:open-in-new", width=16),
                                                    size="xs",
                                                    radius="xl",
                                                    variant="outline",
                                                    color="blue",
                                                ),
                                                href=offer.get('URL', '#'),
                                                target="_blank",
                                            ),
                                            span=3
                                        ),
                                    ],
                                    mb="xs",
                                    align="center",
                                    style={"borderBottom": "1px solid #e9ecef", "paddingBottom": "8px"}
                                ) for i, offer in enumerate(current_offers)
                            ]
                            if current_offers
                            else [
                                dmc.Grid(
                                    [
                                        dmc.GridCol(
                                            dmc.Text("Nenhuma oferta encontrada para este produto.", c="gray.6"),
                                            span=12,
                                            style={"textAlign": "center"}
                                        )
                                    ],
                                    mb="xs",
                                    align="center"
                                )
                            ]),
                        ]
                    ),
                    
                    # Mobile view - Card layout
                    # dmc.Box(
                    #     # Hide on large screens using responsive styles
                    #     children=[
                    #         # Card view for mobile
                    #         *[
                    #             dmc.Card(
                    #                 children=[
                    #                     dmc.Group(
                    #                         [
                    #                             # Store name
                    #                             dmc.Skeleton(height=30, width="80%"),
                    #                             # Price badge
                    #                             dmc.Badge(
                    #                                 children=dmc.Skeleton(height=20, width=60),
                    #                                 color="blue",
                    #                             ),
                    #                         ],
                    #                         justify="space-between",
                    #                     ),
                    #                     dmc.Space(h="xs"),
                    #                     # Price and quantity info
                    #                     dmc.SimpleGrid(
                    #                         cols=2,
                    #                         children=[
                    #                             dmc.Stack(
                    #                                 [
                    #                                     dmc.Text("Preço Un.", size="xs", c="gray.7"),
                    #                                     dmc.Skeleton(height=25, width="60%"),
                    #                                 ],
                    #                                 gap="xs",
                    #                             ),
                    #                             dmc.Stack(
                    #                                 [
                    #                                     dmc.Text("Preço Total", size="xs", c="gray.7"),
                    #                                     dmc.Skeleton(height=25, width="70%"),
                    #                                 ],
                    #                                 gap="xs",
                    #                             ),
                    #                         ],
                    #                     ),
                    #                     dmc.Space(h="md"),
                    #                     dmc.Button(
                    #                         "Ver Oferta",
                    #                         rightSection=DashIconify(icon="mdi:open-in-new", width=16),
                    #                         fullWidth=True,
                    #                         variant="outline",
                    #                         color="blue",
                    #                     ),
                    #                 ],
                    #                 withBorder=True,
                    #                 shadow="sm",
                    #                 mb="md",
                    #                 p="md",
                    #                 radius="md",
                    #             ) for _ in range(5)
                    #         ],
                    #     ]
                    # ),
                ],
                p="lg",
                withBorder=True,
                shadow="sm",
                radius="md",
                mt="md",
            ),
            
            dmc.Space(h="md"),
            
            # Price statistics section
            dmc.Paper(
                children=[
                    dmc.Title("Estatísticas de Preço", order=4, c="blue.7", mb="md"),
                    
                    dmc.SimpleGrid(
                        cols=3,
                        # gap="lg",
                        children=[
                            dmc.Paper(
                                children=[
                                    dmc.Text("Preço Mínimo", fw=500, size="sm", c="gray.6"),
                                    dmc.Text(f"R$ {min_price:.2f}".replace('.', ','), fw=700, size="xl", c="green"),
                                ],
                                p="md",
                                withBorder=True,
                                shadow="xs",
                                radius="md",
                                style={"textAlign": "center"},
                            ),
                            dmc.Paper(
                                children=[
                                    dmc.Text("Preço Médio", fw=500, size="sm", c="gray.6"),
                                    dmc.Text(f"R$ {avg_price:.2f}".replace('.', ','), fw=700, size="xl", c="blue"),
                                ],
                                p="md",
                                withBorder=True,
                                shadow="xs",
                                radius="md",
                                style={"textAlign": "center"},
                            ),
                            dmc.Paper(
                                children=[
                                    dmc.Text("Preço Máximo", fw=500, size="sm", c="gray.6"),
                                    dmc.Text(f"R$ {max_price:.2f}".replace('.', ','), fw=700, size="xl", c="red"),
                                ],
                                p="md",
                                withBorder=True,
                                shadow="xs",
                                radius="md",
                                style={"textAlign": "center"},
                            ),
                        ],
                    ),
                ],
                p="lg",
                withBorder=True,
                shadow="sm",
                radius="md",
            ),
            
            # Hidden div for tracking offer clicks
            html.Div(id="dummy-output", style={"display": "none"}),
            
            # Price alert section
            dmc.Paper(
                children=[
                    dmc.Group(
                        [
                            dmc.Group(
                                [
                                    DashIconify(icon="mdi:bell-outline", width=24, color="#228be6"),
                                    dmc.Title("Alertas de Preço", order=4, c="blue.7"),
                                ],
                                gap="xs",
                            ),
                            dmc.Badge("Novo", color="red"),
                        ],
                        justify="space-between",
                        mb="md",
                    ),
                    dmc.Text(
                        "Receba notificações quando este produto estiver em oferta.",
                        mb="md",
                        c="gray.7",
                    ),
                    dmc.Group(
                        [
                            dmc.TextInput(
                                id="email-input",
                                placeholder="Seu email",
                                leftSection=DashIconify(icon="mdi:email-outline"),
                                style={"flexGrow": 1},
                            ),
                            dmc.Button(
                                "Ativar Alerta",
                                id="subscribe-button",
                                leftSection=DashIconify(icon="mdi:bell-plus-outline"),
                                color="blue",
                            ),
                        ],
                    ),
                    html.Div(id="subscription-result"),
                ],
                p="lg",
                withBorder=True,
                shadow="sm",
                radius="md",
                mt="md",
                mb="md",
            ),
        ],
        style={
            "maxWidth": 1000,
            "margin": "0 auto",
            "padding": "20px",
        }
    )


# Callback for email subscription
@callback(
    Output("subscription-result", "children"),
    Input("subscribe-button", "n_clicks"),
    State("email-input", "value"),
    State("url", "search"),
    prevent_initial_call=True
)
def subscribe_to_alerts(n_clicks, email, url_search):
    if n_clicks is None or not email:
        return ""
        
    # Parse URL parameters to get product info
    import urllib.parse
    parsed = urllib.parse.parse_qs(url_search.lstrip('?'))
    
    categoria = parsed.get('categoria', [''])[0]
    marca = parsed.get('marca', [''])[0]
    submarca = parsed.get('submarca', [''])[0]
    tamanho = parsed.get('tamanho', [''])[0]
    
    if not marca or not submarca or not tamanho:
        return dmc.Alert(
            "Informações de produto incompletas para ativar alertas.",
            title="Erro",
            color="red",
            withCloseButton=True,
        )
        
    # Add subscription
    from utils.subscription import add_subscription
    success = add_subscription(email, categoria, marca, submarca, tamanho)
    
    if success:
        return dmc.Alert(
            f"Você receberá alertas quando {marca} {submarca} {tamanho} estiver em oferta!",
            title="Alerta ativado com sucesso!",
            color="green",
            withCloseButton=True,
        )
    else:
        return dmc.Alert(
            "Você já está inscrito para receber alertas deste produto.",
            title="Alerta já existente",
            color="yellow",
            withCloseButton=True,
        )


# Callback for tracking offer clicks
@callback(
    Output("dummy-output", "children"),
    Input({"type": "offer-button", "index": dash.ALL}, "n_clicks"),
    State("url", "search"),
    prevent_initial_call=True
)
def log_offer_click(n_clicks, url_search):
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
        page='produto'
    )
    
    return ""

