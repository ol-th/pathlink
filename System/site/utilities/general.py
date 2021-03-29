from . import kegg_helper, pathwaycommons_helper, uniprot_helper


def pathways_given_product(protein_name):
    protein_id = uniprot_helper.get_uniprot_identifier(protein_name)
    protein_kegg_id = kegg_helper.kegg_identifier_convert(protein_id)
    protein_info_kegg = kegg_helper.kegg_info(protein_kegg_id)
    index = 0
    in_pathways = False
    kegg_pathways_list = []

    # This wrangles all of the pathway data into a 2d list of format [[accession, description], ...]
    while index < len(protein_info_kegg):
        if not in_pathways and "PATHWAY" in protein_info_kegg[index]:
            in_pathways = True
            kegg_pathways_list.append(protein_info_kegg[index][12:].split("  "))
        elif in_pathways:
            if not protein_info_kegg[index].startswith(" "):
                break
            kegg_pathways_list.append(protein_info_kegg[index][12:].split("  "))
        index += 1

    # pc_pathways_list = pathwaycommons_helper.pathways_given_product(protein_id)

    return kegg_pathways_list


def pathways_given_pathway(pathway_name):
    return pathwaycommons_helper.pathway_given_pathway(pathway_name)


def product_participation(gene, pathway_name, pathway_id=None):

    # PC SEARCH
    pc_outcome = pathwaycommons_helper.pc_participation_check(gene.uniprot_id, pathway_name)

    # KEGG SEARCH
    kegg_pathway_id = None
    if pathway_id is None:
        kegg_pathway_id = kegg_helper.kegg_search("pathway", pathway_name)
    else:
        kegg_pathway_id = pathway_id

    print(repr(gene.kegg_id))
    print(repr(kegg_pathway_id))
    kegg_outcome = kegg_helper.kegg_pathway_participation(gene.kegg_id, kegg_pathway_id)
    print(kegg_outcome)
    return kegg_outcome, pc_outcome
