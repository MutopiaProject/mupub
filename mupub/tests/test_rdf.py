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
        rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        mp = Namespace("http://www.mutopiaproject.org/piece-data/0.1/")
        graph = ConjunctiveGraph()
        piece = URIRef('.')
        graph.bind('mp', mp)
        graph.add((piece, mp['title'], Literal(header.get_field('title'))))
        graph.add((piece, mp['composer'], Literal(header.get_field('composer'))))
        graph.add((piece, mp['opus'], Literal('')))
        graph.serialize(destination='test.rdf',
                        format='pretty-xml')
