# Preliminaries

## Dependencies

To get all the dependencies for this project run 

```
pip install -r requirements.txt
```

In this directory (`/Preliminaries`)
## Pathway_participation

This module is for establishing a Protein's participation in a certain named pathway.

Invoke the module using something like this:

```
python3 -m Pathway_participation.query "PARP1" "Base excision repair"
```

This would query the Pathway Commons and KEGG datasets to establish whether PARP1 participates in the Base excision repair pathway.

## KGML2Neo4j

Given a pathway name this will convert and send the information stored in
KEGG to a Neo4j database.

### Usage

This expects a server_config file in the directory of execution in the form:

```
[KGML2NEO4J]
username = neo4j
password = example
uri = [uri here - usually neo4j://localhost:...]
```

The program is executed as such (this is from the Preliminaries directory):

```
python3 -m KGML2Neo4j.main [pathway name]
```

e.g:

```
python3 -m KGML2Neo4j.main "colorectal cancer"
```