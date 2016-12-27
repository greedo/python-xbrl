try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import os

long_description = 'library for parsing xbrl documents'
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()

setup(
    name='python-xbrl',
    version='1.1.1',
    description='library for parsing xbrl documents',
    author='Joe Cabrera',
    author_email='jcabrera@eminorlabs.com',
    url='https://github.com/greedo/python-xbrl/',
    license='Apache License',
    keywords='xbrl, Financial, Accounting, file formats',
    packages=['xbrl'],
    install_requires=['pytest', 'pep8', 'marshmallow',
    'beautifulsoup4', 'ordereddict', 'lxml', 'six'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
    ],
    long_description=long_description
)
