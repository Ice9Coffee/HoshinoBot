import nonebot
import nonebot.permission as perm
from nonebot import CommandSession, on_command


@on_command('清理数据', permission=perm.SUPERUSER, only_to_me=True)
async def clean_image(session: CommandSession):
    await nonebot.get_bot().clean_data_dir(self_id=session.ctx['self_id'],
                                           data_dir='image')
    await session.send('Image 文件夹已清理')
