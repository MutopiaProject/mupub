import os
from unittest import TestCase
import ruamel.yaml as yaml
import mupub.config

BASIC_CONFIG = """\
%YAML 1.2
---
# a comment
mutopia:
  # and indented comment
  github_repo: my-repo
  local_repo: local-stuff
"""

LIST_CONFIG = """\
%YAML 1.2
---
version:
  - 2.19.47
  - 2.18.2
  - 2.14.2
"""

HERE = os.path.dirname(__file__)
BASIC_CONFIG_FNM = os.path.join(HERE, 'config_basic.yml')

class ConfigTest(TestCase):
    """Configuration tests"""

    @classmethod
    def setUpClass(cls):
        with open(BASIC_CONFIG_FNM, 'w') as base_config:
            base_config.write(BASIC_CONFIG)


    @classmethod
    def tearDownClass(cls):
        pass


    def test_list_config(self):
        """list configuration tests"""
        list_conf = yaml.load(LIST_CONFIG, Loader=yaml.Loader)
        self.assertEqual(len(list_conf['version']), 3)


    def test_iterate(self):
        """Iterating configuration entries"""
        mu_conf = yaml.load(BASIC_CONFIG, Loader=yaml.Loader)
        count = 0
        for item in mu_conf['mutopia']:
            count += 1
        self.assertEqual(count, 2)


    def test_basic_config(self):
        """basic configuration tests"""
        config = mupub.config.load(BASIC_CONFIG_FNM)
        mupub.config.CONFIG_DICT = config

        config_backup = BASIC_CONFIG_FNM + '~'
        config['mutopia']['newthing'] = 'ta-da'
        mupub.config.save(BASIC_CONFIG_FNM)
        self.assertTrue(os.path.exists(config_backup))

        # make sure it saved
        saved_config = mupub.config.load(BASIC_CONFIG_FNM)
        self.assertTrue('newthing' in saved_config['mutopia'])

        # can't just add a new top element
        with self.assertRaises(KeyError):
            saved_config['test']['foo'] = 'bar'

        # ... must create it first
        saved_config['test'] = dict()
        saved_config['test']['foo'] = 'bar'
