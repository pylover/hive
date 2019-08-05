
from .application import SharedLists


__version__ = '1.0.0'


server_main = lambda: SharedLists().cli_main()

