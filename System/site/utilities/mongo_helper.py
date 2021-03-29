import pymongo


def get_mutation_data(gene, variant, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    variant_summaries_collection = db["variant_summaries"]
    return variant_summaries_collection.find({"gene": gene, "variant": variant})


def get_mutations(gene, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    variant_summaries_collection = db["variant_summaries"]
    return variant_summaries_collection.find({"gene": gene})


def variant_evidence(gene, variant, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    evidence_summaries_collection = db["evidence_summaries"]
    return evidence_summaries_collection.find({"gene": gene, "variant": variant})


def get_network_entry(net_id, uri):
    client = pymongo.MongoClient(uri)
    db = client["networks"]
    evidence_summaries_collection = db["kegg_networks"]
    return evidence_summaries_collection.find_one({"id": net_id})
