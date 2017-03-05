"""Validate module tests
"""

import os.path
from unittest import TestCase
import mupub
from clint.textui.validators import ValidationError
from .tutils import PREFIX

_SIMPLE_PATH = os.path.join(PREFIX, 'SorF', 'O77', 'sorf-o77-01',)
_BAD_PATH = os.path.join(PREFIX, 'PaganiniN', 'duh', 'duh_1',)

class ValidateTest(TestCase):

    def test_repository(self):
        is_repo = mupub.in_repository(path=_SIMPLE_PATH)
        self.assertTrue(is_repo)
        is_repo = mupub.in_repository(path='.')
        self.assertFalse(is_repo)
        is_repo = mupub.in_repository(path=_BAD_PATH)
        self.assertFalse(is_repo)
    
