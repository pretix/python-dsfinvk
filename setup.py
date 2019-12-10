import sys
from codecs import open
from os import path

from dsfinvk import version
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

try:
    # Get the long description from the relevant file
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:  # noqa
    long_description = ''

setup(
    name='dsfinvk',
    version=version,
    description='Digitale Schnittstelle der Finanzverwaltung fürKassensysteme',
    long_description=long_description,
    url='https://github.com/pretix/python-dsfinvk',
    author='Raphael Michel',
    author_email='support@pretix.eu',
    license='Apache License',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='germany fiscal export',
    install_requires=[
        'pytz',
    ],
    packages=find_packages(include=['dsfinvk', 'dsfinvk.*']),
    include_package_data=True,
)
