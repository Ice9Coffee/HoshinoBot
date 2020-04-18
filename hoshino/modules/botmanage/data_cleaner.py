import nonebot
import nonebot.permission as perm
from nonebot import on_command, CommandSession
from hoshino.log import logger


# @nonebot.scheduler.scheduled_job('cron', hour='4')
# async def image_cleaner():
#     self_id = list(nonebot.get_bot()._wsr_api_clients.keys())[0]
#     await nonebot.get_bot().clean_data_dir(self_id=self_id, data_dir='image')
#     logger.info('Image 文件夹已清理')


@on_command('清理数据', permission=perm.SUPERUSER, only_to_me=True)
async def clean_image(session:CommandSession):
    await nonebot.get_bot().clean_data_dir(self_id=session.ctx['self_id'], data_dir='image')
    await session.send('Image 文件夹已清理')
