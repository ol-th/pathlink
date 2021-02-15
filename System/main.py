from Database_Tools import general, kegg_helper, uniprot_helper

outcome = general.pathways_given_pathway("base excision repair")
for i in outcome:
    print(i[0])
