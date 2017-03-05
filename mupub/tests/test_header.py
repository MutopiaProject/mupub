"""mupub.Header tests for mupub
"""

import os.path
import sys
from unittest import TestCase
import mupub
import mupub.tests.tutils as tutils

TEST_DATA = 'data'

class HeaderTest(TestCase):
    """mupub.Header test class"""

    def _check_header(self, header):
        """Generic test for headers.

        :param str header: Instantiated header to test

        """
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'basic-hdr.ly')
        header.load_table(path)
        self.assertTrue(header.len() > 0, 'Loader completely failed')
        # test file has both composer and mutopiacomposer
        self.assertEqual(header.get_value('mutopiacomposer'), 'SorF')
        self.assertEqual(header.get_field('composer'), 'SorF')
        # test file has a single 'style' field but get_field should
        # still work properly.
        self.assertEqual(header.get_field('style'), 'Romantic')


    def test_scheme_loader(self):
        """Use scheme loader to build header."""
        self._check_header(mupub.Header(mupub.SchemeLoader()))


    def test_ly_loader(self):
        """Use line parsing loader to build header."""
        self._check_header(mupub.Header(mupub.LYLoader()))


    def test_unicode_read(self):
        """Test reads of utf-8 encoding."""
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'unicode-hdr.ly')
        header = mupub.Header(mupub.LYLoader())
        header.load_table(path)
        self.assertTrue(header.get_value('title').startswith('Six Petites Pièces'))
        self.assertEqual(header.get_value('source'), 'Mainz: B. Schott')


    def test_throws_badfile(self):
        """Make sure an exception is thrown on bad input file."""
        header = mupub.Header(mupub.SchemeLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'foo-bar.ly')
        with self.assertRaises(FileNotFoundError):
            header.load_table(path)


    def test_version_loader(self):
        """Test VersionLoader class"""
        verdup = mupub.Header(mupub.VersionLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'version-dup.ly')
        verdup.load_table(path)
        self.assertEqual(verdup.get_value('lilypondVersion'), '2.19.35')

        vercom = mupub.Header(mupub.VersionLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'version-comment.ly')
        vercom.load_table(path)
        self.assertEqual(vercom.get_value('lilypondVersion'), '2.19.35')

        verobt = mupub.Header(mupub.VersionLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'version-obtuse.ly')
        verobt.load_table(path)
        self.assertEqual(verobt.get_value('lilypondVersion'), '2.19.35')


    def test_multiple(self):
        """Test ability to load multiple header files"""
        header = mupub.Header(mupub.LYLoader())
        prefix = os.path.join(os.path.dirname(__file__), TEST_DATA)
        header.load_table_list(prefix, ['hdr-split-a.ly', 'hdr-split-b.ly'])
        self.assertEqual(header.get_value('composer'), 'F. Sor')
        self.assertEqual(header.get_field('title'), '12 Etudes, No. 1')


    def test_raw(self):
        """Parsing raw headers"""
        header = mupub.Header(mupub.RawLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'hdr-raw.ly')
        header.load_table(path)
        self.assertEqual(header.get_value('title'), '12 Etudes')
        self.assertEqual(header.get_value('style'), '')


    def test_find(self):
        """Find headers"""
        hdr = mupub.find_header('SorF/O5/sor-op5-5', tutils.PREFIX)
        self.assertEqual(hdr.get_field('composer'), 'SorF')


    def test_versions(self):
        """Test LilyPond version matching"""
        lyv_2 = mupub.LyVersion('2.16.2')
        lyv_3 = mupub.LyVersion('2.16.2')
        lyv_4 = mupub.LyVersion('2.19.0')
        lyv_5 = mupub.LyVersion('2.16.2-1')
        self.assertTrue(lyv_4 > lyv_2)
        self.assertTrue(lyv_3 == lyv_2)
        self.assertTrue(lyv_3.match(lyv_2))
        self.assertTrue(lyv_3.strmatch(lyv_2))
        # test boolean inversion
        self.assertFalse(lyv_4 == lyv_2)
        self.assertTrue(lyv_4 != lyv_2)
        # test that it ignores any trailing value
        self.assertTrue(lyv_5 == lyv_2)


    def test_bad_header(self):
        test_db = tutils.getTestDB()
        header = mupub.Header(mupub.LYLoader())
        path = os.path.join(os.path.dirname(__file__),
                            TEST_DATA,
                            'bad-header.ly')
        header.load_table(path)
        fails = mupub.DBValidator(test_db).validate_header(header)
        self.assertTrue(len(fails) > 0, 'Found failures in bad-header')
