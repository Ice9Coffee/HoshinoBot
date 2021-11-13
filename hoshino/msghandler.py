from hoshino import CanceledException, message_preprocessor, trigger
from hoshino.typing import CQEvent

@message_preprocessor
async def handle_message(bot, event: CQEvent, _):

    if event.detail_type != 'group' and event.detail_type != 'guild':
        return

    service_funcs = []
    for t in trigger.chain:
        service_funcs.extend(t.find_handler(event))

    if not service_funcs:
        return  # triggered nothing.

    for service_func in service_funcs:

        if service_func.only_to_me and not event['to_me']:
            continue  # not to me, ignore.

        if not service_func.sv._check_all(event):
            continue  # permission denied.

        service_func.sv.logger.info(f'Message {event.message_id} triggered {service_func.__name__}.')
        try:
            await service_func.func(bot, event)
        except CanceledException:
            raise
        except Exception as e:
            service_func.sv.logger.error(f'{type(e)} occured when {service_func.__name__} handling message {event.message_id}.')
            service_func.sv.logger.exception(e)
        raise CanceledException('Handled by Hoshino')
        # exception raised, no need for break
