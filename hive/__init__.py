
from .application import Hive


__version__ = '1.1.0'


server_main = lambda: Hive().cli_main()

