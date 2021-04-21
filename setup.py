#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='tango-example',
    version='0.3.6',
    description="",
    long_description=readme + '\n\n',
    author="Matteo Di Carlo",
    author_email='matteo.dicarlo@inaf.it',
    url='https://github.com/ska-telescope/tango-example',
    packages=find_packages(),
    include_package_data=True,
    license="BSD license",
    zip_safe=False,
    keywords='ska_python_skeleton',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    install_requires=['pytango'],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort']
    }
)