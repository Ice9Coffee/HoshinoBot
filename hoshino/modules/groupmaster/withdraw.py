from hoshino import Service, priv, logger

sv = Service('撤回', help_='撤回消息', visible=False, manage_priv=priv.SUPERUSER)


@sv.on_keyword("撤回")
async def withdraw(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '群管才能使用撤回命令', at_sender=True)
        return
    else:
        if ev.message[0].type == 'reply':
            msg_id = str(ev.message[0].data['id'])
            if msg_id is None:
                return
            else:
                try:
                    await bot.delete_msg(self_id=ev['self_id'], message_id=msg_id)
                    print(f'撤回了消息{msg_id}')
                except Exception as e:
                    print('[ERROR]撤回失败')
                    logger.error(e)
