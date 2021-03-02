import unittest
from tyto import *


class TestOntology(unittest.TestCase):

    def test_SO(self):
        term_a = 'sequence_feature'
        uri = SO.get_uri_by_term(term_a)  # Confirm term query with underscore works
        self.assertEqual(uri, 'https://identifiers.org/SO:0000110')
        term_b = SO.get_term_by_uri(uri)
        self.assertEqual(term_a, term_b)
        with self.assertRaises(LookupError):
            uri = SO.get_uri_by_term('not_a_term')
        # Test deprecated identifier format
        term_b = SO.get_term_by_uri('http://identifiers.org/so/SO:0000110')
        self.assertEqual(term_a, term_b)

    def test_SBO(self):
        uri_a = 'https://identifiers.org/SBO:0000000'
        term = SBO.get_term_by_uri(uri_a)
        # Confirm term query with space works
        self.assertEqual(term, 'systems biology representation')
        uri_b = SBO.get_uri_by_term(term)
        self.assertEqual(uri_a, uri_b)
        # Test deprecated identifier format
        term = SBO.get_term_by_uri('http://identifiers.org/sbo/SBO:0000000')
        self.assertEqual(term, 'systems biology representation')

    def test_dynamic_ontology_attributes(self):
        # Tests that our override of the __getattr__ method is working.
        # Tests dynamic generation of attributes for ontology terms; also verifies that
        # the Ontology's other methods (e.g., get_uri_by_term) remain accessible
        self.assertEqual(SO.promoter, SO.get_uri_by_term('promoter'))

        # When an Ontology term has spaces, the attribute that is dynamically generated
        # should replace these with underscores
        self.assertEqual(SBO.systems_biology_representation,
                         SBO.get_uri_by_term('systems biology representation'))

        self.assertNotEqual(SBO.systems_biology_representation,
                            SBO.reactant)

        # Raise an exception if an invalid term is specified
        with self.assertRaises(LookupError):
            not_a_term = SO.not_a_term

    def test_NCIT(self):
        self.assertEqual(NCIT.Growth_Medium, 'https://identifiers.org/ncit:C85504')

if __name__ == '__main__':
    unittest.main()
