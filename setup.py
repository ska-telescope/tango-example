#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='ska-skeleton',
    version='0.0.0',
    description="",
    long_description=readme + '\n\n',
    author="Your Name",
    author_email='your.email@mail.com',
    url='https://github.com/ska-telescope/ska-skeleton',
    packages=[
        'ska-skeleton',
    ],
    package_dir={'ska-skeleton':
                 'ska-skeleton'},
    include_package_data=True,
    license="BSD license",
    zip_safe=False,
    keywords='ska-skeleton',
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
    install_requires=[],  # FIXME: add your package's dependencies to this list
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'recommonmark'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort'],
    }
)
