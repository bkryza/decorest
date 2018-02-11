.. role:: py(code)
   :language: python

decorest - decorator heavy REST client for Python
#################################################

.. image::	https://img.shields.io/travis/bkryza/decorest.svg
    :target: https://travis-ci.org/bkryza/decorest

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

decorest_ library provides an easy to use declarative REST API client interface,
where definition of the API methods using decorators automatically gives
a working REST client with no additional code. In practice the library provides
only an interface to describe and interact with REST services - the actual work
is done underneath by the requests_ library.

For example:

.. code-block:: python

    from decorest import RestClient, GET

    class DogClient(RestClient):
        def __init__(self, endpoint):
            super(DogClient, self).__init__(endpoint)

        @GET('breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

    client = DogClient('https://dog.ceo/api')

    print(client.list_subbreeds('hound'))


Installation
============

Using pip:

.. code-block:: bash

    pip install decorest

Usage
=====

Basics
------

For most typical cases the usage should be farily straightforward. Simply create a
sublcass of :py:`decorest.RestClient` and define methods, which will perform calls
to the actual REST service. You can declare how each function should actually
make the request to the service solely using decorators attached to the
method definition. The method itself is not expected to have any implementation
except maybe for a docstring.

After your API client class definition is complete, simply create an instance
of it and it's ready to go. This library relies on the functionality provided
by the requests_ library, which means that any valid named argument which
could be passed to a requests_ HTTP call can be also passed to the calls
of the client methods and will be forwarded as is.

For more information checkout the examples in tests.

Decorators
----------

Below is a list of all supported decorators along with short explanation and
examples. Some decorators can be attached to both client class as well as
methods, in which case the class-level decorator is applied to all HTTP methods
in that class. Furthermore, each decorator can be overriden directly during
the method call by providing a named argument with name equal to the decorator
name.


@GET, @PUT, @POST, @PATCH, @UPDATE, @DELETE, @HEAD, @OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Marks the request with a specific HTTP method and the path relative to
endpoint provided as argument. The path can contain variables enclosed
in curly brackets, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

which will be replaced by the arguments from the method definition.
These decorators apply only to methods.

@query
~~~~~~

Adds a query key-value pair to the request. URL encoding will be applied to
the value using :py:`urlencode`, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @query('long_names', 'longNames')
        @query('limit')
        def list_subbreeds(self, breed_name, long_names, limit=100):
            """List all sub-breeds"""

This decorator can take a single string parameter, which determines the name
of the method argument whose value will be added as the query argument value
of the same name.

In case 2 arguments are provided, the second argument determines the actual
query key name, which will be used in the request query (if for some reason
it cannot be the same as the method argument name).

Furthermore, if a default value is provided in a method declaration, it
will be used whenever a value for this argument is not provided during
invocation.

For example, the following invocation of the above method:

.. code-block:: python

    client.list_subbreeds('hound', 1)

will result in the following query:

.. code-block::

    https://dog.ceo/api/breed/hound?longNames=1&limit=100

This decorator can be added to methods as well as the client class, however
in the latter case it will be added to every method request in that class.

@header
~~~~~~~

Adds a header key-value pair to the request, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
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

:py:`@body` decorator can take an optional argument which provides a serialization
handler, which will be invoked automatically before passing the argument as
body content, which can be a simple lambda or a more complex function with some
logic. For example:

.. code-block:: python

    @POST('pet')
    @header('content-type', 'application/json')
    @header('accept', 'application/json')
    @body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet):
        """Add a new pet to the store"""

The above code will automatically stringify the dictionary provided as
value of 'pet' argument using :py:`json.dumps()` function.

@auth
~~~~~

Allows to specify the authentication method to be used for the requests.
It accepts any valid subclass of :py:`requests.auth.AuthBase`.

.. code-block:: python

        @GET('breed/{breed_name}/list')
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

- :py:`response.json()` if the content type of response is JSON
- :py:`response.content` if the content type is binary
- :py:`response.text` otherwise

In case the request fails, :py:`response.raise_for_status()` is called and
should be handled in the code.

In case another behavior is required, custom handlers can be provided
for each method using lambdas or functions. The provided handler is
expected to take only a single argument, which is the requests_ response
object, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @header('accept', 'application/json')
        @auth(HTTPBasicAuth('user', 'password'))
        @on(200, lambda r: r.json())
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be applied to both methods and classes, however when
applied to a class the handler will be called for method which receives
the provided status code.

@content
~~~~~~~~
This decorator is a shortcut for :py:`@header('content-type', ...)`, e.g:

.. code-block:: python

    @POST('pet')
    @content('application/json')
    @header('accept', 'application/json')
    @body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet):
        """Add a new pet to the store"""

@accept
~~~~~~~~
This decorator is a shortcut for :py:`@header('accept', ...)`, e.g:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @content('application/json')
        @accept('application/xml')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

@endpoint
~~~~~~~~
This decorator enables to define a default endpoint for the service,
which then doesn't have to be provided in the client constructor:

.. code-block:: python

        @endpoint('https://dog.ceo/api')
        class DogClient(RestClient):
            """List all sub-breeds"""
            def __init__(self, endpoint=None):
                super(DogClient, self).__init__(endpoint)

The endpoint provided in the client constructor will take precedence
however.


@timeout
~~~~~~~~
Specifies a default timeout value (in seconds) for method or entire API.

.. code-block:: python

        @endpoint('https://dog.ceo/api')
        @timeout(5)
        class DogClient(RestClient):
            """List all sub-breeds"""
            def __init__(self, endpoint=None):
                super(DogClient, self).__init__(endpoint)

Sessions [TODO]
---------------

Based on the functionality provided by requests_ library in the form of
session objects, sessions can be used instead of making a separate request
on each method call thus significantly improving the performance of the
client in case multiple reponses are peformed.

To start and stop the session, simply call :py:`client.start_session()`
on the client instance. Only the first method after this call will create
the session, consecutive calls will reuse it until :py:`client.stop_session()`
method is called on the client instance.

.. code-block:: python

        client.start_session()
        client.list_subbreeds('hound')
        client.list_subbreeds('husky')
        client.stop_session()

Grouping API methods [TODO]
---------------------------

For larger API's it can be useful to be able to split the API definition
into multiple files but still use it from a single instance in the code.
This can be achieved by creating separate client
classes for each group of operations and then create a common class which
inherits from all the group clients and provides entire API from one instance.

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
.. _decorest: https://github.com/bkryza/decorest
