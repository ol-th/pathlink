from .Database_Tools import kegg_helper, uniprot_helper, pathwaycommons_helper, general
from .classes import Gene


# TODO: Include Relations?
def get_pathway_info(identifier):
    pathway = kegg_helper.kegg_get_pathway(identifier)
    # Outputs tuple (link, name)
    gene_tuple = kegg_helper.kegg_gene_list(pathway.genes)
    return {
        "pathway_name": pathway.name,
        "pathway_link": pathway.link,
        "gene_list": gene_tuple
    }


def pathways_given_gene(gene_name):
    pathways = general.pathways_given_product(gene_name)
    return {
        "kegg_pathways": pathways[0],
        "pc_pathways": pathways[1]
    }

# TODO: function_enrichment_gene_list
# TODO: functional_enrichment_gene
# TODO: functional_enrichment_gene_pathway


# [0 - name, 1 - identifier] for pathway, gene is gene class
def pathway_gene_interaction(pathway, gene):

    participation_verdict = general.product_participation(gene, pathway[0], pathway_id=pathway[1])
    pathway = kegg_helper.kegg_get_pathway(pathway[1])
    participant_ids = [gene.name for gene in pathway.genes]
    enrichment_names = gene.uniprot_id + " "
    for gene in participant_ids:
        enrichment_names += gene.split(" ")[0] + " "
    enrichment_names = enrichment_names[:-1]

    return {
        "participation_verdict": participation_verdict,
        "enrichment_names": enrichment_names
    }

