import os
import sys
sys.path.insert(0, os.path.abspath('python-xbrl'))
import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from parser import soup_maker, XBRLParser, XBRLParserException

def testEmptyFile():
    xbrl_parser = XBRLParser()
    file_to_parse = "tests/nothing.xml"
    with pytest.raises(XBRLParserException):
        xbrl_parser.parse(file(file_to_parse))
