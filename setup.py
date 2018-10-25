#!/usr/bin/env python

import subprocess

from setuptools import setup, Command


# -----------------------------------------------------------------------------

def read(fname):
    with open(fname) as infile:
        return infile.read()


def system(command):
    class SystemCommand(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            subprocess.check_call(command, shell=True)

    return SystemCommand


# -----------------------------------------------------------------------------

setup(
    name='marshmallow-oneofschema',
    version='2.0.0b1',
    description='Marshmallow multiplexing schema',
    long_description=read('README.rst'),
    author='Maxim Kulkin',
    author_email='maxim.kulkin@gmail.com',
    maintainer='Alex Rothberg',
    maintainer_email='agrothberg@gmail.com',
    url='https://github.com/marshmallow-code/marshmallow-oneofschema',
    packages=['marshmallow_oneofschema'],
    license=read('LICENSE'),
    keywords=['serialization', 'deserialization', 'json',
              'marshal', 'marshalling', 'schema', 'validation',
              'multiplexing', 'demultiplexing', 'polymorphic'],
    install_requires=['marshmallow>=3.0.0b12,<=3.0.0b19'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    cmdclass={
        'clean': system('rm -rf build dist *.egg-info'),
        'package': system('python setup.py sdist bdist_wheel'),
        'publish': system('twine upload dist/*'),
        'release': system('python setup.py clean package publish'),
    },
)
