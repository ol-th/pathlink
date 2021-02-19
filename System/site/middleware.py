from System.Database_Tools import kegg_helper


def search(query):
    query = str(query)
    query_list = query.split(";")
    if len(query_list) == 1:
        if query_list[0].startswith("path") or query_list[0].startswith("pathway"):
            return ['Pathway query']
        if query_list[0].startswith("product"):
            return ['Product query']
    elif len(query_list) == 2:
        if (query_list[0].startswith("path") or query_list[0].startswith("pathway")) and query_list[1].startswith("product"):
            return ['Pathway product link']
        if query_list[0].startswith("product") and (query_list[1].startswith("path") or query_list[1].startswith("pathway")):
            return['Product pathway link']
