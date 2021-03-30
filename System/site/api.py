from .utilities import kegg_helper, general, neo4j_helper, mongo_helper, config
from .utilities.classes import Gene
from bson import json_util
import configparser


# Returns pathway name, link, participants
def get_pathway_info(identifier):
    pathway = kegg_helper.kegg_get_pathway(identifier)
    description = kegg_helper.kegg_pathway_desc(identifier)
    # Outputs tuple (link, name)
    gene_tuple = kegg_helper.kegg_gene_list(pathway.genes)
    return {
        "pathway_name": pathway.name,
        "pathway_description": description,
        "pathway_link": pathway.link,
        "gene_list": gene_tuple
    }


# Returns pathways that gene participates in
def pathways_given_gene(gene_name):
    pathways = general.pathways_given_product(gene_name)
    return {
        "kegg_pathways": pathways,
        "pc_pathways": []
    }


# TODO: function_enrichment_gene_list
# TODO: functional_enrichment_gene
# TODO: functional_enrichment_gene_pathway


# Returns interaction data between pathway and gene
def pathway_gene_interaction(pathway_name, pathway_kegg_id=None, input_gene=None, gene_uniprot=None, gene_kegg=None,
                             gene_name=None):
    if input_gene is None:
        gene = Gene(uniprot_id=gene_uniprot, kegg_id=gene_kegg, name=gene_name)
    else:
        gene = input_gene

    kegg_pathway_id = None
    if pathway_kegg_id is None:
        kegg_pathway_id = kegg_helper.kegg_search("pathway", pathway_name)[0]
    else:
        kegg_pathway_id = pathway_kegg_id

    participation_verdict = kegg_helper.kegg_pathway_participation(gene.kegg_id, kegg_pathway_id)
    pathway = kegg_helper.kegg_get_pathway(kegg_pathway_id)
    participant_ids = [gene.name for gene in pathway.genes]
    enrichment_names = gene.uniprot_id + " "
    for gene in participant_ids:
        enrichment_names += gene.split(" ")[0] + " "
    enrichment_names = enrichment_names[:-1]

    return {
        "participation_verdict": participation_verdict,
        "enrichment_names": enrichment_names
    }


def gene_variants(gene_name):
    uri = config.get_config()["mutations_db"]["uri"]
    return mongo_helper.get_mutations(gene_name, uri)


# Returns mutation data from mongo db given gene, variant name
def gene_variant_data(gene, variant):
    db_config = config.get_config()
    return mongo_helper.get_mutation_data(gene, variant, db_config["mutations_db"]["uri"])


# Returns any evidence stored in evidence db
def variant_evidence(gene, variant):
    db_config = config.get_config()

    return mongo_helper.variant_evidence(gene, variant, db_config["mutations_db"]["uri"])


# Returns a cypher query to create a Neo4j representation of an identified pathway
# Expected format: hsa:<id>
# TODO: Add mutation support
# TODO: Add functional enrichment support? Need to complete API stuff first
def neo4j_pathway(identifier, options=None):
    if options is None:
        options = ""
    accession = identifier
    pathway = kegg_helper.kegg_get_pathway(accession)

    gene_names = neo4j_helper.make_genes_from_kegg_pathway(pathway.genes)
    mongo_uri = config.get_config()["mutations_db"]["uri"]

    # This "known" dict is checked afterwards to find unknown nodes in the graph
    known = {}
    create_query = "CREATE "
    query_list = [neo4j_helper.make_gene_query(pathway, gene_names, known),
                  neo4j_helper.make_compound_query(pathway.compounds, known),
                  neo4j_helper.make_reaction_query(pathway.reaction_entries, known),
                  neo4j_helper.make_map_query(pathway.name)]

    if "variants" in options:
        query_list.append(neo4j_helper.make_variants_query(zip(gene_names, pathway.genes)))

    relations_data = neo4j_helper.make_relations_query(pathway.relations, known)
    query_list.append(neo4j_helper.make_unknown_query(relations_data[1]))
    query_list.append(relations_data[0])

    for q in query_list:
        if len(q) > 0:
            create_query += q + ","
    create_query = create_query[:-1]

    pipeline = [create_query]

    if "networks" in options:
        for query in neo4j_helper.make_networks_query(accession):
            pipeline.append(query)
    if "drugs" in options:
        pipeline.append(neo4j_helper.make_drugs_query(pathway))

    pipeline.append("MATCH (n1),(n2) WHERE ANY (x IN n1.kegg_ids WHERE x IN n2.kegg_ids) and id(n1) <> id(n2) "
                    "WITH [n1,n2] as ns CALL apoc.refactor.mergeNodes(ns, {properties:\"combine\", mergeRels:true}) "
                    "YIELD node RETURN node")
    pipeline.append("MATCH (n1:Variant),(n2:Variant) WHERE n1.variant = n2.variant and id(n1) <> id(n2) "
                    "WITH [n1,n2] as ns CALL apoc.refactor.mergeNodes(ns, {properties:\"combine\", mergeRels:true}) "
                    "YIELD node RETURN node")

    return {"neo4j_query_pipeline": pipeline}
