"""Test cases for mupub.commands.check
"""
import os
from unittest import TestCase
import mupub

TEST_DATA = 'data'

class CheckTest(TestCase):

    def test_basic_check(self):
        basic = os.path.join(os.path.dirname(__file__),
                             TEST_DATA,
                             'basic-hdr.ly')
        mupub.check(basic, database='default')
