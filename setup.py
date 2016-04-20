#!/usr/bin/env python
"""
A setuptools based setup module.
"""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'VERSION.txt'), encoding='utf-8') as version_file:
    vf_contents = version_file.read().strip().split("\n")
    version = vf_contents[0]
    development_status = vf_contents[1:]

setup(
    name='TicTacTio',
    version=version,
    description='A TicTacToe project used as educational tool to learn various topics.',
    long_description=long_description,
    url='https://github.com/DevelopForLizardz/TicTacTio.git',
    author='Ryan Drew',
    author_email='developforlizardz@thedrews.org',
    license='MIT',
    classifiers=[
        'Development Status ::' + development_status[0] + ' - ' + development_status[1],
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='TicTacToe machine learning ml genetic algorithms ga neural networks multiplayer pygame',
    packages=['tttio', 'tests'],
    install_requires=['nose2', 'numpy'],
    test_suite='nose2.collector.collector',
    include_package_data=True
)
