import sys
from .uniprot_helper import *
from .kegg_helper import *
from .pathwaycommons_helper import *


def main():
    gene_name = sys.argv[1]
    query = sys.argv[2]

    uniprot_id = get_uniprot_identifier(gene_name)

    # PC SEARCH

    pc_outcome = pc_participation_check(uniprot_id, query)
    if pc_outcome:
        print("Pathway Commons: True")
        return
    print("Pathway Commons: False")

    # KEGG SEARCH

    kegg_identifier = kegg_identifier_convert(uniprot_id)

    if kegg_identifier == None:
        print("KEGG: False")
        return

    kegg_outcome = kegg_pathway_participation(kegg_identifier, query)

    print ("KEGG: " + str(kegg_outcome))
    return


if __name__ == "__main__":
    main()
