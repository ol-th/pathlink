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