from .utilities import kegg_helper, general, neo4j_helper, mongo_helper
from .utilities.classes import Gene
from bson import json_util
import configparser


# Returns pathway name, link, participants
def get_pathway_info(identifier):
    pathway = kegg_helper.kegg_get_pathway(identifier)
    # Outputs tuple (link, name)
    gene_tuple = kegg_helper.kegg_gene_list(pathway.genes)
    return {
        "pathway_name": pathway.name,
        "pathway_link": pathway.link,
        "gene_list": gene_tuple
    }


# Returns pathways that gene participates in
def pathways_given_gene(gene_name):
    pathways = general.pathways_given_product(gene_name)
    return {
        "kegg_pathways": pathways[0],
        "pc_pathways": pathways[1]
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


# Returns mutation data from mongo db given gene, variant name
def gene_mutation_data(gene, variant):
    config = configparser.ConfigParser()
    config.read("server_config")

    if "mutations_db" not in config or "uri" not in config["mutations_db"]:
        print("Server config not found!")
        return None
    
    return mongo_helper.get_mutation_data(gene, variant, config["mutations_db"]["uri"])


# Returns any evidence stored in evidence db
def variant_evidence(gene, variant):
    config = configparser.ConfigParser()
    config.read("server_config")

    if "mutations_db" not in config or "uri" not in config["mutations_db"]:
        print("Server config not found!")
        return None

    return mongo_helper.variant_evidence(gene, variant, config["mutations_db"]["uri"])


# Returns a cypher query to create a Neo4j representation of an identified pathway
# Expected format: hsa:<id>
# TODO: Add mutation support
# TODO: Add functional enrichment support?
def neo4j_pathway(identifier, options=None):
    if options is None:
        options = {}
    identifier_list = identifier.split(":")
    if len(identifier_list) != 2:
        return {}
    accession = identifier_list[0] + identifier_list[1]
    pathway = kegg_helper.kegg_get_pathway(accession)

    # This "known" dict handles the unknown nodes in the graph
    known = {}
    query = "CREATE "
    query_list = [neo4j_helper.make_gene_query(pathway.genes, known),
                  neo4j_helper.make_compound_query(pathway.compounds, known),
                  neo4j_helper.make_reaction_query(pathway.reaction_entries, known),
                  neo4j_helper.make_map_query(pathway.maps, known)]

    relations_data = neo4j_helper.make_relations_query(pathway.relations, known)
    query_list.append(neo4j_helper.make_unknown_query(relations_data[1]))
    query_list.append(relations_data[0])

    for q in query_list:
        if len(q) > 0:
            query += q + ","
    query = query[:-1]

    # if "mutations" in options.keys():
    #     query += neo4j_helper.make_mutation_query(genes)

    # Merge matching nodes
    query += """ MATCH (n1),(n2)
                 WHERE ANY (x IN n1.name WHERE x IN n2.name) and id(n1) < id(n2)
                 WITH [n1,n2] as ns
                 CALL apoc.refactor.mergeNodes(ns) YIELD node"""

    query += """MATCH (a)-[r1]->(b)
             MATCH (a)-[r2]->(b)
             WHERE id(r1) < id(r2)
             WITH [r1,r2] as rs
             CALL apoc.refactor.mergeRelationships(rs) YIELD rel
             RETURN NULL"""

    return {"neo4j_query": query}
