"""Util module tests
"""

import os.path
from unittest import TestCase
import mupub
from clint.textui.validators import ValidationError
from .tutils import PREFIX

_SIMPLE_PATH = os.path.join(
    PREFIX,
    "SorF",
    "O77",
    "sorf-o77-01",
)
_LYS_PATH = os.path.join(
    PREFIX,
    "PaganiniN",
    "O1",
    "Caprice_1",
)


class UtilsTest(TestCase):
    """Utils testing"""

    def test_find(self):
        """Find files (for zipping ly files)"""
        here = os.getcwd()
        try:
            os.chdir(_SIMPLE_PATH)
            flist = mupub.utils.find_files(".")
            self.assertEqual(len(flist), 2)
        finally:
            os.chdir(here)

    def test_resolve(self):
        """Resolving file input"""
        here = os.getcwd()
        try:
            for test_path in [
                _SIMPLE_PATH,
                _LYS_PATH,
            ]:
                os.chdir(test_path)
                base, infile = mupub.utils.resolve_input()
                self.assertEqual(base, os.path.basename(test_path))
                self.assertIsNotNone(infile)
        finally:
            os.chdir(here)

    def test_bools(self):
        boolv = mupub.utils.BooleanValidator("some message")
        boolv_nom = mupub.utils.BooleanValidator()
        self.assertTrue(boolv("y"), "y is True")
        self.assertFalse(boolv("n"), "n is False")
        self.assertTrue(not boolv_nom("N"), "not N is True")
        with self.assertRaises(ValidationError):
            if boolv("x"):
                self.assertFail("should not be here!")
