|PyPI version| |Travis-CI| |license|

**python-xbrl** is a library for parsing
`xbrl <http://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31+corrected-errata-2013-02-20.html>`__
documents providing output as both a basic model object and serialized
objects thur
`marshmallow <http://marshmallow.readthedocs.org/en/latest/>`__ for
rendering into standards formats like JSON or HTTP API

Installation
------------

The easiest way to install python-xbrl is with pip

::

    pip install python-xbrl

Or install the latest dev version from github (or replace `@master` with a 
`release vergitsion like @v1.1.0 <https://github.com/greedo/python-xbrl/releases>`__)

::
    
    pip install git+https://github.com/greedo/python-xbrl.git@master
    
Or

::

    git clone https://github.com/greedo/python-xbrl.git

Or

Copy the python-xbrl directory into your python path. Zip 
`here <https://github.com/greedo/python-xbrl/archive/master.zip>`__
    
Made sure your **sys.path** is correct.

Requirements
------------

- Python >= 2.6 or >= 3.3

python-xbrl relies on `beautifulsoup4 <http://beautiful-soup-4.readthedocs.org/en/latest/>`__ 
which sits on top of the python XML parser `lxml <http://lxml.de/>`__. It also requires 
`marshmallow <http://marshmallow.readthedocs.org/en/latest/>`__ for serializing objects.
For more details see `requirements.txt <https://github.com/greedo/python-xbrl/blob/master/requirements.txt>`__

For PyPI support it is recommended you use `https://github.com/amauryfa/lxml <https://github.com/amauryfa/lxml>`__ for lxml as this is a fork that uses cffi instead of the python capi.

Initialization
--------------

To start using the library, first import the ``XBRLParser``

::

    from xbrl import XBRLParser, GAAP, GAAPSerializer

Simple Parsing Workflow
-----------------------

First parse the incoming XRBL file into a new ``XBRL`` basic object

::

    xbrl_parser = XBRLParser()
    xbrl = xbrl_parser.parse(file("sam-20131228.xml"))

Then you can parse the document using different parsers

::

    gaap_obj = xbrl_parser.parseGAAP(xbrl, doc_date="20131228", context="current", ignore_errors=0)

Now we have a ``GAAP`` model object that has the GAAP parsed elements
from the document.

This model object supports the several different features including:

-  ``context`` current, year, and instant contexts are supported. If available you can also get previous quarter information by number of days from doc date. Example: 90, 180, etc.
-  Error handling. ``0`` raise exception for all parsing errors and halt parsing, ``1`` Supress all parsing errors and continue parsing, ``2`` Log all parsing errors and continue parsing 

You can serialize the GAAP model object into a serialized object
acceptable for rending into a standard format such as JSON or HTTP API.

::

    serializer = GAAPSerializer()
    result = serializer.dump(gaap_obj)

You can also just view the data in the serialized object

::

    print result.data

You can apply various parsers to the base ``XBRLParser`` object to get
different data than just GAAP data from the document. In addition as
expected you can also create different serialized objects on the
resulting parsed data object.


**Extracting DEI Data**

::
    
    dei_obj = xbrl_parser.parseDEI(xbrl)
    serializer = DEISerializer()
    result = serializer.dump(dei_obj)
    
**Extracting Custom Data**

::
    
    custom_obj = xbrl_parser.parseCustom(xbrl)
    print custom_obj()

Testing
-------

To run the unit tests, you need pytest

::

    pip install pytest

Once you have that, ``cd`` into the root directory of this repo and

::

    py.test --tb=line -vs
    
Bugs
-------

For any bugs you encounter please open a Github
`issue <https://github.com/greedo/python-xbrl/issues>`__

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug. 
#. If you feel uncomfortable or uncertain about an issue or your changes, feel free to email @greedo and he will happily help you via email, Skype, remote pairing or whatever you are comfortable with.
#. Fork `the repository <https://github.com/greedo/python-xbrl>`__  on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to `AUTHORS <https://github.com/greedo/python-xbrl/blob/master/AUTHORS.rst>`__.


License
-------

::

    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the license.

.. |PyPI version| image:: https://badge.fury.io/py/python-xbrl.png?style=flat
   :target: http://badge.fury.io/py/python-xbrl
.. |Travis-CI| image:: https://travis-ci.org/greedo/python-xbrl.png?branch=master
   :target: https://travis-ci.org/greedo/python-xbrl
.. |license| image:: https://img.shields.io/pypi/l/python-xbrl.svg?style=flat
    :target: https://pypi.python.org/pypi/python-xbrl

