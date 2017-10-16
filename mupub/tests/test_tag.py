"""mupub tagging tests for mupub
"""

import os.path
from datetime import date
import sys
import shutil
import tempfile
from unittest import TestCase
from .tutils import PREFIX
import mupub

TEST_DATA = 'data'

class TagTest(TestCase):
    """Tag tests"""

    @classmethod
    def setUpClass(cls):
        cls.datapath = os.path.join(os.path.dirname(__file__),
                                     TEST_DATA)
        cls.dirpath = tempfile.mkdtemp(prefix='tag_')
        cls.start_dir = os.getcwd()
        os.chdir(cls.dirpath)


    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.start_dir)
        shutil.rmtree(cls.dirpath, ignore_errors=True)


    def test_tags_untagged_file(self):
        target = os.path.join(self.datapath, 'untagged-file.ly')
        header = shutil.copy(target, '.')
        mupub.tag(header, 77)
        loader = mupub.LYLoader()
        htable = loader.load(header)
        self.assertTrue('footer' in htable, 'Footer should be in table')
        self.assertTrue(htable['footer'].endswith('-77'))


    def test_can_tag_old_files(self):
        target = os.path.join(self.datapath, 'prosperpina-old.ly')
        header = shutil.copy(target, '.')
        today = date.today()
        mupub.tag(header, 0)
        htable = mupub.LYLoader().load(header)
        self.assertTrue('footer' in htable, 'Footer should be in table')
        mod_date,_ = mupub.core.id_from_footer(htable['footer'])
        self.assertEqual(today, mod_date, 'date in footer should match today()')
        self.assertTrue('license' in htable, 'Copyright tag not processed')
