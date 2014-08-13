import os
import sys
sys.path.insert(0, os.path.abspath('python-xbrl'))
import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from parser import soup_maker, XBRLParser, XBRLParserException

class TestParse():

    def testEmptyFile(self):
        fh = StringIO()
        assert XBRLParser.parse(fh) is None

