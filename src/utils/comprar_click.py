from datetime import datetime
from .mongo import DATABASE

COLLECTION = DATABASE['comprar_clicks']

def log_comprar_click(object_id, search_id, page):
    doc = {
        "pourbebe_object": object_id,
        "search_id": search_id,
        "timestamp": datetime.now(),
        "page": page,
    }
    try:
        COLLECTION.insert_one(doc)
        print(f"Logged comprar click: {doc}")
    except Exception as e:
        print(f"[Comprar Click Logging Error] {e}")

if __name__ == "__main__":
    # Example usage
    log_comprar_click("example_object_id", "pesquisa_rapida")
