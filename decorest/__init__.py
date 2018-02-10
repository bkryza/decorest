__version__ = (0, 0, 2)

from .GET import GET
from .POST import POST
from .PUT import PUT
from .PATCH import PATCH
from .DELETE import DELETE
from .UPDATE import UPDATE
from .HEAD import HEAD
from .OPTIONS import OPTIONS
from .client import RestClient, HttpMethod
from .decorators import query, body, header, auth, on, accept, content, endpoint
