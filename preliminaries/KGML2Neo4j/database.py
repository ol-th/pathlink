from neo4j import GraphDatabase


class database:
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

    @staticmethod
    def make_gene_query(gene_list):
        query = ""
        for gene in gene_list:
            query += "(a" + str(gene.id) + ":Gene {"\
                     "name: [\"" + gene.name.strip().replace(" ", "\",\"") + "\"]}),"
        # Removing trailing comma
        query = query[:-1]
        return query

    @staticmethod
    def make_compound_query(compound_list):
        query = ""
        for compound in compound_list:
            query += "(a" + str(compound.id) + ":Compound {" \
                     "name: [\"" + compound.name.strip().replace(" ", "\",\"") + "\"]}),"
        # Removing trailing comma
        query = query[:-1]
        return query

    @staticmethod
    def make_reaction_query(reaction_list):
        query = ""
        for reaction in reaction_list:
            query += "(a" + str(reaction.id) + ":Reaction {" \
                     "name: [\"" + reaction.name.strip().replace(" ", "\",\"") + "\"]}),"
        # Removing trailing comma
        query = query[:-1]
        return query

    @staticmethod
    def make_map_query(map_list):
        query = ""
        for pmap in map_list:
            query += "(a" + str(pmap.id) + ":Map {" \
                     "name: [\"" + pmap.name.strip().replace(" ", "\",\"") + "\"]}),"
        # Removing trailing comma
        query = query[:-1]
        return query

    @staticmethod
    def make_relations_query(relation_list):
        query = ""
        for relation in relation_list:
            current_query = "(a" + str(relation.entry1.id) + ")-[:" + relation.type + " {subtypes: ["
            for subtype in relation.subtypes:
                current_query += "\"" + subtype[0] + "\","
            current_query = current_query[:-1]
            current_query += "]}]->(a" + str(relation.entry2.id) + "),"
            query += current_query
        # Removing trailing comma
        query = query[:-1]
        return query


