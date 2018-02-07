from .client import HttpMethod
from .decorators import HttpMethodDecorator


class GET(HttpMethodDecorator):

    def __init__(self, path):
        super(GET, self).__init__(path)

    def __call__(self, func):
        def get_decorator(*args, **kwargs):
            func._http__method = HttpMethod.GET
            return super(GET, self).call(func, *args, **kwargs)
        return get_decorator
