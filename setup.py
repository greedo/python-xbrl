from distutils.core import setup

setup(
    name='python-xbrl',
    version='1.0.1',
    description='library for parsing xbrl documents',
    author='Joe Cabrera',
    author_email='jcabrera@eminorlabs.com',
    url='https://github.com/greedo/python-xbrl/',
    license='Apache License',
    keywords='xbrl, Financial, Accounting, file formats',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
    ],
    scripts=['python-xbrl/python-xbrl.py'],
)
