decorest - decorator heavy REST client for Python
#################################################

.. image:: https://github.com/bkryza/decorest/actions/workflows/workflow.yml/badge.svg
    :target: https://github.com/bkryza/decorest/actions/workflows/workflow.yml

.. image:: https://img.shields.io/pypi/v/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

.. image:: https://img.shields.io/pypi/l/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

.. image:: https://img.shields.io/pypi/pyversions/decorest.svg
    :target: https://pypi.python.org/pypi/decorest

Declarative, decorator-based REST client for Python.

.. role:: py(code)
   :language: python


.. contents::

Overview
========

decorest_ library provides an easy to use declarative REST API client interface,
where definition of the API methods using decorators automatically produces
a working REST client with no additional code. In practice the library provides
only an interface to describe and interact with REST services - the actual work
is done underneath by either requests_ (default) or httpx_ libraries. Backend
can be selected dynamically during creation of client instance.

For example:

.. code-block:: python

    from decorest import RestClient, GET

    class DogClient(RestClient):
        def __init__(self, *args, **kwargs):
            super(DogClient, self).__init__(*args, **kwargs)

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

For most typical cases the usage should be fairly straightforward. Simply create a
subclass of :py:`decorest.RestClient` and define methods, which will perform calls
to the actual REST service. You can declare how each function should perform
the request to the service solely using decorators attached to the
method definition. The method itself is not expected to have any implementation,
except maybe for a docstring.

After your API client class definition is complete, simply create an instance
of it and you're good to go. This library relies on the functionality provided
by either requests_ or httpx_ libraries, which means that any valid named argument,
which could be passed to a requests_ or httpx_ HTTP call can be also passed to the calls
of the client methods and will be forwarded as is.

For more information checkout sample clients in `examples`.

Choosing backend
----------------

decorest_ supports currently 2 backends:
  * requests_ (Python 2 and 3)
  * httpx_ (only Python 3)

To select a specific backend, simply pass it's name to the constructor of the client:

.. code-block:: python

    client = DogClient('https://dog.ceo/api', backend='httpx')

If no backend is provided, requests_ is used by default. The client usage is largely
independent of the backend, however there some minor differences in handling streams
and multipart messages, please consult tests in `httpbin test suite`_.

Decorators
----------

Below is a list of all supported decorators along with short explanation and
examples. Some decorators can be attached to both client class as well as
methods, in which case the class-level decorator is applied to all HTTP methods
in that class. Furthermore, each decorator can be overridden directly during
the method call by providing a named argument with name equal to the decorator
name.


@GET, @PUT, @POST, @PATCH, @DELETE, @HEAD, @OPTIONS
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

Adds a query parameter to the request. URL encoding will be applied to
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
it should be different than the method argument name).

Furthermore, if a default value is provided in a method declaration, it
will be used whenever a value for this argument is not provided during
invocation.

For example, the following invocation of the above method:

.. code-block:: python

    client.list_subbreeds('hound', 1)

will result in the following query:

.. code-block:: bash

    https://dog.ceo/api/breed/hound?longNames=1&limit=100

This decorator can be added only to methods.

@form
~~~~~~

Adds a form parameter to the request. For example:

.. code-block:: python

        @POST('breed')
        @form('breed_name')
        @form('breed_url', 'breed_wikipedia_link')
        def add_breed(self, breed_name, breed_url):
            """Add sub-breed"""

This decorator can take a single string parameter, which determines the name
of the method argument whose value will be added as the query argument value
of the same name.

In case 2 arguments are provided, the second argument determines the actual
form field name, which will be used in the request form (if for some reason
it cannot be the same as the method argument name).

If a method has at least one :py:`@form` decorator attached, the `Content-type`
header value will be always set to `application/x-www-form-urlencoded`.

This decorator can be added only to methods.

@multipart
~~~~~~~~~~

Adds a multipart parameter to the request. For example:

.. code-block:: python

     @POST('post')
     @multipart('part1')
     @multipart('part_2', 'part2')
     @multipart('test')
     def post_multipart(self, part1, part_2, test):
         """Return multipart POST data."""

The first parameter to the decorator is the name of the variable in the decorated
method and at the same time the name of the part in HTTP request (which will be
set in the :py:`Content-Disposition` header. In case the method argument name
should be different than the part name in the request, a second parameter to the 
decorator will determine the actual name for the part in the HTTP request.

The values for the arguments can be either strings, which will be added directly
as content in the appropriate part, or tuples. In case a tuple is passed, it will
be treated as a file, the same way as is treated by both backend libraries. 

The above method can be thus called as follows:

.. code-block:: python

    f = '/tmp/test.dat'
    res = client.post_multipart('TEST1', 'TEST2',
                                ('filename', open(f, 'rb'), 'text/plain'))

which will generate the following parts:
  * part `part1` with content `TEST1`
  * part `part2` with content `TEST2`
  * part `test` with content read from file `/tmp/test.dat`

@header
~~~~~~~

Adds a header key-value pair to the request, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @header('accept', 'application/json')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be added to both methods and client class. The class level
decorators will be added to every method and can be overridden using method
level decorators.

Decorated methods can use their arguments to pass header values, if the headers
name matches one of the arguments, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @header('accept')
        def list_subbreeds(self, breed_name, accept):
            """List all sub-breeds"""

@body
~~~~~

Body decorator enables to specify which of the method parameters should provide
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

@on
~~~

By default the request method will not return requests_ response object,
but the response will depend on the content type of the response.

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
        @on(200, lambda r: r.json())
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be applied to both methods and classes, however when
applied to a class the handler will be called for method which receives
the provided status code.

The first argument of this decorator must be an integer. On Python 3 it
also possible to pass :py:`...` (i.e. Ellipsis) object, which is equivalent
to :py:`HttpStatus.ANY`. Any other value passed for this argument will
raise :py:`TypeError`.

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
~~~~~~~~~
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

@stream
~~~~~~~
This decorator allows to specify a method which returns binary stream of data.
Adding this decorator to a method will add a :py:`stream=True`
argument to the requests_ call and will by default return entire requests
object which then can be accessed for instance using :py:`iter_content()` method.

.. code-block:: python

    ...

    class MyClient(RestClient):
        ...

        @GET('stream/{n}/{m}')
        @stream
        @query('size')
        @query('offset', 'off')
        def stream(self, n, m, size, offset):
            """Get data range"""

    ...

    with client.stream(2,4, 1024, 200) as r:
        for b in r.iter_content(chunk_size=100):
            content.append(b)


Sessions
--------

Based on the functionality provided by requests_ library in the form of
session objects, sessions can significantly improve the performance of the
client in case multiple responses are performed as well as maintain certain
information between requests such as session cookies.

Sessions in decorest_ can either be created and closed manually:

.. code-block:: python

        s = client._session()
        s.list_subbreeds('hound')
        s.list_subbreeds('husky')
        s._close()

or can be used via the context manager :py:`with` operator:

.. code-block:: python

        with client._session() as s:
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

All session specific methods begin with a single underscore, in order not
to interfere with any possible API method names defined in the base client
class.

If some additional customization of the session is required, the underlying
`requests session`_ object can be retrieved from decorest_ session object
using :py:`_requests_session` attribute:

.. code-block:: python

        with client._session() as s:
            s._requests_session.verify = '/path/to/cert.pem'
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

Authentication
--------------

Since authentication is highly specific to actual invocation of the REST API,
and not to it's specification, there is not decorator for authentication,
but instead an authentication object (compatible with `requests_`
authentication mechanism) can be set in the client object using
:py:`_set_auth()` method, for example:

.. code-block:: python

        client._set_auth(HTTPBasicAuth('user', 'password'))
        with client._session() as s:
            s._requests_session.verify = '/path/to/cert.pem'
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

The authentication object will be used in both regular API calls, as well
as when using sessions.


Error handling
--------------

Due to the fact, that this library supports multiple HTTP backends, exceptions
should be caught through a wrapper class, :py:`decorest.HTTPErrorWrapper`, which
contains the original exception raised by the underlying backend.

.. code-block:: python

    try:
        res = client.update_pet(json.dumps({'id': pet_id, 'status': 'sold'}))
    except HTTPErrorWrapper as e:
        # Print original error message
        print(e.response.text)
        # Reraise the original exception
        raise e.wrapped


Grouping API methods
---------------------------

For larger API's it can be useful to be able to split the API definition
into multiple files but still use it from a single instance in the code.

This can be achieved by creating separate client classes for each group
of operations and then create a common class, which inherits from all the
group clients and provides entire API from one instance.

For example of this checkout the `Petstore Swagger client example`_.


Caveats
-------

Decorator order
~~~~~~~~~~~~~~~

Decorators can be basically added in any order, except for the HTTP method
decorator (e.g. :py:`@GET()`), which should always be at the top of the given
decorator list. Third party decorators should be added above the HTTP method
decorators.

Name conflicts
~~~~~~~~~~~~~~

Decorators can sometimes generate conflicts with decorated method or function
names in case they have the same name as they get merged into the :py:`__globals__`
dictionary. In case this is an issue, decorest decorators should be used with full
module namespace:

.. code-block:: python

    @decorest.POST('pet')
    @decorest.content('application/json')
    @decorest.header('accept', 'application/json')
    @decorest.body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet):
        """Add a new pet to the store"""


Compatibility with other decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general the decorators should work with other decorators, which return
function objects, but your mileage may vary. In general third-party decorators
should be added above the HTTP method decorators as only the HTTP decorators
make the actual HTTP request. Thus, typical decorators, which try to wrap
the actual call should get the HTTP callable returned by HTTP method decorators
such as :py:`@GET()`.

Currently, it is not possible to add decorators such as :py:`@classmethod`
or :py:`@staticmethod` to API methods, as the invocation requires an instance
of client class.

Development
===========

Create virtual env
------------------

.. code-block:: bash

    # For Python 3
    virtualenv -p /usr/bin/python3.8 venv3
    source venv3/bin/activate

    # For Python 2
    virtualenv -p /usr/bin/python2.7 venv2
    source venv2/bin/activate

Formatting
----------
.. code-block:: bash

    yapf -ir decorest tests examples


Running tests
-------------

All tests are stored in tests_ directory. Running tests is fully automated using
tox_ and tox-docker_.

.. code-block:: bash

    # Python 3
    python -m tox -e flake8,basic,httpbin,swaggerpetstore

    # Python 2
    python -m tox -c tox-py2.ini -e flake8,basic,httpbin,swaggerpetstore


Checking README syntax
----------------------

.. code-block:: bash

    rstcheck README.rst

License
=======

Copyright 2018-present Bartosz Kryza <bkryza@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. _tests: https://github.com/bkryza/decorest/tree/master/tests
.. _requests: https://github.com/requests/requests
.. _httpx: https://github.com/encode/httpx
.. _`requests session`: http://docs.python-requests.org/en/master/user/advanced/#session-objects
.. _decorest: https://github.com/bkryza/decorest
.. _`Petstore Swagger client example`: https://github.com/bkryza/decorest/blob/master/examples/swagger_petstore/petstore_client.py
.. _`httpbin test suite`: https://github.com/bkryza/decorest/blob/master/tests/httpbin_test.py
.. _tox: https://github.com/tox-dev/tox
.. _tox-docker: https://github.com/tox-dev/tox-docker
