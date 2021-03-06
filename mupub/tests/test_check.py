"""Test cases for mupub.commands.check
"""
import os
from unittest import TestCase
from .tutils import PREFIX
import mupub

TEST_DATA = 'data'

class CheckTest(TestCase):

    def test_basic_check(self):
        """Basic check command"""
        basic = os.path.join(os.path.dirname(__file__),
                             TEST_DATA,
                             'basic-hdr.ly')
        mupub.check(basic, header_file=None)


    def test_validate(self):
        """Can validate files"""
        header = mupub.find_header('SorF/O5/sor-op5-5', PREFIX)
        fails = mupub.Validator.basic_checks(header)
        self.assertEqual(len(fails), 0)
