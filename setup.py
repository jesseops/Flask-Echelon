#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'enum34'
]

test_requirements = [
    'pytest',
    'flask',
    'pymongo'
]

setup(
    name='flask_echelon',
    version='0.1.0',
    description="Flask-Echelon provides a simple, hierarchical permissions tool. Ideal for Blueprints.",
    long_description=readme + '\n\n' + history,
    author="Jesse Roberts",
    author_email='jesse@jesseops.net',
    url='https://github.com/jesseops/flask_echelon',
    packages=[
        'flask_echelon',
    ],
    package_dir={'flask_echelon':
                 'flask_echelon'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='flask_echelon',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
