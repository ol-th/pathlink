from SPARQLWrapper import SPARQLWrapper, XML
import xml.etree.ElementTree as ET


def pc_participation_check(id, query):

    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    statement = """
    
        PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?pathwayName
        WHERE
        {
        ?protein rdf:type bp:Protein;
                       bp:entityReference ?eref.

        FILTER regex(?eref, "^http://identifiers.org/uniprot/""" + id + """$")

        ?pathway rdf:type bp:Pathway.
        ?interaction bp:participant ?protein.
        ?pathway bp:pathwayComponent ?interaction;
                 bp:displayName ?pathwayName.

        FILTER regex(?pathwayName, \".*""" + query + """.*\", "i")
        }
        LIMIT 10

        """

    sparql.setQuery(statement)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    # If there are results, then the gene is part of the pathway specified
    return len(xml_root[1]) > 0


def pathway_given_pathway(name):
    sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

    query = """
        SELECT DISTINCT ?parentpname ?comment
        WHERE
        {
            ?pathway rdf:type bp:Pathway;
                     bp:displayName ?pname.
            FILTER regex(?pname, \".*""" + name + """.*\", "i")
            
            ?pathwayParent bp:pathwayComponent ?pathway;
                           bp:displayName ?parentpname;
                           bp:comment ?comment.
        }
        LIMIT 200"""

    sparql.setQuery(query)
    sparql.setReturnFormat(XML)
    ret = sparql.query().convert().toxml()
    xml_root = ET.fromstring(ret)
    output_dict = {}
    for i in xml_root[1]:
        pathway_name = i[0][0].text
        if pathway_name not in output_dict.keys():
            output_dict[pathway_name] = []
        output_dict[pathway_name].append(i[1][0].text)
    return output_dict
