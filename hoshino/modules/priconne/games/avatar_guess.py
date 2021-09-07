# ref: https://github.com/GWYOG/GWYOG-Hoshino-plugins/blob/master/pcravatarguess
# Originally written by @GWYOG
# Reflacted by @Ice-Cirno
# GPL-3.0 Licensed
# Thanks to @GWYOG for his great contribution!

import asyncio
import os
import random

from hoshino import Service, util
from hoshino.modules.priconne import _pcr_data, chara
from hoshino.typing import CQEvent
from hoshino.typing import MessageSegment as Seg

from . import GameMaster

PATCH_SIZE = 32
ONE_TURN_TIME = 20
DB_PATH = os.path.expanduser("~/.hoshino/pcr_avatar_guess.db")
BLACKLIST_ID = [1072, 1908, 4031, 9000]

gm = GameMaster(DB_PATH)
sv = Service(
    "pcr-avatar-guess",
    bundle="pcr娱乐",
    help_="""
[猜头像] 猜猜bot随机发送的头像的一小部分来自哪位角色
[猜头像排行] 显示小游戏的群排行榜(只显示前十)
""".strip(),
)


@sv.on_fullmatch("猜头像排行", "猜头像排名", "猜头像排行榜", "猜头像群排行")
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【猜头像小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=ev.group_id, user_id=uid
        )
        name = util.filt_message(m["card"]) or util.filt_message(m["nickname"]) or str(uid)
        msg.append(f"第{i + 1}名：{name} 猜对{count}次")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch("猜头像")
async def avatar_guess(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        ids = list(_pcr_data.CHARA_NAME.keys())
        game.answer = random.choice(ids)
        while chara.is_npc(game.answer):
            game.answer = random.choice(ids)
        c = chara.fromid(game.answer)
        img = c.icon.open()
        w, h = img.size
        l = random.randint(0, w - PATCH_SIZE)
        u = random.randint(0, h - PATCH_SIZE)
        cropped = img.crop((l, u, l + PATCH_SIZE, u + PATCH_SIZE))
        cropped = Seg.image(util.pic2b64(cropped))
        await bot.send(ev, f"猜猜这个图片是哪位角色头像的一部分?({ONE_TURN_TIME}s后公布答案) {cropped}")
        await asyncio.sleep(ONE_TURN_TIME)
        if game.winner:
            return
    await bot.send(ev, f"正确答案是：{c.name} {c.icon.cqcode}\n很遗憾，没有人答对~")


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.winner:
        return
    c = chara.fromname(ev.message.extract_plain_text())
    if c.id != chara.UNKNOWN and c.id == game.answer:
        game.winner = ev.user_id
        n = game.record()
        msg = f"正确答案是：{c.name}{c.icon.cqcode}\n{Seg.at(ev.user_id)}猜对了，真厉害！TA已经猜对{n}次了~\n(此轮游戏将在几秒后自动结束，请耐心等待)"
        await bot.send(ev, msg)
