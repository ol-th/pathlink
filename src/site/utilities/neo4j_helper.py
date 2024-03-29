from neo4j import GraphDatabase
from . import kegg_helper, mongo_helper, config


def make_genes_from_kegg_pathway(gene_list):
    kegg_ids = []
    for gene in gene_list:
        kegg_ids.append(gene.name.split(",")[0])

    gene_names = kegg_helper.kegg_gene_list(gene_list)

    if len(kegg_ids) != len(gene_names):
        return None

    return gene_names


def make_gene_query(pathway, gene_names, known):
    gene_list = pathway.genes
    query = ""
    for gene, gene_name in zip(gene_list, gene_names):
        known[gene.id] = True
        query += (
            "(a" + str(gene.id) + ":Gene {"
            'name: "' + gene_name[1] + '",'
            'kegg_ids: ["' + gene.name.strip().replace(" ", '","') + '"],'
            'kegg_link: "' + gene_name[0] + '",'
            'pathways: ["' + pathway.name + '"]}),'
        )

    # Removing trailing comma
    query = query[:-1]
    return query


# gene_info:
#   [0] - Gene name (0 - link, 1 - name)
#   [1] - Gene object
def make_variants_query(gene_info):
    uri = config.get_config()["mutations_db"]["uri"]
    query = ""
    mutation_id = 0
    for gene_name, gene in gene_info:
        mutations = mongo_helper.get_mutations(gene_name[1], uri)
        for mutation in mutations:
            # Add mutation query
            query += (
                "(v" + str(mutation_id) + ":Variant {"
                'gene: "' + str(mutation["gene"]) + '", '
                'variant: "' + str(mutation["variant"]) + '", '
                'rsid: "' + str(mutation["RS# (dbSNP)"]) + '", '
                'type: "' + str(mutation["Type"]) + '", '
                'clinicalsignificance: "' + str(mutation["ClinicalSignificance"]) + '"'
                "}),"
            )
            query += (
                "(a" + str(gene.id) + ")-[:hasVariant]->(v" + str(mutation_id) + "),"
            )
            mutation_id += 1

    query = query[:-1]
    return query


def make_compound_query(compound_list, known):
    query = ""
    for compound in compound_list:
        known[compound.id] = True
        query += (
            "(a" + str(compound.id) + ":Compound {"
            'kegg_ids: ["' + compound.name.strip().replace(" ", '","') + '"]}),'
        )
    # Removing trailing comma
    query = query[:-1]
    return query


def make_reaction_query(reaction_list, known):
    query = ""
    for reaction in reaction_list:
        known[reaction.id] = True
        query += (
            "(a" + str(reaction.id) + ":Reaction {"
            'kegg_ids: ["' + reaction.name.strip().replace(" ", '","') + '"]}),'
        )
    # Removing trailing comma
    query = query[:-1]
    return query


# These maps are largely useless - insulated nodes representing signalling pathways mentioned in the KEGG entry
# Better to integrate the networks entries!

# def make_map_query(map_list, known):
#     query = ""
#     for pmap in map_list:
#         known[pmap.id] = True
#         query += "(a" + str(pmap.id) + ":Map {" \
#                  "name: [\"" + pmap.name.strip().replace(" ", "\",\"") + "\"]}),"
#     # Removing trailing comma
#     query = query[:-1]
#     return query


def make_map_query(map_id):
    query = '(m1:Map {kegg_ids: ["' + map_id + '"]})'
    return query


def make_relations_query(relation_list, known):
    query = ""
    unknown_set = set()
    for relation in relation_list:
        current_query = (
            "(a" + str(relation.entry1.id) + ")-[:" + relation.type + " {subtypes: ["
        )
        if relation.entry1.id not in known.keys():
            unknown_set.add(relation.entry1.id)
        if relation.entry2.id not in known.keys():
            unknown_set.add(relation.entry2.id)
        for subtype in relation.subtypes:
            current_query += '"' + subtype[0] + '",'
        # Fixes a bug where there's no subtypes and it prints subtypes: ]
        if len(relation.subtypes) > 0:
            current_query = current_query[:-1]
        current_query += "]}]->(a" + str(relation.entry2.id) + "),"
        query += current_query
    # Removing trailing comma
    query = query[:-1]
    return query, unknown_set


def make_unknown_query(unknown_list):
    query = ""
    for unknown in unknown_list:
        query += "(a" + str(unknown) + ":Unknown),"

    query = query[:-1]
    return query


def make_networks_query(pathway_id):
    uri = config.get_config()["mutations_db"]["uri"]
    linked_networks = [
        entry[1] for entry in kegg_helper.kegg_link("network", pathway_id)
    ]

    output = []
    for network_id in linked_networks:
        output.append(mongo_helper.get_network_entry(network_id, uri)["query"])

    return output


def make_drugs_query(pathway):
    uri = config.get_config()["mutations_db"]["uri"]
    drug_connections = {}
    linked_drugs = mongo_helper.get_drug_links(pathway.name, uri)
    if linked_drugs is not None:
        linked_drugs = linked_drugs["drugs"]
        for drug in linked_drugs:
            if drug not in drug_connections.keys():
                drug_connections[drug] = []
            drug_connections[drug].append([True, pathway.name])

    for gene in pathway.genes:
        gene_ids = gene.name.split(" ")
        for gene_id in gene_ids:
            linked_drugs = mongo_helper.get_drug_links(gene_id, uri)
            if linked_drugs is not None:
                linked_drugs = linked_drugs["drugs"]
                for drug in linked_drugs:
                    if drug not in drug_connections.keys():
                        drug_connections[drug] = []
                    drug_connections[drug].append([False, gene_id])

    query = "CREATE "
    current_drug_id = 0
    current_target_id = 0
    for drug in drug_connections.keys():
        targets = drug_connections[drug]

        query += "(b" + str(current_drug_id) + ':Drug {kegg_ids: ["' + drug + '"]}),'

        for target in targets:
            # It's a pathway
            if target[0]:
                query += (
                    "(a"
                    + str(current_target_id)
                    + ':Map { kegg_ids: ["'
                    + target[1]
                    + '"]}),'
                )
                query += (
                    "(a"
                    + str(current_target_id)
                    + ")-[:Targeted]->(b"
                    + str(current_drug_id)
                    + "),"
                )
                current_target_id += 1
            # It's a gene
            else:
                query += (
                    "(a"
                    + str(current_target_id)
                    + ':Gene { kegg_ids: ["'
                    + target[1]
                    + '"]}),'
                )
                query += (
                    "(a"
                    + str(current_target_id)
                    + ")-[:Targeted]->(b"
                    + str(current_drug_id)
                    + "),"
                )
                current_target_id += 1

        current_drug_id += 1

    return query[:-1]
