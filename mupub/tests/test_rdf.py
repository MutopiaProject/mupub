"""Core tests for mut
"""

import os.path
from unittest import TestCase
import mupub
from .tutils import PREFIX

TEST_DATA = 'data'

class RdfTest(TestCase):
    """RDF Testing"""

    def test_basic_rdf(self):
        header = mupub.Header(mupub.LYLoader())
        path = os.path.join(PREFIX,
                            'AguadoD', 'aminor-study', 'aminor-study.ly')
        header.load_table(path)
        header.write_rdf('test.rdf')
