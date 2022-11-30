import requests


def get_functional_network(gene_list):
    gene_list_string = "%0d".join(gene_list)
    params = {
        "identifiers": gene_list_string,
        "species": 9606,
        "required_score": 750,
        "add_nodes": 10,
        "show_query_node_labels": 1,
    }
    r = requests.get("https://string-db.org/api/tsv-no-header/network", params=params)
    if r.status_code != 200 or r.text == "" or r.text.lower().startswith("error"):
        return None

    links_dict = {}
    for line in r.text.split("\n")[:-1]:
        entries = line.split("\t")
        source = entries[2]
        dest = entries[3]
        if source not in links_dict.keys():
            links_dict[source] = []
        if dest not in links_dict[source]:
            links_dict[source].append(dest)

    for line in r.text.split("\n")[:-1]:
        entries = line.split("\t")
        source = entries[3]
        dest = entries[2]
        if source not in links_dict.keys():
            links_dict[source] = []
        if dest not in links_dict[source]:
            links_dict[source].append(dest)

    return links_dict


def get_relevant_links(gene_list):

    links_dict = get_functional_network(gene_list)
    direct = {}
    indirect = {}
    for gene in gene_list:
        direct[gene] = []
        indirect[gene] = {}
        if gene in links_dict.keys():
            gene_links = links_dict[gene]
            for other in gene_list:
                if other in gene_links:
                    direct[gene].append(other)
                if other in links_dict.keys() and other != gene:
                    other_links = links_dict[other]
                    shared_partners = set(gene_links).intersection(set(other_links))
                    for partner in shared_partners:
                        if other not in indirect[gene].keys():
                            indirect[gene][other] = []
                        indirect[gene][other].append(partner)

    return direct, indirect
