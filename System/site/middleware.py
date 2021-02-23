from System.Database_Tools import kegg_helper, pathwaycommons_helper


def search(query):
    query = str(query)
    query_list = query.split(";")
    if len(query_list) == 1:
        if query_list[0].startswith("path") or query_list[0].startswith("pathway"):
            return pathway_query(query_list)
        if query_list[0].startswith("product"):
            return ['Product query']
    elif len(query_list) == 2:
        if (query_list[0].startswith("path") or query_list[0].startswith("pathway")) and query_list[1].startswith("product"):
            return ['Pathway product link']
        if query_list[0].startswith("product") and (query_list[1].startswith("path") or query_list[1].startswith("pathway")):
            return['Product pathway link']


def pathway_query(query_list):
    query = query_list[0].split(":")[1:]
    # Query is a name of pathway
    identifier = ""
    if len(query) == 1:
        sanitised_query = query[0].replace(" ", "+")
        results = kegg_helper.kegg_search("PATHWAY", sanitised_query)
        if len(results) > 0:
            choice = results[0].replace("map", "hsa")
            pathway = kegg_helper.kegg_get_pathway(choice)
            output_list = []
            output_list.append("<a href=\"" + pathway.link + "\"><h2>KEGG entry for pathway</h2></a>")

            gene_list = kegg_helper.kegg_gene_link(pathway.genes)
            gene_list_text = "<p><h2>Gene participants:</h2></p>"
            for gene in gene_list:
                gene_list_text += "<p>" + gene + "</p>"
            output_list.append(gene_list_text)

            parents_text = "<h2>Known parent pathways:</h2>"
            parents = pathwaycommons_helper.pathway_given_pathway(query[0])
            for parent in parents:
                parents_text += "<p>" + parent[0] + "</p>"

            output_list.append(parents_text)
            return output_list

    return ["No results found"]
