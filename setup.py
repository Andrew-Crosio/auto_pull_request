#!/usr/bin/env python
# coding=utf-8
"""Setup egg"""
from distutils.core import setup


setup(
    name='auto_pull_request',
    version='0.2',
    description='Auto-pull request tool',
    author='Andrew Crosio',
    author_email='andrew.crosio@gmail.com',
    url='https://github.com/Andrew-Crosio/auto_pull_request',
    packages=['auto_pull_request'],
    install_requires=[
        'requests',
        'GitPython',
        'Django',
        'pep8',
        'lxml',
        'django-debug-toolbar>=0.8.4',
    ],
    dependency_links=[
        'https://github.com/Andrew-Crosio/diff-coverage/tarball/master#egg=diffcoverage'
    ]
)
