import re
import sys

from setuptools import setup, find_packages

# Read the version from __init__ to avoid importing python-xbrl while installing.
# This lets the install work when the user does not have BeautifulSoup
# installed.
VERSION = re.search(r"__version__ = '(.*?)'",
                    open("python-xbrl/__init__.py").read()).group(1)

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

setup_params = dict(
    name='python-xbrl',
    version=VERSION,
    author='Joe Cabrera',
    author_email='jcabrera@eminorlabs.com',
    keywords='xbrl, Financial, Accounting, file formats',
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 1",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
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
    url='https://github.com/greedo/python-xbrl/',
    license='Apache License',
    description='library for parsing xbrl documents providing output as both a basic model object and serialized objects',
    long_description=open("./README", "r").read(),
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    test_suite='tests',
    )

if __name__ == '__main__':
    setup(**setup_params)
