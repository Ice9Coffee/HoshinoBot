from hoshino import Service

sv = Service('clanbattlev3', bundle='pcr会战', help_='Hoshino会战管理v3（建设中）')

from .cmdv3 import *
