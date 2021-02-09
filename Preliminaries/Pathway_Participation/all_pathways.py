from . import kegg_helper, uniprot_helper
import sys


def main():
    protein_name = sys.argv[1]
    protein_id = uniprot_helper.get_uniprot_identifier(protein_name)
    protein_kegg_id = kegg_helper.kegg_identifier_convert(protein_id)
    print(protein_kegg_id)
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

    print("KEGG:")
    for i in kegg_pathways_list:
        print(i[0] + "\t" + i[1])


if __name__ == "__main__":
    main()
