import dash
from dash import html, Output, Input, callback
import dash_mantine_components as dmc
from utils.cached_functions import cache

dash.register_page(
    __name__,
    path="/clear-cache",
    name="Clear Cache",
    order=9999,  # Hide from navigation if you use a menu
)

layout = dmc.Paper(
    [
        dmc.Title("Admin: Limpar Cache", order=2, mb="md"),
        dmc.Alert(
            "Esta página é apenas para uso administrativo. Não compartilhe o link.",
            color="yellow",
            mb="md",
        ),
        dmc.Button(
            "Limpar Cache",
            id="clear-cache-btn",
            color="red",
            variant="filled",
        ),
        html.Div(id="clear-cache-result", style={"marginTop": "1rem"}),
    ],
    style={"maxWidth": 500, "margin": "40px auto", "padding": "32px"},
)

@callback(
    Output("clear-cache-result", "children"),
    Input("clear-cache-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_cache(n_clicks):
    if n_clicks:
        cache.clear()
        return dmc.Alert("Cache limpo com sucesso!", color="green")
    return ""
