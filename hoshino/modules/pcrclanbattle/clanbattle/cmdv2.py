"""
PCR会战管理命令 v2

猴子也会用的会战管理

命令设计遵循以下原则：
- 中文：降低学习成本
- 唯一：There should be one-- and preferably only one --obvious way to do it.
- 耐草：参数不规范时尽量执行
"""

import os
from datetime import datetime, timedelta
from typing import List
from matplotlib import pyplot as plt

try:
    import ujson as json
except:
    import json

from aiocqhttp.exceptions import ActionFailed
from nonebot import NoneBot
from nonebot import MessageSegment as ms
from nonebot.typing import Context_T
from hoshino import util
from hoshino.service import Privilege as Priv

from . import sv, cb_cmd
from .argparse import ArgParser, ArgHolder, ParseResult
from .argparse.argtype import *
from .battlemaster import BattleMaster
from .exception import *

plt.style.use("seaborn-pastel")
plt.rcParams["font.family"] = [
    "DejaVuSans",
    "Microsoft YaHei",
    "SimSun",
]

USAGE_ADD_CLAN = "!建会"
USAGE_ADD_MEMBER = "!入会"
USAGE_LIST_MEMBER = "!查看成员"

USAGE_TIP = "\n\n※无需输入尖括号，圆括号内为可选参数"

ERROR_CLAN_NOTFOUND = f"公会未初始化：请*群管理*使用【{USAGE_ADD_CLAN}】进行初始化{USAGE_TIP}"
ERROR_ZERO_MEMBER = f"公会内无成员：使用【{USAGE_ADD_MEMBER}】以添加{USAGE_TIP}"
ERROR_MEMBER_NOTFOUND = f"未找到成员：请使用【{USAGE_ADD_MEMBER}】加入公会{USAGE_TIP}"
ERROR_PERMISSION_DENIED = "权限不足：需*群管理*以上权限"


def _check_clan(bm: BattleMaster):
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    return clan


def _check_member(bm: BattleMaster, uid: int, alt: int, tip=None):
    mem = bm.get_member(uid, alt) or bm.get_member(uid, 0)  # 兼容cmdv1
    if not mem:
        raise NotFoundError(tip or ERROR_MEMBER_NOTFOUND)
    return mem


def _check_admin(ctx: Context_T, tip: str = ""):
    if not sv.check_priv(ctx, Priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED + tip)


@cb_cmd(
    "建会",
    ArgParser(
        usage=USAGE_ADD_CLAN,
        arg_dict={
            "N": ArgHolder(tip="公会名"),
            "S": ArgHolder(tip="服务器地区", type=server_code),
        },
    ),
)
async def add_clan(bot: NoneBot, ctx: Context_T, args: ParseResult):
    _check_admin(ctx)
    bm = BattleMaster(ctx["group_id"])
    if bm.has_clan(1):
        bm.mod_clan(1, args.N, args.S)
        await bot.send(ctx, f"公会信息已修改！\n{args.N} {server_name(args.S)}", at_sender=True)
    else:
        bm.add_clan(1, args.N, args.S)
        await bot.send(ctx, f"公会建立成功！{args.N} {server_name(args.S)}", at_sender=True)


@cb_cmd("查看公会", ArgParser("!查看公会"))
async def list_clan(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clans = bm.list_clan()
    if len(clans):
        clans = map(
            lambda x: f"{x['cid']}会：{x['name']} {server_name(x['server'])}", clans
        )
        msg = ["本群公会：", *clans]
        await bot.send(ctx, "\n".join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)


@cb_cmd(
    "入会",
    ArgParser(
        usage=USAGE_ADD_MEMBER,
        arg_dict={
            "": ArgHolder(tip="昵称", default=""),
            "@": ArgHolder(tip="qq号", type=int, default=0),
        },
    ),
)
async def add_member(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    uid = args["@"] or args.at or ctx["user_id"]
    name = args[""]
    if uid != ctx["user_id"]:
        _check_admin(ctx, "才能添加其他人")
        try:  # 尝试获取群员信息，用以检查该成员是否在群中
            await bot.get_group_member_info(
                self_id=ctx["self_id"], group_id=bm.group, user_id=uid
            )
        except:
            raise NotFoundError(f"Error: 无法获取群员信息，请检查{uid}是否属于本群")
    if not name:
        m = await bot.get_group_member_info(
            self_id=ctx["self_id"], group_id=bm.group, user_id=uid
        )
        name = m["card"] or m["nickname"] or str(m["user_id"])

    mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0)  # 兼容cmdv1
    if mem:
        bm.mod_member(uid, mem["alt"], name, 1)
        await bot.send(ctx, f"成员{ms.at(uid)}昵称已修改为{name}")
    else:
        bm.add_member(uid, bm.group, name, 1)
        await bot.send(ctx, f"成员{ms.at(uid)}添加成功！欢迎{name}加入{clan['name']}")


@cb_cmd(("查看成员", "成员查看", "查询成员", "成员查询"), ArgParser(USAGE_LIST_MEMBER))
async def list_member(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    mems = bm.list_member(1)
    if l := len(mems):
        # 数字太多会被腾讯ban
        mems = map(lambda x: "{uid: <11,d} | {name}".format_map(x), mems)
        msg = [f"\n{clan['name']}   {l}/30 人\n____ QQ ____ | 昵称", *mems]
        await bot.send(ctx, "\n".join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_ZERO_MEMBER)


@cb_cmd(
    "退会",
    ArgParser(
        usage="!退会 (@qq)", arg_dict={"@": ArgHolder(tip="qq号", type=int, default=0)}
    ),
)
async def del_member(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    uid = args["@"] or args.at or ctx["user_id"]
    mem = _check_member(bm, uid, bm.group, "公会内无此成员")
    if uid != ctx["user_id"]:
        _check_admin(ctx, "才能踢人")
    bm.del_member(uid, mem["alt"])
    await bot.send(ctx, f"成员{mem['name']}已从公会删除", at_sender=True)


@cb_cmd("清空成员", ArgParser("!清空成员"))
async def clear_member(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    _check_admin(ctx)
    msg = f"{clan['name']}已清空！" if bm.clear_member(1) else f"{clan['name']}已无成员"
    await bot.send(ctx, msg, at_sender=True)


@cb_cmd("一键入会", ArgParser("!一键入会"))
async def batch_add_member(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    _check_admin(ctx)
    try:
        mlist = await bot.get_group_member_list(
            self_id=ctx["self_id"], group_id=bm.group
        )
    except ActionFailed:
        raise ClanBattleError("Bot缓存未更新，暂时无法使用一键入会。请尝试【!入会】命令逐个添加")
    if len(mlist) > 50:
        raise ClanBattleError("群员过多！一键入会仅限50人以内群使用")

    self_id = ctx["self_id"]
    succ, fail = 0, 0
    for m in mlist:
        if m["user_id"] != self_id:
            try:
                bm.add_member(
                    m["user_id"],
                    bm.group,
                    m["card"] or m["nickname"] or str(m["user_id"]),
                    1,
                )
                succ += 1
            except DatabaseError:
                fail += 1
    msg = f"批量注册完成！成功{succ}/失败{fail}\n使用【{USAGE_LIST_MEMBER}】查看当前成员列表"
    await bot.send(ctx, msg, at_sender=True)


def _gen_progress_text(clan_name, round_, boss, hp, max_hp, score_rate):
    return f"{clan_name} 当前进度：\n{round_}周目 {BattleMaster.int2kanji(boss)}王    SCORE x{score_rate:.1f}\nHP={hp:,d}/{max_hp:,d}"


async def process_challenge(bot: NoneBot, ctx: Context_T, ch: ParseResult):
    """
    处理一条报刀 需要保证challenge['flag']的正确性
    """

    bm = BattleMaster(ctx["group_id"])
    now = datetime.now()
    clan = _check_clan(bm)
    mem = _check_member(bm, ch.uid, ch.alt)

    cur_round, cur_boss, cur_hp = bm.get_challenge_progress(1, now)
    round_ = ch.round or cur_round
    boss = ch.boss or cur_boss
    damage = ch.damage if ch.flag != BattleMaster.LAST else (ch.damage or cur_hp)
    flag = ch.flag

    if (ch.flag == BattleMaster.LAST) and (ch.round or ch.boss) and (not damage):
        raise NotFoundError("补报尾刀请给出伤害值")  # 补报尾刀必须给出伤害值

    msg = [""]
    if round_ != cur_round or boss != cur_boss:
        msg.append("⚠️上报与当前进度不一致")
    else:  # 伤害校对
        eps = 30000
        if damage > cur_hp + eps:
            damage = cur_hp
            msg.append(f"⚠️过度虐杀 伤害数值已自动修正为{damage}")
            if flag == BattleMaster.NORM:
                flag = BattleMaster.LAST
                msg.append("⚠️已自动标记为尾刀")
        elif flag == BattleMaster.LAST:
            if damage < cur_hp - eps:
                msg.append("⚠️尾刀伤害不足 请未报刀成员及时上报")
            elif damage < cur_hp:
                if damage % 1000 == 0:
                    damage = cur_hp
                    msg.append(f"⚠️尾刀伤害已自动修正为{damage}")
                else:
                    msg.append("⚠️Boss仍有少量残留血量")

    eid = bm.add_challenge(mem["uid"], mem["alt"], round_, boss, damage, flag, now)
    aft_round, aft_boss, aft_hp = bm.get_challenge_progress(1, now)
    max_hp, score_rate = bm.get_boss_info(aft_round, aft_boss, clan["server"])
    msg.append(
        f"记录编号E{eid}：\n{mem['name']}给予{round_}周目{bm.int2kanji(boss)}王{damage:,d}点伤害\n"
    )
    msg.append(
        _gen_progress_text(
            clan["name"], aft_round, aft_boss, aft_hp, max_hp, score_rate
        )
    )
    await bot.send(ctx, "\n".join(msg), at_sender=True)

    # 判断是否更换boss，呼叫预约
    if aft_round != cur_round or aft_boss != cur_boss:
        await call_subscribe(bot, ctx, aft_round, aft_boss)

    await auto_unlock_boss(bot, ctx, bm)
    await auto_unsubscribe(bot, ctx, bm.group, mem["uid"], boss)


@cb_cmd(
    ("出刀", "报刀"),
    ArgParser(
        usage="!出刀 <伤害值> (@qq)",
        arg_dict={
            "": ArgHolder(tip="伤害值", type=damage_int),
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "R": ArgHolder(tip="周目数", type=round_code, default=0),
            "B": ArgHolder(tip="Boss编号", type=boss_code, default=0),
        },
    ),
)
async def add_challenge(bot: NoneBot, ctx: Context_T, args: ParseResult):
    challenge = ParseResult(
        {
            "round": args.R,
            "boss": args.B,
            "damage": args.get(""),
            "uid": args["@"] or args.at or ctx["user_id"],
            "alt": ctx["group_id"],
            "flag": BattleMaster.NORM,
        }
    )
    await process_challenge(bot, ctx, challenge)


@cb_cmd(
    ("出尾刀", "收尾", "尾刀"),
    ArgParser(
        usage="!出尾刀 (<伤害值>) (@<qq号>)",
        arg_dict={
            "": ArgHolder(tip="伤害值", type=damage_int, default=0),
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "R": ArgHolder(tip="周目数", type=round_code, default=0),
            "B": ArgHolder(tip="Boss编号", type=boss_code, default=0),
        },
    ),
)
async def add_challenge_last(bot: NoneBot, ctx: Context_T, args: ParseResult):
    challenge = ParseResult(
        {
            "round": args.R,
            "boss": args.B,
            "damage": args.get(""),
            "uid": args["@"] or args.at or ctx["user_id"],
            "alt": ctx["group_id"],
            "flag": BattleMaster.LAST,
        }
    )
    await process_challenge(bot, ctx, challenge)


@cb_cmd(
    ("出补时刀", "补时刀", "补时"),
    ArgParser(
        usage="!出补时刀 <伤害值> (@qq)",
        arg_dict={
            "": ArgHolder(tip="伤害值", type=damage_int),
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "R": ArgHolder(tip="周目数", type=round_code, default=0),
            "B": ArgHolder(tip="Boss编号", type=boss_code, default=0),
        },
    ),
)
async def add_challenge_ext(bot: NoneBot, ctx: Context_T, args: ParseResult):
    challenge = ParseResult(
        {
            "round": args.R,
            "boss": args.B,
            "damage": args.get(""),
            "uid": args["@"] or args.at or ctx["user_id"],
            "alt": ctx["group_id"],
            "flag": BattleMaster.EXT,
        }
    )
    await process_challenge(bot, ctx, challenge)


@cb_cmd(
    "掉刀",
    ArgParser(
        usage="!掉刀 (@qq)",
        arg_dict={
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "R": ArgHolder(tip="周目数", type=round_code, default=0),
            "B": ArgHolder(tip="Boss编号", type=boss_code, default=0),
        },
    ),
)
async def add_challenge_timeout(bot: NoneBot, ctx: Context_T, args: ParseResult):
    challenge = ParseResult(
        {
            "round": args.R,
            "boss": args.B,
            "damage": 0,
            "uid": args["@"] or args.at or ctx["user_id"],
            "alt": ctx["group_id"],
            "flag": BattleMaster.TIMEOUT,
        }
    )
    await process_challenge(bot, ctx, challenge)


@cb_cmd(
    "删刀", ArgParser(usage="!删刀 E记录编号", arg_dict={"E": ArgHolder(tip="记录编号", type=int)})
)
async def del_challenge(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    now = datetime.now()
    clan = _check_clan(bm)
    ch = bm.get_challenge(args.E, 1, now)
    if not ch:
        raise NotFoundError(f"未找到出刀记录E{args.E}")
    if ch["uid"] != ctx["user_id"]:
        _check_admin(ctx, "才能删除其他人的记录")
    bm.del_challenge(args.E, 1, now)
    await bot.send(
        ctx, f"{clan['name']}已删除{ms.at(ch['uid'])}的出刀记录E{args.E}", at_sender=True
    )


# TODO 将预约信息转至数据库
SUBSCRIBE_PATH = os.path.expanduser("~/.hoshino/clanbattle_sub/")
SUBSCRIBE_MAX = [99, 6, 6, 6, 6, 6]
SUBSCRIBE_TREE_KEY = "0"
LOCK_KEY = "lock"
os.makedirs(SUBSCRIBE_PATH, exist_ok=True)


def _load_sub(gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf8") as f:
            return json.load(f)
    else:
        return {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],
            SUBSCRIBE_TREE_KEY: [],
            LOCK_KEY: [],
        }


def _save_sub(sub, gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    with open(filename, "w", encoding="utf8") as f:
        json.dump(sub, f, ensure_ascii=False)


def _gen_namelist_text(
    bm: BattleMaster, uidlist: List[int], memolist: List[str] = None, do_at=False
):
    if do_at:
        mems = map(lambda x: str(ms.at(x)), uidlist)
    else:
        mems = map(
            lambda x: bm.get_member(x, bm.group)
            or bm.get_member(x, 0)
            or {"name": str(x)},
            uidlist,
        )
        mems = map(lambda x: x["name"], mems)
    if memolist:
        mems = list(mems)
        for i in range(len(mems)):
            if i < len(memolist) and memolist[i]:
                mems[i] = f"{mems[i]}：{memolist[i]}"
    return mems


SUBSCRIBE_TIP = 'β>预约现在可附留言(不可包含空格)\n例："!预约 5 m留言"'


@cb_cmd(
    "预约",
    ArgParser(
        usage="!预约 <Boss号> M留言",
        arg_dict={
            "": ArgHolder(tip="Boss编号", type=boss_code),
            "M": ArgHolder(tip="留言", default=""),
        },
    ),
)
async def subscribe(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    uid = ctx["user_id"]
    _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    boss = args[""]
    memo = args.M
    memo_key = "m" + str(boss)
    sub.setdefault(str(boss), [])
    slist = sub[str(boss)]
    sub.setdefault(memo_key, [None] * len(slist))
    mlist = sub[memo_key]
    if uid in slist:
        raise AlreadyExistError(f"您已经预约过{bm.int2kanji(boss)}王了")
    msg = [""]
    if len(slist) < SUBSCRIBE_MAX[boss]:
        slist.append(uid)
        mlist.append(memo)
        _save_sub(sub, bm.group)
        msg.append(
            f"已为您预约{bm.int2kanji(boss)}王！\n该Boss当前预约人数：{len(slist)}\n{SUBSCRIBE_TIP}"
        )
    else:
        msg.append(f"预约失败：{bm.int2kanji(boss)}王预约人数已达上限{SUBSCRIBE_MAX[boss]}")
    msg.extend(_gen_namelist_text(bm, slist, mlist))
    await bot.send(ctx, "\n".join(msg), at_sender=True)


@cb_cmd(
    ("取消预约", "预约取消"),
    ArgParser(
        usage="!取消预约 <Boss号>", arg_dict={"": ArgHolder(tip="Boss编号", type=boss_code)}
    ),
)
async def unsubscribe(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    uid = ctx["user_id"]
    _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    boss = args[""]
    sub.setdefault(str(boss), [])
    slist = sub[str(boss)]
    memo_key = "m" + str(boss)
    sub.setdefault(memo_key, [None] * len(slist))
    mlist = sub[memo_key]
    if uid not in slist:
        raise NotFoundError(f"您没有预约{bm.int2kanji(boss)}王")
    i = slist.index(uid)
    slist.pop(i)
    mlist.pop(i)
    _save_sub(sub, bm.group)
    msg = [f"\n已为您取消预约{bm.int2kanji(boss)}王！\n该Boss当前预约人数：{len(slist)}"]
    msg.extend(_gen_namelist_text(bm, slist))
    await bot.send(ctx, "\n".join(msg), at_sender=True)


async def auto_unsubscribe(bot: NoneBot, ctx: Context_T, gid, uid, boss):
    sub = _load_sub(gid)
    slist = sub[str(boss)]
    memo_key = "m" + str(boss)
    sub.setdefault(memo_key, [None] * len(slist))
    mlist = sub[memo_key]
    if uid not in slist:
        return
    i = slist.index(uid)
    slist.pop(i)
    mlist.pop(i)
    _save_sub(sub, gid)
    await bot.send(ctx, f"已为{ms.at(uid)}自动取消{BattleMaster.int2kanji(boss)}王的订阅")


async def call_subscribe(bot: NoneBot, ctx: Context_T, round_: int, boss: int):
    bm = BattleMaster(ctx["group_id"])
    msg = []
    sub = _load_sub(bm.group)
    slist = sub.get(str(boss), [])
    mlist = sub.get("m" + str(boss), [])
    tlist = sub.get(SUBSCRIBE_TREE_KEY, [])
    if slist:
        msg.append(f"您们预约的老{BattleMaster.int2kanji(boss)}出现啦！")
        msg.extend(_gen_namelist_text(bm, slist, mlist, do_at=True))
    if slist and tlist:
        msg.append("==========")
    if tlist:
        msg.append(f"以下成员可以下树了")
        msg.extend(map(lambda x: str(ms.at(x)), tlist))
        tlist.clear()
        _save_sub(sub, bm.group)
    if msg:
        await bot.send(ctx, "\n".join(msg), at_sender=False)  # do not at the sender


@cb_cmd(("查询预约", "预约查询", "查看预约", "预约查看"), ArgParser("!查询预约"))
async def list_subscribe(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    msg = [f"\n{clan['name']}当前预约情况："]
    sub = _load_sub(bm.group)
    for boss in range(1, 6):
        slist = sub.get(str(boss), [])
        mlist = sub.get("m" + str(boss), [])
        msg.append(f"========\n老{bm.int2kanji(boss)}: {len(slist)}人")
        msg.extend(_gen_namelist_text(bm, slist, mlist))
    await bot.send(ctx, "\n".join(msg), at_sender=True)


@cb_cmd(
    ("清空预约", "预约清空", "清理预约", "预约清理"),
    ArgParser("!清空预约", arg_dict={"": ArgHolder(tip="Boss编号", type=boss_code)}),
)
async def clear_subscribe(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    _check_admin(ctx, "才能清理预约队列")
    sub = _load_sub(bm.group)
    boss = args[""]
    slist = sub[str(boss)]
    mlist = sub.get("m" + str(boss), [])
    if slist:
        slist.clear()
        mlist.clear()
        _save_sub(sub, bm.group)
        await bot.send(ctx, f"{bm.int2kanji(boss)}王预约队列已清空", at_sender=True)
    else:
        raise NotFoundError(f"无人预约{bm.int2kanji(boss)}王")


@cb_cmd(("挂树", "上树"), ArgParser("!挂树"))
async def add_sos(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    uid = ctx["user_id"]
    clan = _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    sub.setdefault(SUBSCRIBE_TREE_KEY, [])
    if uid in sub[SUBSCRIBE_TREE_KEY]:
        raise AlreadyExistError("您已在树上")
    sub[SUBSCRIBE_TREE_KEY].append(uid)
    _save_sub(sub, bm.group)
    msg = [
        "\n您已上树，本Boss被击败时将会通知您",
        f"目前{clan['name']}树上共{len(sub[SUBSCRIBE_TREE_KEY])}人",
    ]
    msg.extend(_gen_namelist_text(bm, sub[SUBSCRIBE_TREE_KEY]))
    await bot.send(ctx, "\n".join(msg), at_sender=True)


@cb_cmd(("查树",), ArgParser("!查树"))
async def list_sos(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    sub = _load_sub(bm.group)
    slist = sub.get(SUBSCRIBE_TREE_KEY, [])
    msg = [f"\n目前{clan['name']}树上共{len(sub[SUBSCRIBE_TREE_KEY])}人"]
    msg.extend(_gen_namelist_text(bm, slist))
    await bot.send(ctx, "\n".join(msg), at_sender=True)


@cb_cmd(("锁定", "申请出刀"), ArgParser("!锁定"))
async def lock_boss(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    _check_clan(bm)
    _check_member(bm, ctx["user_id"], bm.group)
    sub = _load_sub(bm.group)
    slist = sub.get(LOCK_KEY, [])
    if slist:
        uid, ts = slist[0]
        time = datetime.fromtimestamp(ts)
        mem = (
            bm.get_member(uid, bm.group) or bm.get_member(uid, 0) or {"name": str(uid)}
        )
        delta = datetime.now() - time
        delta = timedelta(seconds=round(delta.total_seconds()))  # ignore miliseconds
        msg = f"\n锁定失败：{mem['name']}已于{delta}前锁定了Boss"
        await bot.send(ctx, msg, at_sender=True)
    else:
        uid = ctx["user_id"]
        time = datetime.now()
        sub[LOCK_KEY] = [(uid, time.timestamp())]
        _save_sub(sub, bm.group)
        msg = f"已锁定Boss"
        await bot.send(ctx, msg, at_sender=True)


@cb_cmd(("解锁",), ArgParser("!解锁"))
async def unlock_boss(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    _check_clan(bm)
    sub = _load_sub(bm.group)
    slist = sub.get(LOCK_KEY, [])
    if slist:
        uid, ts = slist[0]
        time = datetime.fromtimestamp(ts)
        if uid != ctx["user_id"]:
            mem = (
                bm.get_member(uid, bm.group)
                or bm.get_member(uid, 0)
                or {"name": str(uid)}
            )
            delta = datetime.now() - time
            delta = timedelta(
                seconds=round(delta.total_seconds())
            )  # ignore miliseconds
            _check_admin(ctx, f"才能解锁其他人\n解锁失败：{mem['name']}于{delta}前锁定了Boss")
            sub = _load_sub(bm.group)  # await后重新加载，避免协程间的不安全问题
        sub[LOCK_KEY] = []
        _save_sub(sub, bm.group)
        msg = f"\nBoss已解锁"
        await bot.send(ctx, msg, at_sender=True)
    else:
        msg = "\n无人锁定Boss"
        await bot.send(ctx, msg, at_sender=True)


async def auto_unlock_boss(bot: NoneBot, ctx: Context_T, bm: BattleMaster):
    sub = _load_sub(bm.group)
    slist = sub.get(LOCK_KEY, [])
    if slist:
        uid, ts = slist[0]
        time = datetime.fromtimestamp(ts)
        if uid != ctx["user_id"]:
            mem = (
                bm.get_member(uid, bm.group)
                or bm.get_member(uid, 0)
                or {"name": str(uid)}
            )
            delta = datetime.now() - time
            delta = timedelta(
                seconds=round(delta.total_seconds())
            )  # ignore miliseconds
            msg = f"⚠️{mem['name']}于{delta}前锁定了Boss，您出刀前未申请锁定！"
            await bot.send(ctx, msg, at_sender=True)
        else:
            sub[LOCK_KEY] = []
            _save_sub(sub, bm.group)
            msg = f"\nBoss已自动解锁"
            await bot.send(ctx, msg, at_sender=True)


@cb_cmd(("进度", "进度查询", "查询进度", "进度查看", "查看进度", "状态"), ArgParser(usage="!进度"))
async def show_progress(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    r, b, hp = bm.get_challenge_progress(1, datetime.now())
    max_hp, score_rate = bm.get_boss_info(r, b, clan["server"])
    msg = _gen_progress_text(clan["name"], r, b, hp, max_hp, score_rate)
    await bot.send(ctx, "\n" + msg, at_sender=True)


@cb_cmd("伤害统计", ArgParser(usage="!伤害统计"))
async def stat_damage(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    now = datetime.now()
    clan = _check_clan(bm)
    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_damage(1, now)

    yn = len(stat)
    if not yn:
        await bot.send(ctx, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    stat.sort(key=lambda x: x[3][0], reverse=True)
    name = [s[2] for s in stat]
    y_pos = list(range(yn))
    y_size = 0.3 * yn + 1.0
    unit = 1e4
    unit_str = "w"

    # convert to pre-sum
    for s in stat:
        d = s[3]
        d[0] = 0
        for i in range(2, 6):
            d[i] += d[i - 1]
    pre_sum_dmg = [[s[3][b] for s in stat] for b in range(6)]

    # generate statistic figure
    fig, ax = plt.subplots()
    fig.set_size_inches(10, y_size)
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战伤害统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel("伤害")
    colors = ["#00a2e8", "#22b14c", "#b5e61d", "#fff200", "#ff7f27", "#ed1c24"]
    bars = [
        ax.barh(y_pos, pre_sum_dmg[b], align="center", color=colors[b])
        for b in range(5, -1, -1)
    ]
    bars.reverse()
    ax.ticklabel_format(axis="x", style="plain")
    for b in range(1, 6):
        for i, rect in enumerate(bars[b]):
            x = (rect.get_width() + bars[b - 1][i].get_width()) / 2
            y = rect.get_y() + rect.get_height() / 2
            d = pre_sum_dmg[b][i] - pre_sum_dmg[b - 1][i]
            if d > unit:
                ax.text(x, y, f"{d/unit:.0f}{unit_str}", ha="center", va="center")
    plt.subplots_adjust(
        left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size
    )
    pic = util.fig2b64(plt)
    plt.close()

    await bot.send(ctx, ms.image(pic), at_sender=True)


@cb_cmd(("统计", "分数统计"), ArgParser(usage="!分数统计"))
async def stat_score(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    now = datetime.now()
    clan = _check_clan(bm)
    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_score(1, now)
    stat.sort(key=lambda x: x[3], reverse=True)

    if not len(stat):
        await bot.send(ctx, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    # msg = [ f"\n{yyyy}年{mm}月会战{clan['name']}分数统计：" ]
    # for _, _, name, score in stat:
    #     score = f'{score:,d}'           # 数字太多会被腾讯ban，用逗号分隔
    #     blank = '  ' * (11-len(score))  # QQ字体非等宽，width(空格*2) == width(数字*1)
    #     msg.append(f"{blank}{score}分 | {name}")

    # generate statistic figure
    fig, ax = plt.subplots()
    score = list(map(lambda i: i[3], stat))
    yn = len(stat)
    name = list(map(lambda i: i[2], stat))
    y_pos = list(range(yn))

    if score[0] >= 1e8:
        unit = 1e8
        unit_str = "e"
    else:
        unit = 1e4
        unit_str = "w"

    y_size = 0.3 * yn + 1.0
    fig.set_size_inches(10, y_size)
    bars = ax.barh(y_pos, score, align="center")
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战分数统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel("分数")
    ax.ticklabel_format(axis="x", style="plain")
    for rect in bars:
        w = rect.get_width()
        ax.text(
            w,
            rect.get_y() + rect.get_height() / 2,
            f"{w/unit:.2f}{unit_str}",
            ha="left",
            va="center",
        )
    plt.subplots_adjust(
        left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size
    )
    pic = util.fig2b64(plt)
    plt.close()

    await bot.send(ctx, ms.image(pic), at_sender=True)


async def _do_show_remain(
    bot: NoneBot, ctx: Context_T, args: ParseResult, at_user: bool
):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    if at_user:
        _check_admin(ctx, "才能催刀。您可以用【!查刀】查询余刀")
    rlist = bm.list_challenge_remain(1, datetime.now())
    rlist.sort(key=lambda x: x[3] + x[4], reverse=True)
    msg = [f"\n{clan['name']}今日余刀："]
    for uid, _, name, r_n, r_e in rlist:
        if r_n or r_e:
            msg.append(f"剩{r_n}刀 补时{r_e}刀 | {ms.at(uid) if at_user else name}")
    if len(msg) == 1:
        await bot.send(ctx, f"今日{clan['name']}所有成员均已下班！各位辛苦了！", at_sender=True)
    else:
        msg.append("若有负数说明报刀有误 请注意核对\n使用“!出刀记录 @qq”可查看详细记录")
        if at_user:
            msg.append("=========\n在？阿sir喊你出刀啦！")
        await bot.send(ctx, "\n".join(msg), at_sender=True)


@cb_cmd("查刀", ArgParser(usage="!查刀"))
async def list_remain(bot: NoneBot, ctx: Context_T, args: ParseResult):
    await _do_show_remain(bot, ctx, args, at_user=False)


@cb_cmd("催刀", ArgParser(usage="!催刀"))
async def urge_remain(bot: NoneBot, ctx: Context_T, args: ParseResult):
    await _do_show_remain(bot, ctx, args, at_user=True)


@cb_cmd(
    "出刀记录",
    ArgParser(
        usage="!出刀记录 (@qq)", arg_dict={"@": ArgHolder(tip="qq号", type=int, default=0)}
    ),
)
async def list_challenge(bot: NoneBot, ctx: Context_T, args: ParseResult):
    bm = BattleMaster(ctx["group_id"])
    clan = _check_clan(bm)
    now = datetime.now()
    zone = bm.get_timezone_num(clan["server"])
    uid = args["@"] or args.at
    if uid:
        mem = _check_member(bm, uid, bm.group, "公会内无此成员")
        challen = bm.list_challenge_of_user_of_day(mem["uid"], mem["alt"], now, zone)
    else:
        challen = bm.list_challenge_of_day(clan["cid"], now, zone)

    msg = [f'{clan["name"]}出刀记录：\n编号|出刀者|周目|Boss|伤害|标记']
    challenstr = "E{eid:0>3d}|{name}|r{round}|b{boss}|{dmg: >7,d}{flag_str}"
    for c in [dict(i) for i in challen]:
        mem = bm.get_member(c["uid"], c["alt"])
        c["name"] = mem["name"] if mem else c["uid"]
        flag = c["flag"]
        c["flag_str"] = (
            "|补时"
            if flag & bm.EXT
            else "|尾刀"
            if flag & bm.LAST
            else "|掉线"
            if flag & bm.TIMEOUT
            else "|通常"
        )
        msg.append(challenstr.format_map(c))
    await bot.send(ctx, "\n".join(msg))


from .dao.sqlitedao import PlanDamage, MemberDao

PD = PlanDamage()
MD = MemberDao()


@cb_cmd(
    "预估",
    ArgParser(
        usage="!预估",
        arg_dict={
            "": ArgHolder(tip="伤害", type=damage_int),
            "B": ArgHolder(tip="boss编号", type=int),
            "D": ArgHolder(tip="刀种类", type=int),
            "@": ArgHolder(tip="QQ", type=int, default=0),
        },
    ),
)
async def uploadPredit(bot: NoneBot, ctx: Context_T, args: ParseResult):
    alt = ctx["group_id"]
    uid = args["@"] or args.at or ctx["user_id"]
    damage = args["X"]
    boss = args["B"]
    type = args["D"]

    if uid != ctx["user_id"]:
        _check_admin(ctx)
    id = PD.add(uid=uid, alt=alt, damage=damage, boss=boss, type=type)
    await bot.send(ctx, f"您的预估伤害编号为P{id}")


@cb_cmd(
    "查预估",
    ArgParser(
        usage="!查预估",
        arg_dict={
            "P": ArgHolder(tip="预估编号", type=int, default=0),
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "B": ArgHolder(tip="boss编号", type=int, default=0),
            "D": ArgHolder(tip="刀种类", type=int, default=0),
        },
    ),
)
async def readPredit(bot: NoneBot, ctx: Context_T, args: ParseResult):
    alt = ctx["group_id"]
    uid = args["@"] or args.at or None
    pid = args["P"] or None
    boss = args["B"] or None
    type = args["D"] or None

    read = PD.read(pid=pid, uid=uid, alt=alt, type=type, boss=boss)
    newRead = []
    for i in [dict(i) for i in read]:
        i["name"] = MD.find_one(uid=i["uid"], alt=i["alt"])["name"]
        newRead.append(i)
    await bot.send(
        ctx,
        "\n".join(
            [
                "{pid}.{name}(QQ:{uid})\n- 伤害:{dmg:>7,d}\n- BOSS ID:{boss}\n- 刀种类:{type}".format(
                    **i
                )
                for i in newRead
            ]
        ),
    )


@cb_cmd(
    "删预估",
    ArgParser(
        usage="!删预估",
        arg_dict={
            "P": ArgHolder(tip="预估编号", type=int, default=0),
            "@": ArgHolder(tip="qq号", type=int, default=0),
            "B": ArgHolder(tip="boss编号", type=int, default=0),
            "D": ArgHolder(tip="刀种类", type=int, default=0),
            "Y": ArgHolder(tip="确认", type=int, default=0),
        },
    ),
)
async def deletePredit(bot: NoneBot, ctx: Context_T, args: ParseResult):
    alt = ctx["group_id"]
    uid = args["@"] or args.at or None
    pid = args["P"] or None
    boss = args["B"] or None
    type = args["D"] or None

    if uid != ctx["user_id"]:
        _check_admin(ctx)

    read = PD.read(pid=pid, uid=uid, alt=alt, type=type, boss=boss)
    if len(read) >= 5 and not args["Y"]:
        raise PermissionError("删除记录超过5条,请在指令后添加Y1来确认")

    PD.delete(pid=pid, uid=uid, alt=alt, type=type, boss=boss)
    await bot.send(ctx, f"已删除{len(read)}条记录")
