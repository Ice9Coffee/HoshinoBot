from hoshino import Service
from hoshino.typing import CQEvent

sv = Service("pcr-hedao", help_="请输入：合刀 刀1伤害 刀2伤害 剩余血量\n如：合刀 50 60 70")


@sv.on_prefix("合刀")
async def feedback(bot, ev: CQEvent):
    cmd = ev.message.extract_plain_text()
    content = cmd.split()
    print(content)
    if len(content) != 3:
        await bot.finish(ev, sv.help)
    try:
        d1 = float(content[0])
        d2 = float(content[1])
        rest = float(content[2])
    except (ValueError, RuntimeError):
        await bot.finish(ev, sv.help)
    if d1 + d2 < rest:
        await bot.finish(ev, "醒醒！这两刀是打不死boss的")
    dd1 = d1
    dd2 = d2
    if d1 >= rest:
        dd1 = rest
    if d2 >= rest:
        dd2 = rest
    res1 = (1 - (rest - dd1) / dd2) * 90 + 20
    # 1先出，2能得到的时间
    res2 = (1 - (rest - dd2) / dd1) * 90 + 20
    # 2先出，1能得到的时间
    res1 = round(res1, 2)
    res2 = round(res2, 2)
    res1 = min(res1, 90)
    res2 = min(res2, 90)
    reply = f"{d1}先出，另一刀可获得 {res1} 秒补偿刀\n{d2}先出，另一刀可获得 {res2} 秒补偿刀\n"
    if d1 >= rest or d2 >= rest:
        reply += "\n注："
        if d1 >= rest:
            reply += f"\n第一刀可直接秒杀boss，伤害按 {rest} 计算"
        if d2 >= rest:
            reply += f"\n第二刀可直接秒杀boss，伤害按 {rest} 计算"
    await bot.send(ev, reply)
