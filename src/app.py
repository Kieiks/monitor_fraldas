import dash_mantine_components as dmc
from dash import Dash, html, dcc, Output, Input
import dash
from dash_iconify import DashIconify

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)

def get_navbar(pathname):
    return [
        dmc.Text("Navegação", size="xs", c="gray.6", mb=8, tt="uppercase", fw=700, style={"letterSpacing": 1}),
        # dmc.NavLink(
        #     label="Página Inicial",
        #     fw=600,
        #     href="/",
        #     leftSection=DashIconify(icon="bi:house-heart-fill", width=22, color="#228be6"),
        #     active=(pathname == "/" or pathname == ""),
        #     style={"marginBottom": 6}
        # ),
        dmc.NavLink(
            label="Pesquisa Rápida",
            fw=600,
            href="/",
            leftSection=DashIconify(icon="icomoon-free:price-tags", width=22, color="#228be6"),
            active=(pathname == "/"),
            style={"marginBottom": 6}
        ),
        dmc.NavLink(
            label="Dashboard",
            fw=600,
            href="/dashboard",
            leftSection=DashIconify(icon="mdi:view-dashboard", width=22, color="#228be6"),
            active=(pathname == "/dashboard"),
            style={"marginBottom": 6}
        ),
        # dmc.NavLink(
        #     label="Fraldas",
        #     fw=600,
        #     href="/fraldas",
        #     leftSection=DashIconify(icon="mdi:view-dashboard", width=22, color="#228be6"),
        #     active=(pathname == "/fraldas"),
        #     style={"marginBottom": 6}
        # ),
        dmc.Divider(my="md"),
        dmc.Text("Outros", size="xs", c="gray.6", mb=8, tt="uppercase", fw=700, style={"letterSpacing": 1}),
        # Example for future links
        # dmc.NavLink(
        #     label="Configurações",
        #     fw=500,
        #     href="/settings",
        #     leftSection=DashIconify(icon="mdi:cog", width=20, color="#868e96"),
        # ),
    ]

app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dcc.Location(id="url"),
            # Enhanced Header
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                # dmc.Avatar(src="assets/baby-logo.png", color="blue", radius="xl", size='lg'),  # Use your logo here
                                dmc.ThemeIcon(
                                    DashIconify(icon="streamline-freehand:family-baby-change-diaper", width=32, color="#228be6"),
                                    variant="light",
                                    radius="xl",
                                    size=48
                                ),
                                dmc.Box(
                                    [
                                        dmc.Text("Essenciais do Bebê", size="xl", fw=800, c='blue.7', style={"letterSpacing": 1}),
                                        dmc.Text("Monitoramento inteligente de preços", size="sm", c="gray.6"),
                                    ]
                                ),
                            ],
                            align="center",
                            gap="md"
                        ),
                        dmc.Space(w="auto"),
                        dmc.ThemeIcon(
                            DashIconify(icon="mdi:account-circle", width=32, color="#228be6"),
                            variant="light",
                            radius="xl",
                            size="lg"
                        ),
                    ],
                    justify="space-between",
                    align="center",
                    h="100%",
                    px="lg",
                ),
                style={"borderBottom": "1px solid #e9ecef", "background": "#f8fafc"}
            ),
            # Navbar placeholder, will be updated by callback
            dmc.AppShellNavbar(
                id="navbar",
                children=get_navbar("/"),
                p="md",
                style={"background": "#f8fafc", "borderRight": "1px solid #e9ecef"}
            ),
            dmc.AppShellMain(dash.page_container),
            # Optional Footer
            dmc.AppShellFooter(
                dmc.Text("© 2025 Essenciais do Bebê", size="xs", c="gray.5", ta="center"),
                style={"background": "#f8fafc", "borderTop": "1px solid #e9ecef"}
            ),
        ],
        header={"height": 70},
        navbar={"width": 260, "breakpoint": "sm", "collapsed": {"desktop": False}},
        padding="md",
        id="appshell",
    )
)

@app.callback(
    Output("navbar", "children"),
    Input("url", "pathname"),
)
def update_navbar(pathname):
    return get_navbar(pathname or "/")

if __name__ == "__main__":
    app.run_server(debug=True)