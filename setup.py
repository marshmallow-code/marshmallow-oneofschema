#!/usr/bin/env python

from setuptools import setup


def read(fname):
    with open(fname) as infile:
        return infile.read()

setup(
    name='marshmallow-oneofschema',
    version='2.0.0b1',
    description='Marshmallow multiplexing schema',
    long_description=read('README.rst'),
    author='Maxim Kulkin',
    author_email='maxim.kulkin@gmail.com',
    url='https://github.com/maximkulkin/marshmallow-oneofschema',
    packages=['marshmallow_oneofschema'],
    license=read('LICENSE'),
    keywords=('serialization', 'deserialization', 'json',
              'marshal', 'marshalling', 'schema', 'validation',
              'multiplexing', 'demultiplexing', 'polymorphic'),
    install_requires=['marshmallow>=3.0.0b12,<=3.0.0b18'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
