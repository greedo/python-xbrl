**python-xbrl** is a library for parsing [xbrl](http://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html) documents providing output as both a basic model object and serialized objects
thur [marshmallow](http://marshmallow.readthedocs.org/en/latest/) for rendering into standards formats like JSON or HTTP API

Usage
-----

If you really want to become familiar with this library, read
the docstrings in the code.

Initialization
--------------

To start using the library, first import the `XBRLParser`

    from parser import XBRLParser

Simple Parsing Workflow
-----------------------

First parse the incoming XRBL file into a new XBRL basic object

    xbrl = XBRLParser.parse(file("sam-20131228.xml"))
    
Then you can parse the document using different parser

    gaap_obj = XBRLParser.parseGAAP(xbrl)
    
Now we have a GAAP model object that has the GAAP parsed elements from the document.

You can serialize the GAAP model object into a serialized object acceptable for rending into a standard format such as JSON or HTTP API.

    serialized = GAAPSerializer(gaap_obj)
    
You can also just view the data in the serialized object

    print serialized.data
    
You can apply various parsers to the base `XBRLParser` object to get different data than just GAAP data from the document. In addition as expected you can also create different serialized objects on the resulting parsed data object. 

Testing
-------

To run the unit tests, you need pytest

    pip install pytest

Once you have that, `cd` into the root directory of this repo and

    py.test --tb=line -vs

