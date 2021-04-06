from SPARQLWrapper import SPARQLWrapper, XML
import xml.etree.ElementTree as ET


def pc_participation_check(uniprot_id, pathway_name):

    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    statement = """
    
        PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?pathwayName
        WHERE
        {
        ?protein rdf:type bp:Protein;
                       bp:entityReference ?eref.

        FILTER regex(?eref, "^http://identifiers.org/uniprot/""" + uniprot_id + """$")

        ?pathway rdf:type bp:Pathway.
        ?interaction bp:participant ?protein.
        ?pathway bp:pathwayComponent ?interaction;
                 bp:displayName ?pathwayName.

        FILTER regex(?pathwayName, \".*""" + pathway_name + """.*\", "i")
        }
        LIMIT 10

        """

    sparql.setQuery(statement)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    # If there are results, then the gene is part of the pathway specified
    return len(xml_root[1]) > 0


def pathways_given_product(uniprot_id):

    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    statement = """

            PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT DISTINCT ?pathwayName ?comment
            WHERE
            {
            ?protein rdf:type bp:Protein;
                           bp:entityReference ?eref.

            FILTER regex(?eref, "^http://identifiers.org/uniprot/""" + uniprot_id + """$")

            ?pathway rdf:type bp:Pathway.
            ?interaction bp:participant|bp:left|bp:right ?protein.
            ?pathway bp:pathwayComponent ?interaction;
                     bp:displayName ?pathwayName;
                     bp:comment ?comment.

            }
            LIMIT 50

            """

    sparql.setQuery(statement)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    desc_dict = {}
    for i in xml_root[1]:
        pathway_name = i[0][0].text
        if pathway_name not in desc_dict.keys():
            desc_dict[pathway_name] = []
        desc_dict[pathway_name].append(i[1][0].text)

    output = []
    for pathway in desc_dict.items():
        current_desc = ""
        for i in pathway[1]:
            current_desc += "<p>" + i + "</p>"
        output.append([pathway[0], current_desc])

    return output


def pathway_parents(name):
    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    query = """
        SELECT DISTINCT ?parentpname ?comment
        WHERE
        {

            ?pathway rdf:type bp:Pathway;
                     bp:displayName ?pname.
            FILTER regex(?pname, ".*""" + name + """.*", "i")

            {
                
                ?pathwayParent bp:pathwayComponent ?pathway;
                               bp:displayName ?parentpname;
                               bp:comment ?comment.
                               
            }UNION{
                ?pathwayParent bp:controlled ?pathway.
                ?pathwayParent bp:pathwayComponent ?pathway;
                               bp:displayName ?parentpname;
                               bp:comment ?comment.
            }
        }
        LIMIT 200"""

    sparql.setQuery(query)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    desc_dict = {}
    for i in xml_root[1]:
        pathway_name = i[0][0].text
        if pathway_name not in desc_dict.keys():
            desc_dict[pathway_name] = []
        desc_dict[pathway_name].append(i[1][0].text)

    output = []
    for pathway in desc_dict.items():
        current_desc = ""
        for i in pathway[1]:
            current_desc += "<p>" + i + "</p>"
        output.append([pathway[0], current_desc])

    return output


def get_gene_name(id, limit=1):
    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")
    query = """
        PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?proteinName
        WHERE
        {
        ?protein rdf:type bp:Protein;
                       bp:entityReference ?eref;
                       bp:displayName ?proteinName.

        FILTER regex(?eref, "^http://identifiers.org/uniprot/""" + id + """$")

        }
        LIMIT """ + str(limit)
    sparql.setQuery(query)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    return xml_root[1][0][0][0].text
