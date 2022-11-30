# PathLink

This is the repository containing my 3rd year project research.

## Video Explanation and Demonstration

[<img src="https://i.ytimg.com/vi/A6rYyVcMX_o/maxresdefault.jpg" width="50%">](https://youtu.be/A6rYyVcMX_o)

## Motivation

There is a significant amount of cancer data available in different formats and places.

This is fine for manual use but even then it is lengthy to use the data to come to any conclusions.

We need to be able to use data from the following sources in a single place:

* KEGG
* Pathway Commons
* CIViCDB
* ClinVar
* UniProt
* STRING

The purpose of this project is to provide an API and graphical interface to query cancer-related bioinformatic data.

## Outcomes

The API and GUI provide many ways to get data on genes, drugs, pathways and their interactions.

Importantly, it can output the Cypher queries necessary to produce a comprehensive pathway graph in Neo4j. The outputs look something like this:

![Neo4j Graph](images/graph.png)

These graphs can then be traversed with algorithms to reason about cancer systems.

## Structure

### `preliminaries`

These are the files and programs I used for my preliminary research into the Biological Pathways domain prior to the full system design

### `src`

This is the cumulative result of the work so far with a frontend Flask webserver and a REST API.

This frontend accepts structured queries fulfilling the criteria set out in the report.

For more information about running the system, consult src/README.md

### `scripts`

This contains any scripts used to test the system as a client.

## Implementation Notes

Some raw datasets need to be pulled into an operational MongoDB database in advance:

* KEGG
* CiViCDB
* ClinVar

This is because their APIs are either unacceptably slow or don't provide the functionality we need.

The rest of the data comes live from the API endpoints of the respective services.

## Setup

There is a small amount of preliminary setup required.

1. Install dependencies

    This project uses quite a few python3 modules, so install them as follows:
    
    ```bash
    pip3 install -r src/requirements.txt
    ```

2. Install databases

    The project uses mongoDB and Neo4j so ensure that accessible instances of both are available.

    Once these are running, retrieve the information referred to in `src/server_config` and
paste them into the relevant locations.
   
   
3. Populate cache database

    The project uses the mongoDB to cache slow datasets. This can be filled by running:

    ```
   cd scripts/db_management
   ./populate_mongo.sh
    ```
   

4. Run

    The system can now run. This is achieved by ensuring that you are in the System directory
    and executing `./run`.
   
## Usage

- The system has a frontend available via localhost (usually 127.0.0.1/).
This is a comprehensive interface for simple queries.
  
- The API has a total of 7 endpoints (all `GET`):

    - `/api/pathway` - All data on a pathway identifier / name.
    - `/api/gene` - All data on a gene identifier / name.
    - `/api/variant` - All data on a gene variant.
    - `/api/pathway_gene_interaction` - All interaction data between a gene and pathway. 
    - `/api/variant_evidence` - All CiViC/ClinVar evidence of a gene variant.
    - `/api/functional_enrichment` - Get the functional network of a protein.
    - `/api/pathway_to_cypher` - Get the cypher queries to add a pathway to a Neo4j graph database.
  