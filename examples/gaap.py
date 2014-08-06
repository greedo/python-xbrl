from parser import XBRLParser, GAAP, GAAPSerializer

# Parse an incoming XBRL file
xbrl = XBRLParser.parse(file("sam-20131228.xml"))

# Parse just the GAAP data from the xbrl object
gaap_obj = XBRLParser.parseGAAP(xbrl)

# Serialize the GAAP data
serialized = GAAPSerializer(gaap_obj)

# Print out the serialized GAAP data
print serialized.data
