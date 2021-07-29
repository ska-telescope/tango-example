#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open('README.md') as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name='ska-tango-examples',
    version='0.4.16',
    description="",
    long_description=readme + '\n\n',
    author="Matteo Di Carlo",
    author_email='matteo.dicarlo@inaf.it',
    url='https://github.com/ska-telescope/ska-tango-examples',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    license="BSD license",
    zip_safe=False,
    keywords='ska tango examples',
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
    install_requires=[
        "ska-tango-base >= 0.9.1",
        "pytango >= 9.3.3",
        "jsonschema >= 3.2.0",
        "fire",
        "requests",
    ],
    platforms=["OS Independent"],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort']
    }
)