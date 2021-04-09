import pymongo


def get_mutation_data(gene, variant, uri):
    client = pymongo.MongoClient(uri)
    db = client["variants"]
    variant_summaries_collection = db["variant_summaries"]
    return variant_summaries_collection.find_one({"gene": gene, "variant": variant})


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
    networks_collection = db["kegg_networks"]
    return networks_collection.find_one({"id": net_id})


def get_drug_links(target_id, uri):
    client = pymongo.MongoClient(uri)
    db = client["drugs"]
    drug_links_collection = db["kegg_drug_links"]
    return drug_links_collection.find_one({"target": target_id})


def get_drug_names(kegg_id, uri):
    client = pymongo.MongoClient(uri)
    db = client["drugs"]
    drug_links_collection = db["kegg_drugss"]
    return drug_links_collection.find_one({"kegg_id": kegg_id})
