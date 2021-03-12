import requests
import Bio.KEGG.REST as KEGG_REST
import Bio.KEGG.KGML.KGML_parser as KEGG_KGML_PARSER


def kegg_search(database, query):
    result = KEGG_REST.kegg_find(database, query)
    result_lines = result.read().split('\n')
    result_lines = result_lines[:-1]
    if result_lines[0] == "":
        return []

    output = []
    for result in result_lines:
        output.append(result.split('\t')[0])
    return output


def kegg_identifier_convert(id):
    r = requests.get("http://rest.kegg.jp/conv/genes/uniprot:" + id)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None

    return r.text.split("\t")[1]


def kegg_get_pathway(identifier):
    pathway_kgml = KEGG_REST.kegg_get(identifier, "kgml")
    return KEGG_KGML_PARSER.read(pathway_kgml)


def kegg_pathway_participation(identifier, query):

    r = requests.get("http://rest.kegg.jp/get/" + identifier)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    kegg_info = r.text.split("\n")

    kegg_outcome = False

    for line in kegg_info:
        if query in line:
            kegg_outcome = True
            break

    return kegg_outcome


def kegg_info(id):

    r = requests.get("http://rest.kegg.jp/get/" + id)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    kegg_info = r.text.split("\n")
    return kegg_info


# Returns name of genes given Biopython entry list of genes with their KEGG accession numbers (gene.name)
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
        line = " ".join(line.split(" ")[1:])
        full_list.append("<a href=\"" + gene_list[index].link + "\">" + line + "</a>")

    return full_list

