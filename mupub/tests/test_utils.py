"""Util module tests
"""

import os.path
from unittest import TestCase
from .tutils import PREFIX
import mupub

_HERE = os.getcwd()
_TEST_PATH = os.path.join(PREFIX, 'SorF', 'O77', 'sorf-o77-01',)

class UtilsTest(TestCase):
    """Utils testing"""

    @classmethod
    def setUpClass(cls):
        os.chdir(_TEST_PATH)
        

    @classmethod
    def tearDownClass(cls):
        os.chdir(_HERE)


    def test_find(self):
        """Find files (for zipping ly files)"""
        flist = mupub.utils.find_files('.')
        self.assertEqual(len(flist), 2)


    def test_resolve(self):
        """Resolving file input"""
        base,infile = mupub.utils.resolve_input()
        self.assertEqual(base, os.path.basename(_TEST_PATH))
        self.assertIsNotNone(infile)
