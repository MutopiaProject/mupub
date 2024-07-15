import unittest
import urllib.parse
from bs4 import BeautifulSoup
import re
import requests
import mupub


class BSTest(unittest.TestCase):
    """Beautiful Soup tests"""

    @unittest.skip("Too many external dependencies, requires internet.")
    def test_latest_additions(self):
        table = mupub.CONFIG_DICT["common"]
        url = urllib.parse.urljoin(table["mutopia_url"], "latestadditions.html")
        req = requests.get(url)
        latest_page = BeautifulSoup(req.content, "html.parser")
        # can we find that title?
        self.assertEqual(latest_page.h2.contents[0], "Latest Additions")
        # better?
        plist = latest_page.find_all(href=re.compile("piece-info\.cgi"))
        self.assertEqual(len(plist), 25)
        idlist = []
        for ref in plist:
            href = urllib.parse.urlparse(ref.get("href"))
            if href.query:
                for q in urllib.parse.parse_qsl(href.query):
                    if q[0] == "id":
                        idlist.append(q[1])
        print(max(idlist))
