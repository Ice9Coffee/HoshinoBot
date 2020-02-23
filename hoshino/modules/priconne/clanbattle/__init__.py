from hoshino.service import Service, Privilege
sv = Service('clanbattle', manage_priv=Privilege.SUPERUSER, enable_on_default=False)
from .cmdv1 import *
from .cmdv2 import *
