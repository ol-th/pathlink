# System

This section will take you through setting up and using the system.

## Setup

There is a small amount of preliminary setup required.

1. Install dependencies

    This project uses quite a few python3 modules, so install them as follows:
    
    ```bash
    pip3 install -r requirements.txt
    ```

2. Install databases

    The project uses mongoDB and Neo4j so ensure that accessible instances of both are available.

    Once these are running, retrieve the information referred to in ```server_config``` and
paste them into the relevant locations.
   
   
3. Populate cache database

    The proejct uses the mongoDB as a form of cache. This can be filled by running:

    ```
   cd db_management
   ./update_mongo.sh
    ```
   

4. Run

    The system can now run. This is achieved by ensuring that you are in the System directory
    and executing ```./run```.
   
## Usage

- The system has a frontend available via the root directory (usually 127.0.0.1/).
This is a comprehensive interface for simple queries.
  
- The system also has a total of 7 API endpoints:

    - /api/pathway
    - /api/gene
    - /api/variant
    - /api/pathway_gene_interaction
    - /api/variant_evidence
    - /api/functional_enrichment
    - /api/pathway_to_cypher
  


