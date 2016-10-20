"""Test cases for mupub.commands.build
"""
import os
import unittest
from .tutils import PREFIX
import mupub

_HERE = os.getcwd()
_TEST_PATH = os.path.join(PREFIX, 'AguadoD', 'aminor-study')

class CheckTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.chdir(_TEST_PATH)
        

    @classmethod
    def tearDownClass(cls):
        os.chdir(_HERE)

    """Skipped because running may cause a lilypond compiler download.
    """
    @unittest.skip('skipping single build test')
    def test_single_build(self):
        """Build a simple score"""
        mupub.build(infile=['aminor-study.ly',],
                    header_file=None,
                    database='default',
                    verbose=False,
                    collect_only=False)
