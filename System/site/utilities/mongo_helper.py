import pymongo


def get_mutation_data(gene, variant, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    variant_summaries_collection = db["variant_summaries"]
    return variant_summaries_collection.find({"gene": gene, "variant": variant})


def variant_evidence(gene, variant, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    evidence_summaries_collection = db["evidence_summaries"]
    return evidence_summaries_collection.find({"gene": gene, "variant": variant})
