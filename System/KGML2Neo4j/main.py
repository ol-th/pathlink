import Bio.KEGG.REST as KEGG_REST
import Bio.KEGG.KGML.KGML_parser as KEGG_KGML_PARSER
from .database import database
import configparser


ORGANISM = "hsa"


def generate_database(accession, verbose=False):
    # Expects name of pathway as argument
    # Get the KGML from KEGG
    if verbose:
        print("Getting initial data...")
    query = accession.replace(" ", "+")
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

    if verbose:
        print("Getting pathway data...")

    pathway_kgml = KEGG_REST.kegg_get(identifier, "kgml")
    pathway = KEGG_KGML_PARSER.read(pathway_kgml)
    config = configparser.ConfigParser()
    config.read("server_config")
    if not "KGML2NEO4J" in config:
        print("Server config not found!")
        return

    username = config["KGML2NEO4J"]['username']
    password = config["KGML2NEO4J"]['password']
    server_uri = config["KGML2NEO4J"]['uri']

    db = database(server_uri, username, password)

    if verbose:
        print("Uploading to Neo4j...")

    db.run_query("MATCH (n) DETACH DELETE n")

    known = {}

    query = "CREATE "
    query_list = [db.make_gene_query(pathway.genes, known), db.make_compound_query(pathway.compounds, known),
                  db.make_reaction_query(pathway.reaction_entries, known), db.make_map_query(pathway.maps, known)]

    relations_data = db.make_relations_query(pathway.relations, known)
    query_list.append(db.make_unknown_query(relations_data[1]))
    query_list.append(relations_data[0])

    for q in query_list:
        if len(q) > 0:
            query += q + ","
    query = query[:-1]

    db.run_query(query)

    # Merge matching nodes
    merge_nodes_query = """MATCH (n1),(n2)
                        WHERE ANY (x IN n1.name WHERE x IN n2.name) and id(n1) < id(n2)
                        WITH [n1,n2] as ns
                        CALL apoc.refactor.mergeNodes(ns) YIELD node
                        RETURN node"""

    merge_relations_query = """MATCH (a)-[r1]->(b)
                            MATCH (a)-[r2]->(b)
                            WHERE id(r1) < id(r2)
                            WITH [r1,r2] as rs
                            CALL apoc.refactor.mergeRelationships(rs) YIELD rel
                            RETURN rel"""

    db.run_query(merge_nodes_query)
    db.run_query(merge_relations_query)
