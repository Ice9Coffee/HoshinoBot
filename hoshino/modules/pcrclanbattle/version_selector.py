from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('clanbattle-version-selector', manage_priv=priv.SUPERUSER, visible=False)

@sv.on_prefix('会战启用v', '启用会战v')
async def version_select(bot, ev: CQEvent):
    pass
