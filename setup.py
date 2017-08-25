#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# Hack to use requirements.txt to populate install_requires
try:
    with open('./requirements.txt', 'r') as reqs:
        lines = reqs.readlines()
        __requirements__ = [x.strip() for x in lines if not x.startswith(('--', 'git', '-e', '#'))]
        __dependency_links__ = [x.split()[-1] for x in lines if x.startswith('--find-links')]
except IOError:
    raise Exception("Unable to read from requirements.txt to generate install_requires")

__test_requirements__ = [
    'flake8',
    'pytest',
    'pytest-xdist',
    'pytest-cov',
    'tox',
    'coverage',
    'sphinx'
]

setup(
    name='flask_echelon',
    version='0.1.0',
    description="Flask-Echelon provides a simple, hierarchical permissions tool. Ideal for Blueprints.",
    long_description=readme + '\n\n' + history,
    author="Jesse Roberts",
    author_email='jesse@jesseops.net',
    url='https://github.com/jesseops/flask_echelon',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=__requirements__,
    license="MIT license",
    zip_safe=False,
    keywords='flask_echelon',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=__test_requirements__,
    setup_requires=['pytest-runner']
)
