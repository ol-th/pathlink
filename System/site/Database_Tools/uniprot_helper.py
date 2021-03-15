import requests
import xml.etree.ElementTree as ET


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
    index = 0
    while index < len(xml[0]) and xml[0][index].tag != "{http://uniprot.org/uniprot}protein":
        index += 1

    if index == len(xml[0]):
        return None

    return xml[0][index][0][0].text


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