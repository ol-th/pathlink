import requests
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def kegg_to_uniprot_identifiers(kegg_list):
    query = ""
    for kegg_id in kegg_list:
        query += kegg_id + " "
    query = query[:-1]
    params = {
        "from": "KEGG_ID",
        "to": "ID",
        "format": "tab",
        "query": query
     }
    r = requests.get('https://www.uniprot.org/uploadlists/', params=params)
    prev = ""
    output = []
    for line in r.text.split('\n')[:-1]:
        tabs = line.split("\t")
        if tabs[0] != prev and tabs[0] in kegg_list:
            output.append(tabs[1])
            prev = tabs[0]

    return output


def uniprot_ids_to_names(kegg_list):
    query = ""
    for kegg_id in kegg_list:
        query += kegg_id + " "
    query = query[:-1]
    params = {
        "from": "KEGG_ID",
        "to": "ID",
        "format": "tab",
        "query": query
     }
    r = requests.get('https://www.uniprot.org/uploadlists/', params=params)
    prev = ""
    output = []
    for i in r.text.split('\n')[:-1]:
        tabs = i.split("\t")
        if tabs[0] != prev:
            output.append(tabs[1])
            prev = tabs[0]

    return output


def get_uniprot_identifier(name):
    url = "https://www.uniprot.org/uniprot/?query=" + name + "&fil=organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&sort=score&limit=1&format=XML"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    try:
        xml_root = ET.fromstring(r.text)
    except Exception as e:
        print("Empty or invalid XML search result. Trace: ")
        print(e)
        return None
    return xml_root[0][0].text  # Identifier for highest search result


def get_uniprot_xml(identifier):
    url = "https://www.uniprot.org/uniprot/" + identifier + ".xml"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    try:
        xml_root = ET.fromstring(r.text)
    except Exception as e:
        print("Empty or invalid XML search result. Trace: ")
        print(e)
        return None
    return xml_root


def get_uniprot_name(xml):
    if xml is None:
        return None
    entry = xml[0]
    gene = entry.find("{http://uniprot.org/uniprot}gene")
    names = gene.findall("{http://uniprot.org/uniprot}name")
    for name in names:
        if name.attrib["type"] == "primary":
            return name.text
    return None


def get_uniprot_functions(xml):
    if xml is None:
        return None
    descriptions = []
    for entry in xml[0]:
        if entry.tag == "{http://uniprot.org/uniprot}comment" and entry.attrib['type'] == "function":
            for i in entry:
                if i.tag == "{http://uniprot.org/uniprot}text":
                    descriptions.append(i.text)

    return descriptions