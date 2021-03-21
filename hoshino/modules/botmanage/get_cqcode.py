from hoshino import sucmd
from hoshino.typing import CommandSession
from hoshino.util import escape

@sucmd('取码', force_private=False)
async def get_cqcode(session: CommandSession):
    await session.send(escape(str(session.current_arg)))
