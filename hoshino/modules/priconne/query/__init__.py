from hoshino import Service

sv = Service('pcr-query')
sv = Service('whois')

from .query import *
from .whois import *
from .miner import *
