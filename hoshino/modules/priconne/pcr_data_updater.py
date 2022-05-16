import os
import random

import hoshino
from hoshino import Service, aiorequests, priv, sucmd
from hoshino.config import SUPERUSERS
from hoshino.typing import CommandSession

from . import chara

sv = Service("pcr-data-updater", use_priv=priv.SU, manage_priv=priv.SU, visible=False)


async def report_to_su(sess, msg_with_sess, msg_wo_sess):
    if sess:
        await sess.send(msg_with_sess)
    else:
        bot = hoshino.get_bot()
        sid = bot.get_self_ids()
        if len(sid) > 0:
            sid = random.choice(sid)
            await bot.send_private_msg(self_id=sid, user_id=SUPERUSERS[0], message=msg_wo_sess)


async def pull_chara(sess: CommandSession = None):
    try:
        rsp = await aiorequests.get('https://raw.githubusercontent.com/Ice-Cirno/LandosolRoster/master/_pcr_data.py')
        rsp.raise_for_status()
        rsp = await rsp.text

        filename = os.path.join(os.path.dirname(__file__), '_pcr_data.py')
        with open(filename, 'w', encoding='utf8') as f:
            f.write(rsp)
        result = chara.roster.update()

    except Exception as e:
        sv.logger.exception(e)
        await report_to_su(sess, f'Error: {e}', f'pcr_data定时更新时遇到错误：\n{e}')
        return

    result = f"角色别称导入成功 {result['success']}，重名 {result['duplicate']}"
    await report_to_su(sess, result, f'pcr_data定时更新：\n{result}')


sucmd('update-pcr-chara', force_private=False, aliases=('重载花名册', '更新花名册'))(pull_chara)
sv.scheduled_job('cron', hour=5, jitter=300)(pull_chara)
