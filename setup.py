#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Most fault tolerant protocols (including RAFT, PBFT, Zyzzyva, Q/U)
don't guarantee good performance when there are Byzantine faults. Even
the so-called "robust" BFT protocols (like UpRight, RBFT, Prime,
Spinning, and Stellar) have various hard-coded timeout parameters, and
can only guarantee performance when the network behaves approximately as
expected - hence they are best suited to well-controlled settings like
corporate data centers.

HoneyBadgerBFT is fault tolerance for the wild wild wide-area-network.
HoneyBadger nodes can even stay hidden behind anonymizing relays like
Tor, and the purely-asynchronous protocol will make progress at whatever
rate the network supports.

"""


# 在Makefile文件中会执行本文件
from setuptools import setup


install_requires = [
    'gevent',
    'gmpy2',
    'pysocks',
    'pycrypto',
    'ecdsa',
    'zfec>=1.5.0',
    'gipc',
    'coincurve',
]

tests_require = [
    'coverage',
    'flake8',
    'logutils',
    'pytest',
    'pytest-cov',
    'pytest-mock',
    'pytest-sugar',
    'nose2',
]

dev_require = [
    'ipdb',
    'ipython',
]

docs_require = [
    'Sphinx',
    'sphinx-autobuild',
    'sphinx_rtd_theme',
]

setup(
    name='HoneyBadgerBFT',
    version='0.1.0',
    description='The HoneyBadger of BFT Protocols',
    long_description=__doc__,
    author="Andrew Miller et al",
    url='https://github.com/amiller/HoneyBadgerBFT',
    packages=['honeybadgerbft'],
    package_dir={'honeybadgerbft': 'honeybadgerbft'},
    include_package_data=True,
    install_requires=install_requires,
    license='CRAPL',
    zip_safe=False,
    keywords='distributed systems, cryptography, byzantine fault tolerance',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.10',
    test_suite='tests',
    extras_require={
        'test': tests_require,
        'dev': dev_require + tests_require + docs_require,
        'docs': docs_require,
    },

)
