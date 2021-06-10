import time
import nonebot

from nonebot import get_bot
from nonebot import MessageSegment
from nonebot import permission as perm
from .data import Question
from hoshino import R, Service, priv
from hoshino.typing import CQEvent
answers = {}
sv = Service('QA', manage_priv=priv.ADMIN, enable_on_default=True, visible=True)

def union(group_id, user_id):
    return (group_id << 32) | user_id


# recovery from database
for qu in Question.select():
    if qu.quest not in answers:
        answers[qu.quest] = {}
    answers[qu.quest][union(qu.rep_group, qu.rep_member)] = qu.answer


@sv.on_message('group')
async def handle(bot, context):
    message = context['raw_message']
    if message.startswith('我问'):
        msg = message[2:].split('你答', 1)
        if len(msg) == 1:
            await bot.send(context, '发送“我问xxx你答yyy”我才能记住')
            return
        q, a = msg
        if q not in answers:
            answers[q] = {}
        answers[q][union(context['group_id'], context['user_id'])] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=context['user_id'],
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=True)
        return
    elif message.startswith('大家问') or message.startswith('有人问'):
        if not priv.check_priv(context, require=priv.ADMIN):
            await bot.send(context, f'只有管理员才可以用{message[:3]}')
            return
        msg = message[3:].split('你答', 1)
        if len(msg) == 1:
            await bot.send(context, f'发送“{message[:3]}xxx你答yyy”我才能记住', at_sender=False)
            return
        q, a = msg
        if q not in answers:
            answers[q] = {}
        answers[q][union(context['group_id'], 1)] = a
        Question.replace(
            quest=q,
            rep_group=context['group_id'],
            rep_member=1,
            answer=a,
            creator=context['user_id'],
            create_time=time.time(),
        ).execute()
        await bot.send(context, f'好的我记住了', at_sender=True)
        return
    elif message.startswith('不要回答'):
        q = context['raw_message'][4:]
        ans = answers.get(q)
        if ans is None:
            await bot.send(context, f'我不记得有这个问题', at_sender=False)
            return

        specific = union(context['group_id'], context['user_id'])
        a = ans.get(specific)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == context['user_id'],
            ).execute()
            del ans[specific]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答“{a}”了', at_sender=False)
            return

        if not sv.check_priv(context, required_priv=priv.ADMIN):
            await bot.send(context, f'只有管理员可以删除别人的问题', at_sender=False)
            return

        wild = union(context['group_id'], 1)
        a = ans.get(wild)
        if a:
            Question.delete().where(
                Question.quest == q,
                Question.rep_group == context['group_id'],
                Question.rep_member == 1,
            ).execute()
            del ans[wild]
            if not ans:
                del answers[q]
            await bot.send(context, f'我不再回答“{a}”了', at_sender=True)
            return
    elif message == ('查看qa') or message == ('查看QA'):
        if priv.check_priv(context, priv.ADMIN):
            gid = context.get('group_id',1)
            msg = [f"群{gid}问答一览："]
            i=0
            for b in Question.select().where(Question.rep_group == context['group_id']):
                i=i+1
                msg.append(f"{b.quest}|{b.answer}")  
                if i%10==0:
                    await bot.send(context, '\n'.join(msg))
                    msg = [f"第{(i//10)+1}页："]
            await bot.send(context, '\n'.join(msg))
            return


@sv.on_message('group')
async def answer(bot, context):
    ans = answers.get(context['raw_message'])
    if ans:
        # 回复优先级，有人问>我问
        a = ans.get(union(context['group_id'], 1))
        if a:
            await bot.send(context, f'{a}', at_sender=False)
            return
        else:
            a = ans.get(union(context['group_id'], context['user_id']))
            if a:
                await bot.send(context, f'{a}', at_sender=False)
                return