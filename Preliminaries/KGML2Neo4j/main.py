import Bio.KEGG.REST as KEGG_REST
import Bio.KEGG.KGML.KGML_parser as KEGG_KGML_PARSER
import sys
from .database import database
import configparser


ORGANISM = "hsa"


def main():
    # Expects name of pathway as argument
    # Get the KGML from KEGG
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
    identifier = identifier.replace("map", ORGANISM)

    pathway_kgml = KEGG_REST.kegg_get(identifier, "kgml")
    pathway = KEGG_KGML_PARSER.read(pathway_kgml)
    print(pathway.compounds[0].name)
    print(pathway.compounds[0].components)
    # config = configparser.ConfigParser()
    # config.read("server_config")
    # if not "KGML2NEO4J" in config:
    #     print("Server config not found!")
    #     return

    # username = config["KGML2NEO4J"]['username']
    # password = config["KGML2NEO4J"]['password']
    # server_uri = config["KGML2NEO4J"]['uri']
    #
    # db = database(server_uri, username, password)
    #
    # db.add_genes(pathway.genes)


if __name__ == "__main__":
    main()