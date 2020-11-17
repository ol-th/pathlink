import requests
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

    ######### PATHWAY COMMONS SEARCH #############



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

    for index, line in enumerate(kegg_info):
        if query in line:
            print("KEGG: True")
            return 0
    print("KEGG: False")
    return 0

if __name__ == "__main__":
    main()
