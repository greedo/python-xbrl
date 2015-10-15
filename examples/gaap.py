#! /usr/bin/env python
# encoding: utf-8

from xbrl import XBRLParser, GAAP, GAAPSerializer

xbrl_parser = XBRLParser(precision=0)

# Parse an incoming XBRL file
xbrl = xbrl_parser.parse(file("../tests/sam-20130629.xml"))

# Parse just the GAAP data from the xbrl object
gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                 doc_date="20130629",
                                 doc_type="10-K",
                                 context="current",
                                 ignore_errors=0)

# Serialize the GAAP data
serializer = GAAPSerializer()
result = serializer.dump(gaap_obj)

# Print out the serialized GAAP data
print result
