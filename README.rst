decorest - decorator heavy REST client for Python
#################################################

.. image:: https://github.com/bkryza/decorest/actions/workflows/workflow.yml/badge.svg
    :target: https://github.com/bkryza/decorest/actions/workflows/workflow.yml

.. image:: https://codecov.io/gh/bkryza/decorest/branch/master/graph/badge.svg?token=UGSU07W732
    :target: https://codecov.io/gh/bkryza/decorest

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
        @GET('breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

    client = DogClient('https://dog.ceo/api')

    print(client.list_subbreeds('hound'))


or for an async version (please note the :py:`async` keyword in the API method definition):

.. code-block:: python

    import asyncio
    from decorest import backend, RestClient, GET

    @backend('httpx')
    class DogClient(RestClient):
        @GET('breed/{breed_name}/list')
        async def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

    async def main():
        client = DogClient('https://dog.ceo/api')

        print(await client.list_subbreeds('hound'))

    asyncio.run(main())


Installation
============

**Note:** *As of version `0.1.0`, decorest supports only Python 3.6+.*

Using pip:

.. code-block:: bash

    pip install decorest

To install the library with a specific backend, an environment variable must be provided, e.g.:

.. code-block:: bash

    # This will only install requests and its dependencies (default)
    DECOREST_BACKEND=requests pip install decorest

    # This will only install httpx and its dependencies
    DECOREST_BACKEND=httpx pip install decorest

Of course both requests_ and httpx_ can be installed together and used exchangeably.

Usage
=====

Basics
------

For most typical cases the usage should be fairly straightforward. Simply create a
subclass of :py:`decorest.RestClient` and define methods, which will perform calls
to the actual REST service. You can declare how each function should perform
the request to the service solely using decorators attached to the
method definition. The method itself is not expected to have any implementation,
except for a docstring.

After your API client class definition is complete, simply create an instance
of it and you're good to go. This library relies on the functionality provided
by either requests_ or httpx_ libraries, which means that any valid named argument,
which could be passed to a requests_ or httpx_ HTTP call can be also passed to the calls
of the client methods and will be forwarded as is.

For more information checkout sample clients in `examples`.

Choosing backend
----------------

decorest_ supports currently 2 backends:
  * requests_ (default)
  * httpx_

To select a specific backend, simply pass it's name to the constructor of the client:

.. code-block:: python

    client = DogClient('https://dog.ceo/api', backend='httpx')

Another option is to declare a specific default backend for the client using :py:`@backend()`
decorator, for instance:

.. code-block:: python

    @decorest.backend('httpx')
    class DogClient(decorest.RestClient):
        @GET('breed/{breed_name}/list')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

    client = DogClient('https://dog.ceo/api')

If no backend is provided, requests_ is used by default. The client usage is largely
independent of the backend, however there some minor differences in handling streams
and multipart messages, please consult tests in `httpbin test suite`_
and `httpx compatibility guide`_.

Please note, that :py:`asyncio` is only supported on the httpx_ backend.

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
        @header('user_agent', 'user-agent')
        def list_subbreeds(self, breed_name, accept, user_agent='decorest'):
            """List all sub-breeds"""

In case the first argument of the header decorator matches one of the
method args, it's optional second value determines the actual header
name that will be send in the request. A default value for the header
in such case must be provided in the method signature.

Multiple values for the same header can be provided either as separate
decorators or as a decorator with a list of values, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @header('abc', 'a')
        @header('abc', 'b')
        @header('abc', 'c')
        @header('xyz', ['x', 'y', 'z'])
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

Multiple values will be concatenated to a comma separated list and sent out
as a single header (according to the rfc2616_).

@body
~~~~~

Body decorator enables to specify, which of the method parameters should provide
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
value of :py:`pet` argument using :py:`json.dumps()` function.

@on
~~~

By default the request method will not return requests_ or httpx_ response object,
but the response will depend on the content type of the response.

In case the HTTP request succeeds the following results are expected:

- :py:`response.json()` if the content type of response is JSON
- :py:`response.content` if the content type is binary
- :py:`response.text` otherwise

In case the request fails, :py:`response.raise_for_status()` is called and
should be handled in the client code.

In case another behavior is required, custom handlers can be provided
for each method using lambdas or functions. The provided handler is
expected to take only a single argument, which is the requests_ or httpx_
response object, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @header('accept', 'application/json')
        @on(200, lambda r: r.json())
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

This decorator can be applied to both methods and classes, however when
applied to a class the handler will be called for the method which receives
the provided status code.

The first argument of this decorator must be an :py:`int`. It is
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

Multiple :py:`@accept()` decorators can be added and will be joined into
a list, e.g.:

.. code-block:: python

        @GET('breed/{breed_name}/list')
        @content('application/json')
        @accept('application/xml')
        @accept('application/json')
        @accept('text/plain')
        def list_subbreeds(self, breed_name):
            """List all sub-breeds"""

will submit the following header to the server:

.. code-block:: bash

        Accept: text/plain, application/json, application/xml

@endpoint
~~~~~~~~~
This decorator enables to define a default endpoint for the service,
which then doesn't have to be provided in the client constructor:

.. code-block:: python

        @endpoint('https://dog.ceo/api')
        class DogClient(RestClient):
            """List all sub-breeds"""
            ...

The endpoint provided in the client constructor will take precedence
however.


@timeout
~~~~~~~~
Specifies a default timeout value (in seconds) for a method or entire API.

.. code-block:: python

        @endpoint('https://dog.ceo/api')
        @timeout(5)
        class DogClient(RestClient):
            """List all sub-breeds"""
            ...

@stream
~~~~~~~
This decorator allows to specify a method which returns binary stream of data.
Adding this decorator to a method will add a :py:`stream=True`
argument to the requests_ or httpx_ call and will by default returns entire response
object, which then can be accessed for instance using :py:`iter_content()` method.

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


or for an async API:

.. code-block:: python

    ...

    @backend('httpx')
    class MyClient(RestClient):
        ...

        @GET('stream/{n}/{m}')
        @stream
        @query('size')
        @query('offset', 'off')
        async def stream(self, n, m, size, offset):
            """Get data range"""

    ...
    async def main():
        async with client.async_session_() as s:
            r = await s.stream(5)
            async for _ in r.aiter_raw(chunk_size=100):
                content.append(b)


@backend
~~~~~~~~
Specifies the default backend to use by the client, currently the only possible
values are :py:`'requests'` (default) and :py:`'httpx'`, e.g.:

.. code-block:: python

        @endpoint('https://dog.ceo/api')
        @backend('httpx')
        class DogClient(RestClient):
            """List all sub-breeds"""
            ...

The backend provided in the constructor arguments when creating client instance has precedence
over the value provided in this decorator. This decorator can only be applied to classes.

Sessions
--------

Based on the functionality provided by the backend HTTP library in the form of
session objects, sessions can significantly improve the performance of the
client in case multiple responses are performed as well as maintain certain
information between requests such as session cookies.

Sessions in decorest_ can either be created and closed manually:

.. code-block:: python

        s = client.session_()
        s.list_subbreeds('hound')
        s.list_subbreeds('husky')
        s.close_()

or can be used via the context manager :py:`with` operator:

.. code-block:: python

        with client.session_() as s:
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

All session specific methods begin with a single underscore, in order not
to interfere with any possible API method names defined in the base client
class.

If some additional customization of the session is required, the underlying
`requests session`_ or `httpx session`object can be retrieved from decorest_
session object using :py:`backend_session_` attribute:

.. code-block:: python

        with client.session_() as s:
            s.backend_session_.verify = '/path/to/cert.pem'
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

Async sessions can be created in a similar manner, using :py:`async_session_()` method,
for instance:

.. code-block:: python

        async def main():
            async with client.async_session_() as s:
                await s.list_subbreeds('hound')
                await s.list_subbreeds('husky')


Authentication
--------------

Since authentication is highly specific to actual invocation of the REST API,
and not to it's specification, there is not decorator for authentication,
but instead an authentication object (compatible with `requests_`
or `httpx_` authentication mechanism) can be set in the client object using
:py:`set_auth_()` method, for example:

.. code-block:: python

        client.set_auth_(HTTPBasicAuth('user', 'password'))
        with client.session_() as s:
            s.backend_session_.verify = '/path/to/cert.pem'
            s.list_subbreeds('hound')
            s.list_subbreeds('husky')

The authentication object will be used in both regular API calls, as well
as when using sessions.

Furthermore, the `auth` object - specific for selected backend - can be also
passed to the client constructor, e.g.:

.. code-block:: python

        client = DogClient(backend='httpx', auth=httpx.BasicAuth('user', 'password'))


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

.. code-block:: python

    class A(RestClient):
        """API One client"""
        @GET('stuff/{sth}')
        @on(200, lambda r: r.json())
        def get(self, sth: str) -> typing.Any:
            """Get what"""


    class B(RestClient):
        """API One client"""
        @PUT('stuff/{sth}')
        @body('body')
        @on(204, lambda _: True)
        def put_b(self, sth: str, body: bytes) -> typing.Any:
            """Put sth"""


    @endpoint('https://put.example.com')
    class BB(B):
        """API One client"""
        @PUT('stuff/{sth}')
        @body('body')
        @on(204, lambda _: True)
        def put_bb(self, sth: str, body: bytes) -> typing.Any:
            """Put sth"""


    @endpoint('https://patches.example.com')
    class C(RestClient):
        """API Three client"""
        @PATCH('stuff/{sth}')
        @body('body')
        @on(204, lambda _: True)
        @on(..., lambda _: False)
        def patch(self, sth: str, body: bytes) -> typing.Any:
            """Patch sth"""


    @accept('application/json')
    @content('application/xml')
    @header('X-Auth-Key', 'ABCD')
    @endpoint('https://example.com')
    @backend('httpx')
    class InheritedClient(A, BB, C):
        ...


Please note that the :py:`@endpoint()` decorator can be specified for each
sub API with a different value if necessary. It will be inherited by methods
backwards with respect to the inheritance chain, i.e. the more abstract class
will use the first endpoint specified in it's subclass chain. In the above example
method :py:`B.put_b()` will use :py:`'https://put.example.com'` endpoint, and
method :py:`C.patch()` will use :py:`'https://patches.example.com'`.

For real world example checkout the `Petstore Swagger client example`_.


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

In general, decorest_ decorators should work with other decorators, which return
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

    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate


Formatting
----------
.. code-block:: bash

    yapf -ir decorest tests examples


Running tests
-------------

All tests are stored in tests_ directory. Running tests is fully automated using
tox_ and tox-docker_.

.. code-block:: bash

    python -m tox -e yapf,rstcheck,mypy,flake8,basic,httpbin,asynchttpbin,swaggerpetstore


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
.. _httpx compatibility guide: https://www.python-httpx.org/compatibility/
.. _rfc2616: https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html