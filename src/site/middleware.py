from .utilities import kegg_helper, pathwaycommons_helper
from .utilities.classes import Gene
from bson import json_util
from . import api


# First entrypoint - this handles the query syntax and sends them to respective handlers
# example query: gene:PTEN; path: homologous recombination
# TODO: Find a nicer solution for this
def search(query):
    query = str(query)
    query_list = [i.strip() for i in query.split(";")]
    if len(query_list) == 1:
        if query_list[0].startswith("path") or query_list[0].startswith("pathway"):
            return pathway_query(query_list)
        if query_list[0].startswith("gene"):
            return product_query(query_list)
    elif len(query_list) == 2:
        if (
            query_list[0].startswith("path") or query_list[0].startswith("pathway")
        ) and query_list[1].startswith("gene"):
            return pathway_product_query(query_list[0], query_list[1])
        if query_list[0].startswith("gene") and (
            query_list[1].startswith("path") or query_list[1].startswith("pathway")
        ):
            return pathway_product_query(query_list[1], query_list[0])
        if query_list[0].startswith("gene") and query_list[1].startswith("gene"):
            return product_product_query(query_list[0], query_list[1])
        if query_list[0].startswith("gene") and query_list[1].startswith("variant"):
            return product_variant_query(query_list[0], query_list[1])
        if query_list[1].startswith("gene") and query_list[0].startswith("variant"):
            return product_variant_query(query_list[1], query_list[0])
    else:
        return ["Malformed query"]


def pathway_query(query_list):
    # Splicing out the pathway: component of the query
    query = query_list[0].split(":")[1:]
    # Query is a name of pathway
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

    return [
        "No results found - have you checked for typos? The query may be malformed."
    ]


def get_pathway_results(identifier, name):
    # Keys: pathway_name, pathway_link, gene_list [link, name]
    pathway_info = api.get_pathway(identifier)

    # Adding the pathway link
    output_list = [
        '<a href="'
        + pathway_info["pathway_link"]
        + '"><h2>KEGG entry for pathway</h2></a>',
        "<p>Description: " + pathway_info["pathway_description"] + "<p>",
    ]
    # Adding a list of genes involved
    gene_list_text = "<p><h2>Gene participants:</h2></p>"
    for gene in pathway_info["gene_list"]:
        gene_list_text += '<p><a href="' + gene[0] + '">' + gene[1] + "</a></p>"
    output_list.append(gene_list_text)
    # Finding known parents of the pathway (using pathway commons)
    parents_text = "<h2>Known parent pathways:</h2>"
    parents = pathwaycommons_helper.pathway_parents(name)
    for parent in parents:
        parents_text += "<p>" + parent[0] + "</p>"

    output_list.append(parents_text)
    return output_list


def product_query(query_list):
    query = query_list[0].split(":")[1:]
    gene = None
    # This means it's a name
    if len(query) == 1:
        gene = Gene(name=query[0])
    elif len(query) == 2:
        identifier = query[1]
        gene = Gene(uniprot_id=identifier)

    result = get_product_results(gene)
    if result is not None:
        return result
    return [
        "No results found - have you checked for typos? The query may be malformed."
    ]


def get_product_results(gene):
    output_list = [
        '<a href="http://www.genome.jp/dbget-bin/www_bget?'
        + gene.kegg_id
        + '"><h2>KEGG entry for gene</h2></a>',
        '<p><a href="http://www.uniprot.org/uniprot/'
        + gene.uniprot_id
        + '"><h2>UniProt entry for gene</h2></a></p>',
    ]
    if gene.functions is not None and len(gene.functions) > 0:
        output_list.append("<p><h2>Gene function(s):</h2><p>")
        for index, function in enumerate(gene.functions):
            output_list.append("<p>" + str(index + 1) + ": " + function + "</p>")

    # Retrieving pathways that it participates in
    gene_data = api.get_gene(gene.name, options="variants+pc_pathways")
    if len(gene_data["kegg_pathways"]) > 0:
        output_list.append("<h2>[KEGG] Participant in:</h2>")
        for i in gene_data["kegg_pathways"]:
            line = (
                """
            <p><a href=\"http://www.genome.jp/dbget-bin/www_bget?"""
                + i[0]
                + """\">"""
                + i[1]
                + """</a></p>
            """
            )
            output_list.append(line)
    if len(gene_data["pc_pathways"]) > 0:
        output_list.append("<h2>[Pathway Commons] Participant in:</h2>")
        for i in gene_data["pc_pathways"]:
            line = (
                """
                    <p>"""
                + i[0]
                + """</a></p>
                    """
            )
            output_list.append(line)
    variants = [json_util.loads(result) for result in gene_data["variants"]]
    if len(variants) > 0:
        output_list.append("<p><h2>Variants</h2></p>")
        for variant in variants:
            output_list.append("<p>" + variant["variant"] + "</p>")

    return output_list


def pathway_product_query(pathway_input, product_input):
    pathway_list = pathway_input.split(":")[1:]
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
            pathway_identifier = results[0].replace("map", "hsa")

    # In this case it's an identifier
    elif len(pathway_list) == 2 and pathway_list[0] == "hsa":
        pathway_identifier = pathway_list[0] + ":" + pathway_list[1]
        info = kegg_helper.kegg_info("map" + pathway_list[1])
        if info is not None:
            pathway_name = info[1][12:]

    product_list = product_input.split(":")[1:]
    gene = None

    if len(product_list) == 1:
        gene = Gene(name=product_list[0])
    elif len(product_list) == 2:
        gene_identifier = product_list[1]
        gene = Gene(uniprot_id=gene_identifier)

    if all(
        v is not None
        for v in [gene.name, gene.uniprot_id, pathway_name, pathway_identifier]
    ):
        return get_pathway_product_results(gene, pathway_name, pathway_identifier)

    return [
        "No results found - have you checked for typos? The query may be malformed."
    ]


def get_pathway_product_results(gene, pathway_name, pathway_identifier):
    # Links
    output_list = [
        "<p><h2>" + gene.name + ":</h2></p>"
        '<a href="http://www.genome.jp/dbget-bin/www_bget?'
        + gene.kegg_id
        + '">KEGG</a>',
        '<p><a href="http://www.uniprot.org/uniprot/'
        + gene.uniprot_id
        + '">UniProt</a></p>',
        '<a href="http://www.genome.jp/dbget-bin/www_bget?'
        + pathway_identifier
        + '"><h2>KEGG entry for '
        + pathway_name
        + "</h2></a>",
        "<p><h2>Participation verdict:</h2><p>",
    ]

    # Getting info from the API:
    #  participation_verdict
    #  participant_kegg_ids
    #  TBC...
    interaction_info = api.pathway_gene_interaction(
        pathway_name, pathway_kegg_id=pathway_identifier, input_gene=gene
    )
    participation_verdict = interaction_info["participation_verdict"]

    # Does the gene participate in the pathway?
    output_list.append("<p>KEGG: " + str(participation_verdict) + "</p>")

    # Functional Enrichment
    output_list.append("<p><h2>Functional Enrichment</h2></p>")
    output_list.append("<p><h3>Direct partners</h3></p>")

    output_list.append("<p><h2>Functional Enrichment</h2></p>")

    direct = interaction_info["direct"]
    indirect = interaction_info["indirect"]

    source = gene.name
    if source in direct.keys():
        output_list.append("<p><h3>Direct partners</h3></p>")
        for dest in direct[source]:
            output_list.append("<p>" + source + " -> " + dest + "</p>")

    if source in indirect.keys():
        output_list.append("<p><h3>Indirect partners</h3></p>")
        for dest in indirect[source].keys():
            via = indirect[source][dest]
            if len(via) > 0:
                if len(via) > 5:
                    via = via[:5]
                via = ", ".join(via)
                output_list.append(
                    "<p>" + source + " -> " + dest + " via " + via + "</p>"
                )

    return output_list


def product_product_query(query1, query2):
    list1 = query1.split(":")[1:]
    list2 = query2.split(":")[1:]

    gene1 = gene2 = None

    if len(list1) == 1:
        gene1 = Gene(name=list1[0])
    elif len(list1) == 2:
        identifier = list1[1]
        gene1 = Gene(uniprot_id=identifier)

    if len(list2) == 1:
        gene2 = Gene(name=list2[0])
    elif len(list2) == 2:
        identifier = list2[1]
        gene2 = Gene(uniprot_id=identifier)

    if all(
        v is not None
        for v in [gene1.name, gene1.uniprot_id, gene2.name, gene2.uniprot_id]
    ):
        return get_product_product_results(gene1, gene2)

    return [
        "No results found - have you checked for typos? The query may be malformed."
    ]


def get_product_product_results(gene1, gene2):
    gene1_info = api.get_gene(uniprot_id=gene1.uniprot_id)
    gene2_info = api.get_gene(uniprot_id=gene2.uniprot_id)
    pathways1 = gene1_info["kegg_pathways"]
    pathways2 = gene2_info["kegg_pathways"]

    # pathway[0] contains its accession ID
    accession_numbers2 = [pathway[0] for pathway in pathways2]
    mutual_pathways = []
    for pathway in pathways1:
        if pathway[0] in accession_numbers2:
            mutual_pathways.append(pathway)

    output_list = [
        "<p><h2> Entries for " + gene1.name + ": </h2></p>",
        '<p><a href="http://www.genome.jp/dbget-bin/www_bget?'
        + gene1.kegg_id
        + '">KEGG</a></p>',
        '<p><a href="http://www.uniprot.org/uniprot/'
        + gene1.uniprot_id
        + '">UniProt</a></p>',
        "<p><h2> Entries for " + gene2.name + ": </h2></p>",
        '<p><a href="http://www.genome.jp/dbget-bin/www_bget?'
        + gene2.kegg_id
        + '">KEGG</a></p>',
        '<p><a href="http://www.uniprot.org/uniprot/'
        + gene2.uniprot_id
        + '">UniProt</a></p>',
        "<h2>Mutual pathways:</h2>",
    ]

    if len(mutual_pathways) == 0:
        output_list.append("<p>None</p>")
    else:
        for pathway in mutual_pathways:
            line = (
                '<p><a href="http://www.genome.jp/dbget-bin/www_bget?'
                + pathway[0]
                + '">'
                + pathway[1]
                + "</a><p>"
            )
            output_list.append(line)

    # Functional Enrichment
    direct, indirect = api.functional_enrichment([gene1.name, gene2.name])
    output_list.append("<p><h2>Functional Enrichment</h2></p>")
    output_list.append("<p><h3>Direct partners</h3></p>")

    for source in direct.keys():
        for dest in direct[source]:
            output_list.append("<p>" + source + " -> " + dest + "</p>")

    output_list.append("<p><h3>Indirect partners</h3></p>")
    for source in indirect.keys():
        for dest in indirect[source].keys():
            via = indirect[source][dest]
            print(via)
            if len(via) > 0:
                if len(via) > 5:
                    via = via[:5]
                via = ", ".join(via)
                output_list.append(
                    "<p>" + source + " -> " + dest + " via " + via + "</p>"
                )

    return output_list


# Product-variant interaction query - returns clinical significance etc
def product_variant_query(gene_query, variant_query):

    gene_list = gene_query.split(":")[1:]

    gene = None
    if len(gene_list) == 1:
        gene = Gene(name=gene_list[0])
    elif len(gene_list) == 2:
        identifier = gene_list[1]
        gene = Gene(uniprot_id=identifier)

    variant = variant_query.split(":")[1]

    return get_product_variant_query(gene, variant)


def get_product_variant_query(gene, variant):
    gene_info_dict = api.gene_variant_data(gene.name, variant)
    evidence_info_dicts = api.variant_evidence(gene.name, variant)
    if gene_info_dict is None:
        return ["Variant/mutation not found - malformed query?"]

    first_variant = json_util.loads(gene_info_dict["results"])
    output = [
        "<p><h2>" + gene.name + ":</h2></p>"
        '<a href="http://www.genome.jp/dbget-bin/www_bget?'
        + gene.kegg_id
        + '">KEGG</a>',
        '<p><a href="http://www.uniprot.org/uniprot/'
        + gene.uniprot_id
        + '">UniProt</a></p>',
        "<p><h2>" + gene.name + " " + variant + ":</h2></p>",
        "<p> Clinical Significance (ClinVar): " + first_variant["ClinicalSignificance"],
        "<p> Variant types: " + first_variant["variant_types"],
        '<p><a href="'
        + first_variant["variant_civic_url"]
        + '"> CiViC database Entry</a><p>',
        "<p><h2>Evidence findings:</h2></p>",
        "<p>Potential drugs:</p>",
    ]
    for evidence in evidence_info_dicts:
        output.append(
            "<p>"
            + str(evidence["drugs"])
            + ' - <a href="'
            + str(evidence["evidence_civic_url"])
            + '">Evidence</a></p>'
        )
    return output
