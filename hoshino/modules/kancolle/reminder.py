import pytz
from datetime import datetime

from hoshino.service import Service

sv = Service('kc-reminder', enable_on_default=False, help_='演习/任务/月常远征提醒', bundle='kancolle')

@sv.scheduled_job('cron', hour='13', minute='30')
async def enshu_reminder():
    msgs = [
        '演习即将刷新！\n莫让下午的自己埋怨上午的自己：\n「演習」で練度向上！0/3',
        '[CQ:at,qq=all] 演习即将刷新！',
    ]
    await sv.broadcast(msgs, 'enshu_reminder', 0.2)


@sv.scheduled_job('cron', hour='1', minute='30')
async def enshu_reminder_evening():
    await sv.broadcast('夜猫子提督、夜は長いよ！夜戦、夜戦！\n「演習」で他提督を圧倒せよ！0/5', 'enshu_reminder_evening', 0.2)


@sv.scheduled_job('cron', day='10-14', hour='22')
async def ensei_reminder():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    remain_days = 15 - now.day
    msgs = [
        f'【远征提醒小助手】提醒您月常远征还有{remain_days}天刷新！',
        f'[CQ:at,qq=all] 月常远征还有{remain_days}天刷新！',
    ]
    await sv.broadcast(msgs, 'ensei_reminder', 0.5)

@sv.scheduled_job('cron', hour='3', minute='30')
async def daily_quest_refresh_reminder():
    await sv.broadcast('現在時刻〇三三〇です。提督、そろそろ朝になっちゃいます。\n「遠征」を３回成功させよう！0/3', 'daily_quest_refresh_reminder', 0.2)
