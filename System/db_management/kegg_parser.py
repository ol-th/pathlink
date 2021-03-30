import requests
import sys
import pymongo
import time
import re


def new_gene_dict(input_id, input_name):
    output = {"name": input_name.replace("*", "").strip()}
    if "C" in input_id:
        output["mutation"] = False
        output["type"] = "Compound"
        output["id"] = "cpd:" + input_id
    elif "K" in input_id:
        output["mutation"] = False
        output["type"] = "Perturbant"
        output["id"] = input_id
    else:
        output["type"] = "Gene"
        if "v" in input_id:
            output["mutation"] = True
            output["id"] = "hsa:" + input_id.split("v")[0]
        else:
            output["mutation"] = False
            output["id"] = "hsa:" + input_id

    return output


def new_relation_dict(previous_genes, symbol):
    symbol_table = {
        "->": "activation",
        "-|": "inhibition",
        "=>": "expression",
        "=|": "repression",
        "//": "missing interaction",
        ">>": "enzyme-enzyme",
        "--": "complex formation"
    }

    output = {
        "mutation_activated": any([prev["mutation"] for prev in previous_genes]),
        "type": symbol_table[symbol]
    }

    return output


def create_products(expanded_string, definition_string):
    names_string = definition_string
    ids_string = expanded_string
    for char in "()":
        ids_string = ids_string.replace(char, "")
        names_string = names_string.replace(char, "")

    # This splits on + and ,
    names_string = names_string.replace("+", ",")
    names = names_string.split(",")

    ids_string = ids_string.replace("+", ",")
    gene_ids = ids_string.split(",")

    return [new_gene_dict(gene_id, name) for gene_id, name in zip(gene_ids, names)]


def get_network_entries(ids):
    query = "+".join(ids)
    r = requests.get("http://rest.kegg.jp/get/" + query)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    entries = r.text.split("///")[:-1]
    if not len(entries) == len(ids):
        return None

    entries_lines = [entry.split("\n") for entry in entries]

    output = []
    for net_id, entry in zip(ids, entries_lines):
        current_def_and_expanded = [net_id]
        for line in entry:
            if "DEFINITION" in line:
                current_def_and_expanded.append(line.replace("DEFINITION", "").strip())
            if "EXPANDED" in line:
                current_def_and_expanded.append(line.replace("EXPANDED", "").strip())
        output.append(current_def_and_expanded)

    return output


def get_all_relevant_networks():
    r = requests.get("http://rest.kegg.jp/link/network/pathway")
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    lines = r.text.split("\n")[:-1]
    networks = [line.split("\t")[1] for line in lines]
    return set(networks)


def upload_nets(nets, collection):
    network_dicts = []
    for net in nets:
        definition_tokens = net[1].split(" ")
        expanded_tokens = net[2].split(" ")
        index = 0
        current_id = 0
        net_query = "CREATE "
        products_source = create_products(expanded_tokens[0], definition_tokens[0])
        # To contain ids of source nodes
        source_ids = []
        # Go through first source products, assign ids and add to query
        for product in products_source:
            net_query += "(a" + str(current_id) + ":" + product["type"] + \
                         "{name:\"" + product["name"] + "\", kegg_ids: [\"" + product["id"] + "\"]}),"
            source_ids.append(current_id)
            current_id += 1

        while index + 2 < len(expanded_tokens):
            # Get current relation
            relation_dict = new_relation_dict(products_source, expanded_tokens[index + 1])
            # Get destination products
            products_destination = create_products(expanded_tokens[index + 2], definition_tokens[index + 2])
            # Assign ids to destination products and add to query
            dest_ids = []
            for product in products_destination:
                net_query += "(a" + str(current_id) + ":" + product["type"] + \
                             "{name:\"" + product["name"] + "\", kegg_ids: [\"" + product["id"] + "\"]}),"
                dest_ids.append(current_id)
                current_id += 1

            for source in source_ids:
                for dest in dest_ids:
                    net_query += "(a" + str(source) + ")-[:Network {subtypes:[\"" + relation_dict["type"] + "\""
                    if relation_dict["mutation_activated"]:
                        net_query += ",\"mutation activated\""
                    net_query += "]}]->" + "(a" + str(dest) + "),"
            source_ids = dest_ids
            index += 2
        net_query = net_query[:-1]
        network_dicts.append({"id": net[0], "query": net_query})
    collection.insert_many(network_dicts)


def get_drugs_list():
    r = requests.get("http://rest.kegg.jp/list/drug")
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    lines = r.text.split("\n")[:-1]
    output = []
    for line in lines:
        info = line.split("\t")
        drug_id = info[0]
        drug_names = info[1]
        names_list = []
        for name in drug_names.split(";"):
            names_list.append(re.sub(r"\([^()]*\)", "", name).strip())
        output.append({
            "kegg_id": drug_id,
            "names": names_list
        })

    return output


def get_all_relevant_drug_links():
    output = []

    # Pathways
    r = requests.get("http://rest.kegg.jp/link/drug/pathway")
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    lines = r.text.split("\n")[:-1]

    pathways_to_drugs = {}
    for line in lines:
        entries = line.split("\t")
        pathway = entries[0]
        drug = entries[1]
        if pathway not in pathways_to_drugs.keys():
            pathways_to_drugs[pathway] = []
        pathways_to_drugs[pathway].append(drug)

    for key in pathways_to_drugs.keys():
        output.append({"target": key.replace("map", "hsa"), "drugs": pathways_to_drugs[key]})

    time.sleep(3)
    # Genes
    r = requests.get("http://rest.kegg.jp/link/drug/hsa")
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    lines = r.text.split("\n")[:-1]

    genes_to_drugs = {}
    for line in lines:
        entries = line.split("\t")
        gene = entries[0]
        drug = entries[1]
        if gene not in genes_to_drugs.keys():
            genes_to_drugs[gene] = []
        genes_to_drugs[gene].append(drug)

    for key in genes_to_drugs.keys():
        output.append({"target": key, "drugs": genes_to_drugs[key]})

    return output


def main():
    database_url = sys.argv[1]
    client = pymongo.MongoClient(database_url)
    # db = client["networks"]
    # kegg_networks_collection = db["kegg_networks"]
    #
    # if kegg_networks_collection.count() > 0:
    #     print("Dropping networks collection...")
    #     kegg_networks_collection.drop()
    #
    # print("Importing network ids...")
    # networks = list(get_all_relevant_networks())
    # print("Importing " + str(len(networks)) + " networks.")
    # time.sleep(3)
    #
    # network_index = 0
    #
    # while network_index + 10 <= len(networks):
    #     this_10 = networks[network_index:network_index + 10]
    #     nets = get_network_entries(this_10)
    #
    #     print("Adding networks " + str(network_index) + " - " + str(network_index + 10))
    #     upload_nets(nets, kegg_networks_collection)
    #     time.sleep(3)
    #
    #     network_index += 10
    #
    # last_nets_index = network_index
    # last_nets = networks[last_nets_index:]
    # print("Adding last networks...")
    # upload_nets(last_nets, kegg_networks_collection)

    db = client["drugs"]
    kegg_drugs_collection = db["kegg_drugs"]
    if kegg_drugs_collection.count_documents({}) > 0:
        print("Dropping drugs collection...")
        kegg_drugs_collection.drop()

    print("Updating drugs collection...")
    drugs = get_drugs_list()
    kegg_drugs_collection.insert_many(drugs)

    kegg_drug_links_collection = db["kegg_drug_links"]
    if kegg_drug_links_collection.count_documents({}) > 0:
        print("Dropping drug links collection...")
        kegg_drug_links_collection.drop()

    print("Updating drugs links...")
    drugs = get_all_relevant_drug_links()
    kegg_drug_links_collection.insert_many(drugs)


if __name__ == '__main__':
    main()
