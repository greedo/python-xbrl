from __future__ import print_function

from xbrl import XBRLParser, GAAP, GAAPSerializer

xbrl_parser = XBRLParser(0)

# Parse an incoming XBRL file
#xbrl = xbrl_parser.parse(file("../tests/sam-20131228.xml"))
xbrl = xbrl_parser.parse(file("sam-20140927.xml"))

# Parse just the GAAP data from the xbrl object
gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                 doc_date="20140927",
                                 doc_type="10-K",
                                 context="current",
                                 ignore_errors=0)

# Serialize the GAAP data
serialized = GAAPSerializer(gaap_obj)

# Print out the serialized GAAP data
#print(serialized.data)

for k, v in serialized.data.items():
    print(v)
    with open('d793237d10q.htm', 'r') as f:
        print f.read()
