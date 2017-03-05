"""Utilities for testing.
"""

import os
from unittest import TestCase
import logging
import sqlite3

TEST_DATA = 'data'
PREFIX = os.path.join(os.path.dirname(__file__), TEST_DATA, 'mu', 'ftp')

_TEST_DB = {
    'instrument': ['Guitar', 'Piano',],
    'style': ['Classical', 'Romantic',],
    'composer': ['SorF', 'AguadoD', 'GiuilianiM',],
    'license': ['Creative Commons Attribution 3.0',
                'Creative Commons Attribution 4.0', ],
}

def getTestDB():
    conn = sqlite3.connect(':memory:')
    for k in _TEST_DB.keys():
        conn.execute('create table {0} ({1} text primary key)'
                     .format(k+'s', k))
        for attribute in _TEST_DB[k]:
            conn.execute('insert into {0} ({1}) values (?)'
                         .format(k+'s', k), (attribute,))
    return conn

    
class LogThisTestCase(type):
    def __new__(cls, name, bases, dct):
        # if the TestCase already provides setUp, wrap it
        if 'setUp' in dct:
            setUp = dct['setUp']
        else:
            setUp = lambda self: None

        def wrappedSetUp(self):
            # for hdlr in self.logger.handlers:
            #    self.logger.removeHandler(hdlr)
            self.hdlr = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(self.hdlr)
            setUp(self)
        dct['setUp'] = wrappedSetUp

        # same for tearDown
        if 'tearDown' in dct:
            tearDown = dct['tearDown']
        else:
            tearDown = lambda self: None

        def wrappedTearDown(self):
            tearDown(self)
            self.logger.removeHandler(self.hdlr)
        dct['tearDown'] = wrappedTearDown

        # return the class instance with the replaced setUp/tearDown
        return type.__new__(cls, name, bases, dct)


class LoggedTestCase(TestCase):
    __metaclass__ = LogThisTestCase
    logger = logging.getLogger("unittestLogger")
    logger.setLevel(logging.DEBUG) # or whatever you prefer


class BasicUtils(TestCase):

    def setUpClass(cls):
        self.cur_cwd = os.getcwd()
        os.chdir(os.path.join(PREFIX, 'SorF', 'O5', 'sor-op5-5'))

    def tearDownClass(cls):
        os.chdir(self.cur_cwd)

    def test_resolve(self):
        base, infile = mupub.utils.resolve_input('sor-op5-5.ly')
        self.assertEqual(infile, 'sor-op5-5.ly')
        self.assertEqual(base, 'sor-op5-5')

        
