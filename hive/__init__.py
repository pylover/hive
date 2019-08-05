
from .application import Hive


__version__ = '1.0.1'


server_main = lambda: Hive().cli_main()

