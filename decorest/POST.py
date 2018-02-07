from .client import HttpMethod
from .decorators import HttpMethodDecorator


class POST(HttpMethodDecorator):

    def __init__(self, path):
        super(POST, self).__init__(path)

    def __call__(self, func):
        def post_decorator(*args, **kwargs):
            func._http__method = HttpMethod.POST
            return super(POST, self).call(func, *args, **kwargs)
        return post_decorator
