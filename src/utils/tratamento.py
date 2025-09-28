from datetime import datetime, timedelta
from .mongo import DATABASE

COLLECTION = DATABASE['pourbebe']

def latest_records(categoria=None,marca=None,qualidade=None,tamanho=None):

    latest_ts = COLLECTION.find_one(sort=[("timestamp", -1)])["timestamp"]

    match_stage = {'timestamp': latest_ts}
    if categoria is not None:
        if isinstance(categoria, list):
            match_stage['CATEGORIA'] = {'$in': categoria}
        else:
            match_stage['CATEGORIA'] = categoria
    if marca is not None:
        if isinstance(marca, list):
            match_stage['MARCA'] = {'$in': marca}
        else:
            match_stage['MARCA'] = marca
    if qualidade is not None:
        if isinstance(qualidade, list):
            match_stage['QUALIDADE'] = {'$in': qualidade}
        else:
            match_stage['QUALIDADE'] = qualidade
    if tamanho is not None:
        if isinstance(tamanho, list):
            match_stage['TAMANHO'] = {'$in': tamanho}
        else:
            match_stage['TAMANHO'] = tamanho

    pipeline = [
        {'$match': match_stage},
        # {'$project': {'_id': 0}},
        {"$sort": {"UNIDADE": 1}}
    ]

    results = list(COLLECTION.aggregate(pipeline))

    return results

def listagem_inicial(only_last_timestamp=True, categoria=None):
    # Step 1: Find the latest timestamp in the collection
    latest_ts = COLLECTION.find_one(sort=[("timestamp", -1)])["timestamp"]

    # Step 2: Build pipeline conditionally
    pipeline = []

    if only_last_timestamp:
        # Suggestion: add an index on 'timestamp' for fast lookup
        pipeline.append({"$match": {"timestamp": latest_ts}})

    if categoria is not None:
        if isinstance(categoria, list):
            pipeline.append({"$match": {"CATEGORIA": {"$in": categoria}}})
        else:
            pipeline.append({"$match": {"CATEGORIA": categoria}})

    # Suggestion: add a compound index on (CATEGORIA, MARCA, QUALIDADE, TAMANHO) for fast grouping
    pipeline.extend([
        {"$group": {
            "_id": {
                "CATEGORIA": "$CATEGORIA",
                "MARCA": "$MARCA",
                "QUALIDADE": "$QUALIDADE",
                "TAMANHO": "$TAMANHO"
            }
        }},
        {"$project": {
            "_id": 0,
            "CATEGORIA": "$_id.CATEGORIA",
            "MARCA": "$_id.MARCA",
            "QUALIDADE": "$_id.QUALIDADE",
            "TAMANHO": "$_id.TAMANHO"
        }}
    ])

    uniques = list(COLLECTION.aggregate(pipeline))

    return uniques, latest_ts

def lista_menores_valores_dia(categoria, marca, submarca, tamanho):

    # Step 1: Get latest timestamp
    latest_ts = COLLECTION.find_one(sort=[("timestamp", -1)])["timestamp"]

    match_stage = {'timestamp': latest_ts}
    if categoria is not None:
        if isinstance(categoria, list):
            match_stage['CATEGORIA'] = {'$in': categoria}
        else:
            match_stage['CATEGORIA'] = categoria
    if marca is not None:
        if isinstance(marca, list):
            match_stage['MARCA'] = {'$in': marca}
        else:
            match_stage['MARCA'] = marca
    if submarca is not None:
        if isinstance(submarca, list):
            match_stage['QUALIDADE'] = {'$in': submarca}
        else:
            match_stage['QUALIDADE'] = submarca
    if tamanho is not None:
        if isinstance(tamanho, list):
            match_stage['TAMANHO'] = {'$in': tamanho}
        else:
            match_stage['TAMANHO'] = tamanho

    # Step 2: Aggregation
    pipeline = [
        # Match last timestamp + dropdown filters
        {'$match': match_stage},
        
        # Sort globally by LOJA then UNIDADE ascending
        {"$sort": {"UNIDADE": 1}},
        
        # Group by LOJA, take the first doc (lowest UNIDADE per LOJA)
        {"$group": {
            "_id": {"CATEGORIA": "$CATEGORIA", "MARCA": "$MARCA", "QUALIDADE": "$QUALIDADE", "TAMANHO": "$TAMANHO"}, #"LOJA": "$LOJA", 
            "doc": {"$first": "$$ROOT"}
        }},
        
        {"$replaceRoot": {"newRoot": "$doc"}},

        {"$sort": {"UNIDADE": 1}},
    ]

    results = list(COLLECTION.aggregate(pipeline))

    return results

def lowest_per_timestamp(categoria=None, marca=None, qualidade=None, tamanho=None):

    # compute 90-day cutoff
    cutoff_date = datetime.now() - timedelta(days=90)
    # build match dynamically
    match_stage = {}
    if categoria is not None:
        if isinstance(categoria, list):
            match_stage['CATEGORIA'] = {'$in': categoria}
        else:
            match_stage['CATEGORIA'] = categoria
    if marca is not None:
        if isinstance(marca, list):
            match_stage['MARCA'] = {'$in': marca}
        else:
            match_stage['MARCA'] = marca
    if qualidade is not None:
        if isinstance(qualidade, list):
            match_stage['QUALIDADE'] = {'$in': qualidade}
        else:
            match_stage['QUALIDADE'] = qualidade
    if tamanho is not None:
        if isinstance(tamanho, list):
            match_stage['TAMANHO'] = {'$in': tamanho}
        else:
            match_stage['TAMANHO'] = tamanho

    pipeline = [
        # Add a real date field parsed from your string timestamp
        {"$match": {
            **match_stage,
            "timestamp": {"$gte": cutoff_date}
        }},
        {
            '$group': {
                '_id': '$timestamp',
                'min_value': {'$min': '$UNIDADE'}   # change VALOR if your field has another name
            }
        },
        {
            '$project': {
                '_id': 0,
                'timestamp': '$_id',
                'min_value': 1
            }
        },
        {'$sort': {'timestamp': 1}}
    ]

    results = list(COLLECTION.aggregate(pipeline))
    return results



# merged_df = load_data()
# print(lowest_per_timestamp('fraldas','PAMPERS','AJUSTE TOTAL','XG'))
# print(recommendation_action())
# latest_records()