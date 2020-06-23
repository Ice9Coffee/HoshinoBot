from hoshino.res import R
from hoshino.service import Service

sv = Service('kc-query', enable_on_default=False)

from .fleet import *
from .senka import *
