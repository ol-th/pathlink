import requests

# def kegg_search(query):
#

def kegg_identifier_convert(id):
    r = requests.get("http://rest.kegg.jp/conv/genes/uniprot:" + id)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None

    return r.text.split("\t")[1]

def kegg_pathway_participation(id, query):

    r = requests.get("http://rest.kegg.jp/get/" + id)
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

