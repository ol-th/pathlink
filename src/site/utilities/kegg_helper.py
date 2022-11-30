import requests
import Bio.KEGG.REST as KEGG_REST
import Bio.KEGG.KGML.KGML_parser as KEGG_KGML_PARSER


def kegg_search(database, query):
    result = KEGG_REST.kegg_find(database, query.replace(" ", "+"))
    result_lines = result.read().split("\n")
    result_lines = result_lines[:-1]
    if result_lines[0] == "":
        return []

    output = []
    for result in result_lines:
        output.append(result.split("\t")[0])
    return output


def kegg_identifier_convert(id):
    r = requests.get("http://rest.kegg.jp/conv/genes/uniprot:" + id)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None

    return r.text.split("\t")[1].strip()


def kegg_get_pathway(identifier):
    identifier_sanitised = identifier.replace("path:", "")
    identifier_sanitised = identifier_sanitised.replace("map", "hsa")
    pathway_kgml = KEGG_REST.kegg_get(identifier_sanitised, "kgml")
    return KEGG_KGML_PARSER.read(pathway_kgml)


def kegg_pathway_participation(gene_identifier, pathway_identifier):
    pathway = kegg_get_pathway(pathway_identifier)
    gene_names = [gene.name for gene in pathway.genes]
    return gene_identifier in gene_names


def kegg_pathway_desc(info):
    if info is None:
        return None
    for line in info:
        if "DESCRIPTION" in line:
            return line.replace("DESCRIPTION", "").strip()


def kegg_get_name(info):
    if info is None:
        return None
    for line in info:
        if "NAME" in line:
            # Looks horrible but stops anything too specific
            return line.replace("NAME", "").strip().split(" - ")[0].strip()


def kegg_info(identifier):

    r = requests.get("http://rest.kegg.jp/get/" + identifier)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    kegg_info = r.text.split("\n")
    return kegg_info


# Returns name of genes given Biopython list of gene entries with their KEGG accession numbers (gene.name)
# Outputs tuples pathway_id, link, name
def kegg_gene_list(gene_list):
    query = ""
    for gene in gene_list:
        query += gene.name.split(" ")[0] + "+"

    query = query[:-1]
    r = requests.get("http://rest.kegg.jp/list/" + query)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    result_lines = r.text.split("\n")[:-1]
    full_list = []
    for index, line in enumerate(result_lines):

        names = line.split("\t")[1]
        name = names.split(" ")[0]
        for char in ",;":
            name = name.replace(char, "")
        full_list.append((gene_list[index].link, name))

    return full_list


def kegg_link(arg1, arg2):
    query1 = arg1.replace(" ", "+")
    query2 = arg2.replace(" ", "+")
    r = requests.get("http://rest.kegg.jp/link/" + str(query1) + "/" + str(query2))
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    lines = r.text.split("\n")
    return [line.split("\t") for line in lines][:-1]


def get_network_entry(name):
    return kegg_search("NETWORK", name)


def get_gene_pathways(protein_info_kegg):
    index = 0
    in_pathways = False
    kegg_pathways_list = []

    # This wrangles all of the pathway data into a 2d list of format [[accession, description], ...]
    while index < len(protein_info_kegg):
        if not in_pathways and "PATHWAY" in protein_info_kegg[index]:
            in_pathways = True
            kegg_pathways_list.append(protein_info_kegg[index][12:].split("  "))
        elif in_pathways:
            if not protein_info_kegg[index].startswith(" "):
                break
            kegg_pathways_list.append(protein_info_kegg[index][12:].split("  "))
        index += 1
    return kegg_pathways_list
