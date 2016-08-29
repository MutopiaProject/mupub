"""Core tests for mut
"""

import os.path
import datetime
from unittest import TestCase
import mupub

TEST_DATA = 'data'

class CoreTest(TestCase):
    """Core testing"""

    def test_big_foot(self):
        """Footer parsing"""
        header = mupub.Header(mupub.LYLoader())
        path = os.path.join(os.path.dirname(__file__), TEST_DATA, 'big-foot.ly')
        header.load_table(path)
        (pub_date, mu_id) = mupub.id_from_footer(header.get_value('footer'))
        self.assertEqual(pub_date, datetime.date(2016,6,6))
        self.assertEqual(mu_id, 999999)


    def test_odd_footers(self):
        """Odd footers handling"""
        # empty footer
        with self.assertRaises(ValueError):
            (pub, m_id) = mupub.id_from_footer(None)

        # badly formed id
        with self.assertRaises(ValueError):
            (pub, m_id) = mupub.id_from_footer('Muto-10/11/12-99')

        # badly formed date
        with self.assertRaises(ValueError):
            mupub.id_from_footer('Mutopia-2016/13/1-999')
