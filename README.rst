decorest - decorator based REST client for Python
#################################################

.. image::	https://img.shields.io/travis/bkryza/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

.. image:: https://img.shields.io/pypi/v/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

.. image:: https://img.shields.io/pypi/l/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

.. image:: https://img.shields.io/pypi/pyversions/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

Declarative, decorator-based REST client for Python.

.. contents::

Overview
========

`decorest` library provides an easy to use declarative REST API client interface,
where definition of the API methods using decorators automatically gives
a working REST client with no additional code. In practice the library provides
only an interface to interact with REST services - the actual work is done
underneath by the requests_ library.

For example:

.. code-block:: python

    from decorest import RestClient, GET

    class DogClient(RestClient):
        def __init__(self, endpoint):
            super(DogClient, self).__init__(endpoint)

        @GET('api/breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

    client = DogClient('https://dog.ceo/dog-api')

    print(str(client.list_subbreeds('hound'))


Installation
============

Using pip:

.. code-block:: bash

    pip install decorest

Usage
=====

Basics
------

For most typical cases the usage should be straightforward. Simply create a
sublcass of `decorest.RestClient` and define methods, which will perform calls
to the actual REST service. You can declare how each function should actually
make the request to the service solely using decorators attached to the
method definition. The method itself is not expected to have any implementation
except maybe for a docstring.

After the your client class definition is ready, simply create an instance
of it with the base endpoint and exec

For more information checkout the examples in tests.

Decorators
----------

@GET, @PUT, @POST, @PATCH, @UPDATE, @DELETE, @HEAD, @OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Marks the request with a specific HTTP method and the path relative to
endpoint provided as argument. The path can contain variables enclosed
in curly brackets, e.g.:

.. code-block:: python

        @GET('api/breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator applies only to methods.

@query
~~~~~~

Adds a query key-value pair to the request. URL encoding will be applied to
the value using `urlencode`, e.g.:

.. code-block:: python

        @GET('api/breed/{breed_name}/list')
        @query('limit', 100)
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be added to methods as well as the client class, however
in the latter case it will be added to every method request in that class.

@header
~~~~~~~

Adds a header key-value pair to the request, e.g.:

.. code-block:: python

        @GET('api/breed/{breed_name}/list')
        @query('limit', 100)
        @header('accept', 'application/json')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be added to both methods and client class. The class level
decorators will be added to every method and can be overriden using method
level decorators.

@body
~~~~~

Body decorator enables to specify which of the method params should provide
the body content to the request, e.g.:

.. code-block:: python

    @POST('pet')
    @header('content-type', 'application/json')
    @header('accept', 'application/json')
    @body('pet')
    def add_pet(self, pet):
        """Add a new pet to the store"""


@auth
~~~~~

Allows to specify the authentication method to be used for the requests.
It accepts any valid subclass of `requests.auth.AuthBase`.

.. code-block:: python

        @GET('api/breed/{breed_name}/list')
        @query('limit', 100)
        @header('accept', 'application/json')
        @auth(HTTPBasicAuth('user', 'password'))
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

When added to the client class it will be used for every method call,
unless specific auth decorator is specified for that method.


@on
~~~

By default the request method will not return requests_ response object
but the response will depend on the content type of the reponse.

In case the HTTP request succeeds the following results are expected:

- `response.json()` if the content type of response is JSON
- `response.content` if the content type is binary
- `response.text` otherwise

In case the request fails, response.raise_for_status() is called and
should be handled in the code.

In case another behavior is required, custom handlers can be provided
for each method using lambdas or functions. The provided handler is
expected to take only a single argument, which is the requests_ response
object, e.g.:

.. code-block:: python

        @GET('api/breed/{breed_name}/list')
        @query('limit', 100)
        @header('accept', 'application/json')
        @auth(HTTPBasicAuth('user', 'password'))
        @on(200, lambda r: r.json())
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be applied to both methods and classes, however when
applied to a class the handler will be called for method which receives
the provided status code.

Sessions [TODO]
---------------

Based on the functionality provided by requests_ library in the form of
session objects, sessions can be used instead of making a separate request
on each method call thus significantly improving the performance of the
client in case multiple reponses are peformed.

To start and stop the session, simply call `start_session` on the client
instance. Only the first method after this call will create the session,
consecutive calls will reuse it until `stop_session` method is called on
the client instance.

.. code-block:: python

        client.start_session()
        client.list_subbreeds('hound')
        client.list_subbreeds('husky')
        client.stop_session()

License
=======

Copyright 2018 Bartosz Kryza <bkryza@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. _tests: https://github.com/bkryza/decorest/tests
.. _requests: https://github.com/requests/requests
