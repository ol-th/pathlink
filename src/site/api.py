from .utilities import (
    kegg_helper,
    neo4j_helper,
    mongo_helper,
    config,
    pathwaycommons_helper,
    string_helper,
    ensembl_helper,
)
from .utilities.classes import Gene
from bson import json_util


# TODO: function_enrichment_gene_list
# TODO: functional_enrichment_gene
# TODO: functional_enrichment_gene_pathway


# Returns pathway name, link, participants
def get_pathway(identifier, options=None):
    if options is None:
        options = ""
    pathway = kegg_helper.kegg_get_pathway(identifier)
    info = kegg_helper.kegg_info(identifier)
    name = kegg_helper.kegg_get_name(info)
    description = kegg_helper.kegg_pathway_desc(info)
    # Outputs tuple (link, name)
    gene_tuple = kegg_helper.kegg_gene_list(pathway.genes)
    pathway_parents = pathwaycommons_helper.pathway_parents(name)
    output_dict = {
        "name": name,
        "kegg_id": pathway.name,
        "pathway_description": description,
        "pathway_link": pathway.link,
        "gene_list": gene_tuple,
    }

    if "parents" in options:
        output_dict["pc_pathway_parents"] = pathway_parents

    return output_dict


# Returns pathways that gene participates in
def get_gene(name=None, uniprot_id=None, options=None):
    if name is None and uniprot_id is None:
        return {}
    if options is None:
        options = ""
    gene = Gene(name=name, uniprot_id=uniprot_id)
    gene_kegg_entry = kegg_helper.kegg_info(gene.kegg_id)
    kegg_pathways = kegg_helper.get_gene_pathways(gene_kegg_entry)
    uri = config.get_config()["mutations_db"]["uri"]
    output_dict = {
        "name": gene.name,
        "functions": gene.functions,
        "kegg_id": gene.kegg_id,
        "uniprot_id": gene.uniprot_id,
        "kegg_pathways": kegg_pathways,
    }

    if "pc_pathways" in options:
        pc_pathways = pathwaycommons_helper.pathways_given_product(gene.uniprot_id)
        output_dict["pc_pathways"] = pc_pathways

    if "variants" in options:
        variants_cursor = mongo_helper.get_mutations(gene.name, uri)
        variants_list = [json_util.dumps(result) for result in variants_cursor]
        output_dict["variants"] = variants_list

    if "drugs" in options:
        drugs = mongo_helper.get_drug_links(gene.kegg_id, uri)
        output_dict["drugs"] = drugs["drugs"]

    return output_dict


# Returns interaction data between pathway and gene
def pathway_gene_interaction(
    pathway_name,
    pathway_kegg_id=None,
    input_gene=None,
    gene_uniprot=None,
    gene_kegg=None,
    gene_name=None,
):
    if input_gene is None:
        gene = Gene(uniprot_id=gene_uniprot, kegg_id=gene_kegg, name=gene_name)
    else:
        gene = input_gene

    if pathway_kegg_id is None:
        kegg_pathway_id = kegg_helper.kegg_search("pathway", pathway_name)[0]
    else:
        kegg_pathway_id = pathway_kegg_id

    participation_verdict = kegg_helper.kegg_pathway_participation(
        gene.kegg_id, kegg_pathway_id
    )
    pathway = kegg_helper.kegg_get_pathway(kegg_pathway_id)
    participant_ids = [gene.name.split(" ")[0] for gene in pathway.genes]
    participant_ids.append(gene.name)
    direct, indirect = functional_enrichment(participant_ids)

    return {
        "participation_verdict": participation_verdict,
        "direct": direct,
        "indirect": indirect,
    }


# Returns mutation data from mongo db given gene, variant name
def gene_variant_data(gene, variant):
    db_config = config.get_config()
    results = mongo_helper.get_mutation_data(
        gene, variant, db_config["mutations_db"]["uri"]
    )

    if results is None:
        return {}

    effects = ensembl_helper.get_effect_predictions("rs" + str(results["RS# (dbSNP)"]))
    results = json_util.dumps(results)
    return {"results": results, "ensembl_vep": effects}


# Returns any evidence stored in evidence db
def variant_evidence(gene, variant):
    db_config = config.get_config()

    return mongo_helper.variant_evidence(
        gene, variant, db_config["mutations_db"]["uri"]
    )


def functional_enrichment(gene_list):
    return string_helper.get_relevant_links(gene_list)


# Returns a cypher query to create a Neo4j representation of an identified pathway
# Expected format: hsa:<id>
def neo4j_pathway(identifier, options=None):
    if options is None:
        options = ""
    accession = identifier
    pathway = kegg_helper.kegg_get_pathway(accession)

    gene_names = neo4j_helper.make_genes_from_kegg_pathway(pathway.genes)

    # This "known" dict is checked afterwards to find unknown nodes in the graph
    known = {}
    create_query = "CREATE "
    query_list = [
        neo4j_helper.make_gene_query(pathway, gene_names, known),
        neo4j_helper.make_compound_query(pathway.compounds, known),
        neo4j_helper.make_reaction_query(pathway.reaction_entries, known),
        neo4j_helper.make_map_query(pathway.name),
    ]

    if "variants" in options:
        query_list.append(
            neo4j_helper.make_variants_query(zip(gene_names, pathway.genes))
        )

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

    pipeline.append(
        "MATCH (n1),(n2) WHERE ANY (x IN n1.kegg_ids WHERE x IN n2.kegg_ids) and id(n1) <> id(n2) "
        'WITH [n1,n2] as ns CALL apoc.refactor.mergeNodes(ns, {properties:"combine", mergeRels:true}) '
        "YIELD node RETURN node"
    )
    pipeline.append(
        "MATCH (n1:Variant),(n2:Variant) WHERE n1.variant = n2.variant and id(n1) <> id(n2) "
        'WITH [n1,n2] as ns CALL apoc.refactor.mergeNodes(ns, {properties:"combine", mergeRels:true}) '
        "YIELD node RETURN node"
    )

    return {"neo4j_query_pipeline": pipeline}
