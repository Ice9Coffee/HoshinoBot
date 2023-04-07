import asyncio
import importlib

from hoshino import Service, priv, sucmd, get_bot
from hoshino.config import twitter as cfg
from hoshino.typing import MessageSegment as CommandSession

sv = Service("twitter-poller", use_priv=priv.SU, manage_priv=priv.SU, visible=False)
bot = get_bot()
daemon = None

from .follow import follow_stream

@bot.on_startup
async def start_daemon():
    global daemon

    loop = asyncio.get_event_loop()
    daemon = loop.create_task(stream_daemon(follow_stream))


async def stream_daemon(stream_func):
    while True:
        try:
            await stream_func()
        except (KeyboardInterrupt, asyncio.CancelledError):
            sv.logger.info("Twitter stream daemon exited.")
            raise
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f"Error {type(e)} Occurred in twitter stream. Restarting stream in 1 min.")
            await asyncio.sleep(60)


@sucmd("reload-twitter-stream-daemon", force_private=False, aliases=("重启转推", "重载转推"))
async def reload_twitter_stream_daemon(session: CommandSession):
    try:
        daemon.cancel()
        importlib.reload(cfg)
        await start_daemon()
        await session.send("ok")
    except Exception as e:
        sv.logger.exception(e)
        await session.send(f"Error: {type(e)}")
