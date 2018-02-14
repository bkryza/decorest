# -*- coding: utf-8 -*-
#
# Copyright 2018 Bartosz Kryza <bkryza@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""decorest - decorator heavy REST client library for Python."""


import os

from decorest import __version__

from setuptools import find_packages, setup


def read(fname):
    """Read description from local file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = []

setup(
    name="decorest",
    version=".".join(map(str, __version__)),
    description="`decorest` library provides an easy to use declarative "
    "REST API client interface, where definition of the API methods using "
    "decorators automatically gives a working REST client with no "
    "additional code.",
    long_description=read('README.rst'),
    url='https://github.com/bkryza/decorest',
    license='Apache 2.0',
    author='Bartek Kryza',
    author_email='bkryza@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=['requests', 'six'],
    tests_require=['pytest', 'tox', 'tox-docker']
)
