import requests
import sys
from neo4j import GraphDatabase
import configparser

"""
    Get Pathway ID, use PathLink to populate a Neo4j database with the relevant data.
"""


class Database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # Gene methods
    def run_query(self, query):
        if len(query) == 0:
            return
        with self.driver.session() as session:
            session.write_transaction(self._run_query, query)

    def _run_query(self, tx, query):
        tx.run(query)


def main():
    api_url = "http://127.0.0.1:5000/api/"

    config = configparser.ConfigParser()
    config.read("server_config")
    if not "KGML2NEO4J" in config:
        print("Server config not found!")
        return

    username = config["KGML2NEO4J"]["username"]
    password = config["KGML2NEO4J"]["password"]
    server_uri = config["KGML2NEO4J"]["uri"]

    db = Database(server_uri, username, password)

    ids = sys.argv[1].strip()
    params = {"id": ids[0], "options": sys.argv[2]}
    r = requests.get(api_url + "pathway_to_cypher", params=params)
    pipeline = r.json()["neo4j_query_pipeline"]
    for query in pipeline:
        db.run_query(query)


if __name__ == "__main__":
    main()
