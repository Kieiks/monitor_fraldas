from dash import dcc, html, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify

register_page(__name__, path="/", name="Início", order=0)

layout = dmc.Paper(
    [
        # Hero Section with Clear Value Proposition
        dmc.Box(
            [
                dmc.Group(
                    [
                        dmc.Title("Essenciais do Bebê", order=1, style={"fontSize": 48, "color": "#0a3d62", "fontWeight": 700}),
                        dmc.Badge("BETA", color="blue", variant="filled", size="lg", 
                                 style={"background": "#5dade2", "color": "white"})
                    ],
                    style={"justifyContent": "center", "alignItems": "center"}
                ),
                
                dmc.Text(
                    "Compare preços unitários de fraldas e encontre as melhores ofertas em segundos.",
                    ta="center",
                    style={"fontSize": 22, "color": "#2c3e50", "maxWidth": "750px", "margin": "20px auto"}
                ),
                
                dmc.Group(
                    [
                        dmc.Button(
                            "Ofertas de Fraldas", 
                            leftSection=DashIconify(icon="mdi:diaper-outline", width=24),
                            # href="/fraldas",
                            radius="md",
                            size="lg",
                            variant="outline",
                            color="blue",
                            style={"fontSize": 18, "padding": "10px 30px", "color": "#2980b9", "borderColor": "#2980b9"}
                        ),
                        
                        dmc.Button(
                            "Ofertas de Fórmulas Infantis",
                            leftSection=DashIconify(icon="mdi:baby-bottle-outline", width=24),
                            # href="/aptanutri",
                            radius="md",
                            size="lg",
                            variant="outline",
                            color="blue",
                            style={"fontSize": 18, "padding": "10px 30px", "color": "#2980b9", "borderColor": "#2980b9"}
                        ),
                    ],
                    style={"justifyContent": "center", "marginTop": 40, "marginBottom": 60, "gap": "20px"}
                ),
            ],
            style={"paddingTop": 40, "background": "#e3f2fd", "borderRadius": "8px", "padding": "40px 20px"}
        ),

        # How It Works Section
        dmc.Title("Como Funciona", order=1, ta="center", style={"fontSize": 36, "color": "#0a3d62", "marginTop": 60, "marginBottom": 40}),

        dmc.Grid(
            [
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                dmc.Text("1", fw=700, style={"fontSize": 60, "color": "#0a3d62"}),
                                dmc.Title("Selecione os Filtros", order=3, style={"marginBottom": 10}),
                                dmc.Text(
                                    "Escolha marca, modelo e tamanho das fraldas que você precisa.",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "md": 4}, style={"paddingBottom": 20}
                ),
                
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                dmc.Text("2", fw=700, style={"fontSize": 60, "color": "#0a3d62"}),
                                dmc.Title("Compare Preços Unitários", order=3, style={"marginBottom": 10}),
                                dmc.Text(
                                    "Veja o preço unitário em vez do valor total do pacote.",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "md": 4}, style={"paddingBottom": 20}
                ),
                
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                dmc.Text("3", fw=700, style={"fontSize": 60, "color": "#0a3d62"}),
                                dmc.Title("Compre com Economia", order=3, style={"marginBottom": 10}),
                                dmc.Text(
                                    "Acesse diretamente a loja com o melhor preço.",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "md": 4}, style={"paddingBottom": 20}
                ),
            ],
        ),
        
        # Why Use Section
        dmc.Title("Por que usar o Monitor Fraldas?", order=1, ta="center", 
                 style={"fontSize": 36, "color": "#0a3d62", "marginTop": 60, "marginBottom": 40}),
        
        dmc.Grid(
            [
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                DashIconify(icon="mdi:currency-usd", width=48, color="#5dade2", 
                                          style={"margin": "0 auto 15px", "display": "block"}),
                                dmc.Title("Economize Dinheiro", order=4, ta="center", style={"marginBottom": 10}),
                                dmc.Text(
                                    "Compare preços entre diferentes lojas.",
                                    ta="center",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "sm": 6, "lg": 3}, style={"paddingBottom": 20}
                ),
                
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                DashIconify(icon="mdi:clock-time-four", width=48, color="#5dade2", 
                                          style={"margin": "0 auto 15px", "display": "block"}),
                                dmc.Title("Economize Tempo", order=4, ta="center", style={"marginBottom": 10}),
                                dmc.Text(
                                    "Não perca tempo visitando diversos sites.",
                                    ta="center",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "sm": 6, "lg": 3}, style={"paddingBottom": 20}
                ),
                
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                DashIconify(icon="mdi:update", width=48, color="#5dade2", 
                                          style={"margin": "0 auto 15px", "display": "block"}),
                                dmc.Title("Preços Atualizados", order=4, ta="center", style={"marginBottom": 10}),
                                dmc.Text(
                                    "Preços coletados diariamente.",
                                    ta="center",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "sm": 6, "lg": 3}, style={"paddingBottom": 20}
                ),
                
                dmc.GridCol(
                    [
                        dmc.Paper(
                            [
                                DashIconify(icon="mdi:store", width=48, color="#5dade2", 
                                          style={"margin": "0 auto 15px", "display": "block"}),
                                dmc.Title("Múltiplas Lojas", order=4, ta="center", style={"marginBottom": 10}),
                                dmc.Text(
                                    "Compare preços entre diferentes varejistas.",
                                    ta="center",
                                    style={"color": "#2c3e50"}
                                ),
                            ],
                            p="xl",
                            radius="md",
                            style={"height": "100%", "background": "#f8fafc", "textAlign": "center"}
                        ),
                    ],
                    span={"base": 12, "sm": 6, "lg": 3}, style={"paddingBottom": 20}
                ),
            ],
        ),
        
        # Call to Action Section
        dmc.Box(
            dmc.Button(
                "Comece a economizar agora",
                # href="/fraldas",
                radius="md",
                size="xl",
                color="blue",
                style={"background": "#5dade2", "fontSize": 22, "display": "block", "margin": "60px auto 40px", 
                       "padding": "15px 40px", "maxWidth": "500px"}
            ),
            style={"textAlign": "center"}
        ),
    ],
    style={
        "maxWidth": 1200,
        "margin": "0 auto",
        "padding": "20px",
        "background": "white",
        "minHeight": "calc(100vh - 120px)",
    }
)