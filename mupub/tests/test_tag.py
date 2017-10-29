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
        mupub.tag(header, 77, False)
        loader = mupub.LYLoader()
        htable = loader.load(header)
        self.assertTrue('footer' in htable, 'Footer should be in table')
        self.assertTrue(htable['footer'].endswith('-77'))


    def test_can_tag_old_files(self):
        target = os.path.join(self.datapath, 'prosperpina-old.ly')
        header = shutil.copy(target, '.')
        today = date.today()
        mupub.tag(header, 0, False)
        htable = mupub.LYLoader().load(header)
        self.assertTrue('footer' in htable, 'Footer should be in table')
        mod_date,_ = mupub.core.id_from_footer(htable['footer'])
        self.assertEqual(today, mod_date, 'date in footer should match today()')
        self.assertTrue('license' in htable, 'Copyright tag not processed')


    def test_unquoted(self):
        target = os.path.join(self.datapath, 'unquoted-header.ly')
        header = shutil.copy(target, '.')
        today = date.today()
        mupub.tag(header, 0, False)
        htable = mupub.LYLoader().load(header)
        self.assertTrue('mytagline' in htable, 'mytagline should be in table')
        self.assertTrue('subtitle' in htable, 'subtitle should be in table')


    def test_pd_subs_correctly(self):
        target = os.path.join(self.datapath, 'pd-test.ly')
        header = shutil.copy(target, '.')
        today = date.today()
        mupub.tag(header, 0, False)
        htable = mupub.LYLoader().load(header)
        self.assertTrue('copyright' in htable)
        self.assertTrue(htable['copyright'].find('Placed in') > 0)
