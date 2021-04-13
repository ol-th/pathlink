# Testing

This is a very informal testing directory

The main purpose is to test the Cypher query mechanisms and input the cypher into a Neo4j database.

To do that, ensure that the system is running and execute the following:

```bash
python3 paths2neo4j.py <pathway_id> <comma-separated string of args>
```

The args supported by the program are the same args supported by the pathways_to_cypher endpoint.

e.g.

```bash
python3 paths2neo4j.py hsa05210 "drugs,networks,variants"
```