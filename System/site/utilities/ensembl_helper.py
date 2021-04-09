import requests


def get_effect_predictions(rsid):
    r = requests.get("https://rest.ensembl.org/vep/human/id/" + rsid + "?content-type=application/json&LoF=1")
    if r.status_code != 200:
        return None
    if r.text == "":
        return None
    return r.json()