from datetime import datetime
from .mongo import DATABASE

COLLECTION = DATABASE['filter_usage']

def log_filter_usage(categoria, marca, submarca, tamanho, page, search_id=None):
    doc = {
        "timestamp": datetime.now(),
        "categoria": categoria,
        "marca": marca,
        "submarca": submarca,
        "tamanho": tamanho,
        "page": page,
        "search_id": search_id
    }
    COLLECTION.insert_one(doc)
    print(f"Logged filter usage: {doc}")

if __name__ == "__main__":
    # Example usage
    log_filter_usage("Fraldas", "Pampers", "Ajuste Total", "G", "pesquisa_rapida")
