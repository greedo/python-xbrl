#! /usr/bin/env python
# encoding: utf-8

from __future__ import print_function

from xbrl import XBRLParser, GAAP, GAAPSerializer, DEISerializer

xbrl_parser = XBRLParser(0)

# Parse an incoming XBRL file
file_to_parse = "../tests/sam-20130629.xml"

xbrl = xbrl_parser.parse(file_to_parse)

# Parse just the GAAP data from the xbrl object
gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                 doc_date="20131228",
                                 context="current",
                                 ignore_errors=0)

# Serialize the GAAP data
serializer = GAAPSerializer()
result = serializer.dump(gaap_obj)

# Print out the serialized GAAP data
print(result.data)


# Parse just the DEI data from the xbrl object
dei_obj = xbrl_parser.parseDEI(xbrl)

# Serialize the DEI data
serializer = DEISerializer()
result = serializer.dump(dei_obj)

# Print out the serialized DEI data
print(result.data)

# Parse the custom data from the xbrl object
data_obj = xbrl_parser.parseCustom(xbrl)

# Print out the custom data
print(data_obj())
