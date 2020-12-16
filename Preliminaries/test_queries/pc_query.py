from SPARQLWrapper import SPARQLWrapper, XML
import xml.etree.ElementTree as ET

sparql = SPARQLWrapper("http://rdf.pathwaycommons.org/sparql/")

statement = """
PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?pathwayName
WHERE
{
?protein rdf:type bp:Protein;
               bp:entityReference ?eref.

FILTER regex(?eref, "^http://identifiers.org/uniprot/P09874$")

?pathway rdf:type bp:Pathway.
?interaction bp:participant ?protein.
?pathway bp:pathwayComponent ?interaction;
         bp:displayName ?pathwayName.

FILTER regex(?pathwayName, ".*d4-gdi.*", "i")
}
LIMIT 10

"""

sparql.setQuery(statement)
sparql.setReturnFormat(XML)
ret = sparql.query().convert().toxml()
print(ret)
xml_root = ET.fromstring(ret)
print(len(xml_root[1]))
