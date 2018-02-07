__version__ = (0, 0, 1)

from .GET import GET
from .POST import POST
from .PUT import PUT
from .PATCH import PATCH
from .DELETE import DELETE
from .UPDATE import UPDATE
from .OPTIONS import OPTIONS
from .client import RestClient
from .decorators import query, body, header, auth, on
