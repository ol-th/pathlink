from neo4j import GraphDatabase


class database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    # Gene methods
    def add_genes(self, gene_list):
        with self.driver.session() as session:
            session.write_transaction(self._add_genes, gene_list)

    def _add_genes(self, tx, gene_list):
        tx.run(self._make_gene_query(gene_list))

    @staticmethod
    def _make_gene_query(gene_list):
        query = "CREATE "
        for gene in gene_list:
            query += "(a" + str(gene.id) + ":Gene {"\
                     "name: [\"" + gene.name.strip().replace(" ", "\",\"") + "\"]}),"
        # Removing trailing comma
        query = query[:-1]
        return query


