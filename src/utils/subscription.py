from datetime import datetime
from .mongo import DATABASE

COLLECTION = DATABASE['subscriptions']

def add_subscription(email, categoria, marca, submarca, tamanho):
    """
    Add a subscription to the MongoDB 'subscriptions' collection.
    Returns True if inserted, False if duplicate.
    """
    # Check for duplicate (same email + filters)
    query = {
        "email": email,
        "categoria": categoria,
        "marca": marca,
        "submarca": submarca,
        "tamanho": tamanho
    }
    if COLLECTION.find_one(query):
        return False  # Already subscribed

    doc = {
        "email": email,
        "categoria": categoria,
        "marca": marca,
        "submarca": submarca,
        "tamanho": tamanho,
        "created_at": datetime.now()
    }
    COLLECTION.insert_one(doc)
    return True
