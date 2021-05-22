from hoshino import CanceledException, message_preprocessor, trigger
from hoshino.typing import CQEvent


@message_preprocessor
async def handle_message(bot, event: CQEvent, _):

    if event.detail_type != 'group':
        return

    for t in trigger.chain:
        service_func = t.find_handler(event)
        if service_func:
            trigger_name = t.__class__.__name__
            break

    if not service_func:
        return  # triggered nothing.
    service_func.sv.logger.info(f'Message {event.message_id} triggered {service_func.__name__} by {trigger_name}.')

    if service_func.only_to_me and not event['to_me']:
        return  # not to me, ignore.

    if not service_func.sv._check_all(event):
        return  # permission denied.

    try:
        await service_func.func(bot, event)
    except CanceledException:
        raise
    except Exception as e:
        service_func.sv.logger.error(f'{type(e)} occured when {service_func.__name__} handling message {event.message_id}.')
        service_func.sv.logger.exception(e)
    raise CanceledException(f'Handled by {trigger_name} of Hoshino')
