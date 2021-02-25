from System.Database_Tools import kegg_helper, pathwaycommons_helper, general, uniprot_helper


def search(query):
    query = str(query)
    query_list = query.split(";")
    if len(query_list) == 1:
        if query_list[0].startswith("path") or query_list[0].startswith("pathway"):
            return pathway_query(query_list)
        if query_list[0].startswith("gene"):
            return product_query(query_list)
    elif len(query_list) == 2:
        if (query_list[0].startswith("path") or query_list[0].startswith("pathway")) and query_list[1].startswith("gene"):
            return pathway_product_query(query_list[0], query_list[1])
        if query_list[0].startswith("gene") and (query_list[1].startswith("path") or query_list[1].startswith("pathway")):
            return pathway_product_query(query_list[1], query_list[0])


def pathway_query(query_list):
    # Splicing out the pathway: component of the query
    query = query_list[0].split(":")[1:]
    # Query is a name of pathway
    identifier = ""
    if len(query) == 1:
        # Sanitise for use in HTTP
        sanitised_query = query[0].replace(" ", "+")
        results = kegg_helper.kegg_search("PATHWAY", sanitised_query)
        # If there are results
        if len(results) > 0:
            # Use first choice of the search results - TODO: could change this to let the user choose
            identifier = results[0].replace("map", "hsa")
            return get_pathway_results(identifier, query[0])

    # In this case it's an identifier
    elif len(query) == 2 and query[0] == "hsa":
        info = kegg_helper.kegg_info("map" + query[1])
        if info is not None:
            name = info[1][12:]
            print(name)
            return get_pathway_results(query[0] + query[1], name)

    return ["No results found - have you checked for typos? The query may be malformed."]


def get_pathway_results(identifier, name):
    pathway = kegg_helper.kegg_get_pathway(identifier)

    # Adding the pathway link
    output_list = ["<a href=\"" + pathway.link + "\"><h2>KEGG entry for pathway</h2></a>"]
    # Adding a list of genes involved
    gene_list = kegg_helper.kegg_gene_list(pathway.genes)
    gene_list_text = "<p><h2>Gene participants:</h2></p>"
    for gene in gene_list:
        gene_list_text += "<p>" + gene + "</p>"
    output_list.append(gene_list_text)
    # Finding known parents of the pathway (using pathway commons)
    parents_text = "<h2>Known parent pathways:</h2>"
    parents = pathwaycommons_helper.pathway_given_pathway(name)
    for parent in parents:
        parents_text += "<p>" + parent[0] + "</p>"

    output_list.append(parents_text)
    return output_list


def product_query(query_list):
    query = query_list[0].split(":")[1:]
    # This means it's a name
    if len(query) == 1:
        name = query[0]
        uniprot_id = uniprot_helper.get_uniprot_identifier(name)
        if uniprot_id is not None:
            identifier = kegg_helper.kegg_identifier_convert(uniprot_id)
            return get_product_results(identifier, name)
    elif len(query) == 2:
        identifier = query[0] + ":" + query[1]
        gene_info = kegg_helper.kegg_info(identifier)
        name = gene_info[1][12:].split(",")[0]
        print(name)
        return get_product_results(identifier, name)
    return ["No results found - have you checked for typos? The query may be malformed."]


def get_product_results(identifier, name):
    output_list = ["<a href=\"http://www.genome.jp/dbget-bin/www_bget?" + identifier + "\"><h2>KEGG entry for gene</h2></a>"]
    pathways = general.pathways_given_product(name)
    if len(pathways[0]) > 0:
        output_list.append("<h2>[KEGG] Participant in:</h2>")
        for i in pathways[0]:
            line = """
            <p><a href=\"http://www.genome.jp/dbget-bin/www_bget?""" + i[0] + """\">""" + i[1] + """</a></p>
            """
            output_list.append(line)
    if len(pathways[1]) > 0:
        output_list.append("<h2>[Pathway Commons] Participant in:</h2>")
        for i in pathways[1]:
            line = """
                    <p>""" + i[0] + """</a></p>
                    """
            output_list.append(line)
    output_list.append("<p><h2><a href=\"/enrichment?genes=" + name + "\">Functional enrichment</a></h2></p>")
    return output_list


def pathway_product_query(pathway_query, product_query):
    pathway_list = pathway_query.split(":")[1:]
    product_list = product_query.split(":")[1:]
    # Query is a name of pathway
    pathway_name = None
    pathway_identifier = None
    if len(pathway_list) == 1:
        pathway_name = pathway_list[0]
        # Sanitise for use in HTTP
        sanitised_query = pathway_name.replace(" ", "+")
        results = kegg_helper.kegg_search("PATHWAY", sanitised_query)
        # If there are results
        if len(results) > 0:
            # TODO: could change this to let the user choose
            pathway_identifier = results[0].replace("map", "hsa")

    # In this case it's an identifier
    elif len(pathway_list) == 2 and pathway_list[0] == "hsa":
        pathway_identifier = pathway_list[0] + ":" + pathway_list[1]
        info = kegg_helper.kegg_info("map" + pathway_list[1])
        if info is not None:
            pathway_name = info[1][12:]

    product_name = None
    product_identifier = None

    if len(product_list) == 1:
        product_name = product_list[0]
        uniprot_id = uniprot_helper.get_uniprot_identifier(product_name)
        if uniprot_id is not None:
            product_identifier = kegg_helper.kegg_identifier_convert(uniprot_id)

    elif len(product_list) == 2:
        product_identifier = product_list[0] + ":" + product_list[1]
        gene_info = kegg_helper.kegg_info(product_identifier)
        product_name = gene_info[1][12:].split(",")[0]

    if product_name is not None and product_identifier is not None and pathway_name is not None and pathway_identifier is not None:
        return get_pathway_product_results(pathway_name, pathway_identifier, product_name, product_identifier)

    return ["No results found - have you checked for typos? The query may be malformed."]


def get_pathway_product_results(pathway_name, pathway_identifier, product_name, product_identifier):
    output_list = ["<a href=\"http://www.genome.jp/dbget-bin/www_bget?" + product_identifier +
                   "\"><h2>KEGG entry for " + product_name + "</h2></a>",
                   "<a href=\"http://www.genome.jp/dbget-bin/www_bget?" + pathway_identifier +
                   "\"><h2>KEGG entry for " + pathway_name + "</h2></a>", "<p><h2>Participation verdict:</h2><p>"]
    participation_verdict = general.product_participation(product_name, pathway_name)
    output_list.append("<p>KEGG: " + str(participation_verdict[0]) + "</p>")
    output_list.append("<p>Pathway Commons: " + str(participation_verdict[1]) + "</p>")
    pathway = kegg_helper.kegg_get_pathway(pathway_identifier)
    enrichment_names = product_name + " "
    for gene in pathway.genes:
        enrichment_names += gene.name.split(" ")[0] + " "
    enrichment_names = enrichment_names[:-1]
    output_list.append("<p><h2><a href=\"/enrichment?genes=" + enrichment_names
                       + "\">Functional enrichment</a></h2></p>")
    return output_list
