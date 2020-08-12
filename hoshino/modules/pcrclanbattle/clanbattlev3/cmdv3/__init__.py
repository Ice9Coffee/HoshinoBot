from hoshino import Service

sv = Service("clanbattlev3", bundle="pcr会战", help_="Hoshino会战管理v3（还没写完酷Q就没了 悲）")

from . import clan, challenge, battle_queue, sl, sos, subr, stat, progress
