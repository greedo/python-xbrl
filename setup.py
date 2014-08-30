import re
import sys

from setuptools import setup, find_packages
#from distutils.core import setup

# Read the version from __init__ to avoid importing python-xbrl while installing.
# This lets the install work when the user does not have BeautifulSoup
# installed.
#VERSION = re.search(r"__version__ = '(.*?)'",
#                    open("python-xbrl/__init__.py").read()).group(1)

# Use BeautifulSoup 3 on Python 2.5 and earlier and BeautifulSoup 4 otherwise
if sys.version_info < (2, 6):
    REQUIRES = [
        "beautifulSoup>=3.0",
    ]
else:
    REQUIRES = [
        "beautifulsoup4"
    ]

if sys.version_info < (2, 7):
    REQUIRES.extend([
        "ordereddict>=1.1",
        "marshmallow>=0.7",
    ])

setup = dict(
    name='python-xbrl',
    version='1.0.1',
    author='Joe Cabrera',
    author_email='jcabrera@eminorlabs.com',
    keywords='xbrl, Financial, Accounting, file formats',
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 1",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Topic :: Office/Business :: Financial',
        "License :: OSI Approved :: Apache License",
    ],
    install_requires=[
	'BeautifulSoup',
	're',
	'marshmallow',
	'datetime',
	'pprint'
	],
    scripts=['python-xbrl/parser.py','python-xbrl/gaap.py'],
    packages=find_packages(exclude=['examples', 'tests']),
    url='https://github.com/greedo/python-xbrl/',
    license='Apache License',
    description='library for parsing xbrl documents providing output as both a basic model object and serialized objects',
    long_description=open("./README.md", "r").read(),
    #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    test_suite='tests',
    )
