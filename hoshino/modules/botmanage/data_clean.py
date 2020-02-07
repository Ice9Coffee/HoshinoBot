import nonebot
import nonebot.permission as perm
from nonebot import on_command, CommandSession
from hoshino.log import logger


@nonebot.scheduler.scheduled_job('cron', hour='20', misfire_grace_time=10, coalesce=True)     #UTC+8 0400
async def image_cleaner():
    await nonebot.get_bot().clean_data_dir(data_dir='image')
    logger.info('Image 文件夹已清理')


@on_command('清理数据', permission=perm.SUPERUSER, only_to_me=True)
async def data_clean(session:CommandSession):
    await nonebot.get_bot().clean_data_dir(data_dir='image')
    await session.send('Image 文件夹已清理')
