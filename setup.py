import os
from setuptools import setup, find_packages

from decorest import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = []

setup(
    name="decorest",
    version=".".join(map(str, __version__)),
    description=
        "`decorest` library provides an easy to use declarative REST API " \
        "client interface, where definition of the API methods using " \
        "decorators automatically gives a working REST client with no " \
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
