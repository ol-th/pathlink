from System.site.Database_Tools import uniprot_helper, kegg_helper


# NB: name, kegg_id, functions and (maybe) uniprot_id will be None if this is unsuccessful.
class Gene:
    def __init__(self, uniprot_id=None, name=None):
        self.uniprot_id = uniprot_id
        self.name = None
        self.kegg_id = None
        self.functions = None

        # Finding the name and functions if uniprot id given
        if uniprot_id is not None:
            self.uniprot_id = uniprot_id
            uniprot_xml = uniprot_helper.get_uniprot_xml(uniprot_id)
            self.name = uniprot_helper.get_uniprot_name(uniprot_xml)
            self.functions = uniprot_helper.get_uniprot_functions(uniprot_xml)
        # Finding the uniprot id and functions given the name
        elif name is not None:
            self.uniprot_id = uniprot_helper.get_uniprot_identifier(name)
            uniprot_xml = uniprot_helper.get_uniprot_xml(self.uniprot_id)
            self.name = uniprot_helper.get_uniprot_name(uniprot_xml)
            self.functions = uniprot_helper.get_uniprot_functions(uniprot_xml)
        # Assuming these are successful, find the kegg id.
        if self.uniprot_id is not None:
            self.kegg_id = kegg_helper.kegg_identifier_convert(self.uniprot_id)
