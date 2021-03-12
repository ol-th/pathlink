from System.Database_Tools import kegg_helper, pathwaycommons_helper, general, uniprot_helper
from .classes import Gene


def search(query):
    query = str(query)
    query_list = [i.strip() for i in query.split(";")]
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
        if query_list[0].startswith("gene") and query_list[1].startswith("gene"):
            return product_product_query(query_list[0], query_list[1])


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
        gene = Gene(name=query[0])
    elif len(query) == 2:
        identifier = query[1]
        gene = Gene(uniprot_id=identifier)

    result = get_product_results(gene)
    if result is not None:
        return result
    return ["No results found - have you checked for typos? The query may be malformed."]


def get_product_results(gene):
    output_list = [
        "<a href=\"http://www.genome.jp/dbget-bin/www_bget?" + gene.kegg_id + "\"><h2>KEGG entry for gene</h2></a>",
        "<p><a href=\"http://www.uniprot.org/uniprot/" + gene.uniprot_id + "\"><h2>UniProt entry for gene</h2></a></p>"]
    if gene.functions is not None and len(gene.functions) > 0:
        output_list.append("<p><h2>Gene function(s):</h2><p>")
        for index, function in enumerate(gene.functions):
            output_list.append("<p>" + str(index + 1) + ": " + function + "</p>")
    pathways = general.pathways_given_product(gene.name)
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
    output_list.append("<p><h2><a href=\"/enrichment?genes=" + gene.uniprot_id + "\">Functional enrichment</a></h2></p>")
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


def product_product_query(query1, query2):
    list1 = query1.split(":")[1:]
    list2 = query2.split(":")[1:]

    name1 = identifier1 = name2 = identifier2 = None

    if len(list1) == 1:
        name1 = list1[0]
        uniprot_id1 = uniprot_helper.get_uniprot_identifier(name1)
        if uniprot_id1 is not None:
            identifier1 = kegg_helper.kegg_identifier_convert(uniprot_id1)
    elif len(list1) == 2:
        identifier1 = list1[0] + ":" + list1[1]
        gene_info = kegg_helper.kegg_info(identifier1)
        name1 = gene_info[1][12:].split(",")[0]

    if len(list2) == 1:
        name2 = list2[0]
        uniprot_id2 = uniprot_helper.get_uniprot_identifier(name2)
        if uniprot_id2 is not None:
            identifier2 = kegg_helper.kegg_identifier_convert(uniprot_id2)
    elif len(list2) == 2:
        identifier2 = list2[0] + ":" + list2[1]
        gene_info = kegg_helper.kegg_info(identifier2)
        name2 = gene_info[1][12:].split(",")[0]

    if all(v is not None for v in [name1, name2, identifier1, identifier2]):
        return get_product_product_results(name1, identifier1, name2, identifier2)

    return ["No results found - have you checked for typos? The query may be malformed."]


def get_product_product_results(name1, identifier1, name2, identifier2):
    pathways1 = general.pathways_given_product(name1)
    pathways2 = general.pathways_given_product(name2)
    accession_numbers2 = [i[0] for i in pathways2[0]]
    mutual_pathways = []
    for pathway in pathways1[0]:
        if pathway[0] in accession_numbers2:
            mutual_pathways.append(pathway)

    output = ["<h2>Mutual pathways:</h2>"]

    if len(mutual_pathways) == 0:
        output.append("<p>None</p>")
    else:
        for pathway in mutual_pathways:
            line = "<p><a href=\"http://www.genome.jp/dbget-bin/www_bget?" + pathway[0] + "\">" + pathway[1] + "</a><p>"
            output.append(line)

    output.append("<p><h2><a href=\"/enrichment?genes=" + name1 + " " + name2
                  + "\">Functional enrichment</a></h2></p>")

    return output
