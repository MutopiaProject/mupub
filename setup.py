from setuptools import setup
from codecs import open
from os import path

import mupub

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = mupub.__title__,
    version = mupub.__version__,
    description = mupub.__summary__,
    long_description = long_description,
    url = mupub.__uri__,
    author = mupub.__author__,
    author_email = mupub.__author_email__,
    license = mupub.__license__,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Topic :: Database :: Front-Ends',
        'Topic :: Documentation :: Sphinx',
        'Topic :: ',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages = ['mupub', 'mupub.commands'],
    entry_points = {
        'mupub.registered_commands': [
            'check = mupub.commands.check:main',
        ],
        'console_scripts': [
            'mupub = mupub.__main__:main',
        ],
    },
    install_requires = [
        'requests >= 2.11.1',
        'rdflib >= 4.2.1',
    ],
)
