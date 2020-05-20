import asyncio

import config
import hoshino

bot = hoshino.init(config)
app = bot.asgi

if __name__ == '__main__':
    bot.run(
        debug=False,
        use_reloader=False,
        loop=asyncio.get_event_loop(),
    )
