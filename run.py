import hoshino
import asyncio

bot = hoshino.init()
app = bot.asgi

if __name__ == '__main__':
    bot.run(
    # 请添加以下三个额外参数
    # 不要忘记 import asyncio
    debug=False,
    use_reloader=False,
    loop=asyncio.get_event_loop())
