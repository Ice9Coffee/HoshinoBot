from hoshino.service import Service

svtw = Service('pcr-arena-reminder-tw', enable_on_default=False, help_='背刺时间提醒(台B)', bundle='pcr订阅')
svjp = Service('pcr-arena-reminder-jp', enable_on_default=False, help_='背刺时间提醒(日)', bundle='pcr订阅')
msg = '骑士君、准备好背刺了吗？'

@svtw.scheduled_job('cron', hour='14', minute='45')
async def pcr_reminder_tw():
    await svtw.broadcast(msg, 'pcr-reminder-tw', 0.2)

@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_jp():
    await svjp.broadcast(msg, 'pcr-reminder-jp', 0.2)
