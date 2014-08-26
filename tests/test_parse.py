import os
import sys
sys.path.insert(0, os.path.abspath('python-xbrl'))
import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from parser import soup_maker, XBRLParser, XBRLParserException, GAAP, GAAPSerializer

def test_parse_empty_file():
    xbrl_parser = XBRLParser()
    file_to_parse = "tests/nothing.xml"
    with pytest.raises(XBRLParserException):
        xbrl_parser.parse(file(file_to_parse))

def test_parse_GAAP10Q():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20130629.xml"
    xbrl = xbrl_parser.parse(file(file_to_parse))
    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date=str(file_to_parse.split("-")[1].split(".")[0][:4] + file_to_parse.split("-")[1].split(".")[0][4:6] + file_to_parse.split("-")[1].split(".")[0][6:8]), doc_type="10-Q")

    serialized = GAAPSerializer(gaap_obj)
    assert serialized.data['stockholders_equity'] == 253536.0
    assert serialized.data['net_income_loss'] == 19715.0

def test_parse_GAAP10K():

    xbrl_parser = XBRLParser(0)
    file_to_parse = "tests/sam-20131228.xml"
    xbrl = xbrl_parser.parse(file(file_to_parse))
    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date=str(file_to_parse.split("-")[1].split(".")[0][:4] + file_to_parse.split("-")[1].split(".")[0][4:6] + file_to_parse.split("-")[1].split(".")[0][6:8]), doc_type="10-K")

    serialized = GAAPSerializer(gaap_obj)
    assert serialized.data['stockholders_equity'] == 302085.0
    assert serialized.data['net_income_loss'] == 70392.0
