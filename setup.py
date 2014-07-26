#!/usr/bin/env python

PROJECT = 'mock-s3'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

from setuptools import setup, find_packages

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='A python port of Fake-S3.',
    long_description=long_description,

    author='Joe Server',
    author_email='joe@jserver.io',

    url='https://github.com/jserver/mock-s3',
    download_url='https://github.com/jserver/mock-s3/tarball/master',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'mock_s3 = mock_s3.main:main'
            ],
        },

    zip_safe=False,
)
