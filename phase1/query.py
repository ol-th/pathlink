import requests
from SPARQLWrapper import SPARQLWrapper, XML
import sys
import xml.etree.ElementTree as ET

def main():
    gene_name = sys.argv[1]
    query = sys.argv[2]

    url="https://www.uniprot.org/uniprot/?query="+ gene_name + "&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score&limit=1&format=XML"
    r = requests.get(url)
    if r.status_code != 200:
        return 1

    try:
        xml_root = ET.fromstring(r.text)
    except Exception as e:
        print("Empty or invalid XML search result. Trace: ")
        print(e)
        return 1

    uniprot_id = xml_root[0][0].text # Identifier for highest search result

    ############# PC SEARCH #####################

    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    statement = """
    PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?pathwayName
    WHERE
    {
    ?protein rdf:type bp:Protein;
                   bp:entityReference ?eref.

    FILTER regex(?eref, "^http://identifiers.org/uniprot/"""+ uniprot_id + """$")

    ?pathway rdf:type bp:Pathway.
    ?interaction bp:participant ?protein.
    ?pathway bp:pathwayComponent ?interaction;
             bp:displayName ?pathwayName.

    FILTER regex(?pathwayName, \".*""" + query + """.*\", "i")
    }
    LIMIT 10

    """

    sparql.setQuery(statement)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    #If there are results, then the gene is part of the pathway specified
    pc_outcome = len(xml_root[1]) > 0
    if pc_outcome:
        print(True)
        return

    ############# KEGG SEARCH ####################

    r = requests.get("http://rest.kegg.jp/conv/genes/uniprot:" + uniprot_id)
    if r.status_code != 200:
        return 1
    if r.text == "":
        print("Gene not found on KEGG")
        return 1

    kegg_identifier = r.text.split("\t")[1]

    r = requests.get("http://rest.kegg.jp/get/" + kegg_identifier)
    if r.status_code != 200:
        return 1
    if r.text == "":
        print("Gene information unavailable in KEGG")
        return 1
    kegg_info = r.text.split("\n")

    kegg_outcome = False

    for line in kegg_info:
        if query in line:
            kegg_outcome = True
            break
    print (kegg_outcome)
    return

if __name__ == "__main__":
    main()
