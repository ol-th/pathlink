import Bio.KEGG.REST as KEGG_REST
import Bio.KEGG.KGML.KGML_parser as KEGG_KGML_PARSER
import sys


def main():
    query = sys.argv[1].replace(" ", "+")
    result = KEGG_REST.kegg_find('PATHWAY', query)
    result_txt = result.read().split('\n')
    if len(result_txt) == 1:
        print("Search found no results")
        return

    choice = 0
    if len(result_txt) > 2:
        print("More than 1 result:")
        for index, r in enumerate(result_txt):
            output = r.split("\t")
            if len(output) == 2:
                print(str(index) + "\t" + output[1])
        choice = int(input("Which one? "))

    identifier = result_txt[choice].split("\t")[0].strip()
    identifier = identifier.replace("map", "hsa")

    pathway_kgml = KEGG_REST.kegg_get(identifier, "kgml")
    pathway = KEGG_KGML_PARSER.read(pathway_kgml)

    for i in pathway.genes:
        print(i.name)


main()
