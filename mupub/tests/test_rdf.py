"""Core tests for mut
"""

import os.path
from unittest import TestCase
import mupub
from rdflib import Namespace, URIRef, ConjunctiveGraph, Literal


TEST_DATA = 'data'

class RdfTest(TestCase):
    """RDF Testing"""

    def test_basic_rdf(self):
        header = mupub.Header(mupub.LYLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'mu', 'AguadoD', 'aminor-study', 'aminor-study.ly')
        header.load_table(path)
        header.write_rdf('test.rdf')
