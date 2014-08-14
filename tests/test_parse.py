import os
import sys
sys.path.insert(0, os.path.abspath('python-xbrl'))
import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from parser import soup_maker, XBRLParser, XBRLParserException


class TestParse(TestCase):

    def testEmptyFile(self):
        fh = StringIO()
        assert XBRLParser.parse(fh) is None

        # def test_parse(self):
        # make sure the shuffled sequence does not lose any elements
