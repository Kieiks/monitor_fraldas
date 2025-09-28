import dash_mantine_components as dmc
from dash import Dash, html, dcc, Output, Input, State
import dash
from dash_iconify import DashIconify

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)

server = app.server

def get_navbar(pathname):
    return [
        dmc.Text("Navegação", size="xs", c="gray.6", mb=8, tt="uppercase", fw=700, style={"letterSpacing": 1}),
        dmc.NavLink(
            label="Início",
            fw=600,
            leftSection=DashIconify(icon="ic:round-home", width=26, color="#228be6"),
            href="/",
            active=(pathname == "/"),
            style={"marginBottom": 6}
        ),
        dmc.NavLink(
            label="Fraldas",
            fw=600,
            href="/fraldas",
            leftSection=DashIconify(icon="mdi:diaper-outline", width=26, color="#228be6"),
            active=(pathname == "/fraldas"),
            style={"marginBottom": 6}
        ),
        dmc.NavLink(
            label="Aptanutri",
            fw=600,
            href="/aptanutri",
            leftSection=DashIconify(icon="game-icons:baby-bottle", width=26, color="#228be6"),
            active=(pathname == "/aptanutri"),
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
                                dmc.Burger(
                                    id="burger",
                                    opened=False,
                                    size="sm",
                                    color="#228be6",
                                    # only show Burger on mobile
                                    visibleFrom=None,  # or possibly `hiddenFrom="sm"` to hide on larger screens
                                    hiddenFrom="md",   # this hides the burger when width ≥ md, shows it below that
                                ),
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
                            gap="md",
                        ),
                        dmc.Space(w="auto"),
                        dmc.Box(),
                        # dmc.ThemeIcon(
                        #     DashIconify(icon="mdi:account-circle", width=32, color="#228be6"),
                        #     variant="light",
                        #     radius="xl",
                        #     size="lg"
                        # ),
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
        navbar={"width": 260, "breakpoint": "sm", "collapsed": {"mobile": True, "desktop": False}},
        padding="md",
        id="appshell",
    )
)

@app.callback(
    [Output("navbar", "children"),
    Output("navbar", "collapsed"),  # 👈 control collapse
    Output("burger", "opened"), ],    # 👈 sync burger
    Input("url", "pathname"),
    State("burger", "opened"),
    prevent_initial_call=True,
)
def update_navbar(pathname, opened):
    # your navbar content
    navbar_content = get_navbar(pathname or "/")

    # default collapse config
    collapsed = {"mobile": not opened, "desktop": False}

    # when user clicks a navlink (URL changes),
    # auto-close only on mobile
    collapsed = {"mobile": True, "desktop": False}

    return navbar_content, collapsed, False

@app.callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    prevent_initial_call=True
)
def toggle_navbar(opened):
    return {"width": 260, "breakpoint": "sm", "collapsed": {"mobile": not opened, "desktop": False}}


if __name__ == "__main__":
    app.run(debug=True)