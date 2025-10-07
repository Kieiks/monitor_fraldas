import dash
from dash import html, dcc, Output, Input, callback
import dash_mantine_components as dmc

dash.register_page(
    __name__,
    path="/admin-panel",
    name="Admin Panel",
    order=9999,  # Hidden from navigation
)

layout = dmc.Paper(
    [
        dmc.Title("Painel de Controle", order=2, mb="md"),
        dmc.Alert(
            "Página administrativa. Não compartilhe o link.",
            color="yellow",
            mb="md",
        ),
        dmc.Group(
            [
                dmc.Paper(
                    [
                        dmc.Text("Total de Comprar Clicks", fw=700),
                        dmc.Text(id="comprar-click-count", size="xl", c="blue"),
                    ],
                    p="md",
                    withBorder=True,
                    shadow="xs",
                    radius="md",
                    style={"textAlign": "center"},
                ),
                dmc.Paper(
                    [
                        dmc.Text("Total de Emails Registrados", fw=700),
                        dmc.Text(id="email-count", size="xl", c="teal"),
                    ],
                    p="md",
                    withBorder=True,
                    shadow="xs",
                    radius="md",
                    style={"textAlign": "center"},
                ),
            ],
            gap="md",
            mb="lg",
        ),
        dmc.Title("Últimas Atividades", order=4, mb="md"),
        dmc.Paper(
            [
                dmc.Text("Últimos Comprar Clicks", fw=500, mb="sm"),
                dmc.List(id="comprar-click-list"),
                dmc.Space(h="md"),
                dmc.Text("Últimos Emails Registrados", fw=500, mb="sm"),
                dmc.List(id="email-list"),
            ],
            p="md",
            withBorder=True,
            shadow="xs",
            radius="md",
        ),
        dmc.Space(h="lg"),
        dmc.Paper(
            [
                dmc.Title("Ferramentas Administrativas", order=4, mb="md"),
                dmc.Button(
                    "Limpar Cache",
                    id="admin-clear-cache-btn",
                    color="red",
                    variant="filled",
                ),
                html.Div(id="admin-clear-cache-result", style={"marginTop": "1rem"}),
            ],
            p="md",
            withBorder=True,
            shadow="xs",
            radius="md",
        ),
    ],
    style={"maxWidth": 800, "margin": "40px auto", "padding": "32px"},
)

# Callbacks for statistics and admin actions would go here
