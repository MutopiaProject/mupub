"""Test cases for mupub.commands.check
"""
import os
from unittest import TestCase
import mupub

TEST_DATA = 'data'
PREFIX = os.path.join(os.path.dirname(__file__), TEST_DATA, 'mu')

class CheckTest(TestCase):

    def test_basic_check(self):
        basic = os.path.join(os.path.dirname(__file__),
                             TEST_DATA,
                             'basic-hdr.ly')
        mupub.check(basic, database='default',header_file=None)


    def test_validate(self):
        header = mupub.find_header('SorF/O5/sor-op5-5', PREFIX)
        failed_count = mupub.Validator.basic_checks(header)
        self.assertEqual(failed_count, 0)
        
