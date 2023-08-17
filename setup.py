# -*- coding: utf-8 -*-
#
# Copyright 2018-2023 Bartosz Kryza <bkryza@gmail.com>
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
import pathlib
import re

from setuptools import find_packages, setup

# Determine the dependencies based on preferred backend
# (i.e. requests[default] vs httpx)
backend_deps = ['requests', 'requests-toolbelt']
backend_env = os.environ.get("DECOREST_BACKEND", None)
if backend_env:
    if backend_env not in ['requests', 'httpx']:
        raise ValueError(f'Invalid backend provided in '
                         f'DECOREST_BACKEND: {backend_env}')
    if backend_env == 'httpx':
        backend_deps = ['httpx']


def get_version():
    """Return package version as listed in `__version__` in `init.py`."""
    init_path = \
        str(pathlib.Path(pathlib.Path(__file__).parent.absolute(),
                         'decorest/__init__.py'))
    init_py = open(init_path).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version()


def read(fname):
    """Read description from local file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = []

setup(
    name="decorest",
    version=version,
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
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    install_requires=backend_deps,
    tests_require=['pytest', 'tox', 'tox-docker']
)