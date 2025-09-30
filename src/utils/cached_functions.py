from flask_caching import Cache
from utils.tratamento import listagem_inicial, lista_menores_valores_dia
import dash

# Initialize cache here or import the existing cache object
cache = Cache(config={
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "/tmp/cache",
    "CACHE_DEFAULT_TIMEOUT": 28800  # 8 hours
})
cache.init_app(dash.get_app().server)

# Cached wrappers
@cache.memoize(timeout=28800)
def get_listagem_inicial_cached(categoria):
    print(f"[CACHE] Fetching listagem_inicial for {categoria}")
    return listagem_inicial(only_last_timestamp=True, categoria=categoria)

@cache.memoize(timeout=28800)
def get_lista_menores_cached(categoria=None, marca=None, submarca=None, tamanho=None):
    print(f"[CACHE] Fetching lista_menores_valores_dia for {categoria}, {marca}, {submarca}, {tamanho}")
    return lista_menores_valores_dia(
        categoria=categoria,
        marca=marca,
        submarca=submarca,
        tamanho=tamanho
    )